import os
import re

import sublime
import sublime_plugin

from . import detect_spellcheck
from .latex_fill_all import FillAllHelper
from .utils.decorators import async_completions
from .utils.is_tex_file import get_tex_extensions
from .utils.is_tex_file import is_tex_file
from .utils.settings import get_setting

try:
    installed_locales = sorted(detect_spellcheck._dictionary_mappings.keys())
except Exception:
    installed_locales = ["en", "en-en", "en-us"]

__all__ = ["LatexDirectiveCompletion"]

_EXCLAMATION_MARK_RE = re.compile(r"%+\s*!$", re.UNICODE | re.IGNORECASE)
_TEX_PREFIX_RE = re.compile(r"%+\s*!TEX\s+$", re.UNICODE | re.IGNORECASE)
_LINE_RE = re.compile(
    r"%+\s*!"
    r"TEX\s+"
    r"(?P<directive>[\w-]+)(?P<spaces>\s*)"
    r"=(?P<postspaces>\s*)"
    r"(?P<prefix>.*)",
    re.UNICODE | re.IGNORECASE,
)


def _prettify_locale(locale):
    if "-" not in locale:
        return locale
    try:
        lang, country = locale.split("-")
    except ValueError:
        return locale
    return f"{lang}_{country.upper()}"


def _directive_root_completions(view, value, ac=True):
    if not view.file_name():
        return []

    directory, base_name = os.path.split(view.file_name())
    exts = get_tex_extensions(view)

    def list_tex_files(dir_path):
        for tex_file in os.listdir(dir_path):
            if is_tex_file(tex_file, exts):
                yield tex_file

    tex_files = ["./" + tex_file for tex_file in list_tex_files(directory) if tex_file != base_name]

    # search up to 3 empty folders for tex files
    search_threshold = 3
    search_miss = 0

    path = "../"

    while search_miss < search_threshold:
        parent = os.path.abspath(os.path.join(directory, path))

        parent_tex_files = (path + tex_file for tex_file in list_tex_files(parent))
        if parent_tex_files:
            search_miss = 0
            tex_files.extend(parent_tex_files)
        else:
            search_miss += 1

        path += "../"
        # ensure we are not going into an infinite loop if someone
        # is working on the root directory
        if parent == os.path.abspath(os.path.join(directory, path)):
            break

    len_prefix = len([v for v in value if v in [".", "/"]])
    tex_files = [
        tex_file
        for tex_file in tex_files
        if tex_file.startswith(value) or (not len_prefix and tex_file.startswith("./" + value))
    ]

    kind = (sublime.KIND_ID_VARIABLE, "v", "TeX file")

    if ac:
        comp = [
            sublime.CompletionItem(
                trigger=tex_file, completion=tex_file[len_prefix:], details=tex_file, kind=kind
            )
            for tex_file in tex_files
        ]
    else:
        comp = (
            [
                sublime.QuickPanelItem(
                    trigger=tex_file,
                    details=os.path.abspath(os.path.join(directory, tex_file)),
                    kind=kind,
                )
                for tex_file in tex_files
            ],
            tex_files,
        )

    return comp


def _directive_spellcheck_completions(view, value, ac=True):
    user_sc = get_setting("tex_spellcheck_paths", {}, view)

    locales = [
        locale
        for locale in map(_prettify_locale, sorted(user_sc.keys()) + installed_locales)
        if locale.startswith(value)
    ]

    def spellcheck_file(locale):
        try:
            locale = detect_spellcheck.normalize_locale(locale)
            dic = user_sc.get(locale) or detect_spellcheck.get_dict_path(locale)
            if ac:
                _, dic = os.path.split(dic)
            elif dic.startswith("Packages/"):
                dic = dic[len("Packages/") :]
        except Exception:
            dic = "locale"
        return dic

    kind = (sublime.KIND_ID_VARIABLE, "v", "Locale")

    if ac:
        comp = [
            sublime.CompletionItem(
                trigger=locale, completion=locale, details=spellcheck_file(locale), kind=kind
            )
            for locale in locales
        ]

    else:
        comp = (
            [
                sublime.QuickPanelItem(trigger=locale, details=spellcheck_file(locale), kind=kind)
                for locale in locales
            ],
            locales,
        )

    return comp


