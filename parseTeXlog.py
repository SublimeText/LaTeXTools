import re
import sys
import os.path

print_debug = False
interactive = False
extra_file_ext = []

def debug(s):
	if print_debug:
		print "parseTeXlog: " + s.encode('UTF-8') # I think the ST2 console wants this

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
def debug_skip_file(f):
	# If we are not debugging, then it's not a file for sure, so skip it
	if not (print_debug and interactive):
		return True
	debug("debug_skip_file: " + f)
	f_ext = os.path.splitext(f)[1].lower()[1:]
	# Heuristic: TeXlive on Mac or Linux (well, Ubuntu at least) or Windows / MiKTeX
	# Known file extensions:
	known_file_exts = ['tex','sty','cls','cfg','def','mkii','fd','map','clo', 'dfu', \
						'ldf', 'bdf', 'bbx','cbx','lbx']
	if (f_ext in known_file_exts) and \
	   (("/usr/local/texlive/" in f) or ("/usr/share/texlive/" in f) or ("Program Files\\MiKTeX" in f) \
	   	or re.search(r"\\MiKTeX\\\d\.\d+\\tex",f)) or ("\\MiKTeX\\tex\\" in f):
		print "TeXlive / MiKTeX FILE! Don't skip it!"
		return False
	# Heuristic: "version 2010.12.02"
	if re.match(r"version \d\d\d\d\.\d\d\.\d\d", f):
		print "Skip it!"
		return True
	# Heuristic: TeX Live line
	if re.match(r"TeX Live 20\d\d(/Debian)?\) \(format", f):
		print "Skip it!"
		return True
	# Heuristic: MiKTeX line
	if re.match("MiKTeX \d\.\d\d?",f):
		print "Skip it!"
		return True
	# Heuristic: no two consecutive spaces in file name
	if "  " in f:
		print "Skip it!"
		return True
	# Heuristic: various diagnostic messages
	if f=='e.g.,' or "ext4): destination with the same identifier" in f or "Kristoffer H. Rose" in f:
		print "Skip it!"
		return True
	# Heuristic: file in local directory with .tex ending
	file_exts = extra_file_ext + ['tex', 'aux', 'bbl', 'cls', 'sty','out']
	if f[0:2] in ['./', '.\\', '..'] and f_ext in file_exts:
		print "File! Don't skip it"
		return False
	if raw_input() == "":
		print "Skip it"
		return True
	else:
		print "FILE! Don't skip it"
		return False


# More robust parsing code: October / November 2012
# Input: tex log file, read in **binary** form, unprocessed
# Output: content to be displayed in output panel, split into lines

