import os
import re
import sublime

from .latex_cwl_completions import get_cwl_env_completions
from .latex_fill_all import LatexFillAllPlugin

from .utils import analysis
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root
from .utils.sublime_utils import move_cursor_relative, move_cursor_vertical

BEGIN_END_BEFORE_REGEX = re.compile(r"([^{}\[\]]*)\{(?:\][^]]*\[)*(?:nigeb|dne)\\")
"""
regex pattern to detect that the cursor is predecended by a \\begin{
"""


def get_own_environments(ana):
    return ana.filter_commands(["newenvironment", "renewenvironment"])


def get_own_env_auto_completion(tex_root):
    ana = analysis.get_analysis(tex_root)
    if not ana:
        return []

    kind = (sublime.KIND_ID_NAMESPACE, "e", "Environment")
    return [
        sublime.CompletionItem(
            trigger=e.args,
            annotation="local",
            completion=e.args,
            kind=kind,
            details=f"from {os.path.basename(e.file_name)}",
        )
        for e in get_own_environments(ana)
    ]


class EnvLatexFillAllPlugin(LatexFillAllPlugin):
    def get_auto_completions(self, view, prefix, line):
        tex_root = get_tex_root(view)
        if not tex_root:
            return []

        return get_own_env_auto_completion(tex_root) + get_cwl_env_completions(tex_root)

    def get_completions(self, view, prefix, line):
        display = []
        values = []

        tex_root = get_tex_root(view)
        if not tex_root:
            return []

        completions = get_own_env_auto_completion(tex_root) + get_cwl_env_completions(tex_root)

        for c in completions:
            display.append(
                sublime.QuickPanelItem(trigger=c.trigger, annotation=c.annotation, kind=c.kind)
            )
            values.append(c.completion or c.trigger)

        return (display, values)

    def on_selection(self, view, insert_text, should_complete):
        # Do nothing the fill helper was called to replace the content of a command
        if not should_complete or not get_setting("env_autoclose_trigger", False):
            return

        # The \end{...} is added only if there is a single cursor and if the 4 characters before the cursor are "\end"
        sel = view.sel()
        take_selection = [True]*len(sel) # Indicates if we need the Region at index i will undergo autoclose of environment
        indentation = [0] * len(sel)
        for i in range(len(sel)):
            cursor = sel[i].end()

            # Determines the characters before the cursor
            before_bracket = cursor - 1 - len(insert_text)
            begin = view.substr(sublime.Region(before_bracket-4, before_bracket))

            # Returns if we should not insert the closing environment
            if begin == "\\end":
                take_selection[i] = False

        # First, move the cursor after the {}
        move_cursor_relative(sel, 1, take_selection)

        # Insert the \end{...}
        text_insert = f"\n\\end{{{insert_text}}}"
        view.run_command("insert", {"characters": text_insert})

        # Place the cursor at the end of the line containing the \begin{...}
        move_cursor_vertical(view, sel, -1, take_cursor=take_selection)

        # Add a \n\t for correct indentation
        view.run_command("insert", {"characters": "\n\t"})

    def matches_line(self, line):
        return bool(BEGIN_END_BEFORE_REGEX.match(line))

    def is_enabled(self):
        return get_setting("env_auto_trigger", True)
