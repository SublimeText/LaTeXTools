# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True

import os.path

DEBUG = False


#---------------------------------------------------------------
# PdfBuilder class
#
# Build engines subclass PdfBuilder
# NOTE: this will have to be moved eventually.
#

class PdfBuilder(object):
	"""Base class for build engines"""

	# Configure parameters here
	#
	# tex_root: the full path to the tex root file
	# output: object in main thread responsible for writing to the output panel
	# builder_settings : a dictionary containing the "builder_settings" from LaTeXTools.sublime-settings
	# platform_settings : a dictionary containing the "platform_settings" from LaTeXTools.sublime-settings
	#
	# E.g.: self.path = prefs["path"]
	#
	# Your __init__ method *must* call this (via super) to ensure that
	# tex_root is properly split into the root tex file's directory,
	# its base name, and extension, etc.

	def __init__(self, tex_root, output, builder_settings, platform_settings):
		self.tex_root = tex_root
		self.tex_dir, self.tex_name = os.path.split(tex_root)
		self.base_name, self.tex_ext = os.path.splitext(self.tex_name)
		self.output_callable = output
		self.out = ""
		self.builder_settings = builder_settings
		self.platform_settings = platform_settings

	# Send to callable object
	# Usually no need to override
	def display(self, data):
		self.output_callable(data)

	# Save command output
	# Usually no need to override
	def set_output(self, out):
		if DEBUG:
			print("Setting out")
			print(out)
		self.out = out

	# This is where the real work is done. This generator must yield (cmd, msg) tuples,
	# as a function of the parameters and the output from previous commands (via send()).
	# "cmd" is the command to be run, as an array
	# "msg" is the message to be displayed (or None)
	# As of now, this function *must* yield at least *one* tuple.
	# If no command must be run, just yield ("","")
	# Remember that we are now in the root file's directory
	def commands(self):
		pass

	# Clean up after ourselves
	# Only the build system knows what to delete for sure, so give this option
	# Return True if we actually handle this, False if not
	#
	# NOTE: problem. Either we make the builder class persistent, or we have to
	# pass the tex root again. Need to think about this
	def cleantemps(self):
		return False

