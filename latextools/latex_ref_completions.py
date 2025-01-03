from .latex_fill_all import FillAllHelper
from .utils import analysis
from .utils.logging import logger
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

import re

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
        "tocname",
    ]
)[::-1]

OLD_STYLE_REF_REGEX = re.compile(r"([^_]*_)?(?:\*?s?fer(" + _ref_special_commands + r")?)\\")

NEW_STYLE_REF_REGEX = re.compile(r"([^}]*)\{(?:\*?s?fer(" + _ref_special_commands + r")?)\\")

NEW_STYLE_REF_RANGE_REGEX = re.compile(r"([^}]*)\{(?:\}[^\}]*\{)?\*?egnarfer(egapv|v|egapc|C|c)\\")

NEW_STYLE_REF_MULTIVALUE_REGEX = re.compile(r"([^},]*)(?:,[^},]*)*\{fer(c|C|egapc|egapC)\\")

AUTOCOMPLETE_EXCLUDE_RX = re.compile(r"fer(?:" + _ref_special_commands + r")?\\?")


# recursively search all linked tex files to find all
# included \label{} tags in the document and extract
def find_labels_in_files(root, labels):
    doc = analysis.get_analysis(root)
    for command in doc.filter_commands("label"):
        labels.append(command.args)


# grab labels from all open buffers too
def find_labels_in_open_files(views, labels):
    for view in views:
        if view.match_selector(0, "text.tex.latex"):
            view.find_all(r"\\label\{([^\{\}]+)\}", 0, "\\1", labels)


# get_ref_completions forms the guts of the parsing shared by both the
# autocomplete plugin and the quick panel command
def get_ref_completions(view):
    completions = []

    window = view.window()
    if window:
        find_labels_in_open_files(window.views(), completions)

    root = get_tex_root(view)
    if root:
        logger.debug("TEX root: %s", root)
        find_labels_in_files(root, completions)

    # remove duplicates
    return list(set(completions))


# called by LatextoolsFillAllCommand; provides a list of labels
# for any ref commands
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

        completions = get_ref_completions(view)

        if prefix:
            lower_prefix = prefix.lower()
            completions = [c for c in completions if lower_prefix in c.lower()]

        if old_style:
            return completions, "{"
        else:
            return completions

    def get_completions(self, view, prefix, line):
        completions = get_ref_completions(view)

        if prefix:
            lower_prefix = prefix.lower()
            completions = [c for c in completions if lower_prefix in c.lower()]

        return completions

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
