import sublime, sublime_plugin, re, os.path

class jump_to_includeCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		view = self.view
		selLine = view.substr(view.line(view.sel()[0]))
		match = re.match(r"\\in(?:clude|put)\{([a-zA-Z\._/\\]+)\}", selLine)
		if not match:
			sublime.status_message("Is your cursor on a line with a \input or \include statement?")
			return

		rootDirName = sublime.active_window().folders()[0]
		file = os.path.join(rootDirName, match.groups()[0] + ".tex")
		if not os.path.isfile(file):
			sublime.status_message("File " + file + "not found.")
			return

		view.window().open_file(file, sublime.TRANSIENT)
		return