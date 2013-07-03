# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
else:
    _ST3 = True


import sublime_plugin, os, os.path, re

# References and citations

spaces = {'part' : '', 'chapter' : '  ', 'section' : '    ',
		  'subsection' : '      ', 'subsubsection' : '        ',
		  'subsubsubsection' : '          '}

# ST2 note: we must keep the NamingConventionCommand style in the Python code,
# but the key bindings need "command": "naming_convention" 
#
# Also, for now must explicitly add key bindings in Preferences | User Key Bindings


class TexSectionsCommand(sublime_plugin.TextCommand):
	# ST2 note: (0) import sublime_plugin, not sublimeplugin
	#			(1) second arg is Edit, not View
	#               to get view, use self.view (?)
	#           (2) third arg is **args, not args
	#           (3) remember to change someMethod to some_method
	#           (4) panel not yet implemented :-(
	#			(5) to insert snippets (instead of insertInlineSnippet cmd):
	#				view.run_command('insert_snippet', {'contents' : 'TEXT'})
	#			(6) view.erase(region) becomes view.erase(edit, region) (?)
	#			(7) class names cannot have caps except for first one
	#				they must be: my_command_nameCommand
	#			(8) some commands, e.g. view.replace, require edit as param
	def run(self, edit, **args):
		# First get raw \section{xxx} lines
		# Capture the entire line beginning with our pattern, do processing later
		secRegions = self.view.find_all(r'^\\(begin\{frame\}|part|chapter|(?:sub)*section).*$')
		# Remove \section, etc and only leave spaces and titles
		# Handle frames separately
		# For sections, match \ followed by type followed by * or {, then
		# match everything. This captures the last }, which we'll remove
		secRe = re.compile(r'\\([^{*]+)\*?\{(.*)') # \, then anything up to a * or a {
		# Also, we need to remove \label{} statements
		labelRe = re.compile(r'\\label\{.*\}')
		# And also remove comments at the end of the line
		commentRe = re.compile(r'%.*$')
		# This is to match frames
		# Here we match the \begin{frame} command, with the optional [...]
		# and capture the rest of the line for further processing
		# TODO: find a way to capture \frametitle's on a different line
		frameRe = re.compile(r'\\begin\{frame\}(?:\[[^\]]\])?(.*$)')
		frameTitleRe = re.compile(r'\{(.*)\}')
		def prettify(s):
			s = commentRe.sub('',s).strip() # kill comments at the end of the line, blanks
			s = labelRe.sub('',s).strip() # kill label statements
			frameMatch = frameRe.match(s)
			if frameMatch:
				frame = frameMatch.group(1)
				frameTitleMatch = frameTitleRe.search(frame)
				if frameTitleMatch:
					return "frame: " + frameTitleMatch.group(1)
				else:
					return "frame: (untitled)"
			else:
				m = secRe.match(s)
				#print m.group(1,2)
				secTitle = m.group(2)
				if secTitle[-1]=='}':
					secTitle = secTitle[:-1]
				return spaces[m.group(1)]+secTitle
		prettySecs = [prettify(self.view.substr(reg)) for reg in secRegions]
		
		def onSelect(i):
			#print view.substr(secRegions[i])
			self.view.show(secRegions[i])
			s = self.view.sel() # RegionSet
			s.clear()
			s.add(secRegions[i])
			self.view.runCommand("moveTo bol")

		print (prettySecs)
		#self.view.window().show_select_panel(prettySecs, onSelect, None, 0)
