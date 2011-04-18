import sublime, sublime_plugin, os, os.path, platform, threading, functools, ctypes
from subprocess import Popen, PIPE, STDOUT
import types
import re

DEBUG = False

# Compile current .tex file using platform-specific tool
# On Windows, use texify; on Mac, use latexmk
# Assumes executables are on the path
# Warning: we do not do "deep" safety checks

# This is basically a specialized exec command: we do not capture output,
# but instead look at log files to parse errors

# Encoding: especially useful for Windows
# TODO: counterpart for OSX? Guess encoding of files?
def getOEMCP():
    # Windows OEM/Ansi codepage mismatch issue.
    # We need the OEM cp, because texify and friends are console programs
    codepage = ctypes.windll.kernel32.GetOEMCP()
    return str(codepage)


# Log parsing, TNG :-)
# Input: tex log file (decoded), split into lines
# Output: content to be displayed in output panel, split into lines

def parseTeXlog(log):
	print "Parsing log file"
	errors = []
	warnings = []
	
	# loop over all log lines; construct error message as needed
	# This will be useful for multi-file documents

	# some regexes
	file_rx = re.compile(r"\(([^)]+)$")		# file name: "(" followed by anyting but "(" through the end of the line
	line_rx = re.compile(r"^l\.(\d+)\s(.*)")		# l.nn <text>
	warning_rx = re.compile(r"^(.*?) Warning: (.+)") # Warnings, first line
	line_rx_latex_warn = re.compile(r"input line (\d+)\.$") # Warnings, line number
	matched_parens_rx = re.compile(r"\([^()]*\)") # matched parentheses, to be deleted (note: not if nested)
	assignment_rx = re.compile(r"\\[^=]*=")	# assignment, heuristics for line merging

	files = []

	# Support function to handle warnings
	def handle_warning(l):
		warn_match_line = line_rx_latex_warn.search(l)
		if warn_match_line:
			warn_line = warn_match_line.group(1)
			warnings.append(files[-1] + ":" + warn_line + ": " + l)
		else:
			warnings.append(files[-1] + ": " + l)

	
	# State definitions
	STATE_NORMAL = 0
	STATE_SKIP = 1
	STATE_REPORT_ERROR = 2
	STATE_REPORT_WARNING = 3
	
	state = STATE_NORMAL

	# Use our own iterator instead of for loop
	log_iterator = log.__iter__()
	line_num=0

	while True:
		try:
			line = log_iterator.next() # will fail when no more lines
		except StopIteration:
			break
		line_num += 1
		# Now we deal with TeX's decision to truncate all log lines at 79 characters
		# If we find a line of exactly 79 characters, we add the subsequent line to it, and continue
		# until we find a line of less than 79 characters
		# The problem is that there may be a line of EXACTLY 79 chars. We keep our fingers crossed but also
		# use some heuristics to avoid disastrous consequences
		# We are inspired by latexmk (which has no heuristics, though)

		# HEURISTIC: the first line is always long, and we don't care about it
		# also, the **<file name> line may be long, but we skip it, too (to avoid edge cases)
		if line_num>1 and len(line)>=79 and line[0:2] != "**": 
			# print "Line %d is %d characters long; last char is %s" % (line_num, len(line), line[-1])
			# HEURISTICS HERE
			extend_line = True
			while extend_line:
				try:
					extra = log_iterator.next()
					line_num += 1 # for debugging purposes
					# HEURISTIC: if extra line begins with "Package:" "File:" "Document Class:",
					# we just had a long file name, so do not add
					if len(extra)>0 and \
					   (extra[0:5]=="File:" or extra[0:8]=="Package:" or extra[0:15]=="Document Class:") or \
					   assignment_rx.match(extra):
						extend_line = False
					else:
						line += extra
						if len(extra) < 79:
							extend_line = False
				except StopIteration:
					extend_line = False # end of file, so we must be done. This shouldn't happen, btw
		# Check various states
		if state==STATE_SKIP:
			state = STATE_NORMAL
			continue
		if state==STATE_REPORT_ERROR:
			# skip everything except "l.<nn> <text>"
			print line
			err_match = line_rx.match(line)
			if not err_match:
				continue
			# now we match!
			state = STATE_NORMAL
			err_line = err_match.group(1)
			err_text = err_match.group(2)
			# err_msg is set from last time
			errors.append(files[-1] + ":" + err_line + ": " + err_msg + " [" + err_text + "]")
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
		# Remove matched parentheses: they do not add new files to the stack
		line_purged = matched_parens_rx.sub("", line)
		# if line != line_purged:
			# print "Purged parens on line %d:" % (line_num, )  
			# print line
			# print line_purged
		line = line_purged
		if "!  ==> Fatal error occurred, no output" in line:
			continue
		if "! Emergency stop." in line:
			state = STATE_SKIP
			continue
		# catch over/underfull
		# skip everything for now
		# Over/underfull messages end with [] so look for that
		if line[0:8] in ["Overfull", "Underfull"]:
			if line[-2:]=="[]": # one-line over/underfull message
				continue
			ou_processing = True
			while ou_processing:
				try:
					line = log_iterator.next() # will fail when no more lines
				except StopIteration:
					break
				line_num += 1
				if len(line)>0 and line[0:3] == " []":
					ou_processing = False
			if ou_processing:
				errors.append("Malformed LOG file: over/underfull")
				break
			else:
				continue
		line.strip() # get rid of initial spaces
		# note: in the next line, and also when we check for "!", we use the fact that "and" short-circuits
		while len(line)>0 and line[0]==')': # denotes end of processing of current file: pop it from stack
			files.pop()
			line = line[1:] # lather, rinse, repeat
			print " "*len(files) + files[-1] + " (%d)" % (line_num,)
		line.strip() # again, to make sure there is no ") (filename" pattern
		file_match = file_rx.search(line) # search matches everywhere, not just at the beginning of a line
		if file_match:
			files.append(file_match.group(1))
			print " "*len(files) + files[-1] + " (%d)" % (line_num,)
		if len(line)>0 and line[0]=='!': # Now it's surely an error
			print line
			err_msg = line[2:] # skip "! "
			# next time around, err_msg will be set and we'll extract all info
			state = STATE_REPORT_ERROR
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


	output = []
	if errors:
		output.append("There were errors in your LaTeX source") 
		output.append("")
		output.extend(errors)
	else:
		print "No errors.\n"
		output.append("Texification succeeded: no errors!\n")
		output.append("") 
	if warnings:
		print "There were no warnings.\n"
		skip = 0
		for warning in warnings:
			print warning
			if skip:
				print ""
			skip = 1-skip
		if errors:
			output.append("")
			output.append("There were also warnings.") 
		else:
			output.append("However, there were warnings in your LaTeX source") 
		output.append("")
		output.extend(warnings)
	else:
		print "No warnings.\n"
	return output




