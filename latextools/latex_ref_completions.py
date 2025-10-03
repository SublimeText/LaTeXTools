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
    "|a"
    "|addtocounter"
    "|addtocounterpage"
    "|addx"
    "|aebname"
    "|aeq"
    "|Aeq"
    "|af"
    "|alg"
    "|algorithm"
    "|alias"
    "|AMC"
    "|AMCpage"
    "|AMSeq"
    "|annotation"
    "|apage"
    "|Apage"
    "|app"
    "|appendix"
    "|apx"
    "|Apx"
    "|argpage"
    "|ass"
    "|aster"
    "|auto"
    "|Auto"
    "|autopage"
    "|av"
    "|Av"
    "|aveq"
    "|Aveq"
    "|avpage"
    "|Avpage"
    "|axiom"
    "|B"
    "|b"
    "|bfull"
    "|bracket"
    "|C"
    "|c"
    "|cant"
    "|case"
    "|Chap"
    "|chap"
    "|chappage"
    "|chaprange"
    "|Chaprange"
    "|chapter"
    "|circled"
    "|col"
    "|conjecture"
    "|corollary"
    "|Cpage"
    "|cpage"
    "|crtc"
    "|crtC"
    "|crtextract"
    "|crtextractc"
    "|crthyperc"
    "|crthyperC"
    "|crtlname"
    "|crtname"
    "|crtuname"
    "|cu"
    "|d"
    "|dcto"
    "|def"
    "|definition"
    "|defn"
    "|defpage"
    "|desc"
    "|e"
    "|E"
    "|edline"
    "|edpage"
    "|enumerate"
    "|Eq"
    "|eq"
    "|eqfull"
    "|eqpage"
    "|eqrange"
    "|Eqrange"
    "|equation"
    "|ex"
    "|example"
    "|Example"
    "|examplemargin"
    "|examplename"
    "|examples"
    "|Examples"
    "|examplesname"
    "|ext"
    "|F"
    "|f"
    "|fancy"
    "|fancysub"
    "|Fig"
    "|fig"
    "|figpage"
    "|figrange"
    "|Figrange"
    "|figure"
    "|Figure"
    "|figures"
    "|Figures"
    "|Fn"
    "|fn"
    "|fnpage"
    "|fnrange"
    "|Fnrange"
    "|foot"
    "|footnote"
    "|full"
    "|fullaf"
    "|fullpage"
    "|fv"
    "|globalskills"
    "|glsxtrpage"
    "|gmif"
    "|headname"
    "|hyperget"
    "|hypergetpage"
    "|initval"
    "|item"
    "|iva"
    "|josa"
    "|josaeq"
    "|josapage"
    "|k"
    "|kC"
    "|kc"
    "|kCname"
    "|kcname"
    "|kCpage"
    "|kcpage"
    "|knamec"
    "|knameC"
    "|kpage"
    "|labelc"
    "|labelcpage"
    "|lastpage"
    "|lcnamec"
    "|ldesc"
    "|lem"
    "|lemma"
    "|line"
    "|lst"
    "|m"
    "|mExample"
    "|mexample"
    "|mtoc"
    "|n"
    "|name"
    "|Name"
    "|nameC"
    "|namec"
    "|noeq"
    "|npage"
    "|num"
    "|object"
    "|old"
    "|oldvpage"
    "|P"
    "|p"
    "|page"
    "|pagex"
    "|paragraph"
    "|paren"
    "|parenroman"
    "|parenRoman"
    "|parnote"
    "|Part"
    "|part"
    "|partpage"
    "|partrange"
    "|Partrange"
    "|pfull"
    "|pg"
    "|Pg"
    "|pgfmanualpdf"
    "|ph"
    "|Ph"
    "|phyper"
    "|plain"
    "|pmemlabel"
    "|postnote"
    "|postnotez"
    "|pp"
    "|ppg"
    "|pretty"
    "|prob"
    "|prop"
    "|pstart"
    "|pt"
    "|pu"
    "|px"
    "|q"
    "|question"
    "|rem"
    "|remark"
    "|rn"
    "|roman"
    "|Roman"
    "|RSeq"
    "|S"
    "|s"
    "|safe"
    "|schapter"
    "|SE"
    "|Sec"
    "|sec"
    "|secpage"
    "|secrange"
    "|Secrange"
    "|sect"
    "|section"
    "|Section"
    "|sections"
    "|Sections"
    "|sequation"
    "|setcounter"
    "|setcounterfrom"
    "|setcounterfrompage"
    "|setcounterpage"
    "|sfigure"
    "|sfootnote"
    "|skills"
    "|smart"
    "|spage"
    "|sparagraph"
    "|spart"
    "|square"
    "|srefchapter"
    "|srefequation"
    "|sreffigure"
    "|sreffootnote"
    "|srefpage"
    "|srefparagraph"
    "|srefpart"
    "|srefsection"
    "|srefsubparagraph"
    "|srefsubsection"
    "|srefsubsubsection"
    "|sreftable"
    "|ssection"
    "|ssubparagraph"
    "|ssubsection"
    "|ssubsubsection"
    "|stable"
    "|step"
    "|sub"
    "|Sub"
    "|subcaption"
    "|subfig"
    "|subfigure"
    "|subline"
    "|subparagraph"
    "|subquestion"
    "|subsection"
    "|subsubsection"
    "|subt"
    "|subtab"
    "|synchro"
    "|t"
    "|T"
    "|Tab"
    "|tab"
    "|table"
    "|Table"
    "|tables"
    "|Tables"
    "|tabpage"
    "|tabrange"
    "|Tabrange"
    "|text"
    "|th"
    "|thanks"
    "|theorem"
    "|thm"
    "|thname"
    "|title"
    "|tocname"
    "|ukfaq"
    "|V"
    "|v"
    "|vname"
    "|vpage"
    "|vpageline"
    "|x"
    "|xannotation"
    "|xflag"
    "|xline"
    "|xpage"
    "|xpstart"
    "|xsubline"
    "|xx"
    "|z"
    "|zc"
    "|zcheck"
    "|zcpage"
    "|zfull"
    "|zpage"
    "|ztitle"
    "|zv"
    "|zvpage"
)[::-1] # ..ref / ..refs

