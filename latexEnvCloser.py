# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
else:
    _ST3 = True


import sublime_plugin

# Insert environment closer
# this only looks at the LAST \begin{...}
# need to extend to allow for nested \begin's

class latex_env_closerCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		view = self.view
		pattern = r'\\(begin|end)\{[^\}]+\}'
		b = []
		currpoint = view.sel()[0].b
		point = 0
		r = view.find(pattern, point)
		while r and r.end() <= currpoint:
			be = view.substr(r)
			point = r.end()
			if "\\begin" == be[0:6]:
				b.append(be[6:])
			else:
				if be[4:] == b[-1]:
					b.pop()
				else:
					sublime.error_message("\\begin%s closed with %s on line %d"
					% (b[-1], be, view.rowcol(point)[0])) 
					return
			r = view.find(pattern, point)
		# now either b = [] or b[-1] is unmatched
		if b == []:
			sublime.error_message("Every environment is closed")
		else:
			# note the double escaping of \end
			#view.run_command("insertCharacters \"\\\\end" + b[-1] + "\\n\"")
			print ("now we insert")
			# for some reason insert does not work
			view.run_command("insert_snippet", 
								{'contents': "\\\\end" + b[-1] + "\n"})
