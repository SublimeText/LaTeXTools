# -*- coding:utf-8 -*-
# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
else:
    _ST3 = True
    from . import getTeXRoot

import sublime_plugin
import os, os.path
import re
import json


# Only work for \include{} and \input{} and \includegraphics
TEX_INPUT_FILE_REGEX = re.compile(r'([^{}\[\]]*)\{edulcni\\'
    + r'|([^{}\[\]]*)\{tupni\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?scihpargedulcni\\'
    + r'|([^{}\[\]]*)\{ecruoserbibdda\\'
    + r'|([^{}\[\]]*)\{yhpargoilbib\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?ssalctnemucod\\'
    + r'|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?egakcapesu\\'
    + r'|([^{}\[\]]*)\{elytsyhpargoilbib\\'
)

# Get all file by types
def get_file_list(root, types):

    path = os.path.dirname(root)

    def file_match(f):
        result = True

        # Check is file has an extension name
        if len(os.path.splitext(f)) > 1:
            filename, extname = os.path.splitext(f)

            # if file is in the type list
            if extname[1:] in types:
                result &= True
            else:
                return False

        return result

    completions = []
    for dir_name, dirs, files in os.walk(path):
        files = [f for f in files if f[0] != '.' and file_match(f)]
        dirs[:] = [d for d in dirs if d[0] != '.']
        for i in files:
            #path_i = '{}/{}'.format(dir_name, i)
            path_i = "%s/%s"%(dir_name, i)
            # Exclude image file have the same name of root file, 
            # which may be the pdf file of the root files,
            # only pdf format.
            if os.path.splitext(root)[0] == os.path.splitext(path_i)[0]:
                continue  
            completions.append((os.path.relpath(dir_name, path), i)) 

    return completions


def parse_completions(view, point):

    # reverse line, copied from latex_cite_completions, very cool :)
    line = view.substr(sublime.Region(view.line(point).a, point))
    line = line[::-1]

    # Do matches!
    search = TEX_INPUT_FILE_REGEX.match(line)

    installed_cls = []
    installed_bst = []
    installed_pkg = []
    input_file_types = None

    if search != None:
        include_filter, \
        input_filter, \
        image_filter, \
        addbib_filter, \
        bib_filter, \
        cls_filter, \
        pkg_filter, \
        bst_filter = search.groups()
    else:
        return '', []

    if include_filter != None:
        # if is \include
        prefix = include_filter[::-1] 
        input_file_types = ['tex']
    elif input_filter != None:
        # if is \input search type set to tex
        prefix = input_filter[::-1] 
        input_file_types = ['tex'] 
    elif image_filter != None:
        # if is \includegraphics
        prefix = image_filter[::-1] 
        # Load image types from configurations
        # In order to user input, "image_types" must be set in 
        # LaTeXTools.sublime-settings configure files.
        settings = sublime.load_settings("LaTeXTools.sublime-settings")
        input_file_types = settings.get('image_types')
        if input_file_types == None or len(input_file_types) == 0:
            input_file_types = ['pdf', 'png', 'jpeg', 'jpg', 'eps']
    elif addbib_filter != None or bib_filter != None:

        # For bibliography
        prefix = addbib_filter[::-1] if addbib_filter != None else bib_filter[::-1]
        input_file_types = ['bib']
    elif cls_filter != None or pkg_filter != None or bst_filter != None:
        # for packages, classes and bsts
        if _ST3:
            cache_path = os.path.normpath(sublime.cache_path() + "/" + "LaTeXTools")
        else:
            cache_path = os.path.normpath(sublime.packages_path() + "/" + "LaTeXTools")

        pkg_cache_file = os.path.normpath(cache_path + '/' + 'pkg_cache.cache')

        cache = None
        if not os.path.exists(pkg_cache_file):
            gen_cache = sublime.ok_cancel_dialog("Cache files for installed packages, " 
                +"classes and bibliographystyles do not exists, " 
                + "would you like to generate it? After generating complete, please re-run this completion action!"
            )
            if gen_cache:
                sublime.active_window().run_command("latex_gen_pkg_cache")
                completions = []
        else:
            with open(pkg_cache_file) as f:
                cache = json.load(f)    

        if cache != None:
            if cls_filter != None:
                installed_cls = cache.get("cls")
            elif bst_filter != None:
                installed_bst = cache.get("bst")
            else:
                installed_pkg = cache.get("pkg")

        prefix = ''
    else:
        prefix = ''


    if len(installed_cls) != 0:
        completions = installed_cls
    elif len(installed_bst) != 0:
        completions = installed_bst
    elif len(installed_pkg) != 0:
        completions = installed_pkg
    elif input_file_types != None:
        root = getTeXRoot.get_tex_root(view)
        completions = get_file_list(root, input_file_types)

    return prefix, completions

# class LatexInputComplete(sublime_plugin.EventListener):
    
#     def on_query_completions(self, view, prefix, locations):
#         if not view.match_selector(locations[0],
#                 "text.tex.latex"):
#             return []

#         point = locations[0]

#         # Get some fileters
#         prefix, completions = parse_completions(view, point)

#         result = []

#         # if element in completions is tuple, is does not comes from pkg, 
#         # cls and bst completions. Use not tuple is to make it work with ST2
#         # where unicode str is the type of "unicode" not "str" in ST3.
#         if len(completions) != 0 and not type(completions[0]) is tuple:
#             result = [('%s'%x, x) for x in completions]
#         else:
#             result += [('%s\t%s'%(filename, relpath), '%s/%s'%(relpath, filename)) for relpath, filename in completions]

#         return (result, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


class LatexFillInputCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        view = self.view
        point = view.sel()[0].b
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
            return

        prefix, completions = parse_completions(view, point)

        if len(completions) != 0 and not type(completions[0]) is tuple:
            result = completions
        else:
            root_path = os.path.dirname(getTeXRoot.get_tex_root(self.view))
            
            # Process path separators on Windows platform
            plat = sublime.platform()
            if plat == 'windows':
                result = []
                for relpath, filename in completions:
                    converted_path = os.path.normpath('%s/%s'%(relpath, filename))
                    converted_path = converted_path.replace('\\', '/')
                    result.append([converted_path, os.path.normpath('%s/%s/%s'%(root_path, relpath, filename))])
            else:
                result = [[os.path.normpath('%s/%s'%(relpath, filename)), 
                    os.path.normpath('%s/%s/%s'%(root_path, relpath, filename))] for relpath, filename in completions]



        def on_done(i):
            # Doing Nothing
            if i < 0:
                return
            if type(result[i]) is list: # if result[i] is a list, it comes from input, include and includegraphics
                key = result[i][0]
            else:
                key = result[i]
            startpos = point - len(prefix)
            view.run_command("latex_tools_replace", {"a": startpos, "b": point, "replacement": key})
            caret = view.sel()[0].b
            view.sel().subtract(view.sel()[0])
            view.sel().add(sublime.Region(caret, caret))

        view.window().show_quick_panel(result, on_done)
