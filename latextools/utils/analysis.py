import copy
import itertools
import os
import regex
import sublime
import traceback

from collections.abc import Iterable
from functools import partial

from ...vendor.frozendict import frozendict

from . import utils
from .cache import cache_local
from .logging import logger
from .tex_directives import get_tex_root

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
# this regex does not capture all possibilities, but hopefully,
# all we need and can obviously be extended without losing backward
# compatibility
# regex names are:
# \command[optargs]{args}[optargs2][optargs2a]{args2}[optargs3]{args3}
# the argument names (in correct order!)
_COMMAND_ARG_NAMES = (
    "optargs",
    "args",
    "optargs2",
    "optargs2a",
    "args2",
    "optargs3",
    "args3",
)
_RE_COMMAND = regex.compile(
    r"\\(?P<command>[A-Za-z]+)(?P<star>\*?)" +  # The initial command
    # build the rest from the command arg names
    "\n".join(
        r"""
        (?:
          [ \t]*\n?[ \t]*  # optional whitespaces
          {open}
            (?P<{name}>
              (?:
                [^{open}{close}]++  # everything except recursive matches
                |  # or
                {open}
                    (?&{name})  # match recursive
                {close}
              )*
            )
          {close}
        )?
        """.format(
            name=name,
            # optional arguments are [...], normal arguments are {...}
            open=(r"\[" if name.startswith("opt") else r"\{"),
            close=(r"\]" if name.startswith("opt") else r"\}"),
        )
        for name in _COMMAND_ARG_NAMES
    ),
    flags=regex.MULTILINE | regex.UNICODE | regex.VERBOSE | regex.VERSION1,
    cache_pattern=False,
    ignore_unused=True,
)
# this regex is used to remove comments
_RE_COMMENT = regex.compile(
    r"((?<=^)|(?<=[^\\]))%.*",
    flags=regex.UNICODE | regex.VERSION1,
    cache_pattern=False,
    ignore_unused=True,
)
# the analysis will walk recursively into the included files
# i.e. the 'args' field of the command
_input_commands = ["input", "include", "subfile", "loadglsentries"]
_import_commands = [
    "import",
    "subimport",
    "includefrom",
    "subincludefrom",
    "inputfrom",
    "subinputfrom",
]


# FLAGS
def _flag():
    """get the next free flag"""
    try:
        current_flag = _flag.flag
    except AttributeError:
        current_flag = _flag.flag = 1
    _flag.flag <<= 1
    return current_flag


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
    NO_BEGIN_END_COMMANDS: lambda c: c.command != "begin" and c.command != "end",
    ONLY_COMMANDS_WITH_ARGS: lambda c: c.args is not None,
    ONLY_COMMANDS_WITH_ARG_CONTENT: lambda c: bool(c.args),
}

DEFAULT_FLAGS = NO_BEGIN_END_COMMANDS | ONLY_COMMANDS_WITH_ARGS


class FileNotAnalyzed(Exception):
    pass


