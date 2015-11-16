# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True

from pdfBuilder import PdfBuilder
import sublime_plugin
import re
import os, os.path
import codecs

DEBUG = False

DEFAULT_COMMAND_LATEXMK = ["latexmk", "-cd",
				"-e", "$pdflatex = '%E -interaction=nonstopmode -synctex=1 %S %O'",
				"-f", "-pdf"]

DEFAULT_COMMAND_WINDOWS_MIKTEX = ["texify", 
					"-b", "-p", "--engine=%E",
					"--tex-option=\"--synctex=1\""]


#----------------------------------------------------------------
# TraditionalBuilder class
#
# Implement existing functionality, more or less
# NOTE: move this to a different file, too
#
class TraditionalBuilder(PdfBuilder):

	def __init__(self, tex_root, output, builder_settings, platform_settings):
		# Sets the file name parts, plus internal stuff
		super(TraditionalBuilder, self).__init__(tex_root, output, builder_settings, platform_settings) 
		# Now do our own initialization: set our name
		self.name = "Traditional Builder"
		# Display output?
		self.display_log = builder_settings.get("display_log", False)
		# Build command, with reasonable defaults
		plat = sublime.platform()
		# Figure out which distro we are using
		try:
			distro = platform_settings["distro"]
		except KeyError: # default to miktex on windows and texlive elsewhere
			if plat == 'windows':
				distro = "miktex"
			else:
				distro = "texlive"
		if distro in ["miktex", ""]:
			default_command = DEFAULT_COMMAND_WINDOWS_MIKTEX
		else: # osx, linux, windows/texlive, everything else really!
			default_command = DEFAULT_COMMAND_LATEXMK
		self.cmd = builder_settings.get("command", default_command)
		# Default tex engine (pdflatex if none specified)
		self.engine = builder_settings.get("program", "pdflatex")
		# Sanity check: if "strange" engine, default to pdflatex (silently...)
		if not(self.engine in ['pdflatex', "pdftex", 'xelatex', 'xetex', 'lualatex', 'luatex']):
			self.engine = 'pdflatex'



	#
	# Very simple here: we yield a single command
	# Only complication is handling custom tex engines
	#
	def commands(self):
		# Print greeting
		self.display("\n\nTraditionalBuilder: ")

		# See if the root file specifies a custom engine
		engine = self.engine
		cmd = self.cmd[:] # Warning! If I omit the [:], cmd points to self.cmd!
		for line in codecs.open(self.tex_root, "r", "UTF-8", "ignore").readlines():
			if not line.startswith('%'):
				break
			else:
				# We have a comment match; check for a TS-program match
				mroot = re.match(r"%\s*!TEX\s+(?:TS-)?program *= *(xe(la)?tex|lua(la)?tex|pdf(la)?tex)\s*$",line)
				if mroot:
					engine = mroot.group(1)
					if cmd[0] == "texify":
						if not re.match(r"--engine\s?=\s?%E", cmd[3]):
							cmd.append("--engine=%E")
					if cmd[0] == "latexmk":
					  # Sanity checks
					  if not re.match(r"\$pdflatex\s?=\s?'%E", cmd[3]): # fixup blanks (linux)
						  sublime.error_message("You are using a custom build command.\n"\
							  "Cannot select engine using a %!TEX program directive.\n")
						  yield("", "Could not compile.")
					
					break

		if cmd[0] == "texify":
			engine = engine.replace("la","") # texify's --engine option takes pdftex/xetex/luatex as acceptable values

		if engine != self.engine:
			self.display("Engine: " + self.engine + " -> " + engine + ". ")
			
		cmd[3] = cmd[3].replace("%E", engine)

		# texify wants the .tex extension; latexmk doesn't care either way
		yield (cmd + [self.tex_name], "Invoking " + cmd[0] + "... ")

		self.display("done.\n")
		
		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")	
