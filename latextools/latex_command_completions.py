import os
import re
import sublime
import sublime_plugin

from . import latex_input_completions

from .latex_cite_completions import NEW_STYLE_CITE_REGEX
from .latex_cite_completions import OLD_STYLE_CITE_REGEX
from .latex_cwl_completions import command_to_snippet
from .latex_cwl_completions import get_cwl_command_completions
from .latex_env_completions import BEGIN_END_BEFORE_REGEX
from .latex_env_completions import get_own_environments
from .latex_ref_completions import NEW_STYLE_REF_REGEX
from .latex_ref_completions import OLD_STYLE_REF_REGEX

from .utils import analysis
from .utils.decorators import async_completions
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

__all__ = ["LatexCmdCompletion"]

# Do not do completions in these environments
ENV_DONOT_AUTO_COM = [
    BEGIN_END_BEFORE_REGEX,
    OLD_STYLE_CITE_REGEX,
    NEW_STYLE_CITE_REGEX,
    OLD_STYLE_REF_REGEX,
    NEW_STYLE_REF_REGEX,
]

# whether the leading backslash is escaped
ESCAPE_REGEX = re.compile(r"\w*(\\\\)+([^\\]|$)")


class NoArgs(Exception):
    pass


def get_own_operators(ana):
    return ana.filter_commands(["DeclareMathOperator"])


def get_own_operator_completions(tex_root):
    res = []

    ana = analysis.get_analysis(tex_root)
    if ana:
        kind = (sublime.KIND_ID_FUNCTION, "o", "Operator")
        for c in get_own_operators(ana):
            res.append(
                sublime.CompletionItem(
                    trigger=c.args,
                    annotation="local operator",
                    details=f"from {os.path.basename(c.file_name)}",
                    kind=kind,
                )
            )

    return res


def get_own_commands(ana):
    return ana.filter_commands(["newcommand", "renewcommand"])


def get_own_command_completions(tex_root):
    res = []

    ana = analysis.get_analysis(tex_root)
    if ana:
        kind = (sublime.KIND_ID_FUNCTION, "f", "Command")

        for c in get_own_commands(ana):
            try:
                if not c.optargs2:
                    raise NoArgs()
                arg_count = int(c.optargs2)
                has_opt = bool(c.optargs2a)
                trigger = c.args
                if has_opt:
                    trigger += f"[{c.optargs2a}]"
                    arg_count -= 1
                elif arg_count == 0:
                    raise NoArgs()
                trigger += "{arg}" * arg_count
                completion = command_to_snippet(trigger)
                if completion is None:
                    raise NoArgs()
                completion = completion[1]
            except NoArgs:
                completion = trigger = c.args + "{}"

            res.append(
                sublime.CompletionItem(
                    trigger=trigger,
                    completion=completion,
                    completion_format=sublime.COMPLETION_FORMAT_SNIPPET,
                    annotation="local",
                    details=f"from {os.path.basename(c.file_name)}",
                    kind=kind,
                )
            )

        for c in get_own_environments(ana):
            res.append(
                sublime.CompletionItem(
                    trigger=f"\\begin{{{c.args}}}",
                    completion=f"\\begin{{{c.args}}}\n\t$0\n\\end{{{c.args}}}",
                    completion_format=sublime.COMPLETION_FORMAT_SNIPPET,
                    annotation="local",
                    details=f"from {os.path.basename(c.file_name)}",
                    kind=kind,
                )
            )
            res.append(
                sublime.CompletionItem(
                    trigger=f"\\end{{{c.args}}}",
                    annotation="local",
                    details=f"from {os.path.basename(c.file_name)}",
                    kind=kind,
                )
            )

    return res


class LatexCmdCompletion(sublime_plugin.EventListener):
    _cmd_cache = {}
    _op_cache = {}

    @async_completions
    def on_query_completions(self, view, prefix, locations):
        pt = locations[0]
        if not view.match_selector(pt, "text.tex.latex"):
            return []

        reg = view.line(pt)
        reg.b = pt

        line = view.substr(reg)
        line = line[::-1]

        is_prefixed = line[len(prefix) : len(prefix) + 1] == "\\"

        # default completion level is "prefixed"
        level = get_setting("command_completion", "prefixed", view)
        if not (level == "always" or level == "prefixed" and is_prefixed):
            return []

        # do not autocomplete if the leading backslash is escaped
        if ESCAPE_REGEX.match(line):
            # if there the autocompletion has been opened with the \ trigger
            # (no prefix) and the user has not enabled auto completion for the
            # scope, then hide the auto complete popup
            selector = view.settings().get("auto_complete_selector")
            if not prefix and not view.match_selector(pt, selector):
                view.run_command("hide_auto_complete")
            return []

        # Do not do completions in actions
        if latex_input_completions.TEX_INPUT_FILE_REGEX not in ENV_DONOT_AUTO_COM:
            ENV_DONOT_AUTO_COM.append(latex_input_completions.TEX_INPUT_FILE_REGEX)

        for rex in ENV_DONOT_AUTO_COM:
            if rex.match(line) is not None:
                return []

        tex_root = get_tex_root(view)
        if not tex_root:
            return []

        if tex_root not in self._cmd_cache:
            self._cmd_cache[tex_root] = get_own_command_completions(
                tex_root
            ) + get_cwl_command_completions(tex_root)

        if view.match_selector(pt, "text.tex meta.environment.math"):
            if tex_root not in self._op_cache:
                self._op_cache[tex_root] = get_own_operator_completions(tex_root)

            return self._cmd_cache[tex_root] + self._op_cache[tex_root]

        return self._cmd_cache[tex_root]

    def on_close(self, view):
        tex_root = get_tex_root(view)
        if tex_root:
            self._cmd_cache.pop(tex_root, None)
            self._op_cache.pop(tex_root, None)

    def on_post_save_async(self, view):
        tex_root = get_tex_root(view)
        if tex_root:
            self._cmd_cache.pop(tex_root, None)
            self._op_cache.pop(tex_root, None)


def latextools_plugin_loaded():
    # add `\` as an autocomplete trigger
    prefs = sublime.load_settings("Preferences.sublime-settings")
    acts = prefs.get("auto_complete_triggers", [])

    # Whether auto trigger is already set in
    # Preferences.sublime-settings
    if not any(i.get("selector") == "text.tex.latex" and i.get("characters") == "\\" for i in acts):
        acts.append({"characters": "\\", "selector": "text.tex.latex"})
        prefs.set("auto_complete_triggers", acts)
