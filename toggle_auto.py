# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
else:
    _ST3 = True


import sublime_plugin

# Toggle focus after jumping to PDF

class ToggleAutoCommand(sublime_plugin.TextCommand):
	def run(self, edit, which, **args):
		print ("Toggling Auto " + which)
		s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
		prefs_auto = s.get(which+"_auto_trigger", True)
        
		if self.view.settings().get(which + " auto trigger",prefs_auto):
			self.view.settings().set(which + " auto trigger", False)
			sublime.status_message(which + " auto trigger OFF")
			print (which + " auto OFF")
		else:
			self.view.settings().set(which + " auto trigger", True)
			sublime.status_message(which + " auto trigger ON")
			print (which + " auto ON")

