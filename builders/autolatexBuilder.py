# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True

import os.path
import re
# This will work because makePDF.py puts the appropriate
# builders directory in sys.path
from pdfBuilder import PdfBuilder

DEBUG = False




#----------------------------------------------------------------
# AutoLaTeXBuilder class
#
# Call the autolatex building tool.
#

class AutolatexBuilder(PdfBuilder):

	def __init__(self, tex_root, output, builder_settings, platform_settings):
		# Sets the file name parts, plus internal stuff
		super(AutolatexBuilder, self).__init__(tex_root, output, builder_settings, platform_settings) 
		# Now do our own initialization: set our name, see if we want to display output
		self.name = "AutoLaTeX Builder"
		self.display_log = builder_settings.get("display_log", False)
		self.verbose_level = builder_settings.get("verbose_level", 2)

	def commands(self):
		# Print greeting
		self.display("\n\nAutolatexBuilder: ")

		autolatex = ["autolatex", "--stdout", "--noview", "--pdf", "--pdflatex", "--file="+self.tex_name, "--synctex"]
		for lvl in range(1, self.verbose_level):
			autolatex = autolatex + ["-v"]
		autolatex = autolatex + ["all"]
		
		# We have commands in our PATH, and are in the same dir as the master file

		# This is for debugging purposes 
		def display_results():
			if self.display_log:
				self.display("Command results:\n" )
				self.display(self.out)
				self.display("\n")	

		yield (autolatex, "autolatex run; ")
		display_results()

		self.display("done.\n")
			







