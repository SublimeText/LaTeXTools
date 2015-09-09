import sublime, sublime_plugin

if sublime.version() < '3000':
	from latextools_utils import get_setting
else:
	from .latextools_utils import get_setting

# Show current toggles and prefs

class toggle_showCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		keep_focus = get_setting('keep_focus', '(default)')
		forward_sync = get_setting('forward_sync', '(default)')
		auto_ref = get_setting('ref_auto_trigger', '(default)')
		auto_cite = get_setting('cite_auto_trigger', '(default)')

		sublime.status_message("Keep focus: pref %s toggle %s         Forward sync: pref %s toggle %s         Auto ref: pref %s toggle %s         Auto cite: pref %s toggle %s" 
			% (
                'keep_focus', keep_focus, 
                'forward_sync', forward_sync, 
                'ref_auto_trigger', auto_ref,
                'cite_auto_trigger', auto_cite
            ))
