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
# SimpleBuilder class
#
# Just call a bunch of commands in sequence
# Demonstrate basics
#

class SimpleBuilder(PdfBuilder):

	def __init__(self, *args):
		# Sets the file name parts, plus internal stuff
		super(SimpleBuilder, self).__init__(*args)

		# Now do our own initialization: set our name, see if we want to display output
		self.name = "Simple Builder"
		self.display_log = self.builder_settings.get("display_log", False)

	def commands(self):
		# Print greeting
		self.display("\n\nSimpleBuilder: ")

		pdflatex = ["pdflatex", "-interaction=nonstopmode", "-synctex=1"]
		bibtex = ["bibtex"]

		# Regex to look for missing citations
		# This works for plain latex; apparently natbib requires special handling
		# TODO: does it work with biblatex?
		citations_rx = re.compile(r"Warning: Citation `.+' on page \d+ undefined")

		# We have commands in our PATH, and are in the same dir as the master file

		# This is for debugging purposes 
		def display_results(n):
			if self.display_log:
				self.display("Command results, run %d:\n" % (n,) )
				self.display(self.out)
				self.display("\n")	

		run = 1
		brun = 0
		yield (pdflatex + [self.base_name], "pdflatex run %d; " % (run, ))
		display_results(run)

		# Check for citations
		# Use search, not match: match looks at the beginning of the string
		# We need to run pdflatex twice after bibtex
		if citations_rx.search(self.out):
			brun = brun + 1
			yield (bibtex + [self.base_name], "bibtex run %d; " % (brun,))
			display_results(1)
			run = run + 1
			yield (pdflatex + [self.base_name], "pdflatex run %d; " % (run, ))
			display_results(run)
			run = run + 1
			yield (pdflatex + [self.base_name], "pdflatex run %d; " % (run, ))
			display_results(run)

		# Apparently natbib needs separate processing
		if "Package natbib Warning: There were undefined citations." in self.out:
			brun = brun + 1
			yield (bibtex + [self.base_name], "bibtex run %d; " % (brun,))
			display_results(2)
			run = run + 1
			yield (pdflatex + [self.base_name], "pdflatex run %d; " % (run, ))
			display_results(run)
			run = run + 1
			yield (pdflatex + [self.base_name], "pdflatex run %d; " % (run, ))
			display_results(run)

		# Check for changed labels
		# Do this at the end, so if there are also citations to resolve,
		# we may save one pdflatex run
		if "Rerun to get cross-references right." in self.out:
			run = run + 1
			yield (pdflatex + [self.base_name], "pdflatex run %d; " % (run, ))
			display_results(run)

		self.display("done.\n")
			







