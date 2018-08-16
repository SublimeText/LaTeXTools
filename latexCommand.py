# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = True
else:
    _ST3 = False

import sublime_plugin
import re


# Insert LaTeX command based on current word
# Position cursor inside braces

class latexcmdCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		view = self.view

		# Workaround: env* and friends trip ST2 up because * is a word boundary,
		# so we search for a word boundary

		# Code is similar to latex_cite_completions.py (should prbly factor out)
		point = view.sel()[0].b
		line = view.substr(sublime.Region(view.line(point).a, point))
		line = line[::-1]
		# Stop at space, {,[,( or $
		rex = re.compile(r"([^\s\{\[\(\$]*)\s?\{?")
		expr = re.match(rex, line)
		if expr:
			command = expr.group(1)[::-1]
			if command:
				command_region = sublime.Region(point-len(command),point)
				view.erase(edit, command_region)
				# Be forgiving and skip \ if the user provided one (by mistake...)
				bslash = "" if command[0] == '\\' else "\\\\"
				snippet = bslash + command + "{$1} $0"
			else:
				snippet = "\\\\$1{$2} $0"
			view.run_command("insert_snippet", {'contents': snippet})
		else:
			sublime.status_message("LATEXTOOLS INTERNAL ERROR: could not find command to expand")

