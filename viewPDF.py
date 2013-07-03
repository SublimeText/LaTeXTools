# ST2/ST3 compat
from __future__ import print_function
import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
else:
	_ST3 = True
	from . import getTeXRoot

import sublime_plugin, os, os.path, platform
from subprocess import Popen


# View PDF file corresonding to TEX file in current buffer
# Assumes that the SumatraPDF viewer is used (great for inverse search!)
# and its executable is on the %PATH%
# Warning: we do not do "deep" safety checks (e.g. see if PDF file is old)

class View_pdfCommand(sublime_plugin.WindowCommand):
	def run(self):
		s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
		prefs_keep_focus = s.get("keep_focus", True)
		prefs_lin = s.get("linux")

		view = self.window.active_view()
		texFile, texExt = os.path.splitext(view.file_name())
		if texExt.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot view." % (os.path.basename(view.file_name()),))
			return
		quotes = ""# \"" MUST CHECK WHETHER WE NEED QUOTES ON WINDOWS!!!
		root = getTeXRoot.get_tex_root(view)

		rootFile, rootExt = os.path.splitext(root)
		pdfFile = quotes + rootFile + '.pdf' + quotes
		s = platform.system()
		script_path = None
		if s == "Darwin":
			# for inverse search, set up a "Custom" sync profile, using
			# "subl" as command and "%file:%line" as argument
			# you also have to put a symlink to subl somewhere on your path
			# Also check the box "check for file changes"
			viewercmd = ["open", "-a", "Skim"]
		elif s == "Windows":
			# with new version of SumatraPDF, can set up Inverse 
			# Search in the GUI: under Settings|Options...
			# Under "Set inverse search command-line", set:
			# sublime_text "%f":%l
			viewercmd = ["SumatraPDF", "-reuse-instance"]		
		elif s == "Linux":
			# the required scripts are in the 'evince' subdir
			script_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'evince')
			ev_sync_exec = os.path.join(script_path, 'evince_sync') # so we get inverse search
			# Get python binary if set in preferences:
			py_binary = prefs_lin["python2"] or 'python'
			sb_binary = prefs_lin["sublime"] or 'sublime-text'
			viewercmd = ['sh', ev_sync_exec, py_binary, sb_binary]
		else:
			sublime.error_message("Platform as yet unsupported. Sorry!")
			return	
		print (viewercmd + [pdfFile])
		try:
			Popen(viewercmd + [pdfFile], cwd=script_path)
		except OSError:
			sublime.error_message("Cannot launch Viewer. Make sure it is on your PATH.")

			
