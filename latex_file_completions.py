import os
import re

import sublime
import sublime_plugin

if sublime.version() < '3000':
    _ST3 = False
    # we are on ST2 and Python 2.X
    from getTeXRoot import get_tex_root
else:
    _ST3 = True
    from .getTeXRoot import get_tex_root

# compile when the autocompletion should be triggered
_RE_BEFORE = re.compile(
    r".*\\(?P<command>(include)|(input)|(includegraphics))"
    r"(\[.*\])?"
    r"{"
    r"(?P<prefix>(\w/\\-)*)"
    r"[\w-]*"
    r"$"
)

# define which extensions should be removed
_STRIP_EX = [
    ".tex"
]


def strip_extension(file_name):
    new_name, ext = os.path.splitext(file_name)
    return new_name if ext in _STRIP_EX else file_name


def walk_directory(current_dir, file_extensions):
    # walk over all subdirectories and search files
    tex_files = []
    current_dir_len = len(current_dir) + 1
    for root, dirs, files in os.walk(current_dir):
        for tex_file in files:
            # only handle files, which are white-listed
            if file_extensions is None or any(
                    tex_file.lower().endswith(".%s" % ext)
                    for ext in file_extensions):
                # get the directory offset to the current directory
                directory = ""
                if current_dir_len < len(root):
                    directory = root[current_dir_len:] + "/"
                    # replace the path for windows platforms
                    directory = directory.replace("\\", "/")
                full_tex_name = directory + tex_file
                tex_files.append(full_tex_name)
    # strip file extensions
    return [strip_extension(f) for f in tex_files]


class LatexFileCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        # Only trigger within LaTeX
        if not view.match_selector(locations[0], "text.tex.latex"):
            return []

        point = locations[0]
        line = view.line(point)
        before = view.substr(sublime.Region(line.a, point))

        # check if the line starts with an insertion statement
        m = _RE_BEFORE.match(before)
        if not m:
            return []

        tex_root = get_tex_root(view)
        if not tex_root:
            return []
        current_dir = os.path.dirname(tex_root)

        command = m.group("command")
        files = []
        if command == "input" or command == "include":
            files = walk_directory(current_dir, ["tex", "tikz"])
        elif command == "includegraphics":
            files = walk_directory(current_dir,
                                   ["eps", "jpg", "jpeg", "png", "pdf"])

        return [(f, f) for f in files]


class InsertFileNameCommand(sublime_plugin.TextCommand):
    def run(self, edit, insert_before=None, insert_after=None,
            file_extensions=None):
        view = self.view
        window = view.window()

        # assign the text before and after if None
        if insert_before is None:
            insert_before = ""
        if insert_after is None:
            close_parens = {"(": ")", "{": "}", "[": "]"}
            insert_after = close_parens.get(insert_before, "")

        # retrieve the directory, in which the files are listed
        # i.e. directory of the tex root or the current file
        tex_root = get_tex_root(view)
        if tex_root is None:
            sublime.status_message(
                "Save your file to show available inputs.")
            insert_str = "%s$0%s" % (insert_before, insert_after)
            view.run_command("insert_snippet", {"contents": insert_str})
            return

        current_dir = os.path.dirname(tex_root)
        tex_files = walk_directory(current_dir, file_extensions)

        def insert_file_name(index):
            if index != -1:
                file_name = tex_files[index]
                insert_str = insert_before + file_name + insert_after
                view.run_command("insert", {"characters": insert_str})
            else:
                insert_str = "%s$0%s" % (insert_before, insert_after)
                view.run_command("insert_snippet", {"contents": insert_str})

        window.show_quick_panel(tex_files, insert_file_name)
