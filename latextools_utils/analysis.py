import os
import re
import codecs
import itertools

import sublime

try:
    _ST3 = True
    from ..getTeXRoot import get_tex_root
    from . import cache
except:
    _ST3 = False
    from getTeXRoot import get_tex_root
    from latextools_utils import cache

# attributes of an entry (for documentation)
"""
Attributes of an entry:

- args: the string in the args part
- args_region: the region of the args part as a sublime region in the buffer
for each regex name:
- $name$: the string in the part
- $name$_region: the region of the part

- file_name: the name of the file, in which the entry appers
- text: the full text of the entry, e.g. '\\command{args}'
- start: the start position in the buffer
- end: the end position in the buffer
- region: a sublime region containing the whole entry
"""

# regex for a latex expression
# usually it is \command[optargs]{args}
# but it can be way more complicated, e.g.
# \newenvironment{ENVIRONMENTNAME}[COUNT][OPTIONAL]{BEGIN}{END}
# this regex does not capture all posibilities, but hopefully,
# all we need and can obviously be extended without losing backward
# compatibility
# regex names are:
# \command[optargs]{args}[optargs2][optargs2a]{args2}[optargs3]{args3}
_RE_COMMAND = re.compile(
    r"\\(?P<command>[A-Za-z]+)(?P<star>\*?)\s*?"
    r"(?:\[(?P<optargs>[^\]]*)\])?\s*?"
    r"(\{(?P<args>[^\}]*)\}\s*?)?"
    r"(?:\[(?P<optargs2>[^\]]*)\])?\s*?"
    r"(?:\[(?P<optargs2a>[^\]]*)\])?\s*?"
    r"(?:\{(?P<args2>[^\}]*)\})?"
    r"(?:\[(?P<optargs3>[^\]]*)\])?\s*?"
    r"(?:\{(?P<args3>[^\}]*)\})?",
    re.MULTILINE | re.UNICODE
)
# this regex is used to remove comments
_RE_COMMENT = re.compile(
    r"((?<=^)|(?<=[^\\]))%.*",
    re.UNICODE
)
# the analysis will walk recursively into the included files
# i.e. the 'args' field of the command
_input_commands = ["input", "include", "subfile"]


# FLAGS
def _flag():
    """get the next free flag"""
    current_flag = _flag.flag
    _flag.flag <<= 1
    return current_flag
_flag.flag = 1

# dummy for no flag
ALL_COMMANDS = 0
# exclude \begin{} and \end{} commands
NO_BEGIN_END_COMMANDS = _flag()
# allows \com{args} and \com{} but not \com
ONLY_COMMANDS_WITH_ARGS = _flag()
# only allow \com{args} not \com{} or \com
ONLY_COMMANDS_WITH_ARG_CONTENT = _flag()
# only in the preamble, i.e. before \begin{document}
ONLY_PREAMBLE = _flag()

# all filter functions to filter out commands,
# which do not need a special treatment
_FLAG_FILTER = {
    NO_BEGIN_END_COMMANDS:
        lambda c: c.command != "begin" and c.command != "end",
    ONLY_COMMANDS_WITH_ARGS:
        lambda c: c.args is not None,
    ONLY_COMMANDS_WITH_ARG_CONTENT:
        lambda c: bool(c.args)
}

DEFAULT_FLAGS = NO_BEGIN_END_COMMANDS | ONLY_COMMANDS_WITH_ARGS


class FileNotAnalyzed(Exception):
    pass


