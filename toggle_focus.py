import sublime, sublime_plugin

# Toggle focus after jumping to PDF

class toggle_focusCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		if self.view.settings().get("keep focus",True):
			self.view.settings().set("keep focus", False)
			sublime.status_message("Focus PDF")
			print "Focus PDF"
		else:
			self.view.settings().set("keep focus", True)
			sublime.status_message("Focus editor")
			print "Focus ST2"

