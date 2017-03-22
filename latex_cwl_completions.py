# -*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function

import sublime
import sublime_plugin
import glob
import os
import re
import threading

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    from latex_cite_completions import (
        OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, match
    )
    from latex_ref_completions import (
        OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
    )
    import latex_input_completions
    from latex_own_command_completions import (
        get_own_command_completion, get_own_env_completion
    )
    from getRegion import getRegion
    from getTeXRoot import get_tex_root
    from latextools_utils import get_setting, analysis, utils
    from latextools_utils.parser_utils import command_to_snippet
else:
    _ST3 = True
    from .latex_cite_completions import (
        OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, match
    )
    from .latex_ref_completions import (
        OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
    )
    from . import latex_input_completions
    from .latex_own_command_completions import (
        get_own_command_completion, get_own_env_completion
    )
    from .getRegion import getRegion
    from .getTeXRoot import get_tex_root
    from .latextools_utils import get_setting, analysis, utils
    from .latextools_utils.parser_utils import command_to_snippet

__all__ = ['get_cwl_completions', 'is_cwl_available']

# Do not do completions in these environments
ENV_DONOT_AUTO_COM = [
    OLD_STYLE_CITE_REGEX,
    NEW_STYLE_CITE_REGEX,
    OLD_STYLE_REF_REGEX,
    NEW_STYLE_REF_REGEX
]

# whether the leading backslash is escaped
ESCAPE_REGEX = re.compile(r"\w*(\\\\)+([^\\]|$)")

# regex to detect that the cursor is predecended by a \begin{
BEGIN_END_BEFORE_REGEX = re.compile(
    r"([^{}\[\]]*)\{"
    r"(?:\][^{}\[\]]*\[)?"
    r"(?:nigeb|dne)\\"
)

# regex to parse a environment line from the cwl file
# only search for \end to create a list without duplicates
ENVIRONMENT_REGEX = re.compile(
    r"\\end"
    r"\{(?P<name>[^\}]+)\}"
)

# global setting to check whether the LaTeX-cwl package is available or not
CWL_COMPLETION_ENABLED = None

# global instance of CwlCompletions class
CWL_COMPLETIONS = None

# KOMA-Script classes are all in one cwl file
KOMA_SCRIPT_CLASSES = set(('class-scrartcl', 'class-scrreprt', 'class-book'))


# -- Public Methods --
def is_cwl_available(view=None):
    if CWL_COMPLETION_ENABLED is None:
        _check_if_cwl_enabled(view)
    return CWL_COMPLETION_ENABLED


# returns the cwl completions instances
def get_cwl_completions():
    plugin_loaded()
    return CWL_COMPLETIONS


class CwlCompletions(object):
    '''
    Completion manager that coordinates between between the event listener and
    the thread that does the actual parsing. It also stores the completions
    once they have been parsed.

    N.B. This class should not be instantiated directly. It is intended to
    be used a single object stored in the CWL_COMPLETION value of this module
    '''

    def __init__(self):
        self._started = False
        self._completed = False
        self._triggered = False
        self._completions = None
        self._environment_completions = None
        self._WLOCK = threading.RLock()

    # get the completions
    def get_completions(self, env=False):
        with self._WLOCK:
            if self._completed:
                self._triggered = False

                cwl_files = []
                packages = self.get_packages()
                if len(packages) == 0:
                    return []

                for package in packages:
                    if package.endswith('.cwl'):
                        cwl_file = package
                    else:
                        cwl_file = '{0}.cwl'.format(package)

                    # some hacks for particular packages that do not match
                    # the standard pattern
                    if package == 'polyglossia':
                        cwl_file = 'babel.cwl'
                    elif package in KOMA_SCRIPT_CLASSES:
                        cwl_file = 'class-scrartcl,scrreprt,scrbook.cwl'

                    if cwl_file not in cwl_files:
                        cwl_files.append(cwl_file)

                completions = []
                if env:
                    completion_dict = self._environment_completions
                else:
                    completion_dict = self._completions

                for cwl_file in cwl_files:
                    try:
                        completions.extend(completion_dict[cwl_file])
                    except KeyError:
                        # TODO - should we attempt to load the package?
                        pass
                return completions
            else:
                self._triggered = True
                if not self._started:
                    self.load_completions()
                return []

    # loads the list of currently specified cwl files
    def get_packages(self):
        packages = get_setting('cwl_list', [
            "latex-document.cwl",
            "tex.cwl",
            "latex-dev.cwl",
            "latex-209.cwl",
            "latex-l2tabu.cwl",
            "latex-mathsymbols.cwl"
        ])

        # autoload packages by scanning the document
        if get_setting('cwl_autoload', True):
            root = get_tex_root(sublime.active_window().active_view())
            if root is not None:
                doc = analysis.get_analysis(root)

                # really, there should only be one documentclass
                packages.extend([
                    'class-{0}'.format(documentclass.args)
                    for documentclass in doc.filter_commands(
                        'documentclass',
                        analysis.ONLY_PREAMBLE |
                        analysis.ONLY_COMMANDS_WITH_ARGS
                    )
                ])

                packages.extend([
                    package.args for package in doc.filter_commands(
                        'usepackage',
                        analysis.ONLY_PREAMBLE |
                        analysis.ONLY_COMMANDS_WITH_ARGS
                    )
                ])
            # TODO - Attempt to read current buffer

        return packages

    # loads all available completions on a new background thread
    # set force to True to force completions to load regardless
    # of whether they have already been loaded
    def load_completions(self, force=False):
        with self._WLOCK:
            if self._started or (self._completed and not force):
                return

            self._started = True
            t = threading.Thread(
                target=cwl_parsing_handler,
                args=(
                    self._on_completions,
                )
            )
            t.daemon = True
            t.start()

    # hack to display the autocompletions once they are available
    def _hack(self):
        sublime.active_window().run_command("hide_auto_complete")
        def hack2():
            sublime.active_window().active_view().run_command("auto_complete")
        sublime.set_timeout(hack2, 1)

    # callback when completions are loaded
    def _on_completions(self, completions, environment_completions):
        with self._WLOCK:
            self._completions = completions
            self._environment_completions = environment_completions
            self._started = False
            self._completed = True

            # if the user has tried to summon autocompletions, reload
            # now that we have some
            if self._triggered and len(self._completions) != 0:
                sublime.set_timeout(self._hack, 0)


