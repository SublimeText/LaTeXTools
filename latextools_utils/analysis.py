import os
import re
import itertools
import traceback

import sublime

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import cache, utils
    from latextools_utils.tex_directives import get_tex_root
else:
    _ST3 = True
    from . import cache, utils
    from .tex_directives import get_tex_root

if _ST3:
    strbase = str
else:
    strbase = basestring

# because we cannot natively pickle sublime.Region in ST2
# we provide the ability to pickle
if not _ST3:
    import copy_reg

    def pickle_region(region):
        return (sublime.Region, (region.a, region.b))

    copy_reg.pickle(sublime.Region, pickle_region)

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
_input_commands = ["input", "include", "subfile", "loadglsentries"]


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
            function of command->bool - should return true iff the command
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
        if isinstance(how, strbase):
            def command_filter(c):
                return c.command == how
        elif type(how) is list:
            def command_filter(c):
                return c.command in how
        elif callable(how):
            def command_filter(c):
                return how(c)
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
    if tex_root is None:
        return
    elif isinstance(tex_root, sublime.View):
        tex_root = get_tex_root(tex_root)
    elif not isinstance(tex_root, strbase):
        raise ValueError("tex_root must be a string or view")

    result = cache.cache(tex_root, "analysis",
                         lambda: analyze_document(tex_root))
    return result


def analyze_document(tex_root):
    """
    Analyzes the document

    Arguments:
    tex_root -- the path to the tex root as a string
                if you use the view instead, the tex root will be extracted
                automatically

    Returns:
    An Analysis of the view, which contains all relevant information and
    provides access methods to useful properties
    """
    if tex_root is None:
        return
    elif isinstance(tex_root, sublime.View):
        tex_root = get_tex_root(tex_root)
    elif not isinstance(tex_root, strbase):
        raise ValueError("tex_root must be a string or view")

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
        raw_content, content = _preprocess_file(file_name)
    except:
        print('Error occurred while preprocessing {0}'.format(file_name))
        traceback.print_exc()
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


def _preprocess_file(file_name):
    """
    reads and preprocesses a file, return the raw content
    and the content without comments
    """
    raw_content = utils.get_file_content(file_name, force_lf_endings=True)

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
