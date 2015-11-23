# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	strbase = basestring
else:
	_ST3 = True
	strbase = str

from pdfBuilder import PdfBuilder
import sublime_plugin
import re
import os, os.path
import codecs

DEBUG = False

DEFAULT_COMMAND_LATEXMK = ["latexmk", "-cd", "-e", "-f", "-%E",
					"-latexoption=\"-interaction=nonstopmode\"",
					"-latexoption=\"-synctex=1\""]

DEFAULT_COMMAND_WINDOWS_MIKTEX = ["texify", "-b", "-p", "--engine=%E",
					"--tex-option=\"--synctex=1\""]

DOCUMENTCLASS_RE = re.compile(r'\\documentclass(?:\[[^\]]+\])?\{[^\}]+\}')


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
		self.options = builder_settings.get("options", [])
		if isinstance(self.options, strbase):
			self.options = [self.options]

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

		# check if the command even wants the engine selected
		engine_used = False
		for c in cmd:
			if "%E" in c:
				engine_used = True
				break

		# load the header from the root file to check for engine or options
		texroot_header = []
		for line in codecs.open(self.tex_root, "r", "UTF-8", "ignore").readlines():
			m = DOCUMENTCLASS_RE.search(line)
			if m:
				texroot_header.append(line[:m.start()])
				break
			elif not line.startswith('%'):
				continue

			texroot_header.append(line)

		texify = cmd[0] == 'texify'
		latexmk = cmd[0] == 'latexmk'

		if not engine_used:
			self.display("Your custom command does not allow the engine to be selected\n\n")
		else:
			for line in texroot_header:
				# We have a comment match; check for a TS-program match
				mroot = re.match(r"%+\s*!TEX\s+(?:TS-)?program *= *(xe(la)?tex|lua(la)?tex|pdf(la)?tex)\s*$",line)
				if mroot:
					engine = mroot.group(1)
					break

			if texify:
				# texify's --engine option takes pdftex/xetex/luatex as acceptable values
				engine = engine.replace("la","")
			elif latexmk:
				if "la" not in engine:
					# latexmk options only supports latex-specific versions
					engine = {
						"pdftex": "pdflatex",
						"xetex": "xelatex",
						"luatex": "lualatex"
					}[engine]

				# latexmk doesn't support -pdflatex
				if engine == 'pdflatex':
					engine = 'pdf'

			if engine != self.engine:
				self.display("Engine: " + self.engine + " -> " + engine + ". ")

			for i, c in enumerate(cmd):
				cmd[i] = c.replace("%E", engine)

		# handle any options
		if texify or latexmk:
			for line in texroot_header:
				m = re.match(r'%+\s*!TEX\s+option *= *([-\w]+)\s*$', line)
				if m:
					if texify:
						cmd.append("--tex-option=\"" + m.group(1) + "\"")
					else:
						cmd.append("-latexoption=\"" + m.group(1) + "\"")

			for option in self.options:
				if texify:
					cmd.append("--tex-option=\"" + option + "\"")
				else:
					cmd.append("-latexoption=\"" + option + "\"")

		# texify wants the .tex extension; latexmk doesn't care either way
		yield (cmd + [self.tex_name], "Invoking " + cmd[0] + "... ")

		self.display("done.\n")
		
		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")	