def parse_tex_log(data):
	debug("Parsing log file")
	errors = []
	warnings = []

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
		return (errors, warnings)

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
	pagenum_begin_rx = re.compile(r"\s*\[\d*(.*)")
	line_rx = re.compile(r"^l\.(\d+)\s(.*)")		# l.nn <text>
	warning_rx = re.compile(r"^(.*?) Warning: (.+)") # Warnings, first line
	line_rx_latex_warn = re.compile(r"input line (\d+)\.$") # Warnings, line number
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
			errors.append("LaTeXTools cannot correctly detect file names in this LOG file.")
			errors.append("(where: trying to display warning message)")
			errors.append("Please let me know via GitHub (warnings). Thanks!")
		else:
			location = files[-1]		

		warn_match_line = line_rx_latex_warn.search(l)
		if warn_match_line:
			warn_line = warn_match_line.group(1)
			warnings.append(location + ":" + warn_line + ": " + l)
		else:
			warnings.append(location + ": " + l)

	
	# State definitions
	STATE_NORMAL = 0
	STATE_SKIP = 1
	STATE_REPORT_ERROR = 2
	STATE_REPORT_WARNING = 3
	
	state = STATE_NORMAL

	# Use our own iterator instead of for loop
	log_iterator = log.__iter__()
	line_num=0
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
			line_num +=1
		elif reprocess_extra:
			line = extra # NOTE: we must remember that we are reprocessing. See long-line heuristics
		else: # we read a new line
			# save previous line for "! File ended while scanning use of..." message
			prev_line = line
			try:
				line, linelen = log_iterator.next() # will fail when no more lines
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
		if (not reprocess_extra) and line_num>1 and linelen>=79 and line[0:2] != "**": 
			debug ("Line %d is %d characters long; last char is %s" % (line_num, len(line), line[-1]))
			# HEURISTICS HERE
			extend_line = True
			recycle_extra = False
			# HEURISTIC: check first if we just have a long "(.../file.tex" (or similar) line
			# A bit inefficient as we duplicate some of the code below for filename matching
			file_match = file_rx.match(line)
			if file_match:
				debug("MATCHED (long line)")
				file_name = file_match.group(1)
				file_extra = file_match.group(2) + file_match.group(3) # don't call it "extra"
				# remove quotes if necessary, but first save the count for a later check
				quotecount = file_name.count("\"")
				file_name = file_name.replace("\"", "")
				# NOTE: on TL201X pdftex sometimes writes "pdfTeX warning" right after file name
				# This may or may not be a stand-alone long line, but in any case if we
				# extend, the file regex will fire regularly
				if file_name[-6:]=="pdfTeX" and file_extra[:8]==" warning":
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
				elif (not os.path.isfile(file_name)) and debug_skip_file(file_name):
					debug("Not a file name")
				else:
					debug("IT'S A (LONG) FILE NAME WITH NO EXTRA TEXT")
					extend_line = False # so we exit right away and continue with parsing

			while extend_line:
				debug("extending: " + line)
				try:
					extra, extralen = log_iterator.next()
					debug("extension? " + extra)
					line_num += 1 # for debugging purposes
					# HEURISTIC: if extra line begins with "Package:" "File:" "Document Class:",
					# or other "well-known markers",
					# we just had a long file name, so do not add
					if extralen>0 and \
					   (extra[0:5]=="File:" or extra[0:8]=="Package:" or extra[0:15]=="Document Class:") or \
					   (extra[0:9]=="LaTeX2e <") or assignment_rx.match(extra):
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
					else:
						line += extra
						debug("Extended: " + line)
						linelen += extralen
						if extralen < 79:
							extend_line = False
				except StopIteration:
					extend_line = False # end of file, so we must be done. This shouldn't happen, btw
		# We may skip the above "if" because we are reprocessing a line, so reset flag:
		reprocess_extra = False
		# Check various states
		if state==STATE_SKIP:
			state = STATE_NORMAL
			continue
		if state==STATE_REPORT_ERROR:
			# skip everything except "l.<nn> <text>"
			debug(line)
			# We check for emergency stops here, too, because it may occur before the l.nn text
			if "! Emergency stop." in line:
				emergency_stop = True
				debug("Emergency stop found")
				continue
			err_match = line_rx.match(line)
			if not err_match:
				continue
			# now we match!
			state = STATE_NORMAL
			err_line = err_match.group(1)
			err_text = err_match.group(2)
			# err_msg is set from last time
			if files==[]:
				location = "[no file]"
				errors.append("LaTeXTools cannot correctly detect file names in this LOG file.")
				errors.append("(where: trying to display error message)")
				errors.append("Please let me know via GitHub. Thanks!")
			else:
				location = files[-1]
			debug("Found error: " + err_msg)		
			errors.append(location + ":" + err_line + ": " + err_msg + " [" + err_text + "]")
			continue
		if state==STATE_REPORT_WARNING:
			# add current line and check if we are done or not
			current_warning += line
			if line[-1]=='.':
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
		if len(line)>0 and \
			(line[0:5]=="File:" or line[0:8]=="Package:" or line[0:15]=="Document Class:") or \
			(line[0:9]=="LaTeX2e <"):
			continue

		# Are we done? Get rid of extra spaces, just in case (we may have extended a line, etc.)
		if line.strip() == "Here is how much of TeX's memory you used:":
			if len(files)>0:
				if emergency_stop or incomplete_if:
					debug("Done processing, files on stack due to known conditions (all is fine!)")
				elif xypic_flag:
					warnings.append("LaTeXTools cannot correctly detect file names in this LOG file.")
					warnings.append("However, you are using the xypic package, which does nonstandard logging.")
					warnings.append("You may report this on GitHub, but I can't promise I will fix it.")
					warnings.append("Try recompiling without xypic to see if there are other log parsing issues.")
					warnings.append("In any case, compilation was successful.")
					debug("Done processing, some files left on the stack, BUT user had xypic!")
					debug(";".join(files))
				else:
					errors.append("LaTeXTools cannot correctly detect file names in this LOG file.")
					errors.append("(where: finished processing)")
					errors.append("Please let me know via GitHub")
					debug("Done processing, some files left on the stack")
					debug(";".join(files))
				files=[]			
			break

		# Special error reporting for e.g. \footnote{text NO MATCHING PARENS & co
		if "! File ended while scanning use of" in line:
			scanned_command = line[35:-2] # skip space and period at end
			# we may be unable to report a file by popping it, so HACK HACK HACK
			file_name, linelen = log_iterator.next() # <inserted text>
			file_name, linelen = log_iterator.next() #      \par
			file_name, linelen = log_iterator.next()
			file_name = file_name[3:] # here is the file name with <*> in front
			errors.append("TeX STOPPED: " + line[2:-2]+prev_line[:-5])
			errors.append("TeX reports the error was in file:" + file_name)
			continue

		# Here, make sure there was no uncaught error, in which case we do more special processing
		if "!  ==> Fatal error occurred, no output" in line:
			if errors == []:
				errors.append("TeX STOPPED: fatal errors occurred but LaTeXTools did not see them")
				errors.append("Check the TeX log file, and please let me know via GitHub. Thanks!")
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
			if line[-2:]=="[]": # one-line over/underfull message
				continue
			ou_processing = True
			while ou_processing:
				try:
					line, linelen = log_iterator.next() # will fail when no more lines
				except StopIteration:
					debug("Over/underfull: StopIteration (%d)" % line_num)
					break
				line_num += 1
				debug("Over/underfull: skip " + line + " (%d) " % line_num)
				# Sometimes it's " []" and sometimes it's "[]"...
				if len(line)>0 and line in [" []", "[]"]:
					ou_processing = False
			if ou_processing:
				errors.append("Malformed LOG file: over/underfull")
				break
			else:
				continue

		# Special case: the bibgerm package, which has comments starting and ending with
		# **, and then finishes with "**)"
		if len(line)>0 and line[:2] == "**" and line[-3:] == "**)" \
						and files and "bibgerm" in files[-1]:
			debug("special case: bibgerm")
			debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
			files.pop()
			continue

		# Special case: the relsize package, which puts ")" at the end of a
		# line beginning with "Examine \". Ah well!
		if len(line)>0 and line[:9] == "Examine \\" and line[-3:] == ". )" \
						and files and  "relsize" in files[-1]:
			debug("special case: relsize")
			debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
			files.pop()
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
			files.pop()
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
				files.pop()
				extra = xypic_match.group(1)
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue
			else:
				debug("Found loaded) but top file name doesn't have xy")


		line = line.strip() # get rid of initial spaces
		# note: in the next line, and also when we check for "!", we use the fact that "and" short-circuits
		if len(line)>0 and line[0]==')': # denotes end of processing of current file: pop it from stack
			if files:
				debug(" "*len(files) + files[-1] + " (%d)" % (line_num,))
				files.pop()
				extra = line[1:]
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue
			else:
				errors.append("LaTeXTools cannot correctly detect file names in this LOG file.")
				errors.append("Please let me know via GitHub. Thanks!")
				debug("Popping inexistent files")
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
			debug("MATCHED")
			file_name = file_match.group(1)
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
			if (not os.path.isfile(file_name)) and debug_skip_file(file_name):
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
				files.pop()
				extra = xypic_match.group(1)
				debug("Reprocessing " + extra)
				reprocess_extra = True
				continue
			else:
				debug("Found loaded) but top file name doesn't have xy")

		if len(line)>0 and line[0]=='!': # Now it's surely an error
			debug(line)
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

	return (errors, warnings)


# If invoked from the command line, parse provided log file

if __name__ == '__main__':
	print_debug = True
	interactive = True
	try:
		logfilename = sys.argv[1]
		# logfile = open(logfilename, 'r') \
		# 		.read().decode(enc, 'ignore') \
		# 		.encode(enc, 'ignore').splitlines()
		if len(sys.argv) == 3:
			extra_file_ext = sys.argv[2].split(" ")
		data = open(logfilename,'r').read()
		(errors,warnings) = parse_tex_log(data)
		print ""
		print "Warnings:"
		for warn in warnings:
			print warn.encode('UTF-8')
		print ""
		print "Errors:"
		for err in errors:
			print err.encode('UTF-8')

	except Exception, e:
		import traceback
		traceback.print_exc()