import sublime, sublime_plugin, os, os.path, platform
import getTeXRoot
from subprocess import Popen

# View PDF file corresonding to TEX file in current buffer
# Assumes that the SumatraPDF viewer is used (great for inverse search!)
# and its executable is on the %PATH%
# Warning: we do not do "deep" safety checks (e.g. see if PDF file is old)

class View_pdfCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		texFile, texExt = os.path.splitext(view.file_name())
		if texExt.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot view." % (os.path.basename(view.fileName()),))
			return
		quotes = ""# \"" MUST CHECK WHETHER WE NEED QUOTES ON WINDOWS!!!
		root = getTeXRoot.get_tex_root(view.file_name())
		rootFile, rootExt = os.path.splitext(root)
		pdfFile = quotes + rootFile + '.pdf' + quotes
		s = platform.system()
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
		else:
			sublime.error_message("Platform as yet unsupported. Sorry!")
			return	
		print viewercmd + [pdfFile]
		try:
			# this works on OSX but not Windows, and in any case it's old-fashioned
			#os.system(viewercmd + pdfFile)
			# better:
			Popen(viewercmd + [pdfFile])
		except OSError:
			sublime.error_message("Cannot launch Viewer. Make sure it is on your PATH.")

			
