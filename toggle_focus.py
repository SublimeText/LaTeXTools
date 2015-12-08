# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	from latextools_utils import get_setting
else:
	from .latextools_utils import get_setting


import sublime_plugin

# Toggle focus after jumping to PDF

class toggle_focusCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		keep_focus = get_setting('keep_focus', True)

		if keep_focus:
			self.view.settings().set("keep_focus", False)
			sublime.status_message("Focus PDF")
			print ("Focus PDF")
		else:
			self.view.settings().set("keep_focus", True)
			sublime.status_message("Focus editor")
			print ("Focus ST")
