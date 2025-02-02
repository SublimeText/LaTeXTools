import re
import sublime

from .latex_fill_all import FillAllHelper
from .utils import analysis
from .utils.cache import cache_local
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

GLO_LINE_RE = re.compile(r"([^{}\[\]]*)\{*?(?:lp|lobmys)?slg\\", re.IGNORECASE)
ACR_LINE_RE = re.compile(r"([^{}\[\]]*)\{(?:(?:lp)?lluf|gnol|trohs)rca\\", re.IGNORECASE)


def _get_compl_type(line):
    if ACR_LINE_RE.match(line[::-1]):
        return "acr"
    # elif GLO_LINE_RE.match(line[::-1]):
    #     return "glo"
    else:
        return "glo"


def _get_acr_completion_items(ana):
    """
    Gets the glossary commands.

    Expected format of returned commands is:

        \\newacronym{key}{The Name}{The Description}
    """
    return ana.filter_commands("newacronym")


def _get_acr_auto_completions(ana):
    kind = (sublime.KIND_ID_VARIABLE, "a", "Acronym")

    return [
        sublime.CompletionItem(
            trigger=a.args, completion=a.args, annotation=a.args2, details=a.args3, kind=kind
        )
        for a in _get_acr_completion_items(ana)
    ]


def _get_acr_kbd_completions(ana):
    kind = (sublime.KIND_ID_VARIABLE, "a", "Acronym")

    display = []
    value = []

    for a in _get_acr_completion_items(ana):
        display.append(
            sublime.QuickPanelItem(trigger=a.args, annotation=a.args2, details=a.args3, kind=kind)
        )
        value.append(a.args)

    return (display, value)


def _get_glo_completion_items(ana):
    """
    Gets the glossary commands.

    Expected format of returned commands is:

        \\newglossary{key}{name={The Name} description={The Description}}
    """
    return ana.filter_commands(["newglossaryentry", "longnewglossaryentry"])


def _get_glo_auto_completions(ana):
    kind = (sublime.KIND_ID_VARIABLE, "g", "Glossary")

    return [
        sublime.CompletionItem(
            trigger=a.args,
            completion=a.args,
            annotation=_get_pgfkeys_value(a.args2, "name"),
            details=_get_pgfkeys_value(a.args2, "description"),
            kind=kind,
        )
        for a in _get_glo_completion_items(ana)
    ]


def _get_glo_kbd_completions(ana):
    kind = (sublime.KIND_ID_VARIABLE, "g", "Glossary")

    display = []
    value = []

    for a in _get_glo_completion_items(ana):
        display.append(
            sublime.QuickPanelItem(
                trigger=a.args,
                annotation=_get_pgfkeys_value(a.args2, "name"),
                details=_get_pgfkeys_value(a.args2, "description"),
                kind=kind,
            )
        )
        value.append(a.args)

    return (display, value)


def _get_pgfkeys_value(kv_str, key, strip=True):
    """
    Extract the value of a pgfkeys like string.

    I.e. a string with the format:
    k1=value1, k2={long value 2}
    """
    if not kv_str:
        return ""
    # TODO this is only heuristically over re search and
    # can still be improved
    m = re.search(key + r"\s*=\s*(\{[^\}]+\}|\w+)", kv_str)
    if not m:
        return ""
    result = m.group(1)
    if strip and result and result.startswith("{") and result.endswith("}"):
        result = result[1:-1]
    return result


class GlossaryFillAllHelper(FillAllHelper):
    def get_auto_completions(self, view, prefix, line):
        tex_root = get_tex_root(view)
        if not tex_root:
            return []

        comp_type = _get_compl_type(line)

        def make():
            ana = analysis.get_analysis(tex_root)
            if comp_type == "acr":
                return _get_acr_auto_completions(ana)
            elif comp_type == "glo":
                return _get_acr_auto_completions(ana) + _get_glo_auto_completions(ana)
            else:
                return []

        comp = cache_local(tex_root, f"glocomp_{comp_type}_ac", make)
        if comp and prefix:
            prefix = prefix.lower()
            comp = [c for c in comp if c.trigger.lower().startswith(prefix)]

        return comp

    def get_completions(self, view, prefix, line):
        tex_root = get_tex_root(view)
        if not tex_root:
            return []

        comp_type = _get_compl_type(line)

        def make():
            ana = analysis.get_analysis(tex_root)
            if comp_type == "acr":
                return _get_acr_kbd_completions(ana)
            elif comp_type == "glo":
                acr_display, acr_value = _get_acr_kbd_completions(ana)
                glo_display, glo_value = _get_glo_kbd_completions(ana)
                return (acr_display + glo_display, acr_value + glo_value)
            else:
                return []

        comp = cache_local(tex_root, f"glocomp_{comp_type}_kbd", make)
        if comp and prefix:
            prefix = prefix.lower()
            comp = [c for c in comp if c.trigger.lower().startswith(prefix)]

        return comp

    def matches_line(self, line):
        return bool(GLO_LINE_RE.match(line) or ACR_LINE_RE.match(line))

    def is_enabled(self):
        return get_setting("glossary_auto_trigger", True)
