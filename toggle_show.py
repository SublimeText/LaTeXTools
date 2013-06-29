import sublime, sublime_plugin

# Show current toggles and prefs

class toggle_showCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
		prefs_keep_focus = s.get("keep_focus", "(default)")
		prefs_forward_sync = s.get("forward_sync", "(default)")
		prefs_auto_ref = s.get("ref_auto_trigger", "(default)")
		prefs_auto_cite = s.get("cite_auto_trigger", "(default)")
		keep_focus = self.view.settings().get("keep focus","undefined")
		forward_sync = self.view.settings().get("forward_sync","undefined")
		auto_ref = self.view.settings().get("ref auto trigger", "undefined")
		auto_cite = self.view.settings().get("cite auto trigger", "undefined")


		sublime.status_message("Keep focus: pref %s toggle %s         Forward sync: pref %s toggle %s         Auto ref: pref %s toggle %s         Auto cite: pref %s toggle %s" 
			% (prefs_keep_focus, keep_focus, prefs_forward_sync, forward_sync, prefs_auto_ref, auto_ref,prefs_auto_cite,auto_cite))