def _directive_program_completions(view, value, ac=True):
    engines = ("pdflatex", "xelatex", "lualatex", "pdftex", "xetex", "luatex")
    engines = [e for e in engines if e.startswith(value)]

    kind = (sublime.KIND_ID_VARIABLE, "v", "Engine")

    if ac:
        comp = [sublime.CompletionItem(trigger=e, completion=e, kind=kind) for e in engines]

    else:
        comp = (
            [sublime.QuickPanelItem(trigger=e, kind=kind) for e in engines],
            engines,
        )

    return comp


def _directive_output_directory_completions(view, value, ac=True):
    kind = (sublime.KIND_ID_VARIABLE, "v", "Output")

    if not ac:
        comp = [
            (["Other", "Define your own path"], ""),
            (["Cache", "Use LaTeXTools cache path"], "<<cache>>"),
            (["Project", "Use a folder relative to project root"], "<<project>>"),
            (["Temporary", "Use a temporary directory"], "<<temp>>"),
        ]
        comp = [c for c in comp if c[1].startswith(value) or c[1].startswith("<<" + value)]

        return (
            [sublime.QuickPanelItem(trigger=c[0][0], details=c[0][1], kind=kind) for c in comp],
            [c[1] for c in comp],
        )

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

    return [
        c
        for c in (
            sublime.CompletionItem(
                trigger="cache",
                completion="<<cache>>"[lstrip:],
                annotation="<<cache>>",
                details="Use LaTeXTools cache path",
                kind=kind,
            ),
            sublime.CompletionItem(
                trigger="project",
                completion="<<project>>"[lstrip:],
                annotation="<<project>>",
                details="Use a folder relative to project root",
                kind=kind,
            ),
            sublime.CompletionItem(
                trigger="temporary",
                completion="<<temp>>"[lstrip:],
                annotation="<<temp>>",
                details="Use a temporary directory",
                kind=kind,
            ),
        )
        if c.trigger.startswith(value) or c.completion.startswith(value)
    ]


_directive_aux_directory_completions = _directive_output_directory_completions


class DirectiveFillAllHelper(FillAllHelper):
    def _get_completions(self, view, prefix, line, ac=False):
        m = re.match(_LINE_RE, line)
        if not m:
            return []

        directive = m.group("directive").lower()
        # remove leading TS-
        if directive.startswith("ts-"):
            directive = directive[3:]

        try:
            get_completions = globals()[f"_directive_{directive}_completions"]
        except KeyError:
            return []

        value = m.group("prefix")
        comp = get_completions(view, value, ac)

        # surround assignment operator with spaces
        # e.g.: directive = value
        if not ac and not prefix and m.group("spaces"):
            comp = comp[0], [" " + c for c in comp[1]]

        return comp

    def get_auto_completions(self, view, prefix, line):
        return self._get_completions(view, prefix, line, ac=True)

    def get_completions(self, view, prefix, line):
        return self._get_completions(view, prefix, line, ac=False)

    def matches_line(self, line):
        return bool(_LINE_RE.match(line[::-1]))

    def get_supported_scope_selector(self):
        return "comment.line.percentage"

    def is_enabled(self):
        return get_setting("tex_directive_auto_trigger", True)


class LatexDirectiveCompletion(sublime_plugin.EventListener):
    @async_completions
    def on_query_completions(self, view, prefix, locations):
        if len(locations) > 1:
            return []

        pt = locations[0]
        if not view.match_selector(pt, "text.tex.latex comment.line.percentage"):
            return []

        line_reg = view.line(pt)
        line_reg.b = pt
        line_str = view.substr(line_reg)
        if prefix:
            line_str = line_str[: -len(prefix)]

        # circumvent completion if it cannot be possible
        if "!" not in line_str:
            return []

        completions = []

        directives = [
            "root",
            "spellcheck",
            "program",
            "output_directory",
            "aux_directory",
            "jobname",
            "options",
        ]

        kind = [sublime.KIND_ID_KEYWORD, "d", "Directive"]

        if _EXCLAMATION_MARK_RE.match(line_str):
            row, _ = view.rowcol(pt)
            # do this completion only in the first 20 lines
            if row < 20:
                completions = [
                    sublime.CompletionItem(trigger="TEX " + directive, kind=kind, details=" ")
                    for directive in directives
                ]

        elif _TEX_PREFIX_RE.match(line_str):
            completions = [
                sublime.CompletionItem(trigger=directive, kind=kind, details=" ")
                for directive in directives
            ]

        return completions
