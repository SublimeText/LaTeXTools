import re
import sublime

from .latex_fill_all import FillAllHelper
from .utils import analysis
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

_ref_special_commands = "|".join(
    [
        "",
        "eq",
        "page",
        "v",
        "V",
        "auto",
        "autopage",
        "name",
        "c",
        "C",
        "cpage",
        "Cpage",
        "namec",
        "nameC",
        "lcnamec",
        "labelc",
        "labelcpage",
        "sub",
        "f",
        "F",
        "vpage",
        "t",
        "p",
        "A",
        "B",
        "P",
        "S",
        "title",
        "headname",
        "th",
        "tocname",
    ]
)[::-1]

OLD_STYLE_REF_REGEX = re.compile(r"([^_]*_)?(?:\*?s?fer(" + _ref_special_commands + r")?)\\")

NEW_STYLE_REF_REGEX = re.compile(r"([^}]*)\{(?:\*?s?fer(" + _ref_special_commands + r")?)\\")

NEW_STYLE_REF_RANGE_REGEX = re.compile(r"([^}]*)\{(?:\}[^\}]*\{)?\*?egnarfer(egapv|v|egapc|C|c)\\")

NEW_STYLE_REF_MULTIVALUE_REGEX = re.compile(r"([^},]*)(?:,[^},]*)*\{fer(c|C|egapc|egapC)\\")

AUTOCOMPLETE_EXCLUDE_RX = re.compile(r"fer(?:" + _ref_special_commands + r")?\\?")


def get_ref_completions(view):
    """
    Find all labels

    get_ref_completions forms the guts of the parsing shared by both the
    autocomplete plugin and the quick panel command
    """
    completions = []

    # Finds labels in open files.
    window = view.window()
    if window:
        for view in window.views():
            if view.is_primary() and view.match_selector(0, "text.tex.latex"):
                view.find_all(r"\\(?:th)?label\{([^\{\}]+)\}", 0, "\\1", completions)

    # Finds labels in associated files.
    root = get_tex_root(view)
    if root:
        ana = analysis.get_analysis(root)
        if ana:
            for command in ana.filter_commands(["label", "thlabel"]):
                completions.append(command.args)

    # remove duplicates
    return set(completions)


class RefFillAllHelper(FillAllHelper):
    def get_auto_completions(self, view, prefix, line):
        # Reverse, to simulate having the regex
        # match backwards (cool trick jps btw!)
        line = line[::-1]

        # Check the first location looks like a ref, but backward
        old_style = OLD_STYLE_REF_REGEX.match(line)

        # Do not match on plain "ref" when autocompleting,
        # in case the user is typing something else
        if old_style and not prefix:
            return []

        kind = (sublime.KindId.NAVIGATION, "l", "Label")

        completions = [
            sublime.CompletionItem(trigger=c, completion=c, details=" ", kind=kind)
            for c in get_ref_completions(view)
        ]

        return completions, "{" if old_style else completions

    def get_completions(self, view, prefix, line):
        display = []
        value = []

        kind = (sublime.KindId.NAVIGATION, "l", "Label")

        for c in get_ref_completions(view):
            display.append(sublime.QuickPanelItem(trigger=c, annotation="label", kind=kind))
            value.append(c)

        return (display, value)

    def matches_line(self, line):
        return bool(
            (not line.startswith(",") or NEW_STYLE_REF_MULTIVALUE_REGEX.match(line))
            and (
                OLD_STYLE_REF_REGEX.match(line)
                or NEW_STYLE_REF_REGEX.match(line)
                or NEW_STYLE_REF_RANGE_REGEX.match(line)
            )
        )

    def matches_fancy_prefix(self, line):
        return bool(OLD_STYLE_REF_REGEX.match(line))

    def is_enabled(self):
        return get_setting("ref_auto_trigger", True)
