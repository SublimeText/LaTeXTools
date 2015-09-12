import re
import os

import sublime
import sublime_plugin

if sublime.version() < '3000':
    _ST3 = False
    # we are on ST2 and Python 2.X
    from getTeXRoot import get_tex_root
else:
    _ST3 = True
    from .getTeXRoot import get_tex_root


class JumptoTexFileUnderCaretCommand(sublime_plugin.TextCommand):

    def _create_folders(self, base_path, new_file_name, test_only):
        # create missing folders
        create_path = base_path
        # gain the path to the file, e.g. "a/b/c.tex" -> ["a", "b"]
        path = new_file_name.split("/")[:-1]
        for folder in path:
            create_path += "/" + folder
            if not os.path.exists(create_path):
                if test_only:
                    return False
                os.mkdir(create_path)
                print("Created folder: '%s'" % create_path)
        return True

    def _insert_root_to_file(self, root_name, new_file_name):
        base_path, base_name = os.path.split(root_name)
        new_file = base_path + "/" + new_file_name
        if not os.path.exists(new_file):
            # set the path to the root, from the path to the file, e.g.
            # "a/b/new_file.tex" -> "../../root.tex"
            path = re.sub(r"[\w]+/", "../", new_file_name)
            path = re.sub(r"[^/]*$", "", path)
            root_string = "%!TEX root = " + path + base_name
            with open(new_file, "a", encoding="utf8") as f:
                f.write(root_string)

    def run(self, edit, auto_create_missing_folders=True,
            auto_insert_root=True):
        view = self.view
        tex_root = get_tex_root(view)
        if tex_root is None:
            sublime.status_message("Save your current file first")
            return

        # the base path to the root file
        base_path, base_name = os.path.split(tex_root)

        reg = re.compile(
            r"\\in((clude)|(put))(\[.*\])?"
            r"\{(?P<file>[\w/]+)(?P<end>\.((tex)|(tikz)))?\}"
        )
        for sel in view.sel():
            line = view.substr(view.line(sel))
            g = re.search(reg, line)
            if g and g.group("file"):
                # the file ending (tex or tikz)
                end = g.group("end") if g.group("end") else ".tex"
                new_file_name = "%s%s" % (g.group("file"), end)

                # create the missing folder / check if all path folders exists
                valid = self._create_folders(base_path, new_file_name,
                                             not auto_create_missing_folders)
                if not valid:
                    sublime.status_message(
                        "Cannot open tex file, folders are missing")
                    return

                if auto_insert_root:
                    self._insert_root_to_file(tex_root, new_file_name)

                full_new_file_name = base_path + "/" + new_file_name
                self.view.window().open_file(full_new_file_name)
