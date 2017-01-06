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
import shlex

DEBUG = False

DEFAULT_COMMAND_LATEXMK = ["latexmk", "-cd", "-f", "-%E",
					"-interaction=nonstopmode", "-synctex=1"]

DEFAULT_COMMAND_WINDOWS_MIKTEX = ["texify", "-b", "-p", "--engine=%E",
					"--tex-option=\"--synctex=1\""]


#----------------------------------------------------------------
# TraditionalBuilder class
#
# Implement existing functionality, more or less
# NOTE: move this to a different file, too
#
class TraditionalBuilder(PdfBuilder):

	def __init__(self, *args):
		# Sets the file name parts, plus internal stuff
		super(TraditionalBuilder, self).__init__(*args)
		# Now do our own initialization: set our name
		self.name = "Traditional Builder"
		# Display output?
		self.display_log = self.builder_settings.get("display_log", False)
		# Build command, with reasonable defaults
		plat = sublime.platform()
		# Figure out which distro we are using
		distro = self.platform_settings.get(
			"distro",
			"miktex" if plat == "windows" else "texlive"
		)
		if distro in ["miktex", ""]:
			default_command = DEFAULT_COMMAND_WINDOWS_MIKTEX
		else:  # osx, linux, windows/texlive, everything else really!
			default_command = DEFAULT_COMMAND_LATEXMK

		self.cmd = self.builder_settings.get("command", default_command)
		if isinstance(self.cmd, strbase):
			self.cmd = shlex.split(self.cmd)

	#
	# Very simple here: we yield a single command
	# Only complication is handling custom tex engines
	#
	def commands(self):
		# Print greeting
		self.display("\n\nTraditionalBuilder: ")

		# See if the root file specifies a custom engine
		engine = self.engine
		cmd = self.cmd[:]  # Warning! If I omit the [:], cmd points to self.cmd!

		# check if the command even wants the engine selected
		engine_used = False
		for c in cmd:
			if "%E" in c:
				engine_used = True
				break

		texify = cmd[0] == 'texify'
		latexmk = cmd[0] == 'latexmk'

		if not engine_used:
			self.display("Your custom command does not allow the engine to be selected\n\n")
		else:
			self.display("Engine: {0}. ".format(engine))

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

			for i, c in enumerate(cmd):
				cmd[i] = c.replace(
					"-%E", "-" + engine if texify or engine != 'pdflatex' else '-pdf'
				).replace("%E", engine)

		# handle any options
		if texify or latexmk:
			# we can only handle aux_directory, output_directory, or jobname
			# with latexmk
			if latexmk:
				if (
					self.aux_directory is not None and
					self.aux_directory != self.output_directory
				):
					# DO NOT ADD QUOTES HERE
					cmd.append(
						u"--aux-directory=" +
						self.aux_directory
					)

				if (
					self.output_directory is not None
				):
					# DO NOT ADD QUOTES HERE
					cmd.append(
						u"--output-directory=" +
						self.output_directory
					)

				if self.job_name != self.base_name:
					cmd.append(
						u"--jobname=" + self.job_name
					)

			for option in self.options:
				if texify:
					cmd.append(u"--tex-option=\"" + option + "\"")
				else:
					cmd.append(u"-latexoption=" + option)

		# texify wants the .tex extension; latexmk doesn't care either way
		yield (cmd + [self.tex_name], "Invoking " + cmd[0] + "... ")

		self.display("done.\n")

		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")	