class LatexCwlCompletion(sublime_plugin.EventListener):
    '''
    Event listener to supply cwl completions at appropriate points
    '''

    def on_query_completions(self, view, prefix, locations):
        if not is_cwl_available():
            return []

        point = locations[0]
        if not view.score_selector(point, "text.tex.latex"):
            return []

        point_before = point - len(prefix)
        char_before = view.substr(getRegion(point_before - 1, point_before))
        is_prefixed = char_before == "\\"

        line = view.substr(getRegion(view.line(point).begin(), point))
        line = line[::-1]
        is_env = bool(BEGIN_END_BEFORE_REGEX.match(line))

        # default completion level is "prefixed"
        completion_level = get_setting(
            "command_completion", "prefixed"
        )

        do_complete = {
            "never": False,
            "prefixed": is_prefixed or is_env,
            "always": True
        }.get(completion_level, is_prefixed or is_env)

        if not do_complete:
            return []

        # do not autocomplete if the leading backslash is escaped
        if ESCAPE_REGEX.match(line):
            # if there the autocompletion has been opened with the \ trigger
            # (no prefix) and the user has not enabled auto completion for the
            # scope, then hide the auto complete popup
            selector = view.settings().get("auto_complete_selector")
            if not prefix and not view.score_selector(point, selector):
                view.run_command("hide_auto_complete")
            return []

        # Do not do completions in actions
        if (
            latex_input_completions.TEX_INPUT_FILE_REGEX not in
            ENV_DONOT_AUTO_COM
        ):
            ENV_DONOT_AUTO_COM.append(
                latex_input_completions.TEX_INPUT_FILE_REGEX)

        for rex in ENV_DONOT_AUTO_COM:
            if match(rex, line) is not None:
                return []

        # load the completions for the document
        if is_env:
            completions = CWL_COMPLETIONS.get_completions(env=True) + \
                get_own_env_completion(view)
        else:
            completions = CWL_COMPLETIONS.get_completions() + \
                get_own_command_completion(view)

        # autocompleting with slash already on line
        # this is necessary to work around a short-coming in ST where having a
        # keyed entry appears to interfere with it recognising that there is a
        # \ already on the line
        #
        # NB this may not work if there are other punctuation marks in the
        # completion
        if is_prefixed:
            completions = [
                (c[0], c[1][1:]) if c[1].startswith("\\") else c
                for c in completions
            ]

        return (
            completions,
            sublime.INHIBIT_WORD_COMPLETIONS |
            sublime.INHIBIT_EXPLICIT_COMPLETIONS
        )

    # This functions is to determine whether LaTeX-cwl is installed,
    # if so, trigger auto-completion in latex buffers by '\'
    def on_activated_async(self, view):
        is_cwl_available(view)

    # used to ensure that completions are loaded whenever a LaTeX document
    # is loaded; run on_load instead of on_load_async to assure that view
    # exists / is active
    def on_load(self, view):
        if not view.score_selector(0, "text.tex.latex"):
            return

        CWL_COMPLETIONS.load_completions()

    if not _ST3:
        on_activated = on_activated_async


# -- Internal API --
# run to see if cwl completions should be enabled
CWL_PACKAGE_PATHS = []


def _create_cwl_packages_paths():
    global CWL_PACKAGE_PATHS
    CWL_PACKAGE_PATHS = [os.path.join(sublime.packages_path(), 'LaTeX-cwl')]
    if _ST3:
        # add to the front as this is most likely to exist
        CWL_PACKAGE_PATHS.insert(0, os.path.join(
            sublime.installed_packages_path(), 'LaTeX-cwl.sublime-package'
        ))
    CWL_PACKAGE_PATHS.append(
        os.path.join(sublime.packages_path(), 'User', 'cwl'))


