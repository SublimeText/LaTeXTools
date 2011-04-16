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
	file_rx = re.compile("^\s*\(([^)]+)$")		# file name
	line_rx = re.compile("^l\.(\d+)\s(.*)")		# l.nn <text>
	warning_rx = re.compile("^(.*?) Warning: (.+)") # Warnings, first line
	line_rx_latex_warn = re.compile("input line (\d+)\.$") # Warnings, line number

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

	while True:
		try:
			line = log_iterator.next() # will fail when no more lines
		except StopIteration:
			break
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
		if "!  ==> Fatal error occurred, no output" in line:
			continue
		if "! Emergency stop." in line:
			state = STATE_SKIP
			continue
		file_match = file_rx.match(line)
		if file_match:
			files.append(file_match.group(1))
			print files
		if line[0]==')': # TODO here after ) there may be ( with new file!!!
			for i in range(len(line)):
				files.pop()
				print files
		if line[0]=='!': # Now it's surely an error
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
		# self.output_view.settings().set("result_base_dir", working_dir)

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
		sublime.set_timeout(functools.partial(self.append_data, data), 0)

	def append_data(self, data):
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
