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


# ## FOR TESTING: put PdfBuilder here

# #---------------------------------------------------------------
# # PdfBuilder class
# #
# # Build engines subclass PdfBuilder
# # NOTE: this will have to be moved eventually.
# #

# class PdfBuilder(object):
# 	"""Base class for build engines"""

# 	# Configure parameters here
# 	#
# 	# tex_root: the full path to the tex root file
# 	# output: object in main thread responsible for writing to the output panel
# 	# prefs : a dictionary with the appropriate prefs (from the settings file, or defaults)
# 	#
# 	# E.g.: self.path = prefs["path"]
# 	#
# 	# Your __init__ method *must* call this (via super) to ensure that
# 	# tex_root is properly split into the root tex file's directory,
# 	# its base name, and extension

# 	def __init__(self, tex_root, output, prefs):
# 		self.tex_root = tex_root
# 		self.tex_dir, self.tex_name = os.path.split(tex_root)
# 		self.base_name, self.tex_ext = os.path.splitext(self.tex_name)
# 		# output("\n\n")
# 		# output(tex_root + "\n")
# 		# output(self.tex_dir + "\n")
# 		# output(self.tex_name + "\n") 
# 		# output(self.base_name + "\n")
# 		# output(self.tex_ext + "\n")
# 		self.output_callable = output
# 		self.name = "Abstract Builder: does nothing!"
# 		self.out = ""

# 	# Send to callable object
# 	def display(self, data):
# 		self.output_callable(data)

# 	# Save command output
# 	def set_output(self, out):
# 		print("Setting out")
# 		print(out)
# 		self.out = out

# 	# This is where the real work is done. This generator must yield (cmd, msg) tuples,
# 	# as a function of the parameters and the output from previous commands (via send()).
# 	# "cmd" is the command to be run, as an array
# 	# "msg" is the message to be displayed (or None)
# 	# Remember that we are now in the root file's directory
# 	def commands(self):
# 		pass

# 	# Clean up after ourselves
# 	# Only the build system knows what to delete for sure, so give this option
# 	# Return True if we actually handle this, False if not
# 	#
# 	# NOTE: problem. Either we make the builder class persistent, or we have to
# 	# pass the tex root again. Need to think about this
# 	def cleantemps(self):
# 		return False





#----------------------------------------------------------------
# SimpleBuilder class
#
# Just call a bunch of commands in sequence
# Demonstrate basics
#

class SimpleBuilder(PdfBuilder):

	def __init__(self, tex_root, output, prefs):
		# Sets the file name parts, plus internal stuff
		super(SimpleBuilder, self).__init__(tex_root, output, prefs) 
		# Now do our own initialization: set our name, see if we want to display output
		self.name = "Simple Builder"
		self.display_log = prefs.get("display_log", False)

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
			