# First, define thread class for async processing

class CmdThread ( threading.Thread ):

	# Use __init__ to pass things we need
	# in particular, we pass the caller in teh main thread, so we can display stuff!
	def __init__ (self, caller):
		self.caller = caller
		threading.Thread.__init__ ( self )

	def run ( self ):
		print "Welcome to the thread!"
		cmd = self.caller.make_cmd + [self.caller.file_name]
		self.caller.output("[Compiling " + self.caller.file_name + "]\n\n")
		if DEBUG:
			print cmd
		out, err = Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()
		if DEBUG:
			self.caller.output(out)
		# this is a conundrum. We used (ST1) to open in binary mode ('rb') to avoid
		# issues, but maybe we just need to decode?
		# try 'ignore' option: just skip unknown characters
		data = open(self.caller.tex_base + ".log", 'r') \
				.read().decode(self.caller.encoding, 'ignore').splitlines()
		self.caller.output(parseTeXlog(data))
		self.caller.output("\n\n[Done!]\n")
		self.caller.finish()


# Actual Command

# TODO latexmk stops if bib files can't be found (on subsequent compiles)
# I.e. it doesn't even start bibtex!
# If so, find out! Otherwise log file is never refreshed
# Work-around: check file creation times

class make_pdfCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		self.file_name = view.file_name()
		self.tex_base, self.tex_ext = os.path.splitext(self.file_name)
		# On OSX, change to file directory, or latexmk will spew stuff into root!
		tex_dir = os.path.dirname(self.file_name)
		
		# Output panel: from exec.py
		if not hasattr(self, 'output_view'):
			self.output_view = self.window.get_output_panel("exec")

		# Dumb, but required for the moment for the output panel to be picked
        # up as the result buffer
		self.window.get_output_panel("exec")

		self.output_view.settings().set("result_file_regex", "^([^:\n\r]*):([0-9]+):?([0-9]+)?:? (.*)$")
		# self.output_view.settings().set("result_line_regex", line_regex)
		self.output_view.settings().set("result_base_dir", tex_dir)

		self.window.run_command("show_panel", {"panel": "output.exec"})

		if view.is_dirty():
			print "saving..."
			view.run_command('save') # call this on view, not self.window
		
		if self.tex_ext.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot compile." % (os.path.basename(view.fileName()),))
			return
		
		s = platform.system()
		if s == "Darwin":
			# use latexmk
			# -f forces compilation even if e.g. bib files are not found
			self.make_cmd = ["latexmk", 
						"-e", "$pdflatex = 'pdflatex %O -synctex=1 %S'",
						"-f", "-pdf",]
			self.encoding = "UTF-8"
		elif s == "Windows":
			self.make_cmd = ["texify", "-b", "-p",
			"--tex-option=\"--synctex=1\"", 
			#"--tex-option=\"--max-print-line=200\"", 
			#"--tex-option=\"-file-line-error\""
			]
			self.encoding = getOEMCP()
		else:
			sublime.error_message("Platform as yet unsupported. Sorry!")
			return	
		print self.make_cmd + [self.file_name]
		
		os.chdir(tex_dir)
		CmdThread(self).start()


	# Threading headaches :-)
	# The following function is what gets called from CmdThread; in turn,
	# this spawns append_data, but on the main thread.

	def output(self, data):
		sublime.set_timeout(functools.partial(self.do_output, data), 0)

	def do_output(self, data):
        # if proc != self.proc:
        #     # a second call to exec has been made before the first one
        #     # finished, ignore it instead of intermingling the output.
        #     if proc:
        #         proc.kill()
        #     return

		# try:
		#     str = data.decode(self.encoding)
		# except:
		#     str = "[Decode error - output not " + self.encoding + "]"
		#     proc = None

		# decoding in thread, so we can pass coded and decoded data
		# handle both lists and strings
		str = data if isinstance(data, types.StringTypes) else "\n".join(data)

		# Normalize newlines, Sublime Text always uses a single \n separator
		# in memory.
		str = str.replace('\r\n', '\n').replace('\r', '\n')

		selection_was_at_end = (len(self.output_view.sel()) == 1
		    and self.output_view.sel()[0]
		        == sublime.Region(self.output_view.size()))
		self.output_view.set_read_only(False)
		edit = self.output_view.begin_edit()
		self.output_view.insert(edit, self.output_view.size(), str)
		if selection_was_at_end:
		    self.output_view.show(self.output_view.size())
		self.output_view.end_edit(edit)
		self.output_view.set_read_only(True)	

	# Also from exec.py
	# Set the selection to the start of the output panel, so next_result works	

	def finish(self):
		sublime.set_timeout(self.do_finish, 0)

	def do_finish(self):
		edit = self.output_view.begin_edit()
		self.output_view.sel().clear()
		reg = sublime.Region(0)
		self.output_view.sel().add(reg)
		self.output_view.show(reg) # scroll to top
		self.output_view.end_edit(edit)
