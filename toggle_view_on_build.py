# ST2/ST3 compat
from __future__ import print_function

import sublime
import sublime_plugin

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    from latextools_utils import get_setting
else:
    from .latextools_utils import get_setting


# Toggle viewing the PDF after compiling
class ToggleViewOnBuild(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        if get_setting('open_pdf_on_build', True):
            self.view.settings().set("open_pdf_on_build", False)
            sublime.status_message("Do not open PDF on build")
            print("Do not open PDF on build")
        else:
            self.view.settings().set("open_pdf_on_build", True)
            sublime.status_message("Open PDF on build")
            print("Open PDF on build")
