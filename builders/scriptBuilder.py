from pdfBuilder import PdfBuilder
import sublime

import subprocess
from subprocess import Popen, PIPE, STDOUT

from copy import copy
import os
import shlex
import sys

if sys.version_info < (3, 0):
	strbase = basestring
else:
	strbase = str


#----------------------------------------------------------------
# ScriptBuilder class
#
# Launch a user-specified script
#
class ScriptBuilder(PdfBuilder):

	def __init__(self, tex_root, output, builder_settings, platform_settings):
		# Sets the file name parts, plus internal stuff
		super(ScriptBuilder, self).__init__(tex_root, output, builder_settings, platform_settings) 
		# Now do our own initialization: set our name
		self.name = "Script Builder"
		# Display output?
		self.display_log = builder_settings.get("display_log", False)
		plat = sublime.platform()
		self.cmd = builder_settings[plat].get("command", None)
		self.env = builder_settings[plat].get("env", None)

	# Very simple here: we yield a single command
	# Also add environment variables
	def commands(self):
		# Print greeting
		self.display("\n\nScriptBuilder: ")

		# figure out safe way to pass self.env back
		# OK, probably need to modify yield call throughout
		# and pass via Popen. Wait for now

		if self.cmd is None:
			sublime.error_message(
				"You MUST set an command in your LaTeXTools.sublime-settings " +
				"file before launching the script builder."
			)

		if isinstance(self.cmd, strbase):
			cmd = shlex.split(self.cmd)
		else:
			cmd = self.cmd

		cmd.append(self.tex_name)

		# pass the base name, without extension
		self.display("Invoking '{0}'... ".format(" ".join(cmd)))
		startupinfo = None

		if sublime.platform() == 'windows':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		env = copy(os.environ)
		if self.env is not None and isinstance(self.env, dict):
			env.update(self.env)

		p = Popen(
			cmd,
			stdout=PIPE,
			stderr=STDOUT,
			startupinfo=startupinfo,
			shell=True,
			env=env,
			cwd=self.tex_dir
		)

		stdout, _ = p.communicate()

		print(p.returncode)

		self.display("done.\n")

		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(stdout.decode('utf-8'))
			self.display("\n\n")

		yield("", "")

