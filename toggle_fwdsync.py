# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
else:
    _ST3 = True


import sublime, sublime_plugin

# Toggle forward syncing to PDF after compiling

class toggle_fwdsyncCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
		prefs_forward_sync = s.get("forward_sync", True)

		if self.view.settings().get("forward_sync",prefs_forward_sync):
			self.view.settings().set("forward_sync", False)
			sublime.status_message("Do not forward sync PDF (keep current position)")
			print ("Do not forward sync PDF")
		else:
			self.view.settings().set("forward_sync", True)
			sublime.status_message("Forward sync PDF after compiling")
			print ("Forward sync PDF")