class Analysis:
    def __init__(self, tex_root):
        self._tex_root = tex_root
        self._content = {}
        self._raw_content = {}

        self._all_commands = []
        self._command_cache = {}

        self._import_base_paths = {}
        self._graphics_path = None

        self.__frozen = False

        # This state is used to hold the state during the analysis
        # and will be deleted afterwards
        self._state = {}

    def tex_root(self):
        """The tex root of the analysis"""
        return self._tex_root

    def tex_base_path(self, file_path):
        """
        The folder in which the file is seen by the latex compiler.
        This is usually the folder of the tex root, but can change if
        the import package is used.
        Use this instead of the tex root path to implement functions
        like the \\input command completion.
        """
        file_path = os.path.normpath(file_path)
        try:
            return self._import_base_paths[file_path]
        except KeyError:
            return os.path.dirname(self._tex_root)

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
        return self._commands(flags)

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
        A `generator` expression producing all commands, which are preprocessed
        with the flags.
        """
        if isinstance(how, str):
            return (c for c in self._commands(flags) if c.command == how)

        elif isinstance(how, Iterable):
            return (c for c in self._commands(flags) if c.command in how)

        elif callable(how):
            return (c for c in self._commands(flags) if how(c))

        raise Exception(f"Unsupported filter type: {type(how)}")

    def graphics_paths(self):
        if self._graphics_path is None:
            result = []
            commands = self.filter_commands(["appendtographicspath", "graphicspath"])
            for com in commands:
                base_path = os.path.join(self.tex_base_path(com.file_name))
                paths = (p.rstrip("}") for p in com.args.split("{") if p)
                result.extend(
                    os.path.normpath(p if os.path.isabs(p) else os.path.join(base_path, p))
                    for p in paths
                )
            # freeze result
            self._graphics_path = result

        return self._graphics_path

    def _add_command(self, command):
        self._all_commands.append(command)

    def _extend_commands(self, commands):
        self._all_commands.extend(commands)

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
        self._command_cache[flags] = tuple(com)

    def _commands(self, flags):
        if flags not in self._command_cache:
            self._build_cache(flags)
        return self._command_cache[flags]

    def _freeze(self):
        if self.__frozen:
            return
        self._content = frozendict(**self._content)
        self._raw_content = frozendict(**self._raw_content)
        self._all_commands = tuple(c for c in self._all_commands)
        self.__frozen = True
        try:
            del self._state
        except AttributeError:
            pass

    def __copy__(self):
        return self


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
    if not tex_root:
        return
    if isinstance(tex_root, sublime.View):
        tex_root = get_tex_root(tex_root)
        if not tex_root:
            return
    elif not isinstance(tex_root, str):
        raise TypeError("tex_root must be a string or view")

    return cache_local(tex_root, "analysis", partial(analyze_document, tex_root))


def _generate_entries(m, file_name, offset=0):
    # insert all relevant information into this dict, which is based
    # on the group dict, i.e. all regex matches
    entryDict = m.groupdict()

    entryDict.update(
        {
            "file_name": file_name,
            "text": m.group(0),
            "start": offset + m.start(),
            "end": offset + m.end(),
            "region": sublime.Region(offset + m.start(), offset + m.end()),
        }
    )
    # insert the regions of the matches into the entry dict
    for k in m.groupdict().keys():
        region_name = k + "_region"
        reg = m.regs[m.re.groupindex[k]]
        entryDict[region_name] = sublime.Region(offset + reg[0], offset + reg[1])
    # create an object from the dict and insert it into the analysis
    entry = objectview(frozendict(entryDict))
    yield entry

    # recursively add commands, which are inside arguments
    for args_name in _COMMAND_ARG_NAMES:
        args_content = entryDict[args_name]
        if not args_content:
            continue
        for em in _RE_COMMAND.finditer(args_content):
            if not em:
                continue
            try:
                offset = entryDict[args_name + "_region"].begin()
            except KeyError:
                continue
            yield from _generate_entries(em, file_name, offset=offset)


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
    if not tex_root:
        return
    if isinstance(tex_root, sublime.View):
        tex_root = get_tex_root(tex_root)
        if not tex_root:
            return
    elif not isinstance(tex_root, str):
        raise TypeError("tex_root must be a string or view")

    result = _analyze_tex_file(tex_root)
    if result:
        result._freeze()
    return result


def _analyze_tex_file(
    tex_root,
    file_name=None,
    process_file_stack=[],
    ana=None,
    import_path=None,
    only_preamble=False,
):
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
        logger.error("File appears cyclic: %s\n%s", file_name, process_file_stack)
        return ana

    base_path = import_path if import_path else os.path.dirname(tex_root)

    # store import path at the base path, such that it can be accessed
    if import_path:
        if file_name in ana._import_base_paths:
            if ana._import_base_paths[file_name] != import_path:
                logger.warning(
                    "'%s' is imported twice. Cannot handle this correctly in the analysis.",
                    file_name,
                )
        else:
            ana._import_base_paths[file_name] = base_path

    # read the content from the file
    try:
        raw_content, content = _preprocess_file(file_name)
    except Exception:
        logger.error("Error occurred while preprocessing %s", file_name)
        traceback.print_exc()
        logger.info("Continuing...")
        return ana

    ana._content[file_name] = content
    ana._raw_content[file_name] = raw_content

    for m in _RE_COMMAND.finditer(content):
        # TODO maybe also handle all generated entries
        g = m.group

        # precancel if we only parse the preamble (for subfiles)
        if only_preamble and g("command") == "begin" and g("args") == "document":
            ana._state["preamble_finished"] = True
            return ana

        ana._extend_commands(_generate_entries(m, file_name))
        cmd = g("command")
        args = g("args")

        # read child files if it is an input command
        if cmd in _input_commands and args is not None:
            process_file_stack.append(file_name)
            open_file = os.path.join(base_path, args.strip('"'))
            _analyze_tex_file(tex_root, open_file, process_file_stack, ana)
            process_file_stack.pop()
            # check that we still need to analyze
            if only_preamble and ana._state.get("preamble_finished", False):
                return ana

        elif cmd in _import_commands and args is not None and g("args2") is not None:
            if cmd.startswith("sub"):
                next_import_path = os.path.join(base_path, args.strip('"'))
            else:
                next_import_path = args.strip('"')
            # normalize the path
            next_import_path = os.path.normpath(next_import_path)
            open_file = os.path.join(next_import_path, g("args2"))

            process_file_stack.append(file_name)
            _analyze_tex_file(
                tex_root,
                open_file,
                process_file_stack,
                ana,
                import_path=next_import_path,
                only_preamble=only_preamble,
            )
            process_file_stack.pop()
            # check that we still need to analyze
            if only_preamble and ana._state.get("preamble_finished", False):
                return ana

        elif cmd == "documentclass":

            # subfile support:
            # if we are not in the root file (i.e. not call from included files)
            # and have the command \documentclass[main.tex]{subfiles}
            # analyze the root file
            if tex_root != file_name and args == "subfiles":
                main_file = g("optargs")
                if not main_file:
                    continue
                main_file = os.path.join(base_path, main_file)
                process_file_stack.append(file_name)
                _analyze_tex_file(
                    main_file,
                    main_file,
                    process_file_stack,
                    ana,
                    import_path=None,
                    only_preamble=True,
                )
                process_file_stack.pop()
                try:
                    del ana._state["preamble_finished"]
                except KeyError:
                    pass

            # For given \documentclass{myclass} analyze locally available myclass.cls
            # as part of main document to load packages, commands or bibliography from.
            # resolves: issue #317
            elif args is not None:
                fn = os.path.join(base_path, os.path.splitext(args.strip('"'))[0])
                for ext in (".cls", ):
                    open_file = fn + ext
                    if os.path.isfile(open_file):
                        process_file_stack.append(file_name)
                        _analyze_tex_file(tex_root, open_file, process_file_stack, ana)
                        process_file_stack.pop()
                        break

                # check that we still need to analyze
                if only_preamble and ana._state.get("preamble_finished", False):
                    return ana

        # usepackage(local) support:
        # analyze existing local packages or stylesheets
        elif cmd == "usepackage" and args is not None:
            fn = os.path.join(base_path, os.path.splitext(args.strip('"'))[0])
            for ext in (".sty", ".tex"):
                open_file = fn + ext
                if os.path.isfile(open_file):
                    process_file_stack.append(file_name)
                    _analyze_tex_file(tex_root, open_file, process_file_stack, ana)
                    process_file_stack.pop()
                    break

            # check that we still need to analyze
            if only_preamble and ana._state.get("preamble_finished", False):
                return ana

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
            content[i] = " "
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


class objectview:
    """
    Converts an dict into an object, such that every dict entry
    is an attribute of the object
    """

    def __init__(self, d):
        self.__dict__.update(d)

    def __setattr__(self, attr, value):
        raise TypeError("cannot set value on an objectview")
