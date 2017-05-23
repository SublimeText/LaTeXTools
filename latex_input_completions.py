# -*- coding:utf-8 -*-
# ST2/ST3 compat
from __future__ import print_function
import sublime
import sublime_plugin

import os
import re
import json

try:
    from latex_fill_all import FillAllHelper
    from latextools_utils import analysis
    from latextools_utils.is_tex_file import get_tex_extensions
    from latextools_utils.output_directory import (
        get_aux_directory, get_output_directory
    )
except ImportError:
    from .latex_fill_all import FillAllHelper
    from .latextools_utils import analysis
    from .latextools_utils.is_tex_file import get_tex_extensions
    from .latextools_utils.output_directory import (
        get_aux_directory, get_output_directory
    )

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
    from latextools_utils import get_setting
else:
    _ST3 = True
    from . import getTeXRoot
    from .latextools_utils import get_setting


def _filter_invalid_entries(entries):
    """Remove entries without a regex or sufficient fields."""
    remove_entries = []
    for i, entry in enumerate(entries):
        if "extensions" not in entry:
            print("Missing field 'extensions' in entry {0}".format(entry))
            remove_entries.append(i)
            continue
        if "regex" not in entry:
            print("Missing field 'regex' in entry {0}".format(entry))
            remove_entries.append(i)
            continue

        try:
            reg = re.compile(entry["regex"])
        except Exception as e:
            print("Invalid regex: '{0}' ({1})".format(entry["regex"], e))
            remove_entries.append(i)
            continue
        if reg.groups != 0:
            print("The regex must not have a capturing group, invalidated in "
                  "entry {0}. You might escape your group with (?:...)"
                  .format(entry))
            remove_entries.append(i)
            continue
        # remove all blacklisted entries in reversed order, so the remaining
        # indexes stay the same
        for i in reversed(remove_entries):
            del entries[i]


def _update_input_entries(entries):
    for entry in entries:
        comma = entry.get("comma_separated", False)
        if comma:
            entry["regex"] = r"([^{}\[\]]*)\{" + entry["regex"]
        else:
            entry["regex"] = r"([^,{}\[\]]*)\{" + entry["regex"]
        entry["type"] = "input"


_fillall_entries = []

_TEX_INPUT_GROUP_MAPPING = None
TEX_INPUT_FILE_REGEX = None


def _post_process_path_only(completions):
    result = []
    added = set()
    for t in completions:
        try:
            relpath, file_name = t
        except:
            continue
        if relpath == "." or relpath in added:
            continue
        added.add(relpath)
        result.append(relpath + "/")
    return result


def plugin_loaded():
    # get additional entries from the settings
    _setting_entries = get_setting("fillall_helper_entries", [])
    _filter_invalid_entries(_setting_entries)
    _fillall_entries.extend(_setting_entries)

    _fillall_entries.extend([
        # input/include
        {
            "regex": r'(?:edulcni|tupni)\\',
            "extensions": [e[1:] for e in get_tex_extensions()],
            "strip_extensions": [".tex"]
        },
        # includegraphics
        {
            "regex": r'(?:\][^{}\[\]]*\[)?scihpargedulcni\\',
            "extensions": get_setting("image_types", [
                "pdf", "png", "jpeg", "jpg", "eps"
            ])
        },
        # import/subimport
        {
            "regex": r'\*?(?:tropmibus)\\',
            "extensions": [e[1:] for e in get_tex_extensions()],
            "strip_extensions": [".tex"],
            "post_process": "path_only"
        },
        {
            "regex": r'\}[^{}\[\]]*\{\*?(?:tropmi|morftupni|morfedulcni)?bus\\',
            "extensions": [e[1:] for e in get_tex_extensions()],
            "strip_extensions": [".tex"],
            "post_regex": (
                r'\\sub(?:import|includefrom|inputfrom)\*?'
                r'\{([^{}\[\]]*)\}\{[^\}]*?$'
            ),
            "folder": "$base/$_1"
        },
        {
            "regex": r'\}[^{}\[\]]*\{\*?(?:tropmi|morftupni|morfedulcni)\\',
            "extensions": [e[1:] for e in get_tex_extensions()],
            "strip_extensions": [".tex"],
            "post_regex": (
                r'\\(?:import|includefrom|inputfrom)\*?'
                r'\{([^{}\[\]]*)\}\{[^\}]*?$'
            ),
            "folder": "$_1"
        },
        {
            "regex": r'(?:\][^{}\[\]]*\[)?ecruoserbibdda\\',
            "extensions": ["bib"]
        },
        {
            "regex": r'yhpargoilbib\\',
            "extensions": ["bib"],
            "strip_extensions": [".bib"],
            "comma_separated": True
        }
    ])

    # update the fields of the entries
    _update_input_entries(_fillall_entries)

    _fillall_entries.extend([
        {
            "regex": r'([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?ssalctnemucod\\',
            "type": "cached",
            "cache_name": "cls"
        },
        {
            "regex": r'([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?egakcapesu\\',
            "type": "cached",
            "cache_name": "pkg"
        },
        {
            "regex": r'([^{}\[\]]*)\{elytsyhpargoilbib\\',
            "type": "cached",
            "cache_name": "bst"
        }
    ])

    global _TEX_INPUT_GROUP_MAPPING, TEX_INPUT_FILE_REGEX
    _TEX_INPUT_GROUP_MAPPING = dict((i, v) for i, v in enumerate(_fillall_entries))
    TEX_INPUT_FILE_REGEX = re.compile(
        "(?:{0})".format("|".join(entry["regex"] for entry in _fillall_entries))
    )

