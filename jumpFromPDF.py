import sublime, sublime_plugin, re, os
from jumpToPDF import jump_to_pdfCommand

# Addendum adding LilyPond-book support to the LaTeXTools package for Sublime Text 2 by msiniscalchi.
# Please report bugs related to this addendum to Yannis Rammos (yannis.rammos [at] me.com)
# or github.com/yrammos.
#
# The map_tex2lytex() command maps a .tex line number onto its corresponding .lytex file, if one exists.
# It subsequently opens the .tex, or the .lytex file if available, and moves the cursor to
# the appropriate line.
#
# The command adds support for synctex syncing from PDF viewer to Sublime Text 2 when .lytex
# (LaTeX + LilyPond) files are being edited and compiled.
#
# The sublsync script (available as part of this fork) is also required for setting up your PDF viewer.
# Please see instructions on github.
#
# As a final note, the .lytex and .tex extensions are case-sensitive.

class jump_from_pdfCommand(sublime_plugin.WindowCommand):
	# The following delimiters (and one regex) are hard-coded as they cover all cases 
	# I've encountered so far. If more cases crop up, they may warrant a user setting
	# via some preference file.
	re_lytex_opening = re.compile(r"\\begin(\[[A-Za-z0-9=., ]*\])?{lilypond}", re.IGNORECASE)
	lytex_opening_markers = ["\\begin{lilypond}"]
	lytex_closing_markers = ["\\end{lilypond}" + '\n']
	tex_opening_markers = ["{%" + '\n', "\\begin{quote}" + '\n']
	tex_closing_markers = ["}" + '\n', "\\end{quote}" + '\n']
	lily_packages = ["\\usepackage{graphics}" + '\n']

	# Remove whitespace characters, but not newlines, from string s. Convert s to lowercase.
	# Used to used to normalize .lytex and .tex files prior to scanning for Lilypond scopes.
	def filter_line(self, s):
		s = s.replace(' ', '')
		s = s.replace('\t', '')
		s = s.replace('\r', '').lower()
		return s

	# Look for the next occurence of at least one among "strings" in file "target" and 
	# assume that the current index of the file is at line "startpos".
	# Return the line number of that next occurence and the index of the matched delimiter (if applicable).
	def line_of_next_occurrence(self, target, startpos, strings):
		r = target.readline()
		r = self.filter_line(r)
		counter = startpos + 1 			# print "			scanning line: ", counter, ":  ", repr(r)
		while r:
			if r in strings:
				return counter, strings.index(r)
			if (self.re_lytex_opening.match(r)):
				return counter, 0
			r = target.readline()
			r = self.filter_line(r)
			counter = counter + 1 		# print "			scanning line: ", counter, ":  ", repr(r)
		return counter, 0

	def map_tex2lytex(self, old_line, fileName):
		# Ensure that both files (.tex and .lytex) are open. 
		tex = open(fileName + '.tex')
		lytex = open(fileName + '.lytex')

		# Initialize the line number offset (iteratively computed as "cur_sigma").
		cur_sigma = 0

		# Initialize line number registers: 
		# i, ii hold the line numbers opening and closing, respectively, the most recently scanned  "lilypond" environment in the .lytex file.
		# j, jj hold the line numbers opening and closing, respectively, the corresponding code block generated by lilypond-book in the .tex file.
		i = ii = j = jj = g = -1

		# Find the opening and closing line numbers of the next LilyPond hunk in the .tex and .lytex files. 
		while i < old_line:
			i, r = self.line_of_next_occurrence(tex, ii, self.tex_opening_markers)
			print "i = ", i, 'r = ', r, 'closing marker = ', self.tex_closing_markers[r].split(' ')
			ii, r = self.line_of_next_occurrence(tex, i, self.tex_closing_markers[r].split(' '))
			print "ii = ", ii
			j, r = self.line_of_next_occurrence(lytex, jj, self.lytex_opening_markers)
			print "j = ", j
			jj, r = self.line_of_next_occurrence(lytex, j, self.lytex_closing_markers[r].split(' '))
			print "jj = ", jj
			cur_sigma = cur_sigma + (ii - i - (jj - j))
			print "cur_sigma = ", cur_sigma

		# The previous loop has stopped at the Lilypond hunk immediately following the cursor. Revoke the last iteration to account only for hunks before the cursor.
		cur_sigma = cur_sigma - (ii - i - (jj - j))
		print "cur_sigma (adjusted) = ", cur_sigma

		# Preliminarily calculate at which line the old_line of the .texly maps into the .tex.
		mapping = old_line - cur_sigma
		print "Old line:", old_line, "New line:", mapping

		# Find line where Lilypond has injected \usepackage{graphics} into the .tex file.
		tex.seek(0)
		g = self.line_of_next_occurrence(tex, g, self.lily_packages)

		# Inefficient but readable way to obtain the line count of the .tex file.
		tex.seek(0)
		l = len(tex.readlines())

		# Add -1 to the preliminary mapping if the \usepackage{graphics} line of the .tex file is located before the mapping.
		# This last calculation finally yields the exact mapping.
		if (g[0] < l and old_line > g[0]):
			return mapping-1
		else:
			return mapping

	def run(self):
		# Try to open the file where the synctex-enabled PDF viewer has been instructed by the user to store the filename and coordinates of the corresponding .tex file. This is assumed to be ~/.sublatex.txt but may be overridden via a "synctex_output" parameter in a LaTeXTools.sublime-settings preference file.
		settings = sublime.load_settings("LyTeXTools.sublime-settings")
		self.pdf_loc_filename = os.path.abspath(settings.get("synctex_output", os.path.join(os.path.expanduser("~"), ".sublatex.txt")))
		try:
			self.pdf_loc_file = open(os.path.abspath(self.pdf_loc_filename), "r", 0)
		# In case that file does not exist or cannot be open, produce an error message and exit.
		except:
			sublime.error_message("LyTeXTools/SyncTeX: Error interfacing with the PDF viewer (" + str(self.pdf_loc_file) + ").")
			return

		# Attempt to obtain the name and location of the appropriate .tex file.
		# First, read the first two lines of the file, which should contain the .tex filename and line number respectively.
		self.tex_filename, self.tex_line = self.pdf_loc_file.readline().strip('\n'), self.pdf_loc_file.readline().strip('\n')
		# Then check that neither line is empty. If the test fails, exit.
		if (not self.tex_filename or not self.tex_line):
			sublime.error_message("LyTeXTools/SyncTeX: Requested source file location is incomplete (less than two lines of data). Please check your PDF viewer settings.")
			return

		# Finally, check that the first line contains a syntactically valid file path and the second line a syntactically valid line number (i.e. a natural number not starting with zero), otherwise exit.
		re_filepath = re.compile(r"^(.*/)?(?:$|(.+?)(?:(\\.[^.]*$)|$))")
		re_linenumber = re.compile("^[1-9][0-9]*$")
		if (not re_filepath.match(self.tex_filename) or not re_linenumber.match(self.tex_line)):
			sublime.error_message("LyTeXTools/SyncTeX: Requested source file location contains incorrect data types. Please check your PDF viewer settings.")
			return
		self.tex_line = int(self.tex_line)
		print "SyncTeX is pointing at .tex file ", self.tex_filename, "line", self.tex_line

		# Attempt to open the eponymous .lytex file. If it is unavailable, simply open the .tex file itself.
		self.tex_filename, self.tex_extension = os.path.splitext(self.tex_filename)
		if os.path.isfile(self.tex_filename + '.lytex'):
			print self.tex_filename + '.lytex', "found. Opening right now."
			# Map the .tex line number onto the .lytex file.
			self.tex_line = self.map_tex2lytex(self.tex_line, self.tex_filename)
			self.window.open_file(self.tex_filename + '.lytex:' + str(self.tex_line + 1), sublime.ENCODED_POSITION)
		else:
			print "There is no", self.tex_filename + '.lytex file.\n', 'Opening line', str(self.tex_line), 'of .tex file instead.'
			self.window.open_file(self.tex_filename + '.tex:' + str(self.tex_line + 1), sublime.ENCODED_POSITION)