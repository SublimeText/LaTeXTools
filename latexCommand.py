import sublime, sublime_plugin

# Insert LaTeX command based on current word
# Position cursor inside braces

class latexcmdCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		view = self.view
		currword = view.word(view.sel()[0])
		command = view.substr(currword)
		view.erase(edit, currword)
		snippet = "\\\\" + command + "{$1} $0"
		print "insertInlineSnippet" + snippet
		view.run_command("insert_snippet", {'contents': snippet})
