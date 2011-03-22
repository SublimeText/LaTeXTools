import sublime, sublime_plugin, os, os.path, re

# References and citations

done = False

class tex_refCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		# get current point
		# assume no selection, or a singe selection (for now)
		print "Hello!"
		currsel = self.view.sel()[0]
		point = currsel.b
		prefix = self.view.substr(self.view.word(point)).strip()
		print currsel, point, prefix,len(prefix)
		completions = []
		self.view.find_all('\\label\{([^\{]*)\}',0,'\\1',completions)
#		print completions
#		print "%d labels" % (len(completions),)
		# no prefix, or braces
		if not prefix in ["", "{}", "{", "}"]:
			fcompletions = [comp for comp in completions if prefix in comp]
		else:
			prefix = "" # in case it's {} or { or }
			fcompletions = completions
		# The drop-down completion menu contains at most 16 items, so
		# show selection panel if we have more.
		print prefix, len(fcompletions)
		if len(fcompletions) == 0:
			sublime.error_message("No references starting with %s!" % (prefix,))
			return
		if len(fcompletions) <= 16:
			self.view.show_completions(point, prefix, fcompletions)
		else:
			def onSelect(i):
				# if we had an actual prefix, replace it with the label,
				# otherwise insert the label.
				# FIXME like TextMate, if you give e.g. thm:so as prefix
				# you may get thm:thm:something
				if prefix not in ["", "{}", "{", "}"]:
					view.replace(currword, fcompletions[i])
				else:
					view.insert(point, fcompletions[i])
			view.window().show_select_panel(fcompletions, onSelect, None, 0)
		print "done"

