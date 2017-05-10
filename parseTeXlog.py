# ST2/ST3 compat
from __future__ import print_function 

import re
import sys
import os.path


# To accommodate both Python 2 and 3
if sys.version_info >= (3,):
	advance_iterator = next
else:
	def _advance_iterator(it):
		return it.next()
	advance_iterator = _advance_iterator

print_debug = False
interactive = False
extra_file_ext = []

def debug(s):
	if print_debug:
		print(u"parseTeXlog: {0}".format(s))

# The following function is only used when debugging interactively.
#
# If file is not found, ask me if we are debugging
# Rationale: if we are debugging from the command line, perhaps we are parsing
# a log file from a user, so apply heuristics and / or ask if the file not
# found is actually legit
#
# Return value: the question is, "Should I skip this file?" Hence:
# 	True means YES, DO SKIP IT, IT IS NOT A FILE
#	False means NO, DO NOT SKIP IT, IT IS A FILE
def debug_skip_file(f, root_dir):
	# If we are not debugging, then it's not a file for sure, so skip it
	# if not (print_debug or interactive):
	if not (interactive or print_debug):
		return True
	debug("debug_skip_file: " + f)
	f_ext = os.path.splitext(f)[1].lower()[1:]
	# Heuristic: TeXlive on Mac or Linux (well, Ubuntu at least) or Windows / MiKTeX
	# Known file extensions:
	known_file_exts = ['tex','sty','cls','cfg','def','mkii','fd','map','clo', 'dfu',
						'ldf', 'bdf', 'bbx','cbx','lbx','dict']
	if (f_ext in known_file_exts) and \
	   (("/usr/local/texlive/" in f) or ("/usr/share/texlive/" in f) or ("Program Files\\MiKTeX" in f) \
	   	or re.search(r"\\MiKTeX(?:\\| )\d\.\d+\\tex",f)) or ("\\MiKTeX\\tex\\" in f):
		print ("TeXlive / MiKTeX FILE! Don't skip it!")
		return False
	if (f_ext in known_file_exts and re.search(r'(\\|/)texmf\1', f, re.I)):
		print ("File in TEXMF tree! Don't skip it!")
		return False
	# Heuristic: "version 2010.12.02"
	if re.match(r"version \d\d\d\d\.\d\d\.\d\d", f):
		print ("Skip it!")
		return True
	# Heuristic: TeX Live line
	if re.match(r"TeX Live 20\d\d(/Debian)?\) \(format", f):
		print ("Skip it!")
		return True
	# Heuristic: MiKTeX line
	if re.match("MiKTeX \d\.\d\d?",f):
		print ("Skip it!")
		return True
	# Heuristic: no two consecutive spaces in file name
	if "  " in f:
		print ("Skip it!")
		return True
	# Heuristic: various diagnostic messages
	if f=='e.g.,' or "ext4): destination with the same identifier" in f or "Kristoffer H. Rose" in f:
		print ("Skip it!")
		return True
	# Heuristic: file in local directory with .tex ending
	file_exts = extra_file_ext + ['tex', 'aux', 'bbl', 'cls', 'sty', 'out', 'toc', 'dbx']
	if (f.startswith(root_dir) or f[0:2] in ['./', '.\\', '..']) and f_ext in file_exts:
		print ("File! Don't skip it")
		return False

	# Heuristic: absolute path that looks like home directory
	if f[0] == '/':
		if f.split('/')[1] in ['home', 'Users']:
			print("Assuming home directory file. Don't skip!")
			return False
	# N.B. this is not a good technique for detecting the user folder
	# on Windows, but is hopefully "good enough" for the common configuration
	# (given that this will not usually be run on the computer that generated
	# the log)
	elif re.match(r'^[A-Z]:\\(?:Documents and Settings|Users)\\', f):
		print("Assuming home directory file. Don't skip!")
		return False

	if not interactive:
		print("Automatically skipping")
		return True

	if sys.version_info < (3,):
		choice = raw_input()
	else:
		choice = input()

	if choice == "":
		print ("Skip it")
		return True
	else:
		print ("FILE! Don't skip it")
		return False


# More robust parsing code: October / November 2012
# Input: tex log file, read in **binary** form, unprocessed
# Output: content to be displayed in output panel, split into lines

