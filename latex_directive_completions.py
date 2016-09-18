import os
import re

import sublime
import sublime_plugin


_ST3 = sublime.version() >= "3000"

if _ST3:
    from . import detect_spellcheck
    from .latex_fill_all import FillAllHelper
    from .latextools_utils import get_setting
else:
    import detect_spellcheck
    from latextools_utils.internal_types import FillAllHelper
    from latextools_utils import get_setting

try:
    installed_locales = sorted(detect_spellcheck._dictionary_mappings.keys())
except:
    installed_locales = ["en", "en-en", "en-us"]


def _prettify_locale(loc):
    if "-" not in loc:
        return loc
    try:
        lang, country = loc.split("-")
    except ValueError:
        return loc
    return "{0}_{1}".format(lang, country.upper())


def _directive_root_completions(view, value, ac=True):
    if not view.file_name():
        return []

    directory, base_name = os.path.split(view.file_name())
    exts = get_setting("tex_file_exts", view=view)

    def is_tex_file(file_name):
        return any(file_name.endswith(e) for e in exts)

    def list_tex_files(dir_path):
        return (f for f in os.listdir(dir_path) if is_tex_file(f))

    tex_files = [
        "./" + f for f in list_tex_files(directory) if not base_name == f
    ]

    # search up to 3 empty folders for tex files
    search_threshold = 3
    search_miss = 0

    path = "../"

    while search_miss < search_threshold:
        parent = os.path.abspath(os.path.join(directory, path))

        parent_tex_files = list(path + s for s in list_tex_files(parent))
        tex_files.extend(parent_tex_files)

        if not parent_tex_files:
            search_miss += 1
        else:
            search_miss = 0

        path += "../"
        # ensure we are not going into an infinite loop if someone
        # is working on the root directory
        if parent == os.path.abspath(os.path.join(directory, path)):
            break

    len_prefix = len([v for v in value if v in [".", "/"]])
    tex_files = [
        s for s in tex_files
        if s.startswith(value) or
        (not len_prefix and s.startswith("./" + value))
    ]
    if ac:
        comp = [(s + "\ttex-file", s[len_prefix:]) for s in tex_files]
    else:
        comp = [
            [s, os.path.abspath(os.path.join(directory, s))] for s in tex_files
        ], tex_files

    return comp


def _directive_spellcheck_completions(view, value, ac=True):
    user_sc = get_setting("tex_spellcheck_paths", view=view, default={})
    locales = sorted(user_sc.keys())

    locales.extend(installed_locales)

    def get_locale(loc):
        try:
            loc = detect_spellcheck.normalize_locale(loc)
            dic = user_sc.get(loc) or detect_spellcheck.get_dict_path(loc)
            if ac:
                _, dic = os.path.split(dic)
            elif dic.startswith("Packages/"):
                dic = dic[len("Packages/"):]
        except:
            dic = "locale"
        return dic
    locales = [
        loc
        for loc in map(_prettify_locale, locales)
        if loc.startswith(value)
    ]

    if ac:
        comp = [
            ("{0}\t{1}".format(loc, get_locale(loc)), loc)
            for loc in locales
        ]
    else:
        comp = [[loc, get_locale(loc)] for loc in locales], locales
    return comp


def _directive_program_completions(view, value, ac=True):
    engines = [
        "pdflatex", "xelatex", "lualatex", "pdftex", "xetex", "luatex"
    ]
    engines = [e for e in engines if e.startswith(value)]
    if ac:
        comp = [(e + "\ttex-program", e) for e in engines]
    else:
        comp = engines, engines
    return comp


def _directive_output_directory_completions(view, value, ac=True):
    if not ac:
        # deal popup panel trigger
        comp = [
            (["Other", "Define your own path"], ""),
            (["Cache", "Use LaTeXTools cache path"], "<<cache>>"),
            (["Project", "Use a folder relative to project root"],
             "<<project>>"),
            (["Temporary", "Use a temporary directory"], "<<temp>>")
        ]
        comp = [
            c for c in comp
            if c[1].startswith(value) or c[1].startswith("<<" + value)
        ]
        return [c[0] for c in comp], [c[1] for c in comp]

    if value.endswith(">>"):
        return []

    # special behavior to deal with << and  and >
    if value.endswith(">"):
        lstrip = len(value)
    elif value.startswith("<<"):
        lstrip = 2
    elif value.startswith("<"):
        lstrip = 1
    else:
        lstrip = 0
    comp = [
        ("cache\tLaTeXTools cache", "<<cache>>"),
        ("project\tRelative to project", "<<project>>"),
        ("temp\tTemporary directory", "<<temp>>"),
    ]
    comp = [
        (c[0], c[1][lstrip:]) for c in comp
        if c[0].startswith(value) or c[1].startswith(value)
    ]
    return comp


_directive_aux_directory_completions = _directive_output_directory_completions


_EXCLAMATION_MARK_RE = re.compile(
    r"%+\s*!"
    r"$",
    re.UNICODE | re.IGNORECASE
)
_TEX_PREFIX_RE = re.compile(
    r"%+\s*!"
    r"TEX\s+"
    r"$",
    re.UNICODE | re.IGNORECASE
)
_LINE_RE = re.compile(
    r"%+\s*!"
    r"TEX\s+"
    r"(?P<directive>[\w-]+)(?P<spaces>\s*)"
    r"=(?P<postspaces>\s*)"
    r"(?P<prefix>.*)",
    re.UNICODE | re.IGNORECASE
)


class DirectiveFillAllHelper(FillAllHelper):

    def _get_completions(self, view, prefix, line, ac=False):
        m = re.match(_LINE_RE, line)
        if not m:
            return []
        directive = m.group("directive").lower()
        # remove leading TS-
        if directive.startswith("ts-"):
            directive = directive[3:]

        value = m.group("prefix")

        function = "_directive_{0}_completions".format(directive)
        # call the completion
        try:
            comp = globals().get(function)(view, value, ac)
        except:
            comp = []

        if not ac and not prefix and m.group("spaces"):
            comp = comp[0], [" " + c for c in comp[1]]

        return comp

    def get_auto_completions(self, view, prefix, line):
        comp = self._get_completions(view, prefix, line, ac=True)
        return comp

    def get_completions(self, view, prefix, line):
        comp = self._get_completions(view, prefix, line, ac=False)
        return comp

    def matches_line(self, line):
        return bool(_LINE_RE.match(line[::-1]))

    def get_supported_scope_selector(self):
        return "comment"

    def is_enabled(self):
        return get_setting("tex_directive_auto_trigger", True)


class LatexDirectiveCompletion(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if len(locations) > 1:
            return
        point = locations[0]
        if not view.score_selector(
                point, "text.tex.latex comment.line.percentage"):
            return

        line_str = view.substr(sublime.Region(view.line(point).a, point))
        if prefix:
            line_str = line_str[:-len(prefix)]

        # circumvent completion if it cannot be possible
        if "!" not in line_str:
            return

        comp = None

        tex_directives = [
            "root", "spellcheck", "program", "output_directory",
            "aux_directory", "jobname", "options"
        ]
        if _EXCLAMATION_MARK_RE.match(line_str):
            row, _ = view.rowcol(point)
            # do this completion only in the first 20 lines
            if row < 20:
                comp = [
                    ("TEX {0}\tTEX directive".format(s), "TEX " + s)
                    for s in tex_directives
                ]
        elif _TEX_PREFIX_RE.match(line_str):
            comp = [(s + "\tTEX directive", s) for s in tex_directives]
        # other completions are handled via fill all helper
        return comp