class Analysis():
    def __init__(self, tex_root):
        self._tex_root = tex_root
        self._content = {}
        self._raw_content = {}

        self._all_commands = []
        self._command_cache = {}

        self._finished = False

    def tex_root(self):
        """The tex root of the analysis"""
        return self._tex_root

    def content(self, file_name):
        """
        The content of the file without comments (a string)
        """
        if file_name not in self._content:
            raise FileNotAnalyzed(file_name)
        return self._content[file_name]

    def raw_content(self, file_name):
        """
        The raw unprocessed content of the file (a string)
        """
        if file_name not in self._raw_content:
            raise FileNotAnalyzed(file_name)
        return self._raw_content[file_name]

    def rowcol(self, file_name):
        """
        Returns a rowcol function for the file with the same behavior as the
        view.rowcol function from the sublime api
        """
        return make_rowcol(self.raw_content(file_name))

    def commands(self, flags=DEFAULT_FLAGS):
        """
        Returns a list with copies of each command entry in the document

        Arguments:
        flags -- flags to filter the commands, which should for a be used over
            over filtering the commands on your own (optimization/caching).
            Possible flags are:
            NO_BEGIN_END_COMMANDS - removes all begind and end commands
                i.e.: exclude \\begin{} and \\end{} commands
            ONLY_COMMANDS_WITH_ARGS - removes all commands without arguments
                i.e.: allows \\com{args} and \\com{} but not \\com
            default flags are:
            NO_BEGIN_END_COMMANDS | ONLY_COMMANDS_WITH_ARGS

        Returns:
        A list of all commands, which are preprocessed with the flags
        """
        return _copy_entries(self._commands(flags))

    def filter_commands(self, how, flags=DEFAULT_FLAGS):
        """
        Returns a filtered list with copies of each command entry
        in the document

        Arguments:
        how -- how it should be filtered, possible types are:
            string - only commands, which equals this string
            list of string - only commands which are in this list
            function of string->bool - should return true iff the command
                should be in the result
        flags -- flags to filter the commands, which should for a be used over
            over filtering the commands on your own (optimization/caching).
            Possible flags are:
            NO_BEGIN_END_COMMANDS - removes all begin and end commands
                i.e.: exclude \\begin{} and \\end{} commands
            ONLY_COMMANDS_WITH_ARGS - removes all commands without arguments
                i.e.: allows \\com{args} and \\com{} but not \\com
            default flags are:
            NO_BEGIN_END_COMMANDS | ONLY_COMMANDS_WITH_ARGS

        Returns:
        A list of all commands, which are preprocessed with the flags
        """
        # convert the filter into a function
        if type(how) is str:
            def command_filter(c): return c.command == how
        elif type(how) is list:
            def command_filter(c): return c.command in how
        elif callable(how):
            def command_filter(c): return how(c.command)
        else:
            raise Exception("Unsupported filter type: " + str(type(how)))
        com = self._commands(flags)
        return _copy_entries(filter(command_filter, com))

    def _add_command(self, command):
        self._all_commands.append(command)

    def _build_cache(self, flags):
        com = self._all_commands
        if flags & ONLY_PREAMBLE:
            def is_not_begin_document(c):
                return not (c.command == "begin" and c.args == "document")
            com = itertools.takewhile(is_not_begin_document, com)
        for cflag in sorted(_FLAG_FILTER.keys()):
            if flags & cflag:
                f = _FLAG_FILTER[cflag]
                com = filter(f, com)
        self._command_cache[flags] = list(com)

    def _commands(self, flags):
        if flags not in self._command_cache:
            self._build_cache(flags)
        return self._command_cache[flags]


def get_analysis(tex_root):
    """
    Returns an analysis of the document using a cache

    Use this method if you want a fast result and don't mind if there
    are small changes between the analysis and the usage.
    Don't use this method if you ware looking forward in using
    the regions of the commands (it will most likely not yield proper result)
    (and is currently not supported with st2)

    Arguments:
    tex_root -- the path to the tex root as a string
                if you use the view instead, the tex root will be extracted
                automatically

    Returns:
    An Analysis of the view, which contains all relevant information and
    provides access methods to useful properties
    """
    view = tex_root  # store for the case, that the analysis have to be done
    if type(tex_root) is str or not _ST3 and type(tex_root) is unicode:
        tex_root = tex_root
    else:
        tex_root = get_tex_root(tex_root)

    try:
        result = cache.read(tex_root, "analysis")
    except cache.CacheMiss:
        result = analyze_document(view)
        # TODO
        # cannot pickle sublime.Region in st2 this is a hacky workaround
        # to remove those regions if someone is interested in the regions
        # this method is not recommended anyways
        if not _ST3:
            for c in result._all_commands:
                c.region = None
                for k in _RE_COMMAND.groupindex.keys():
                    region_name = k + "_region"
                    c.__dict__[region_name] = None
        cache.write(tex_root, "analysis", result)
    return result


