# -*- coding:utf-8 -*-
# ST2/ST3 compat
from __future__ import print_function
import sublime
import sublime_plugin

import os
import re
import json

try:
    from latextools_utils.is_tex_file import get_tex_extensions
    from latextools_utils.output_directory import (
        get_aux_directory, get_output_directory
    )
except ImportError:
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


def plugin_loaded():
    # get additional entries from the settings
    _setting_entries = get_setting("fillall_helper_entries", [])
    _filter_invalid_entries(_setting_entries)
    _fillall_entries.extend(_setting_entries)

    _fillall_entries.extend([
        {
            "regex": r'(?:edulcni|tupni)\\',
            "extensions": [e[1:] for e in get_tex_extensions()],
            "strip_extensions": [".tex"]
        },
        {
            "regex": r'(?:\][^{}\[\]]*\[)?scihpargedulcni\\',
            "extensions": get_setting("image_types", [
                "pdf", "png", "jpeg", "jpg", "eps"
            ])
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
def get_file_list(root, types, filter_exts=[], output_directory=None,
                  aux_directory=None):
    path = os.path.dirname(root)

    def file_match(f):
        filename, extname = os.path.splitext(f)
        # ensure file has extension and its in the list of types
        if extname and not extname[1:].lower() in types:
            return False

        return True

    completions = []
    for dir_name, dirs, files in os.walk(path):
        files = [f for f in files if f[0] != '.' and file_match(f)]
        dirs[:] = [d for d in dirs if d[0] != '.' and
                   os.path.join(dir_name, d) != output_directory and
                   os.path.join(dir_name, d) != aux_directory]
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

            completions.append((os.path.relpath(dir_name, path), f))

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
    # search dynamic entries
    dyn_entries, dyn_regex = _get_dyn_entries()
    if dyn_regex:
        search = dyn_regex.match(line)
        entries = dyn_entries

    # search static entries if no dynamic matches found
    if not search:
        search = TEX_INPUT_FILE_REGEX.match(line)
        entries = _fillall_entries

    # if no regex matched, cancel completions
    if not search:
        return "", []

    try:
        # extract the first group and the prefix from the maching regex
        group, prefix = next((i, v) for i, v in enumerate(search.groups())
                             if v is not None)
        entry = entries[group]
        prefix = prefix[::-1]
    except Exception as e:
        print("Error occurred while extracting entry from matching group.")
        print(e)
        return "", []

    # adjust the prefix (don't include commas)
    if "," in prefix:
        prefix = prefix[prefix.rindex(",") + 1:]
    completions = []

    if entry["type"] == "input":
        root = getTeXRoot.get_tex_root(view)
        if root:
            output_directory = get_output_directory(root)
            aux_directory = get_aux_directory(root)
            completions = get_file_list(
                root, entry["extensions"],
                entry.get("strip_extensions", []),
                output_directory, aux_directory
            )
        else:
            # file is unsaved
            completions = []
    elif entry["type"] == "cached":
        cache = _get_cache()
        if cache is not None:
            completions = cache.get(entry["cache_name"])
    else:
        print("Unknown entry type {0}.".format(entry["type"]))

    return prefix, completions


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


def add_closing_bracket(view, edit):
    # only add the closing bracked if auto match is enabled
    if not view.settings().get("auto_match_enabled", True):
        return
    new_sel = []
    for sel in view.sel():
        caret = sel.b
        view.insert(edit, caret, "}")
        new_sel.append(sublime.Region(caret, caret))
    if new_sel:
        view.sel().clear()
        if _ST3:
            view.sel().add_all(new_sel)
        else:
            for sel in new_sel:
                view.sel().add(sel)


class LatexFillInputCompletions(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key not in ["lt_fill_input.open", "lt_fill_input.inside"]:
            return False
        fill_char = "{" if key == "lt_fill_input.open" else ","
        _, dyn_regex = _get_dyn_entries()
        for sel in view.sel():
            line_reg = view.line(sel)
            before = sublime.Region(line_reg.begin(), sel.b)
            line = fill_char + view.substr(before)[::-1]
            search = (TEX_INPUT_FILE_REGEX.match(line) or
                      dyn_regex and dyn_regex.match(line))
            if match_all and not search:
                result = False
                break
            elif not match_all and search:
                result = True
                break
        else:
            result = match_all

        if operator == sublime.OP_EQUAL:
            result = result == operand
        elif operator == sublime.OP_NOT_EQUAL:
            result = result != operand

        return result

    def on_query_completions(self, view, prefix, locations):
        if view.score_selector(0, 'text.tex.latex') == 0:
            return []

        results = []

        for location in locations:
            _, completions = parse_completions(
                view,
                view.substr(sublime.Region(view.line(location).a, location))
            )

            if len(completions) == 0:
                continue
            elif not type(completions[0]) is tuple:
                pass
            else:
                completions = [
                    # Replace backslash with forward slash to fix Windows paths
                    # LaTeX does not support forward slashes in paths
                    os.path.normpath(os.path.join(relpath, filename)).replace('\\', '/')
                    for relpath, filename in completions
                ]

            line_remainder = view.substr(sublime.Region(location, view.line(location).b))
            if not line_remainder.startswith('}'):
                results.extend([(completion, completion + '}')
                    for completion in completions
                ])
            else:
                results.extend([(completion, completion)
                    for completion in completions
                ])

        if results:
            return (
                results,
                sublime.INHIBIT_WORD_COMPLETIONS |
                sublime.INHIBIT_EXPLICIT_COMPLETIONS
            )
        else:
            return []

class LatexFillInputCommand(sublime_plugin.TextCommand):
    def run(self, edit, insert_char=""):
        view = self.view
        point = view.sel()[0].b
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point, "text.tex.latex"):
            return

        if insert_char:
            # append the insert_char to the end of the current line if it
            # is given so this works when being triggered by pressing "{"
            point += len(insert_char)
            # insert the char to every selection
            for sel in view.sel():
                view.insert(edit, sel.b, insert_char)

            do_completion = get_setting("fill_auto_trigger", True)

            if not do_completion and insert_char == "{":
                add_closing_bracket(view, edit)
                return

        prefix, completions = parse_completions(
            view,
            view.substr(sublime.Region(view.line(point).a, point)))

        if len(completions) == 0:
            result = []
        elif not type(completions[0]) is tuple:
            result = completions
        else:
            tex_root = getTeXRoot.get_tex_root(self.view)
            if tex_root:
                root_path = os.path.dirname(tex_root)
            else:
                print("Can't find TeXroot. Assuming current directory is {0}".format(os.curdir))
                root_path = os.curdir

            result = [[
                # Replace backslash with forward slash to fix Windows paths
                # LaTeX does not support forward slashes in paths
                os.path.normpath(os.path.join(relpath, filename)).replace('\\', '/'),
                os.path.normpath(os.path.join(root_path, relpath, filename))
            ] for relpath, filename in completions]

        def on_done(i):
            # Doing Nothing
            if i < 0:
                return
            if type(result[i]) is list:  # if result[i] is a list, it comes from input, include and includegraphics
                key = result[i][0]
            else:
                key = result[i]

            # close bracket
            if insert_char == "{":
                key += "}"

            if prefix:
                for sel in view.sel():
                    point = sel.b
                    startpoint = point - len(prefix)
                    endpoint = point
                    view.run_command('latex_tools_replace', {'a': startpoint, 'b': endpoint, 'replacement': key})
            else:
                view.run_command("insert", {"characters": key})

        # autocomplete bracket if we aren't doing anything
        if not result and insert_char == "{":
            add_closing_bracket(view, edit)
        else:
            view.window().show_quick_panel(result, on_done)
