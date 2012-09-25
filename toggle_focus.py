import sublime, sublime_plugin

# Toggle focus after jumping to PDF

class toggle_focusCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
		prefs_keep_focus = s.get("keep_focus", True)

		if self.view.settings().get("keep focus",prefs_keep_focus):
			self.view.settings().set("keep focus", False)
			sublime.status_message("Focus PDF")
			print "Focus PDF"
		else:
			self.view.settings().set("keep focus", True)
			sublime.status_message("Focus editor")
			print "Focus ST2"