def analyze_document(view):
    """
    Analyzes the document

    Arguments:
    view -- the view, which should be analyzed
            if it is a str, it will be treated as the path to the tex root

    Returns:
    An Analysis of the view, which contains all relevant information and
    provides access methods to useful properties
    """
    if view is None:
        return
    if type(view) is str or not _ST3 and type(view) is unicode:
        tex_root = view
    else:
        # if the view is dirty save it (only thread-safe on st3)
        if _ST3 and view.is_dirty():
            view.run_command("save")
        tex_root = get_tex_root(view)
    result = _analyze_tex_file(tex_root)
    return result


def _analyze_tex_file(tex_root, file_name=None, process_file_stack=[],
                      ana=None):
    # init ana and the file name
    if not ana:
        ana = Analysis(tex_root)
    if not file_name:
        file_name = tex_root
    # if the file name has no extension use ".tex"
    elif not os.path.splitext(file_name)[1]:
        file_name += ".tex"
    # normalize the path
    file_name = os.path.normpath(file_name)
    # ensure not to go into infinite recursion
    if file_name in process_file_stack:
        print("File appears cyclic: ", file_name)
        print(process_file_stack)
        return ana

    base_path, _ = os.path.split(tex_root)

    # read the content from the file
    try:
        raw_content, content = _read_file(file_name)
    except:
        return ana

    ana._content[file_name] = content
    ana._raw_content[file_name] = raw_content

    for m in _RE_COMMAND.finditer(content):
        g = m.group

        # insert all relevant information into this dict, which is based
        # on the group dict, i.e. all regex matches
        entryDict = m.groupdict()
        entryDict.update({
            "file_name": file_name,
            "text": g(0),
            "start": m.start(),
            "end": m.end(),
            "region": sublime.Region(m.start(), m.end())
        })
        # insert the regions of the matches into the entry dict
        for k in m.groupdict().keys():
            region_name = k + "_region"
            reg = m.regs[_RE_COMMAND.groupindex[k]]
            entryDict[region_name] = sublime.Region(reg[0], reg[1])
        # create an object from the dict and insert it into the analysis
        entry = objectview(entryDict)
        ana._add_command(entry)

        # read child files if it is an input command
        if g("command") in _input_commands and g("args") is not None:
            process_file_stack.append(file_name)
            open_file = os.path.join(base_path, g("args"))
            _analyze_tex_file(tex_root, open_file, process_file_stack, ana)
            process_file_stack.pop()

        # don't parse further than \end{document}
        if g("args") == "document" and g("command") == "end" or ana._finished:
            ana._finished = True
            break

    return ana


def _read_file(file_name):
    """
    reads and preprocesses a file, return the raw content
    and the content without comments
    """

    try:
        with codecs.open(file_name, "r", "utf8") as f:
            raw_content = f.read()
    except IOError as e:
        # file does not exists / permission exception
        print(str(e))
        raise
    except UnicodeDecodeError as e:
        print("UnicodeDecodeError in file {0}".format(file_name))
        raise
    except:
        print("Unexpected exception raised while reading file", file_name)
        import traceback
        traceback.print_exc()
        raise
    # replace all comments with spaces to not change the position
    # of the rest
    comments = [c for c in _RE_COMMENT.finditer(raw_content)]
    content = list(raw_content)
    for m in comments:
        for i in range(m.start(), m.end()):
            content[i] = ' '
    content = "".join(content)
    return raw_content, content


def make_rowcol(string):
    """
    Creates a rowcol function similar to the rowcol function of a view

    Arguments:
    string -- The string on which the rowcol function should hold

    Returns:
    A function similar to the rowcol function of a sublime text view
    """
    rowlens = [len(x) + 1 for x in string.split("\n")]
    rowpos = []
    acc = 0
    for i in rowlens:
        acc += i
        rowpos.append(acc)

    def rowcol(pos):
        last = 0
        for i, k in enumerate(rowpos, 0):
            if pos < k:
                return (i, pos - last)
            last = k
        return (-1, -1)
    return rowcol


class objectview(object):
    """
    Converts an dict into an object, such that every dict entry
    is an attribute of the object
    """
    def __init__(self, d):
        self.__dict__ = d

    def copy(self):
        return objectview(self.__dict__.copy())

    def __repr__(self):
        return repr(self.__dict__)


def _copy_entries(arr):
    """creates an array with a copy of each entry of arr"""
    return [c.copy() for c in arr]
