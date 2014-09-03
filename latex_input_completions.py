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


# Only work for \include{} and \input{} and \includegraphics
TEX_INPUT_FILE_REGEX = re.compile(r'([^{}\[\]]*)\{edulcni\\|([^{}\[\]]*)\{tupni\\|([^{}\[\]]*)\{(?:\][^{}\[\]]*\[)?scihpargedulcni\\')

# Get all file by types
def get_file_list(root, types):

    # Find if the file of f is a tex source file or image files
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
            path_i = '{}/{}'.format(dir_name, i)

            # Exclude image file have the same name of root file, 
            # which may be the pdf file of the root files,
            # only pdf format.
            if os.path.splitext(root)[0] == os.path.splitext(path_i)[0]:
                continue  
            completions.append((os.path.relpath(dir_name, path), i)) 

    return completions


def get_file_completions(view, point):

    # reverse line, copied from latex_cite_completions, very cool :)
    line = view.substr(sublime.Region(view.line(point).a, point))
    line = line[::-1]

    # Do matches!
    search = TEX_INPUT_FILE_REGEX.match(line)

    if search != None:
        include_filter, input_filter, image_filter = search.groups()
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
    else:
        prefix = ''


    root = getTeXRoot.get_tex_root(view)
    if root:
        print ("TEX root: " + repr(root))

    completions = get_file_list(root, input_file_types)

    return prefix, completions

class LatexInputComplete(sublime_plugin.EventListener):
    
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0],
                "text.tex.latex"):
            return []

        point = locations[0]

        # Get some fileters
        prefix, completions = get_file_completions(view, point)

        result = []
        result += [('{}\t{}'.format(filename, relpath), '{}/{}'.format(relpath, filename)) for relpath, filename in completions]

        return (result, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


class LatexInputFileCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        view = self.view
        point = view.sel()[0].b
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
            return

        prefix, completions = get_file_completions(view, point)

        root_path = os.path.dirname(getTeXRoot.get_tex_root(self.view))
        result = [[os.path.normpath('{}/{}'.format(relpath, filename)), 
            os.path.normpath('{}/{}/{}'.format(root_path, relpath, filename))] for relpath, filename in completions]

        def on_done(i):
            # Doing Nothing
            if i < 0:
                return
            key = result[i][0]
            startpos = point - len(prefix)
            view.run_command("latex_tools_replace", {"a": startpos, "b": point, "replacement": key})
            caret = view.sel()[0].b
            view.sel().subtract(view.sel()[0])
            view.sel().add(sublime.Region(caret, caret))

        view.window().show_quick_panel(result, on_done)
