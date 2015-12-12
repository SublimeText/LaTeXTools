import os
import sublime
import sublime_plugin


class open_latextools_default_settings(sublime_plugin.WindowCommand):
	def __init__(self, *args, **kwargs):
		super(open_latextools_default_settings, self).__init__(*args, **kwargs)
		self.view = None

	def run(self):
		self.view = sublime.active_window().open_file(
			os.path.join(
				sublime.packages_path(),
				"LaTeXTools",
				"LaTeXTools.sublime-settings"
			)
		)

		sublime.set_timeout(self.set_view_readonly, 1)

	def set_view_readonly(self):
		if self.view is None or self.view.is_loading():
			sublime.set_timeout(self.set_view_readonly, 1)

		self.view.set_read_only(True)
