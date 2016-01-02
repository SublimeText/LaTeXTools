# ST2/ST3 compat
from __future__ import print_function
import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
	from latextools_utils.is_tex_file import is_tex_file
	from latextools_utils import get_setting
else:
	_ST3 = True
	from . import getTeXRoot
	from .latextools_utils.is_tex_file import is_tex_file
	from .latextools_utils import get_setting

import sublime_plugin, os, os.path
from subprocess import Popen


# View PDF file corresonding to TEX file in current buffer
# Assumes that the SumatraPDF viewer is used (great for inverse search!)
# and its executable is on the %PATH%
# Warning: we do not do "deep" safety checks (e.g. see if PDF file is old)

class View_pdfCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if not is_tex_file(view.file_name()):
			sublime.error_message("%s is not a TeX source file: cannot view." % (os.path.basename(view.file_name()),))
			return
		quotes = ""# \"" MUST CHECK WHETHER WE NEED QUOTES ON WINDOWS!!!
		root = getTeXRoot.get_tex_root(view)

		rootFile, rootExt = os.path.splitext(root)
		pdfFile = quotes + rootFile + '.pdf' + quotes
		script_path = None
		p = sublime.platform()
		if p == "osx":
			# for inverse search, set up a "Custom" sync profile, using
			# "subl" as command and "%file:%line" as argument
			# you also have to put a symlink to subl somewhere on your path
			# Also check the box "check for file changes"
			viewercmd = ["open", "-a", "Skim"]
		elif p == "windows":
			# with new version of SumatraPDF, can set up Inverse 
			# Search in the GUI: under Settings|Options...
			# Under "Set inverse search command-line", set:
			# sublime_text "%f":%l
			su_binary = get_setting("sumatra", "SumatraPDF.exe")
			viewercmd = [su_binary, "-reuse-instance"]		
		elif p == "linux":
			# the required scripts are in the 'evince' subdir
			script_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'evince')
			ev_sync_exec = os.path.join(script_path, 'evince_sync') # so we get inverse search
			# Get python binary if set in preferences:
			py_binary = get_setting('python2', 'python')
			sb_binary = get_setting('sublime', 'sublime_text')
			viewercmd = ['sh', ev_sync_exec, py_binary, sb_binary]
		else:
			sublime.error_message("Platform as yet unsupported. Sorry!")
			return	
		print (viewercmd + [pdfFile])
		try:
			Popen(viewercmd + [pdfFile], cwd=script_path)
		except OSError:
			sublime.error_message("Cannot launch Viewer. Make sure it is on your PATH.")
