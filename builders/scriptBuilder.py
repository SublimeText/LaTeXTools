# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True

from pdfBuilder import PdfBuilder
import re
import os, os.path
import codecs

DEBUG = False


#----------------------------------------------------------------
# ScriptBuilder class
#
# Launch a user-specified script
# STILL NOT FUNCTIONAL!!!
#
class ScriptBuilder(PdfBuilder):

	def __init__(self, tex_root, output, builder_settings, platform_settings):
		# Sets the file name parts, plus internal stuff
		super(TraditionalBuilder, self).__init__(tex_root, output, builder_settings, platform_settings) 
		# Now do our own initialization: set our name
		self.name = "Script Builder"
		# Display output?
		self.display_log = builder_settings.get("display_log", False)
		plat = sublime.platform()
		self.cmd = builder_settings[plat]["command"]
		self.env = builder_settings[plat]["env"]


	#
	# Very simple here: we yield a single command
	# Also add environment variables
	#
	def commands(self):
		# Print greeting
		self.display("\n\nScriptBuilder: ")

		# figure out safe way to pass self.env back
		# OK, probably need to modify yield call throughout
		# and pass via Popen. Wait for now

		# pass the base name, without extension
		yield (cmd + [self.base_name], " ".join(cmd) + "... ")

		self.display("done.\n")
		
		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")	
