from pdfBuilder import PdfBuilder
import sublime

import subprocess
from subprocess import Popen, PIPE, STDOUT

from copy import copy
import os
import re
import shlex
import sys

from string import Template

if sys.version_info < (3, 0):
	strbase = basestring
	from pipes import quote
else:
	strbase = str
	from shlex import quote


#----------------------------------------------------------------
# ScriptBuilder class
#
# Launch a user-specified script
#
class ScriptBuilder(PdfBuilder):

	CONTAINS_VARIABLE = re.compile(
		r'\$(?:File|FileDir|FileName|FileExt|BaseName)',
		re.IGNORECASE | re.UNICODE
	)

	def __init__(self, tex_root, output, builder_settings, platform_settings):
		# Sets the file name parts, plus internal stuff
		super(ScriptBuilder, self).__init__(tex_root, output, builder_settings, platform_settings) 
		# Now do our own initialization: set our name
		self.name = "Script Builder"
		# Display output?
		self.display_log = builder_settings.get("display_log", False)
		plat = sublime.platform()
		self.cmd = builder_settings.get(plat, {}).get("command", None)
		self.env = builder_settings.get(plat, {}).get("env", None)

	# Very simple here: we yield a single command
	# Also add environment variables
	def commands(self):
		# Print greeting
		self.display("\n\nScriptBuilder: ")

		# create an environment to be used for all subprocesses
		# adds any settings from the `env` dict to the current
		# environment
		env = copy(os.environ)
		if self.env is not None and isinstance(self.env, dict):
			env.update(self.env)

		if self.cmd is None:
			sublime.error_message(
				"You MUST set an command in your LaTeXTools.sublime-settings " +
				"file before launching the script builder."
			)

		if isinstance(self.cmd, strbase):
			self.cmd = [self.cmd]

		for c in self.cmd:
			if isinstance(c, list):
				cmd = " ".join([quote(s) for s in c])
			else:
				cmd = c

			if self.CONTAINS_VARIABLE.search(cmd):
				template = Template(cmd)
				cmd = template.safe_substitute(
					File=self.tex_root,
					file=self.tex_root,
					FileDir=self.tex_dir,
					filedir=self.tex_dir,
					FileName=self.tex_name,
					filename=self.tex_name,
					FileExt=self.tex_ext,
					fileext=self.tex_ext,
					BaseName=self.base_name,
					basename=self.base_name
				)

				cmd = shlex.split(cmd)
			else:
				cmd = shlex.split(cmd)
				cmd.append(self.base_name)

			self.display("Invoking '{0}'... ".format(
				" ".join([quote(s) for s in cmd]))
			)

			startupinfo = None

			if sublime.platform() == 'windows':
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

			p = Popen(
				cmd,
				stdout=PIPE,
				stderr=STDOUT,
				startupinfo=startupinfo,
				shell=True,
				env=env,
				cwd=self.tex_dir
			)

			yield (p, "")

			self.display("done.\n")

		# This is for debugging purposes 
		if self.display_log and p.stdout is not None:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")
