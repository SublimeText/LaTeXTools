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

class ToggleAutoCommand(sublime_plugin.TextCommand):
	def run(self, edit, which, **args):
		print ("Toggling Auto " + which)
		auto = get_setting(which + '_auto_trigger', True)
        
		if auto:
			self.view.settings().set(which + "_auto_trigger", False)
			sublime.status_message(which + " auto trigger OFF")
			print (which + " auto OFF")
		else:
			self.view.settings().set(which + "_auto_trigger", True)
			sublime.status_message(which + " auto trigger ON")
			print (which + " auto ON")