if not _ST3:
    plugin_loaded()


# Get all file by types
def get_file_list(root, types, filter_exts=[], base_path=None, output_directory=None,
                  aux_directory=None):
    if not base_path:
        base_path = os.path.dirname(root)

    def file_match(f):
        filename, extname = os.path.splitext(f)
        # ensure file has extension and its in the list of types
        if extname and not extname[1:].lower() in types:
            return False

        return True

    def dir_match(d):
        _d = os.path.realpath(os.path.join(dir_name, d))
        if (
            _d in handled_directories or
            _d == output_directory or
            _d == aux_directory
        ):
            return False

        return True

    completions = []
    handled_directories = set([])
    for dir_name, dirs, files in os.walk(base_path, followlinks=True):
        handled_directories.add(os.path.realpath(dir_name))
        files = [f for f in files if f[0] != '.' and file_match(f)]
        dirs[:] = [d for d in dirs if d[0] != '.' and dir_match(d)]
        for f in files:
            full_path = os.path.join(dir_name, f)
            # Exclude image file have the same name of root file,
            # which may be the pdf file of the root files,
            # only pdf format.
            if os.path.splitext(root)[0] == os.path.splitext(full_path)[0]:
                continue

            for ext in filter_exts:
                if f.endswith(ext):
                    f = f[:-len(ext)]

            completions.append((os.path.relpath(dir_name, base_path), f))

    return completions


def _get_dyn_entries():
    dyn_entries = get_setting("dynamic_fillall_helper_entries", [])
    if dyn_entries:
        _filter_invalid_entries(dyn_entries)
        _update_input_entries(dyn_entries)
        dyn_regex = re.compile("(?:{0})".format(
            "|".join(entry["regex"] for entry in dyn_entries)))
        return dyn_entries, dyn_regex
    else:
        return [], None


