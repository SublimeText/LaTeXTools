import os
import re

import sublime
import sublime_plugin


_ST3 = sublime.version() >= "3000"

if _ST3:
    from . import detect_spellcheck
    from .latextools_utils import get_setting
else:
    import detect_spellcheck
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


def _directive_root_completions(view, value):
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
        # (s, s[len_prefix:])
        s
        for s in tex_files
        if s.startswith(value) or
        (not len_prefix and s.startswith("./" + value))
    ]

    comp = [(s + "\ttex-file", s[len_prefix:]) for s in tex_files]
    return comp


def _directive_spellcheck_completions(view, value):

    user_sc = get_setting("tex_spellcheck_paths", view=view, default={})
    locales = sorted(user_sc.keys())

    locales.extend(installed_locales)

    def get_locale(loc):
        try:
            loc = detect_spellcheck.normalize_locale(loc)
            dic = user_sc.get(loc) or detect_spellcheck.get_dict_path(loc)
            _, dic = os.path.split(dic)
        except:
            dic = "locale"
        return dic
    locales = [
        loc
        for loc in map(_prettify_locale, locales)
        if loc.startswith(value)
    ]

    comp = [
        ("{0}\t{1}".format(loc, get_locale(loc)), loc)
        for loc in locales
    ]
    return comp


def _directive_program_completions(view, value):

    engines = [
        "pdflatex", "xelatex", "lualatex", "pdftex", "xetex", "luatex"
    ]
    engines = [e for e in engines if e.startswith(value)]
    comp = [(e + "\ttex-program", e) for e in engines]
    return comp


class LatexDirectiveCompletion(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if len(locations) > 1:
            return
        # return
        point = locations[0]
        if not view.score_selector(
                point, "text.tex.latex comment.line.percentage.tex"):
            return

        line_str = view.substr(sublime.Region(view.line(point).a, point))
        if prefix:
            line_str = line_str[:-len(prefix)]

        # circumvent completion if it cannot be possible
        if "!" not in line_str:
            return

        comp = None

        ts_directives = ["root", "spellcheck", "program"]
        if re.match("\s*%\s*!$", line_str):
            comp = [
                ("TEX {0}\tTS-directive".format(s), "TEX " + s)
                for s in ts_directives
            ]
        elif re.match("\s*%\s*!TEX\s+$", line_str):
            comp = [(s + "\tTS-directive", s) for s in ts_directives]
        else:
            m = re.match("\s*%\s*!TEX\s+([\w-]+)\s*=\s*(.*)$", line_str)
            if not m:
                return
            directive = m.group(1).lower()
            # remove leading TS-
            if directive.startswith("ts-"):
                directive = directive[3:]
            value = m.group(2) + prefix
            function = "_directive_{0}_completions".format(directive)
            # call the completion
            try:
                comp = globals().get(function)(view, value)
            except:
                pass

        if comp is not None:
            return (
                comp,
                sublime.INHIBIT_WORD_COMPLETIONS |
                sublime.INHIBIT_EXPLICIT_COMPLETIONS
            )