def parse_tex_log(data, root_dir):
	debug("Parsing log file")
	errors = []
	warnings = []
	badboxes = []
	parsing = []

	guessed_encoding = 'UTF-8' # for now

	# Split data into lines while in binary form
	# Then decode using guessed encoding
	# We need the # of bytes per line, not the # of chars (codepoints), to undo TeX's line breaking
	# so we construct an array of tuples:
	#   (decoded line, length of original byte array)

	try:
		log = [(l.decode(guessed_encoding, 'ignore'), len(l))  for l in data.splitlines()]
	except UnicodeError:
		debug("log file not in UTF-8 encoding!")
		errors.append("ERROR: your log file is not in UTF-8 encoding.")
		errors.append("Sorry, I can't process this file")
		return (errors, warnings, badboxes)

	# loop over all log lines; construct error message as needed
	# This will be useful for multi-file documents

	# some regexes
	# file_rx = re.compile(r"\(([^)]+)$") # OLD
	# Structure (+ means captured, - means not captured)
	# + maybe " (for Windows)
	# + maybe a drive letter and : (for Windows)
	# + maybe . NEW: or ../ or ..\, with repetitions
	# + then any char, matched NON-GREEDILY (avoids issues with multiple files on one line?)
	# + then .
	# + then any char except for whitespace or " or ); at least ONE such char
	# + then maybe " (on Windows/MikTeX)
 	# - then whitespace or ), or end of line
 	# + then anything else, captured for recycling
	# This should take care of e.g. "(./test.tex [12" or "(./test.tex (other.tex"
	# NOTES:
	# 1. we capture the initial and ending " if there is one; we'll need to remove it later
	# 2. we define the basic filename parsing regex so we can recycle it
	# 3. we allow for any character besides "(" before a file name starts. This gives a lot of 
	#	 false positives but we kill them with os.path.isfile
	file_basic = r"\"?(?:[a-zA-Z]\:)?(?:\.|(?:\.\./)|(?:\.\.\\))*.+?\.[^\s\"\)\.]+\"?"
	file_rx = re.compile(r"[^\(]*?\((" + file_basic + r")(\s|\"|\)|$)(.*)")
	# Useless file #1: {filename.ext}; capture subsequent text
	# Will avoid nested {'s as these can't really appear, except if file names have braces
	# which is REALLY bad!!!
	file_useless1_rx = re.compile(r"\{\"?(?:\.|\.\./)*[^\.]+\.[^\{\}]*\"?\}(.*)")
	# Useless file #2: <filename.ext>; capture subsequent text
	file_useless2_rx = re.compile(r"<\"?(?:\.|\.\./)*[^\.]+\.[^>]*\"?>(.*)")
	# attempt to filter out log messages like this:
	#  (package)          continued warning...
	# from being considered files
	file_badmatch_rx = re.compile(r"^\s*\([a-zA-Z]+\)\s{4,}.+")
	pagenum_begin_rx = re.compile(r"\s*\[\d*(.*)")
	line_rx = re.compile(r"^l\.(\d+)\s(.*)")  # l.nn <text>

	warning_rx = re.compile(r"^(.*?) Warning: (.+)") # Warnings, first line
	line_rx_latex_warn = re.compile(r"input line (\d+)\..*") # Warnings, line number
	
	badbox_rx = re.compile(r"^(.*?)Overfull (.*)")  # Bad box warning
	line_rx_latex_badbox = re.compile(r"lines (\d+)--(.*?)")   # Bad box lines
	matched_parens_rx = re.compile(r"\([^()]*\)") # matched parentheses, to be deleted (note: not if nested)
	assignment_rx = re.compile(r"\\[^=]*=")	# assignment, heuristics for line merging
	# Special case: the xy package, which reports end of processing with "loaded)" or "not reloaded)"
	xypic_begin_rx = re.compile(r"[^()]*?(?:not re)?loaded\)(.*)")
	xypic_rx = re.compile(r".*?(?:not re)?loaded\)(.*)")
	# Special case: the comment package, which prints ")" after some text
	comment_rx = re.compile(r"Excluding comment '.*?'(.*)")

	files = []
	xypic_flag = False # If we have seen xypic, report a warning, not an error for incorrect parsing

	# Support function to handle warnings
	def handle_warning(l):
		if files==[]:
			location = "[no file]"
			parsing.append("PERR [handle_warning no files] " + l)
			debug("PERR [handle_warning no files] (%d)" % (line_num,))
		else:
			location = files[-1]		

		warn_match_line = line_rx_latex_warn.search(l)

		if warn_match_line:
			warn_line = warn_match_line.group(1)
			warnings.append(location + ":" + warn_line + ": " + l)
		else:
			warnings.append(location + ": " + l)

	# Support function to handle bad boxes
	def handle_badbox(l):
		if files==[]:
			location = "[no file]"
			parsing.append("PERR [handle_badbox no files] " + l)
			debug("PERR [handle_badbox no files] (%d)" % (line_num,))
		else:
			location = files[-1]		

		badbox_match_line = line_rx_latex_badbox.search(l)

		if badbox_match_line:
			badbox_line = badbox_match_line.group(1)
			badboxes.append(location + ":" + badbox_line + ": " + l)
		else:
			badboxes.append(location + ": " + l)
	
	# State definitions
	STATE_NORMAL = 0
	STATE_SKIP = 1
	STATE_REPORT_ERROR = 2
	STATE_REPORT_WARNING = 3
	
	state = STATE_NORMAL

	# Use our own iterator instead of for loop
	log_iterator = log.__iter__()
	line_num = 0
	line = ""
	linelen = 0

	recycle_extra = False		# Should we add extra to newly read line?
	reprocess_extra = False		# Should we reprocess extra, without reading a new line?
	emergency_stop = False		# If TeX stopped processing, we can't pop all files
	incomplete_if = False  		# Ditto if some \if... statement is not complete	

	while True:
		# first of all, see if we have a line to recycle (see heuristic for "l.<nn>" lines)
		if recycle_extra:
			line, linelen = extra, extralen
			recycle_extra = False
			line_num += 1
		elif reprocess_extra:
			line = extra # NOTE: we must remember that we are reprocessing. See long-line heuristics
		else: # we read a new line
			# save previous line for "! File ended while scanning use of..." message
			prev_line = line
			try:
				line, linelen = advance_iterator(log_iterator) # will fail when no more lines
				line_num += 1
			except StopIteration:
				break
		# Now we deal with TeX's decision to truncate all log lines at 79 characters
		# If we find a line of exactly 79 characters, we add the subsequent line to it, and continue
		# until we find a line of less than 79 characters
		# The problem is that there may be a line of EXACTLY 79 chars. We keep our fingers crossed but also
		# use some heuristics to avoid disastrous consequences
		# We are inspired by latexmk (which has no heuristics, though)

		# HEURISTIC: the first line is always long, and we don't care about it
		# also, the **<file name> line may be long, but we skip it, too (to avoid edge cases)
		# We make sure we are NOT reprocessing a line!!!
		# Also, we make sure we do not have a filename match, or it would be clobbered by exending!
		if (not reprocess_extra) and line_num > 1 and linelen >= 79 and line[0:2] != "**": 
			debug ("Line %d is %d characters long; last char is %s" % (line_num, len(line), line[-1]))
			# HEURISTICS HERE
			extend_line = True
			recycle_extra = False
			# HEURISTIC: check first if we just have a long "(.../file.tex" (or similar) line
			# A bit inefficient as we duplicate some of the code below for filename matching
			file_match = file_rx.match(line)
			if file_match:
				if line.startswith('runsystem') or file_badmatch_rx.match(line):
					debug("Ignoring possible file: " + line)
					file_match = False

			if file_match:
				debug("MATCHED (long line)")
				file_name = file_match.group(1)
				file_name = os.path.normpath(file_name.strip('"'))

				if not os.path.isabs(file_name):
					file_name = os.path.normpath(os.path.join(root_dir, file_name))

				file_extra = file_match.group(2) + file_match.group(3) # don't call it "extra"
				# remove quotes if necessary, but first save the count for a later check
				quotecount = file_name.count("\"")
				file_name = file_name.replace("\"", "")
				# NOTE: on TL201X pdftex sometimes writes "pdfTeX warning" right after file name
				# This may or may not be a stand-alone long line, but in any case if we
				# extend, the file regex will fire regularly
				if file_name[-6:] == "pdfTeX" and file_extra[:8] == " warning":
					debug("pdfTeX appended to file name, extending")
				# Else, if the extra stuff is NOT ")" or "", we have more than a single
				# file name, so again the regular regex will fire
				elif file_extra not in [")", ""]:
					debug("additional text after file name, extending")
				# If we have exactly ONE quote, we are on Windows but we are missing the final quote
				# in which case we extend, because we may be missing parentheses otherwise
				elif quotecount==1:
					debug("only one quote, extending")
				# Now we have a long line consisting of a potential file name alone
				# Check if it really is a file name
				elif (not os.path.isfile(file_name)) and debug_skip_file(file_name, root_dir):
					debug("Not a file name")
				else:
					debug("IT'S A (LONG) FILE NAME WITH NO EXTRA TEXT")
					extend_line = False # so we exit right away and continue with parsing

			while extend_line:
				debug("extending: " + line)
				try:
					# different handling for Python 2 and 3
					extra, extralen = advance_iterator(log_iterator)
					debug("extension? " + extra)
					line_num += 1 # for debugging purposes
					# HEURISTIC: if extra line begins with "Package:" "File:" "Document Class:",
					# or other "well-known markers",
					# we just had a long file name, so do not add
					if extralen > 0 and (
						extra[0:5] == "File:" or
						extra[0:8] == "Package:" or
						extra[0:11] == "Dictionary:" or
						extra[0:15] == "Document Class:"
					) or (
						extra[0:9] == "LaTeX2e <" or
						assignment_rx.match(extra)
					):
						extend_line = False
						# no need to recycle extra, as it's nothing we are interested in
					# HEURISTIC: when TeX reports an error, it prints some surrounding text
					# and may use the whole line. Then it prints "...", and "l.<nn> <text>" on a new line
					# pdftex warnings also use "..." at the end of a line.
					# If so, do not extend
					elif line[-3:]=="...": # and line_rx.match(extra): # a bit inefficient as we match twice
						debug("Found [...]")
						extend_line = False
						recycle_extra = True # make sure we process the "l.<nn>" line!
					# unsure about this...
					# if the "extra" (next line) starts with a ( and we already have a
					# valid file, this likely starts something else we need to
					# process as a file, so add a space...
					elif extralen > 0 and extra[0] == '(' and (
						os.path.isfile(file_name) or not debug_skip_file(file_name, root_dir)
					):
						line += " " + extra
						debug("Extended: " + line)
						linelen += extralen + 1
						if extralen < 79:
							extend_line = False
					else:
						line += extra
						debug("Extended: " + line)
						linelen += extralen
						if extralen < 79:
							extend_line = False
				except StopIteration:
					extend_line = False # end of file, so we must be done. This shouldn't happen, btw

		# NOW WE GOT OUR EXTENDED LINE, SO START PROCESSING

		# We may skip the above "if" because we are reprocessing a line, so reset flag:
		reprocess_extra = False
		# Check various states
		if state==STATE_SKIP:
			state = STATE_NORMAL
			continue
		if state==STATE_REPORT_ERROR:
			# skip everything except "l.<nn> <text>"
			debug("Reporting error in line: " + line)
			# We check for emergency stops here, too, because it may occur before the l.nn text
			if "! Emergency stop." in line:
				emergency_stop = True
				debug("Emergency stop found")
				continue
			err_match = line_rx.match(line)
			if not err_match:
				continue
			# now we match!
			# state = STATE_NORMAL
			# TeX splits the error line in two, so we skip the
			# second part. In the future we may want to capture that, too
			# and figure out the column, perhaps.
			state = STATE_SKIP 
			err_line = err_match.group(1)
			err_text = err_match.group(2)
			# err_msg is set from last time
			if files==[]:
				location = "[no file]"
				parsing.append("PERR [STATE_REPORT_ERROR no files] " + line)
				debug("PERR [STATE_REPORT_ERROR no files] (%d)" % (line_num,))
			else:
				location = files[-1]
			debug("Found error: " + err_msg)		
			errors.append(location + ":" + err_line + ": " + err_msg + " [" + err_text + "]")
			continue
		if state == STATE_REPORT_WARNING:
			# add current line and check if we are done or not
			current_warning += line
			if len(line) == 0 or line[-1] == '.':
				handle_warning(current_warning)
				current_warning = None
				state = STATE_NORMAL # otherwise the state stays at REPORT_WARNING
			continue
		if line=="":
			continue

		# Sometimes an \if... is not completed; in this case some files may remain on the stack
		# I think the same format may apply to different \ifXXX commands, so make it flexible
		if len(line)>0 and line.strip()[:23]=="(\\end occurred when \\if" and \
						   line.strip()[-15:]=="was incomplete)":
			incomplete_if = True
			debug(line)

		# Skip things that are clearly not file names, though they may trigger false positives
		if len(line) > 0 and (
			line[0:5] == "File:" or
			line[0:8] == "Package:" or
			line[0:11] == "Dictionary:" or
			line[0:15 ] == "Document Class:"
		) or (
			line[0:9] == "LaTeX2e <" or assignment_rx.match(line)
		):
			continue

		# Are we done? Get rid of extra spaces, just in case (we may have extended a line, etc.)
		if line.strip() == "Here is how much of TeX's memory you used:":
			if len(files)>0:
				if emergency_stop or incomplete_if:
					debug("Done processing, files on stack due to known conditions (all is fine!)")
				elif xypic_flag:
					parsing.append("PERR [files on stack (xypic)] " + ";".join(files))
				else:
					parsing.append("PERR [files on stack] " + ";".join(files))
				files=[]			
			# break
			# We cannot stop here because pdftex may yet have errors to report.

		# Special error reporting for e.g. \footnote{text NO MATCHING PARENS & co
		if "! File ended while scanning use of" in line:
			scanned_command = line[35:-2] # skip space and period at end
			# we may be unable to report a file by popping it, so HACK HACK HACK
			file_name, linelen = advance_iterator(log_iterator) # <inserted text>
			file_name, linelen = advance_iterator(log_iterator) #      \par
			file_name, linelen = advance_iterator(log_iterator)
			file_name = file_name[3:] # here is the file name with <*> in front
			errors.append("TeX STOPPED: " + line[2:-2]+prev_line[:-5])
			errors.append("TeX reports the error was in file:" + file_name)
			continue

		# Here, make sure there was no uncaught error, in which case we do more special processing
		# This will match both tex and pdftex Fatal Error messages
		if "==> Fatal error occurred," in line:
			debug("Fatal error detected")
			if errors == []:
				errors.append("TeX STOPPED: fatal errors occurred. Check the TeX log file for details")
			continue

		# If tex just stops processing, we will be left with files on stack, so we keep track of it
		if "! Emergency stop." in line:
			state = STATE_SKIP
			emergency_stop = True
			debug("Emergency stop found")
			continue

		# TOo many errors: will also have files on stack. For some reason
		# we have to do differently from above (need to double-check: why not stop processing if
		# emergency stop, too?)
		if "(That makes 100 errors; please try again.)" in line:
			errors.append("Too many errors. TeX stopped.")
			debug("100 errors, stopping")
			break

		# catch over/underfull
		# skip everything for now
		# Over/underfull messages end with [] so look for that
		if line[0:8] == "Overfull" or line[0:9] == "Underfull":

			current_badbox = line;
			if line[-2:]=="[]": # one-line over/underfull message
				handle_badbox(current_badbox)
				continue

			ou_processing = True
			while ou_processing:
				try:
					line, linelen = advance_iterator(log_iterator) # will fail when no more lines
				except StopIteration:
					debug("Over/underfull: StopIteration (%d)" % line_num)
					break
				line_num += 1
				debug("Over/underfull: skip " + line + " (%d) " % line_num)
				# Sometimes it's " []" and sometimes it's "[]"...
