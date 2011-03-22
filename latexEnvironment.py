import sublime, sublime_plugin

# Insert LaTeX environment based on current word
# Position cursor inside environment

class latexenvCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		view = self.view
		currword = view.word(view.sel()[0])
		command = view.substr(currword)
		view.erase(edit, currword)
		snippet = "\\\\begin{" + command + "}\n$1\n\\\\end{" + command + "}$0"
		view.run_command("insert_snippet", {'contents' : snippet})
