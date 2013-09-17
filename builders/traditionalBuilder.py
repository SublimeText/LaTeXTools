# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	import builders.pdfBuilder
else:
	_ST3 = True
	from . import pdfBuilder

import sublime_plugin
import sys, os, os.path

DEBUG = False


#----------------------------------------------------------------
# TraditionalBuilder class
#
# Implement existing functionality, more or less
# NOTE: move this to a different file, too
#
class TraditionalBuilder(PdfBuilder):

	def __init__(self, params):
		pass
#### TO BE CONTINUED		

		###
		# THIS WILL BE IN THE TRADITIONAL BUILDER
		###

		# # I actually think self.file_name is it already
		# self.engine = 'pdflatex' # Standard pdflatex
		# for line in codecs.open(self.file_name, "r", "UTF-8", "ignore").readlines():
		# 	if not line.startswith('%'):
		# 		break
		# 	else:
		# 		# We have a comment match; check for a TS-program match
		# 		mroot = re.match(r"%\s*!TEX\s+(?:TS-)?program *= *(xelatex|lualatex|pdflatex)\s*$",line)
		# 		if mroot:
		# 			# Sanity checks
		# 			if "texify" == self.make_cmd[0]:
		# 				sublime.error_message("Sorry, cannot select engine using a %!TEX program directive on MikTeX.")
		# 				return 
		# 			if not ("$pdflatex = '%E" in self.make_cmd[3]):
		# 				sublime.error_message("You are using a custom LaTeX.sublime-build file (in User maybe?). Cannot select engine using a %!TEX program directive.")
		# 				return
		# 			self.engine = mroot.group(1)
		# 			break
		# if self.engine != 'pdflatex': # Since pdflatex is standard, we do not output a msg. for it.
		# 	self.output("Using engine " + self.engine + "\n")
		# self.make_cmd[3] = self.make_cmd[3].replace("%E", self.engine)