#				if len(line)>0 and line[:3] == " []" or line[:2] == "[]":
				# NO, it really should be just " []"
				if len(line)>0 and line == " []":
					ou_processing = False
				else:
					current_badbox += line

			if ou_processing:
				warnings.append("Malformed LOG file: over/underfull")
				warnings.append("Please let me know via GitHub")
				break
			else:
				handle_badbox(current_badbox)
				continue

		# Special case: the bibgerm package, which has comments starting and ending with
		# **, and then finishes with "**)"
		if len(line)>0 and line[:2] == "**" and line[-3:] == "**)" \
						and files and "bibgerm" in files[-1]:
			debug("special case: bibgerm")
			debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
			f = files.pop()
			debug(u"Popped file: {0} ({1})".format(f, line_num))
			continue

		# Special case: the relsize package, which puts ")" at the end of a
		# line beginning with "Examine \". Ah well!
		if len(line)>0 and line[:9] == "Examine \\" and line[-3:] == ". )" \
						and files and  "relsize" in files[-1]:
			debug("special case: relsize")
			debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
			f = files.pop()
			debug(u"Popped file: {0} ({1})".format(f, line_num))
			continue
		
		# Special case: the comment package, which puts ")" at the end of a 
		# line beginning with "Excluding comment 'something'"
		# Since I'm not sure, we match "Excluding comment 'something'" and recycle the rest
		comment_match = comment_rx.match(line)
		if comment_match and files and "comment" in files[-1]:
			debug("special case: comment")
			extra = comment_match.group(1)
			debug("Reprocessing " + extra)
			reprocess_extra = True
			continue

		# Special case: the numprint package, which prints a line saying
		# "No configuration file... found.)"
		# if there is no config file (duh!), and that (!!!) signals the end of processing :-(

		if len(line)>0 and line.strip() == "No configuration file `numprint.cfg' found.)" \
						and files and "numprint" in files[-1]:
			debug("special case: numprint")
			debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
			f = files.pop()
			debug(u"Popped file: {0} ({1})".format(f, line_num))
			continue	

		# Special case: xypic's "loaded)" at the BEGINNING of a line. Will check later
		# for matches AFTER other text.
		xypic_match = xypic_begin_rx.match(line)
		if xypic_match:
			debug("xypic match before: " + line)
			# Do an extra check to make sure we are not too eager: is the topmost file
			# likely to be an xypic file? Look for xypic in the file name
			if files and "xypic" in files[-1]:
				debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
				f = files.pop()
				debug(u"Popped file: {0} ({1})".format(f, line_num))
				extra = xypic_match.group(1)
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue
			else:
				debug("Found loaded) but top file name doesn't have xy")

		# mostly these are caused by hyperref and re-using internal identifiers
		if "pdfTeX warning (ext4): destination with the same identifier" in line:
			# add warning
			handle_warning(line[line.find("destination with the same identifier"):])
			continue

		line = line.strip() # get rid of initial spaces
		# note: in the next line, and also when we check for "!", we use the fact that "and" short-circuits
		# denotes end of processing of current file: pop it from stack
		if len(line) > 0 and line[0] == ')':
			if files:
				debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
				f = files.pop()
				debug(u"Popped file: {0} ({1})".format(f, line_num))
				extra = line[1:]
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue
			else:
				parsing.append("PERR [')' no files]")
				debug("PERR [')' no files] (%d)" % (line_num,))
				break

		# Opening page indicators: skip and reprocess
		# Note: here we look for matches at the BEGINNING of a line. We check again below
		# for matches elsewhere, but AFTER matching for file names.
		pagenum_begin_match = pagenum_begin_rx.match(line)
		if pagenum_begin_match:
			extra = pagenum_begin_match.group(1)
			debug("Reprocessing " + extra)
			reprocess_extra = True
			continue

		# Closing page indicators: skip and reprocess
		# Also, sometimes we have a useless file <file.tex, then a warning happens and the
		# last > appears later. Pick up such stray >'s as well.
		if len(line)>0 and line[0] in [']', '>']:
			extra = line[1:]
			debug("Reprocessing " + extra)
			reprocess_extra = True
			continue

		# Useless file matches: {filename.ext} or <filename.ext>. We just throw it out
		file_useless_match = file_useless1_rx.match(line) or file_useless2_rx.match(line)
		if file_useless_match: 
			extra = file_useless_match.group(1)
			debug("Useless file: " + line)
			debug("Reprocessing " + extra)
			reprocess_extra = True
			continue


		# this seems to happen often: no need to push / pop it
		if line[:12]=="(pdftex.def)":
			continue

		# Now we should have a candidate file. We still have an issue with lines that
		# look like file names, e.g. "(Font)     blah blah data 2012.10.3" but those will
		# get killed by the isfile call. Not very efficient, but OK in practice
		debug("FILE? Line:" + line)
		file_match = file_rx.match(line)
		if file_match:
			if line.startswith('runsystem') or file_badmatch_rx.match(line):
				debug("Ignoring possible file: " + line)
				file_match = False

		if file_match:
			debug("MATCHED")
			file_name = file_match.group(1)
			file_name = os.path.normpath(file_name.strip('"'))

			if not os.path.isabs(file_name):
				file_name = os.path.normpath(os.path.join(root_dir, file_name))

			extra = file_match.group(2) + file_match.group(3)
			# remove quotes if necessary
			file_name = file_name.replace("\"", "")
			# on TL2011 pdftex sometimes writes "pdfTeX warning" right after file name
			# so fix it
			# TODO: report pdftex warning
			if file_name[-6:]=="pdfTeX" and extra[:8]==" warning":
				debug("pdfTeX appended to file name; removed")
				file_name = file_name[:-6]
				extra = "pdfTeX" + extra
			# This kills off stupid matches
			if (not os.path.isfile(file_name)) and debug_skip_file(file_name, root_dir):
				#continue
				# NOTE BIG CHANGE HERE: CONTINUE PROCESSING IF NO MATCH
				pass
			else:
				debug("IT'S A FILE!")
				files.append(file_name)
				debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
				# Check if it's a xypic file
				if (not xypic_flag) and "xypic" in file_name:
					xypic_flag = True
					debug("xypic detected, demoting parsing error to warnings")
				# now we recycle the remainder of this line
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue

		# Special case: match xypic's " loaded)" markers
		# You may think we already checked for this. But, NO! We must check both BEFORE and
		# AFTER looking for file matches. The problem is that we
		# may have the " loaded)" marker either after non-file text, or after a loaded
		# file name. Aaaarghh!!!
		xypic_match = xypic_rx.match(line)
		if xypic_match:
			debug("xypic match after: " + line)
			# Do an extra check to make sure we are not too eager: is the topmost file
			# likely to be an xypic file? Look for xypic in the file name
			if files and "xypic" in files[-1]:
				debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
				f = files.pop()
				debug(u"Popped file: {0} ({1})".format(f, line_num))
				extra = xypic_match.group(1)
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue
			else:
				debug("Found loaded) but top file name doesn't have xy")

		if len(line)>0 and line[0]=='!': # Now it's surely an error
			debug("Error found: " + line)
			# If it's a pdftex error, it's on the current line, so report it
			if "pdfTeX error" in line:
				err_msg = line[1:].strip() # remove '!' and possibly spaces
				# This may or may not have a file location associated with it. 
				# Be conservative and do not try to report one.
				errors.append(err_msg)
				errors.append("Check the TeX log file for more information")
				continue
			# Now it's a regular TeX error 
			err_msg = line[2:] # skip "! "
			# next time around, err_msg will be set and we'll extract all info
			state = STATE_REPORT_ERROR
			continue

		# Second match for opening page numbers. We now use "search" which matches
		# everywhere, not just at the beginning. We do so AFTER matching file names so we
		# don't miss any.
		pagenum_begin_match = pagenum_begin_rx.search(line)
		if pagenum_begin_match:
			debug("Matching [xx after some text")
			extra = pagenum_begin_match.group(1)
			debug("Reprocessing " + extra)
			reprocess_extra = True
			continue		

		warning_match = warning_rx.match(line)
		if warning_match:
			# if last character is a dot, it's a single line
			if line[-1] == '.':
				handle_warning(line)
				continue
			# otherwise, accumulate it
			current_warning = line
			state = STATE_REPORT_WARNING
			continue

	# If there were parsing issues, output them to debug
	if parsing:
		warnings.append("(Log parsing issues. Disregard unless something else is wrong.)")
		print_debug = True
		for l in parsing:
			debug(l)
	return (errors, warnings, badboxes)


# If invoked from the command line, parse provided log file

if __name__ == '__main__':
	print_debug = True
	interactive = True
	try:
		logfilename = sys.argv[1]
		if len(sys.argv) == 3:
			extra_file_ext = sys.argv[2].split(" ")
		data = open(logfilename, 'rb').read()
		root_dir = os.path.dirname(logfilename)
		errors, warnings, badboxes = parse_tex_log(data, logfilename)
		print("")
		print("Errors:")
		for err in errors:
			print(err)
		print("")
		print ("Warnings:")
		for warn in warnings:
			print(warn)
		print("")
		print("Bad boxes:")
		for box in badboxes:
			print(box)
	except Exception as e:
		import traceback
		traceback.print_exc()