def parse_completions(view, line):
    # reverse line, copied from latex_cite_completions, very cool :)
    line = line[::-1]

    search = None

    # search static entries first
    search = TEX_INPUT_FILE_REGEX.match(line)
    if search:
        entries = _fillall_entries
    # then search dynamic entries if no static entries match
    else:
        dyn_entries, dyn_regex = _get_dyn_entries()
        if dyn_regex:
            search = dyn_regex.match(line)
            entries = dyn_entries

    # if no regex matched, cancel completions
    if not search:
        return []

    try:
        # extract the first group and the prefix from the maching regex
        group = next(i for i, v in enumerate(search.groups())
                     if v is not None)
        entry = entries[group]
    except Exception as e:
        print("Error occurred while extracting entry from matching group.")
        print(e)
        return []

    completions = []

    if entry["type"] == "input":
        root = getTeXRoot.get_tex_root(view)
        if root:
            ana = analysis.get_analysis(root)
            tex_base_path = ana.tex_base_path(view.file_name())
            completions = []
            sub = {
                "root": root,
                "base": tex_base_path
            }
            if "post_regex" in entry:
                m = re.search(entry["post_regex"], line[::-1])
                if m:
                    for i in range(1, len(m.groups()) + 1):
                        sub["_{0}".format(i)] = m.group(i)
            if "folder" in entry:
                folders = []
                for folder in entry["folder"].split(";"):
                    import string
                    temp = string.Template(folder)
                    folders.append(temp.safe_substitute(sub))
            else:
                folders = [tex_base_path]
            for base_path in folders:
                output_directory = get_output_directory(view)
                aux_directory = get_aux_directory(view)
                completions.extend(get_file_list(
                    root, entry["extensions"],
                    entry.get("strip_extensions", []),
                    base_path=base_path,
                    output_directory=output_directory,
                    aux_directory=aux_directory
                ))
        else:
            # file is unsaved
            completions = []
    elif entry["type"] == "cached":
        cache = _get_cache()
        if cache is not None:
            completions = cache.get(entry["cache_name"])
    else:
        print("Unknown entry type {0}.".format(entry["type"]))

    if "post_process" in entry:
        fkt = globals().get(
            "_post_process_{0}".format(entry["post_process"]), None)
        if fkt:
            completions = fkt(completions)

    return completions


def _get_cache():
    if _ST3:
        cache_path = os.path.normpath(
            os.path.join(sublime.cache_path(), "LaTeXTools"))
    else:
        cache_path = os.path.normpath(
            os.path.join(sublime.packages_path(), "User"))

    pkg_cache_file = os.path.normpath(
        os.path.join(cache_path, 'pkg_cache.cache'
                     if _ST3 else 'latextools_pkg_cache.cache'))

    cache = None
    if not os.path.exists(pkg_cache_file):
        gen_cache = sublime.ok_cancel_dialog(
            "Cache files for installed packages, "
            "classes and bibliographystyles do not exists, "
            "would you like to generate it? After generating complete, "
            "please re-run this completion action!"
        )

        if gen_cache:
            sublime.active_window().run_command("latex_gen_pkg_cache")
    else:
        with open(pkg_cache_file) as f:
            cache = json.load(f)
    return cache


class InputFillAllHelper(FillAllHelper):

    def get_auto_completions(self, view, prefix, line):
        completions = parse_completions(view, line)

        if len(completions) == 0:
            return []
        elif not type(completions[0]) is tuple:
            return completions
        else:
            return [
                # Replace backslash with forward slash to fix Windows paths
                # LaTeX does not support forward slashes in paths
                os.path.normpath(
                    os.path.join(relpath, filename)
                ).replace('\\', '/')
                for relpath, filename in completions
            ]

    def get_completions(self, view, prefix, line):
        completions = parse_completions(view, line)

        if len(completions) == 0:
            return
        elif not type(completions[0]) is tuple:
            return completions
        else:
            tex_root = getTeXRoot.get_tex_root(view)
            if tex_root:
                root_path = os.path.dirname(tex_root)
            else:
                print(
                    "Can't find TeXroot. "
                    "Assuming current directory is {0}".format(os.curdir)
                )
                root_path = os.curdir

            formatted_completions = []
            normal_completions = []
            for relpath, filename in completions:
                latex_formatted = os.path.normpath(os.path.join(
                    relpath, filename)).replace('\\', '/')

                formatted_completions.append([
                    latex_formatted,
                    os.path.normpath(os.path.join(
                        root_path, relpath, filename)
                    )
                ])

                normal_completions.append(latex_formatted)

            return formatted_completions, normal_completions

    def matches_line(self, line):
        if TEX_INPUT_FILE_REGEX.match(line):
            return True

        _, dyn_regex = _get_dyn_entries()
        return bool(
            dyn_regex and dyn_regex.match(line)
        )

    def is_enabled(self):
        return get_setting('fill_auto_trigger', True)
