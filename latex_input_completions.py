# -*- coding:utf-8 -*-
# ST2/ST3 compat
from __future__ import print_function
import sublime
import sublime_plugin

import os
import re
import json

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
else:
    _ST3 = True
    from . import getTeXRoot


# Only work for \include{} and \input{} and \includegraphics
TEX_INPUT_FILE_REGEX = re.compile(
      r'([^{}\[\]]*)\{edulcni\\'
    + r'|([^{}\[\]]*)\{tupni\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?scihpargedulcni\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?ecruoserbibdda\\'
    + r'|([^{}\[\]]*)\{yhpargoilbib\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?ssalctnemucod\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?egakcapesu\\'
    + r'|([^{}\[\]]*)\{elytsyhpargoilbib\\'
)

# Get all file by types
def get_file_list(root, types, filter_exts=[]):
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
        dirs[:] = [d for d in dirs if d[0] != '.']
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


def parse_completions(view, line):
    # reverse line, copied from latex_cite_completions, very cool :)
    line = line[::-1]

    # Do matches!
    search = TEX_INPUT_FILE_REGEX.match(line)

    installed_cls = []
    installed_bst = []
    installed_pkg = []
    input_file_types = None

    if search is not None:
        (   include_filter,
            input_filter,
            image_filter,
            addbib_filter,
            bib_filter,
            cls_filter,
            pkg_filter,
            bst_filter) = search.groups()
    else:
        return '', []

    # it isn't always correct to include the extension in the output filename
    # esp. with \bibliography{}; here we provide a mechanism to permit this
    filter_exts = []

    if include_filter is not None:
        # if is \include
        prefix = include_filter[::-1]
        input_file_types = ['tex']
        filter_exts = ['.tex']
    elif input_filter is not None:
        # if is \input search type set to tex
        prefix = input_filter[::-1]
        input_file_types = ['tex']
        filter_exts = ['.tex']
    elif image_filter is not None:
        # if is \includegraphics
        prefix = image_filter[::-1]
        # Load image types from configurations
        # In order to user input, "image_types" must be set in
        # LaTeXTools.sublime-settings configuration file or the
        # project settings for the current view.
        view = sublime.active_window().active_view()
        settings = sublime.load_settings("LaTeXTools.sublime-settings")
        input_file_types = view.settings().get('image_types',
            settings.get('image_types', [
                'pdf', 'png', 'jpeg', 'jpg', 'eps'
            ]))
    elif addbib_filter is not None or bib_filter is not None:
        # For bibliography
        if addbib_filter is not None:
            prefix = addbib_filter[::-1]
        else:
            prefix = ''
            bib_filter[::-1]
            filter_exts = ['.bib']
        input_file_types = ['bib']
    elif cls_filter is not None or pkg_filter is not None or bst_filter is not None:
        # for packages, classes and bsts
        if _ST3:
            cache_path = os.path.normpath(
                os.path.join(
                    sublime.cache_path(),
                    "LaTeXTools"
                ))
        else:
            cache_path = os.path.normpath(
                os.path.join(
                    sublime.packages_path(),
                    "User"
                ))

        pkg_cache_file = os.path.normpath(
            os.path.join(cache_path, 'pkg_cache.cache' if _ST3 else 'latextools_pkg_cache.cache'))

        cache = None
        if not os.path.exists(pkg_cache_file):
            gen_cache = sublime.ok_cancel_dialog("Cache files for installed packages, "
                + "classes and bibliographystyles do not exists, "
                + "would you like to generate it? After generating complete, please re-run this completion action!"
            )

            if gen_cache:
                sublime.active_window().run_command("latex_gen_pkg_cache")
                completions = []
        else:
            with open(pkg_cache_file) as f:
                cache = json.load(f)

        if cache is not None:
            if cls_filter is not None:
                installed_cls = cache.get("cls")
            elif bst_filter is not None:
                installed_bst = cache.get("bst")
            else:
                installed_pkg = cache.get("pkg")

        prefix = ''
    else:
        prefix = ''

    if len(installed_cls) > 0:
        completions = installed_cls
    elif len(installed_bst) > 0:
        completions = installed_bst
    elif len(installed_pkg) > 0:
        completions = installed_pkg
    elif input_file_types is not None:
        root = getTeXRoot.get_tex_root(view)
        if root:
            completions = get_file_list(root, input_file_types, filter_exts)
        else:
            # file is unsaved
            completions = []

    return prefix, completions

def add_closing_bracket(view, edit):
    caret = view.sel()[0].b
    view.insert(edit, caret, "}")
    view.sel().subtract(view.sel()[0])
    view.sel().add(sublime.Region(caret, caret))

class LatexFillInputCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(0, 'text.tex.latex'):
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
            point += view.insert(edit, point, insert_char)

            s = sublime.load_settings("LaTeXTools.sublime-settings")
            do_completion = view.settings().get("fill auto trigger",
                s.get("fill_auto_trigger", True))
            
            if not do_completion:
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
            if insert_char:
                key += "}"

            startpos = point - len(prefix)
            view.run_command("latex_tools_replace", {"a": startpos, "b": point, "replacement": key})
            caret = view.sel()[0].b
            view.sel().subtract(view.sel()[0])
            view.sel().add(sublime.Region(caret, caret))

        # autocomplete bracket if we aren't doing anything
        if not result and insert_char:
            add_closing_bracket(view, edit)
        else:
            view.window().show_quick_panel(result, on_done)
