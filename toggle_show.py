import sublime, sublime_plugin

# Show current toggles and prefs

class toggle_showCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
		prefs_keep_focus = s.get("keep_focus", "undefined")
		prefs_forward_sync = s.get("forward_sync", "undefined")
		keep_focus = self.view.settings().get("keep focus","undefined")
		forward_sync = self.view.settings().get("forward_sync","undefined")

		sublime.status_message("Keep focus: pref %s toggle %s\t Forward sync: pref %s toggle %s" 
			% (prefs_keep_focus, keep_focus, prefs_forward_sync, forward_sync))