_ref_range_prefixes = (
    "C"
    "|C"
    "|Cpage"
    "|cpage"
)[::-1] # ...refrange

_ref_multivalue_prefixes = (
    "algorithm"
    "|appendix"
    "|axiom"
    "|c"
    "|C"
    "|chapter"
    "|conjecture"
    "|corollary"
    "|Cpage"
    "|cpage"
    "|definition"
    "|equation"
    "|example"
    "|examples"
    "|Examples"
    "|examplesname"
    "|figure"
    "|figures"
    "|Figures"
    "|footnote"
    "|item"
    "|kc"
    "|kC"
    "|kcpage"
    "|kCpage"
    "|labelc"
    "|labelcpage"
    "|lemma"
    "|namec"
    "|nameC"
    "|noeq"
    "|object"
    "|paragraph"
    "|part"
    "|remark"
    "|section"
    "|subfig"
    "|subtab"
    "|table"
    "|tables"
    "|Tables"
    "|th"
    "|theorem"
    "|zc"
    "|zcheck"
    "|zcpage"
)[::-1] # ..ref

OLD_STYLE_REF_REGEX = re.compile(fr"([^_]*_)?(?:(?:[-+]|\*?s?)fer(?:{_ref_prefixes})?)\\")

NEW_STYLE_REF_REGEX = re.compile(fr"([^}}]*)\{{(?:(?:[-+]|\*?s?)fer(?:{_ref_prefixes})?)\\")

NEW_STYLE_REF_RANGE_REGEX = re.compile(fr"([^}}]*)\{{(?:\}}[^\}}]*\{{)?\*?egnarfer(?:{_ref_range_prefixes})\\")

NEW_STYLE_REF_MULTIVALUE_REGEX = re.compile(fr"([^}},]*)(?:,[^}},]*)*\{{[-+*]?fer(?:{_ref_multivalue_prefixes})\\")

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
