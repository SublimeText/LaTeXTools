import os
import re
import sublime

from .latex_cwl_completions import get_cwl_env_completions
from .latex_fill_all import FillAllHelper

from .utils import analysis
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

BEGIN_END_BEFORE_REGEX = re.compile(r"([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?(?:nigeb|dne)\\")
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


class EnvFillAllHelper(FillAllHelper):
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

    def matches_line(self, line):
        return bool(BEGIN_END_BEFORE_REGEX.match(line))

    def is_enabled(self):
        return get_setting("env_auto_trigger", True)
