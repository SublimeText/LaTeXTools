import re
import os
import codecs
import traceback

import sublime
import sublime_plugin

try:
    _ST3 = True
    from .getTeXRoot import get_tex_root
except:
    _ST3 = False
    from getTeXRoot import get_tex_root


# TODO this might be moved to a generic util
def run_after_loading(view, func):
    """Run a function after the view has finished loading"""
    def run():
        if view.is_loading():
            sublime.set_timeout(run, 10)
        else:
            # add an additional delay, because it might not be ready
            # even if the loading function returns false
            sublime.set_timeout(func, 10)
    run()


class JumptoTexFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, auto_create_missing_folders=True,
            auto_insert_root=True):
        view = self.view
        window = view.window()
        tex_root = get_tex_root(view)
        if tex_root is None:
            sublime.status_message("Save your current file first")
            return

        # the base path to the root file
        base_path, base_name = os.path.split(tex_root)

        reg = re.compile(
            r"\\(?:input|include|subfile)\{(?P<file>[^}]+)\}",
            re.UNICODE
        )
        for sel in view.sel():
            line = view.substr(view.line(sel))
            g = re.search(reg, line)
            if g and g.group("file"):
                new_file_name = g.group('file')

                _, ext = os.path.splitext(new_file_name)
                if not ext:
                    new_file_name += '.tex'

                # clean-up any directory manipulating components
                new_file_name = os.path.normpath(new_file_name)

                containing_folder, new_file_name = os.path.split(new_file_name)

                # allow absolute paths on \include or \input
                isabs = os.path.isabs(containing_folder)
                if not isabs:
                    containing_folder = os.path.normpath(
                        os.path.join(base_path, containing_folder))

                # create the missing folder
                if auto_create_missing_folders and\
                        not os.path.exists(containing_folder):
                    try:
                        os.makedirs(containing_folder)
                    except OSError:
                        # most likely a permissions error
                        print('Error occurred while creating path "{0}"'
                              .format(containing_folder))
                        traceback.print_last()
                    else:
                        print('Created folder: "{0}"'
                              .format(containing_folder))

                if not os.path.exists(containing_folder):
                    sublime.status_message(
                        "Cannot open tex file as folders are missing")
                    continue

                is_root_inserted = False
                full_new_path = os.path.join(containing_folder, new_file_name)
                if auto_insert_root and not os.path.exists(full_new_path):
                    if isabs:
                        root_path = tex_root
                    else:
                        root_path = os.path.join(
                            os.path.relpath(base_path, containing_folder),
                            base_name)

                    # Use slashes consistent with TeX's usage
                    if sublime.platform() == 'windows' and not isabs:
                        root_path = root_path.replace('\\', '/')

                    root_string = '%!TEX root = {0}\n'.format(root_path)
                    try:
                        with codecs.open(full_new_path, "w", "utf8") as new_file:
                            new_file.write(root_string)
                        is_root_inserted = True
                    except OSError:
                        print('An error occurred while creating file "{0}"'
                              .format(new_file_name))
                        traceback.print_last()

                # open the file
                new_view = window.open_file(full_new_path)

                # await opening and move cursor to end of the new view
                # (does not work on st2)
                if _ST3 and auto_insert_root and is_root_inserted:
                    def set_caret_position():
                        cursor_pos = len(root_string)
                        new_view.sel().clear()
                        new_view.sel().add(sublime.Region(cursor_pos,
                                                          cursor_pos))
                    run_after_loading(new_view, set_caret_position)
