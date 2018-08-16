import os
import re

import sublime
import sublime_plugin

if sublime.version() < '3000':
    _ST3 = False
else:
    _ST3 = True


_OVERWRITE, _CHANGE, _CANCEL = 0, 1, 2
if _ST3:
    def _user_permission_dialog():
        message = ("Mousemap already exists. "
                   "Do you want to overwrite or change it?")
        answer = sublime.yes_no_cancel_dialog(message, "Overwrite",
                                              "Change existing mousemap")
        if answer == sublime.DIALOG_YES:
            result = _OVERWRITE
        elif answer == sublime.DIALOG_NO:
            result = _CHANGE
        else:
            result = _CANCEL
        return result
else:
    def _user_permission_dialog():
        message = "Mousemap already exists. Do you want to overwrite it?"
        ok = sublime.ok_cancel_dialog(message, "Overwrite")
        if ok:
            result = _OVERWRITE
        else:
            message = "Do you want me to change it?"
            ok = sublime.ok_cancel_dialog(message, "Change existing mousemap")
            result = _CHANGE if ok else _CANCEL
        return result


class LatextoolsCreateMousemapCommand(sublime_plugin.WindowCommand):
    def run(self):
        # detect whether SublimeCodeIntel is installed or not
        try:
            import SublimeCodeIntel
            sci_installed = True
            print("SublimeCodeIntel is installed")
        except:
            sci_installed = False
            print("SublimeCodeIntel is not installed")
        ltt_folder = os.path.join(sublime.packages_path(), "LaTeXTools")
        user_folder = os.path.join(sublime.packages_path(), "User")
        plat = sublime.platform()
        if plat == "osx":
            plat = plat.upper()
        else:
            plat = plat.title()
        mousemap_file = "Default ({0}).sublime-mousemap".format(plat)

        ltt_mouse_file = os.path.join(ltt_folder, mousemap_file)
        user_mouse_file = os.path.join(user_folder, mousemap_file)

        if not os.path.exists(ltt_mouse_file):
            print("Mousemap is missing {0}".format(ltt_mouse_file))
            return

        def read_ltt_content():
            with open(ltt_mouse_file, "r") as f:
                content = f.read()
            if sci_installed:
                # add the fallback command
                replace_from = '"fallback_command": ""'
                replace_to = '"fallback_command": "goto_python_definition"'
                content = content.replace(replace_from, replace_to)
                # change the keybindings to the one used by SCI
                if plat == "OSX":
                    replace_from = '["ctrl", "super"]'
                    replace_to = '["ctrl"]'
                    content = content.replace(replace_from, replace_to)
                elif plat == "Windows":
                    replace_from = '["ctrl", "alt"]'
                    replace_to = '["alt"]'
                    content = content.replace(replace_from, replace_to)
            return content

        def replace_old_mousemap():
            content = read_ltt_content()
            with open(user_mouse_file, "w") as f:
                f.write(content)
            # open the mouse map, such that the user can change the modifier
            self.window.open_file(user_mouse_file)

        def append_to_old_mousemap():
            with open(user_mouse_file, "r") as f:
                user_content = f.read()
            ltt_content = read_ltt_content()
            # replace leading [ by , (will be appended to the other mousemap)
            ltt_content = "," + ltt_content[1:]
            # replace the last closing ] with the ltt command, i.e.
            # add the ltt command to the user mouse map
            end_brace = re.compile(r"\s*\]\s*$", re.UNICODE | re.MULTILINE)
            content = re.sub(end_brace, ltt_content, user_content)
            with open(user_mouse_file, "r+") as f:
                f.write(content)
            # open the mouse map, such that the user can check the correctness
            self.window.open_file(user_mouse_file)

        if not os.path.exists(user_mouse_file):
            replace_old_mousemap()
        else:
            choosen_option = _user_permission_dialog()
            if choosen_option == _OVERWRITE:
                replace_old_mousemap()
            elif choosen_option == _CHANGE:
                append_to_old_mousemap()
