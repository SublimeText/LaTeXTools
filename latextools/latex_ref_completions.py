import re
import sublime

from .latex_fill_all import LatexFillAllPlugin
from .utils import analysis
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

LABELS = (
    "addxref",
    "algocfconts",
    "AMClabel",
    "Anotelabel",
    "assume",
    "asternote",
    "asternotesuperscript",
    "asternotetext",
    "beschlussthema",
    "besluitonderwerp",
    "Bnotelabel",
    "chaplabel",
    "CheckListDefaultLabel",
    "Cnotelabel",
    "compdlabel",
    "conclude",
    "culabel",
    "decisiontheme",
    "derivalabel",
    "derivlabel",
    "Dnotelabel",
    "edlabel",
    "edmakelabel",
    "Enotelabel",
    "eqlabel",
    "figlabel",
    "figureconts",
    "floatconts",
    "fltditem",
    "fnlabel",
    "folionolabel",
    "folionolabelwithstyles",
    "ftblabel",
    "fullref",
    "GDaffilitem",
    "glsxtr",
    "Glsxtr",
    "glsxtrnewnumber",
    "glsxtrnewsymbol",
    "glsxtrpl",
    "Glsxtrpl",
    "glsxtrsetglossarylabel",
    "HistLabel",
    "inlinelabel",
    "inlinelabel\\*",
    "introduce",
    "itemLabel",
    "label",
    "labelflow",
    "labelflowidn",
    "labelOP",
    "lb",
    "lba",
    "lbb",
    "lbp",
    "lbp\\*",
    "lbpa",
    "lbpa\\*",
    "lbpb",
    "lbpb\\*",
    "lbpc",
    "lbpc\\*",
    "lbpd",
    "lbpd\\*",
    "lbpsep",
    "lbu",
    "lbu\\*",
    "lbusep",
    "lbz",
    "linelabel",
    "lnl",
    "longnewglossaryentry",
    "longnewglossaryentry\\*",
    "longprovideglossaryentry",
    "makepoemlabel",
    "minilab",
    "mtoclabel",
    "namedLabel",
    "nblabel",
    "nbVlabel",
    "NDAL",
    "NDDL",
    "newabbr",
    "newabbreviation",
    "newacronym",
    "newentry",
    "newglosentrymath",
    "newglossaryentry",
    "newleipzig",
    "newnum",
    "newpmemlabel",
    "newsym",
    "newterm",
    "nllabel",
    "nocompdlabel",
    "noderivalabel",
    "noderivlabel",
    "oldlabel",
    "partlabel",
    "pglabel",
    "plabel",
    "pmemlabel",
    "poemlinelabel",
    "pplabel",
    "proseaccidental",
    "proselinelabel",
    "prosetsaccidental",
    "provideglossaryentry",
    "recordExerciseLabel",
    "RecordProperties",
    "renewleipzig",
    "safelabel",
    "SE",
    "seclabel",
    "sentencelabel",
    "skilldef",
    "slabel",
    "sreflabel",
    "step",
    "STEZA",
    "synchrolabel",
    "tablabel",
    "tableconts",
    "TE",
    "TEZA",
    "thlabel",
    "tracklabel",
    "zctarget",
    "zlabel",
    "zsavepos",
    "zsaveposx",
    "zsaveposy",
)

LABEL_PATTERN = fr"\\(?:{'|'.join(LABELS)})\{{([^\{{\}}]+)\}}"

_ref_prefixes = (
    "A"
    "|alg"
    "|app"
    "|auto"
    "|autopage"
    "|B"
    "|c"
    "|C"
    "|cpage"
    "|Cpage"
    "|eq"
    "|f"
    "|F"
    "|fig"
    "|Fig"
    "|headname"
    "|labelc"
    "|labelcpage"
    "|lcnamec"
    "|name"
    "|namec"
    "|nameC"
    "|p"
    "|P"
    "|page"
    "|S"
    "|sec"
    "|Sec"
    "|sub"
    "|t"
    "|tab"
    "|th"
    "|title"
    "|tocname"
    "|v"
    "|V"
    "|vpage"
    "|zc"
    "|zcpage"
)[::-1]

OLD_STYLE_REF_REGEX = re.compile(fr"([^_]*_)?(?:\*?s?fer(?:{_ref_prefixes})?)\\")

NEW_STYLE_REF_REGEX = re.compile(fr"([^}}]*)\{{(?:\*?s?fer(?:{_ref_prefixes})?)\\")

NEW_STYLE_REF_RANGE_REGEX = re.compile(r"([^}]*)\{(?:\}[^\}]*\{)?\*?egnarfer(egapv|v|egapc|C|c)\\")

NEW_STYLE_REF_MULTIVALUE_REGEX = re.compile(r"([^},]*)(?:,[^},]*)*\{fer(c|C|egapc|egapC)\\")

LSTSET_LABEL_REGEX = re.compile(r"label\s*=\s*([^\s,}]*)")


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
        for v in window.views():
            if v.is_primary() and v.match_selector(0, "text.tex.latex"):
                # \label, \thlabel
                v.find_all(LABEL_PATTERN, 0, r"\1", completions)
                # \lstset
                v.find_all(r"\\lstset\{[^{}]*label\s*=\s*([^\s,}]+)", 0, r"\1", completions)

    completions = set(completions)

    # Finds labels in associated files.
    ana = analysis.get_analysis(view)
    if ana:
        # Find labels
        # \label{code:label}
        for command in ana.filter_commands(LABELS):
            completions.add(command.args)

        # Find lstset labels
        # \lstset{language=Pascal, label=code:label, caption={caption text}}
        for command in ana.filter_commands("lstset"):
            match = LSTSET_LABEL_REGEX.search(command.args)
            if match:
                completions.add(match.group(1))

    return completions


class RefLatexFillAllPlugin(LatexFillAllPlugin):
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

        kind = (sublime.KIND_ID_NAVIGATION, "l", "Label")

        completions = [
            sublime.CompletionItem(trigger=c, completion=c, details=" ", kind=kind)
            for c in get_ref_completions(view)
        ]

        return completions, "{" if old_style else completions

    def get_completions(self, view, prefix, line):
        display = []
        value = []

        kind = (sublime.KIND_ID_NAVIGATION, "l", "Label")

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
