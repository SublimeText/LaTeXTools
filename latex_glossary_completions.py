import re

import sublime


_ST3 = sublime.version() >= "3000"

if _ST3:
    from .latex_fill_all import FillAllHelper
    from .latextools_utils import analysis, cache, get_setting
    from .latextools_utils.tex_directives import get_tex_root

else:
    from latextools_utils.internal_types import FillAllHelper
    from latextools_utils import analysis, cache, get_setting
    from latextools_utils.tex_directives import get_tex_root


GLO_LINE_RE = re.compile(
    r"([^{}\[\]]*)\{*?(?:lp|lobmys)?sl(?:G|g)\\"
)
ACR_LINE_RE = re.compile(
    r"([^{}\[\]]*)\{(?:lluf|gnol|trohs)rca\\"
)


def _get_glo_completions(ana, prefix, ac):
    comp = []
    glo_commands = ana.filter_commands(
        ["newglossaryentry", "longnewglossaryentry", "newacronym"])
    if ac:
        comp = [(a.args + "\tGlossary", a.args) for a in glo_commands]
    else:
        glo_commands = [a for a in glo_commands if a.args.startswith(prefix)]
        comp = [
            [a.args]
            for a in glo_commands
        ], [
            a.args for a in glo_commands
        ]
    return comp


def _get_acr_completions(ana, prefix, ac):
    acr_commands = ana.filter_commands("newacronym")
    if ac:
        comp = [(a.args + "\tAcronym", a.args) for a in acr_commands]
    else:
        acr_commands = [a for a in acr_commands if a.args.startswith(prefix)]
        comp = [
            [a.args, "{0} - {1}".format(a.args2 or "", a.args3 or "")]
            for a in acr_commands
        ], [
            a.args for a in acr_commands
        ]
    return comp


class GlossaryFillAllHelper(FillAllHelper):
    def _get_completions(self, view, prefix, line, comp_type="glo", ac=False):
        tex_root = get_tex_root(view)
        if not tex_root:
            return []

        cache_name = "glocomp_{0}_{1}".format(comp_type, "ac" if ac else "kbd")

        def make_compl():
            ana = analysis.get_analysis(tex_root)
            if comp_type == "glo":
                comp = _get_glo_completions(ana, prefix, ac)
            elif comp_type == "acr":
                comp = _get_acr_completions(ana, prefix, ac)
            else:
                comp = []
            return comp

        comp = cache.cache(tex_root, cache_name, make_compl)
        return comp

    def get_compl_type(self, line):
        if GLO_LINE_RE.match(line[::-1]):
            return "glo"
        elif ACR_LINE_RE.match(line[::-1]):
            return "acr"
        else:
            return "glo"

    def get_auto_completions(self, view, prefix, line):
        comp_type = self.get_compl_type(line)
        comp = self._get_completions(
            view, prefix, line, comp_type=comp_type, ac=True)
        return comp

    def get_completions(self, view, prefix, line):
        comp_type = self.get_compl_type(line)
        comp = self._get_completions(
            view, prefix, line, comp_type=comp_type, ac=False)
        return comp

    def matches_line(self, line):
        return bool(GLO_LINE_RE.match(line) or ACR_LINE_RE.match(line))

    def is_enabled(self):
        return get_setting("glossary_auto_trigger", True)