def _check_if_cwl_enabled(view=None):
    if view is None:
        try:
            view = sublime.active_window().active_view()
        except AttributeError:
            return

    if view is None or not view.score_selector(0, "text.tex.latex"):
        return

    if get_setting('command_completion', 'prefixed', view=view) == 'never':
        return

    # Checking whether LaTeX-cwl is installed
    global CWL_COMPLETION_ENABLED
    for path in CWL_PACKAGE_PATHS:
        if os.path.exists(path):
            CWL_COMPLETION_ENABLED = True
            break
    else:
        CWL_COMPLETION_ENABLED = False
        return

    # add `\` as an autocomplete trigger
    g_settings = sublime.load_settings("Preferences.sublime-settings")
    acts = g_settings.get("auto_complete_triggers", [])

    # Whether auto trigger is already set in
    # Preferences.sublime-settings
    TEX_AUTO_COM = False
    for i in acts:
        if (
            i.get("selector") == "text.tex.latex" and
            i.get("characters") == "\\"
        ):
            TEX_AUTO_COM = True

    if not TEX_AUTO_COM:
        acts.append({
            "characters": "\\",
            "selector": "text.tex.latex"
        })
        g_settings.set("auto_complete_triggers", acts)

    # pre-load the completions
    get_cwl_completions().load_completions()


# -- Internal Parsing API --

# this is the function called by the CwlCompletions class to handle parsing
# it loads every cwl in turn and returns a dictionary mapping from the
# cwl file name to the set of parsed completions
def cwl_parsing_handler(callback):
    completion_results = {}
    environment_results = {}
    cwl_files, use_package = get_cwl_package_files()

    for cwl_file in cwl_files:
        base_name = os.path.basename(cwl_file)
        if use_package:
            try:
                s = (sublime.load_resource(cwl_file).replace("\r\n", "\n")
                     .replace("\r", "\n"))
            except IOError:
                print(
                    u'{0} does not exist or could not be accessed'.format(
                        cwl_file
                    )
                )
                continue
        else:
            if not os.path.isabs(cwl_file) and cwl_file.startswith('Package'):
                cwl_file = os.path.normpath(
                    cwl_file.replace('Package', sublime.packages_path())
                )

            try:
                s = utils.read_file_unix_endings(cwl_file)
            except IOError:
                print(
                    u'{0} does not exist or could not be accessed'.format(
                        cwl_file
                    )
                )
                continue

        completions = parse_cwl_file(base_name, s)
        completion_results[base_name] = completions

        environments = parse_cwl_file(base_name, s, parse_line_as_environment)
        environment_results[base_name] = environments

    callback(completion_results, environment_results)


# gets a list of all cwl package files available, whether in the
# sublime-package file or an exploded directory; returns a tuple
# consisting of the list of cwl files and a boolean indicating
# whether it is in a .sublime-package file or an expanded directory
if _ST3:
    def get_cwl_package_files():
        results = [
            r for r in sublime.find_resources('*.cwl')
            if (r.startswith('Packages/User/cwl/') or
                r.startswith('Packages/LaTeX-cwl/'))
        ]
        return(results, True) if results else ([], False)
else:
    def get_cwl_package_files():
        results = [
            glob.glob(os.path.join(p, '*.cwl'))
            for p in CWL_PACKAGE_PATHS
        ]

        # flatten the results
        results = [i for sublist in results for i in sublist]

        return (results, False)


def parse_line_as_environment(line):
    m = ENVIRONMENT_REGEX.match(line)
    if not m:
        return
    env_name = m.group("name")
    return env_name, env_name


def parse_line_as_command(line):
    return command_to_snippet(line)


# actually does the parsing of the cwl files
def parse_cwl_file(cwl, s, parse_line=parse_line_as_command):
    completions = []
    method = os.path.splitext(cwl)[0]

    # we need some state tracking to ignore keyval data
    # it could be useful at a later date
    KEYVAL = False
    for line in s.split('\n'):
        line = line.lstrip()
        if line == '':
            continue

        if line[0] == '#':
            if line.startswith('#keyvals') or line.startswith('#ifOption'):
                KEYVAL = True
            if line.startswith('#endkeyvals') or line.startswith('#endif'):
                KEYVAL = False

            continue

        # ignore TeXStudio's keyval structures
        if KEYVAL:
            continue

        # remove everything after the comment hash
        # again TeXStudio uses this for interesting
        # tracking purposes, but we can ignore it
        line = line.split('#', 1)[0]

        # trailing spaces aren't relevant (done here in case they precede)
        # a # char
        line = line.rstrip()

        result = parse_line(line)
        if result is None:
            continue
        keyword, insertion = result

        # pad the keyword with spaces; this is to keep the size of the
        # autocompletions consistent regardless of the returned results
        keyword = keyword.ljust(50)

        item = (u'%s\t%s' % (keyword, method), insertion)
        completions.append(item)

    return completions


# ensure that CWL_COMPLETIONS has a value
# its better to do it here because its more stable across reloads
def plugin_loaded():
    global CWL_COMPLETIONS
    _create_cwl_packages_paths()
    if CWL_COMPLETIONS is None:
        CWL_COMPLETIONS = CwlCompletions()

if not _ST3:
    plugin_loaded()
