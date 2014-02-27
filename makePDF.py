# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
	import parseTeXlog
else:
	_ST3 = True
	from . import getTeXRoot
	from . import parseTeXlog

import sublime_plugin
import sys, os, os.path, platform, threading, functools
import subprocess
import types
import re
import codecs

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
    import ctypes
    codepage = ctypes.windll.kernel32.GetOEMCP()
    return str(codepage)





# First, define thread class for async processing

class CmdThread ( threading.Thread ):

	# Use __init__ to pass things we need
	# in particular, we pass the caller in teh main thread, so we can display stuff!
	def __init__ (self, caller):
		self.caller = caller
		threading.Thread.__init__ ( self )

	def run ( self ):
		print ("Welcome to thread " + self.getName())
		cmd = self.caller.make_cmd + [self.caller.file_name]
		self.caller.output("[Compiling " + self.caller.file_name + "]")
		if DEBUG:
			print (cmd.encode('UTF-8'))

		# Handle path; copied from exec.py
		if self.caller.path:
			old_path = os.environ["PATH"]
			# The user decides in the build system  whether he wants to append $PATH
			# or tuck it at the front: "$PATH;C:\\new\\path", "C:\\new\\path;$PATH"
			# Handle differently in Python 2 and 3, to be safe:
			if not _ST3:
				os.environ["PATH"] = os.path.expandvars(self.caller.path).encode(sys.getfilesystemencoding())
			else:
				os.environ["PATH"] = os.path.expandvars(self.caller.path)


		try:
			if platform.system() == "Windows":
				# make sure console does not come up
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				proc = subprocess.Popen(cmd, startupinfo=startupinfo)
			else:
				proc = subprocess.Popen(cmd)
		except:
			self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
			self.caller.output("Attempted command:")
			self.caller.output(" ".join(cmd))
			self.caller.proc = None
			return
		
		# restore path if needed
		if self.caller.path:
			os.environ["PATH"] = old_path

		# Handle killing
		# First, save process handle into caller; then communicate (which blocks)
		self.caller.proc = proc
		# out, err = proc.communicate()
		proc.wait() # TODO: if needed, must use tempfiles instead of stdout/err

		# if DEBUG:
		# 	self.caller.output(out)

		# Here the process terminated, but it may have been killed. If so, do not process log file.
		# Since we set self.caller.proc above, if it is None, the process must have been killed.
		# TODO: clean up?
		if not self.caller.proc:
			print (proc.returncode)
			self.caller.output("\n\n[User terminated compilation process]\n")
			self.caller.finish(False)	# We kill, so won't switch to PDF anyway
			return
		# Here we are done cleanly:
		self.caller.proc = None
		print ("Finished normally")
		print (proc.returncode)

		# this is a conundrum. We used (ST1) to open in binary mode ('rb') to avoid
		# issues, but maybe we just need to decode?
		# 12-10-27 NO! We actually do need rb, because MikTeX on Windows injects Ctrl-Z's in the
		# log file, and this just causes Python to stop reading the file.

		# OK, this seems solid: first we decode using the self.caller.encoding, 
		# then we reencode using the default locale's encoding.
		# Note: we get this using ST2's own getdefaultencoding(), not the locale module
		# We ignore bad chars in both cases.

		# CHANGED 12/10/19: use platform encoding (self.caller.encoding), then
		# keep it that way!

		# CHANGED 12-10-27. OK, here's the deal. We must open in binary mode on Windows
		# because silly MiKTeX inserts ASCII control characters in over/underfull warnings.
		# In particular it inserts EOFs, which stop reading altogether; reading in binary
		# prevents that. However, that's not the whole story: if a FS character is encountered,
		# AND if we invoke splitlines on a STRING, it sadly breaks the line in two. This messes up
		# line numbers in error reports. If, on the other hand, we invoke splitlines on a
		# byte array (? whatever read() returns), this does not happen---we only break at \n, etc.
		# However, we must still decode the resulting lines using the relevant encoding.
		# 121101 -- moved splitting and decoding logic to parseTeXlog, where it belongs.
		
		# Note to self: need to think whether we don't want to codecs.open this, too...
		data = open(self.caller.tex_base + ".log", 'rb').read()		

		errors = []
		warnings = []

		try:
			(errors, warnings) = parseTeXlog.parse_tex_log(data)
			content = ["",""]
			if errors:
				content.append("There were errors in your LaTeX source") 
				content.append("")
				content.extend(errors)
			else:
				content.append("Texification succeeded: no errors!")
				content.append("") 
			if warnings:
				if errors:
					content.append("")
					content.append("There were also warnings.") 
				else:
					content.append("However, there were warnings in your LaTeX source") 
				content.append("")
				content.extend(warnings)
		except Exception as e:
			content=["",""]
			content.append("LaTeXtools could not parse the TeX log file")
			content.append("(actually, we never should have gotten here)")
			content.append("")
			content.append("Python exception: " + repr(e))
			content.append("")
			content.append("Please let me know on GitHub. Thanks!")

		self.caller.output(content)
		self.caller.output("\n\n[Done!]\n")
		self.caller.finish(len(errors) == 0)


# Actual Command

# TODO latexmk stops if bib files can't be found (on subsequent compiles)
# I.e. it doesn't even start bibtex!
# If so, find out! Otherwise log file is never refreshed
# Work-around: check file creation times

# We get the texification command (cmd), file regex and path (TODO) from
# the sublime-build file. This allows us to use the ST2 magic: we can keep both
# windows and osx settings there, and we get handed the right one depending on
# the platform! Cool!

class make_pdfCommand(sublime_plugin.WindowCommand):

	def run(self, cmd="", file_regex="", path=""):
		
		# Try to handle killing
		if hasattr(self, 'proc') and self.proc: # if we are running, try to kill running process
			self.output("\n\n### Got request to terminate compilation ###")
			self.proc.kill()
			self.proc = None
			return
		else: # either it's the first time we run, or else we have no running processes
			self.proc = None
		
		view = self.window.active_view()

		self.file_name = getTeXRoot.get_tex_root(view)
		if not os.path.isfile(self.file_name):
			sublime.error_message(self.file_name + ": file not found.")
			return

		self.tex_base, self.tex_ext = os.path.splitext(self.file_name)
		tex_dir = os.path.dirname(self.file_name)
		
		# Extra paths
		self.path = path
			
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

		# Get parameters from sublime-build file:
		self.make_cmd = cmd

		# I actually think self.file_name is it already
		self.engine = 'pdflatex' # Standard pdflatex
		for line in codecs.open(self.file_name, "r", "UTF-8", "ignore").readlines():
			if not line.startswith('%'):
				break
			else:
				# We have a comment match; check for a TS-program match
				mroot = re.match(r"%\s*!TEX\s+(?:TS-)?program *= *(xelatex|lualatex|pdflatex)\s*$",line)
				if mroot:
					# Sanity checks
					if "texify" == self.make_cmd[0]:
						sublime.error_message("Sorry, cannot select engine using a %!TEX program directive on MikTeX.")
						return 
					if not ("$pdflatex = '%E" in self.make_cmd[3]):
						sublime.error_message("You are using a custom LaTeX.sublime-build file (in User maybe?). Cannot select engine using a %!TEX program directive.")
						return
					self.engine = mroot.group(1)
					break
		if self.engine != 'pdflatex': # Since pdflatex is standard, we do not output a msg. for it.
			self.output("Using engine " + self.engine + "\n")
		self.make_cmd[3] = self.make_cmd[3].replace("%E", self.engine)
		self.output_view.settings().set("result_file_regex", file_regex)

		if view.is_dirty():
			print ("saving...")
			view.run_command('save') # call this on view, not self.window
		
		if self.tex_ext.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot compile." % (os.path.basename(view.file_name()),))
			return
		
		s = platform.system()
		if s == "Darwin":
			self.encoding = "UTF-8"
		elif s == "Windows":
			self.encoding = getOEMCP()
		elif s == "Linux":
			self.encoding = "UTF-8"
		else:
			sublime.error_message("Platform as yet unsupported. Sorry!")
			return	
		print (self.make_cmd + [self.file_name])
		
		os.chdir(tex_dir)
		CmdThread(self).start()
		print (threading.active_count())


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
		# Need different handling for python 2 and 3
		if not _ST3:
			strdata = data if isinstance(data, types.StringTypes) else "\n".join(data)
		else:
			strdata = data if isinstance(data, str) else "\n".join(data)

		# Normalize newlines, Sublime Text always uses a single \n separator
		# in memory.
		strdata = strdata.replace('\r\n', '\n').replace('\r', '\n')

		selection_was_at_end = (len(self.output_view.sel()) == 1
		    and self.output_view.sel()[0]
		        == sublime.Region(self.output_view.size()))
		self.output_view.set_read_only(False)
		# Move this to a TextCommand for compatibility with ST3
		self.output_view.run_command("do_output_edit", {"data": strdata, "selection_was_at_end": selection_was_at_end})
		# edit = self.output_view.begin_edit()
		# self.output_view.insert(edit, self.output_view.size(), strdata)
		# if selection_was_at_end:
		#     self.output_view.show(self.output_view.size())
		# self.output_view.end_edit(edit)
		self.output_view.set_read_only(True)	

	# Also from exec.py
	# Set the selection to the start of the output panel, so next_result works
	# Then run viewer

	def finish(self, can_switch_to_pdf):
		sublime.set_timeout(functools.partial(self.do_finish, can_switch_to_pdf), 0)

	def do_finish(self, can_switch_to_pdf):
		# Move to TextCommand for compatibility with ST3
		# edit = self.output_view.begin_edit()
		# self.output_view.sel().clear()
		# reg = sublime.Region(0)
		# self.output_view.sel().add(reg)
		# self.output_view.show(reg) # scroll to top
		# self.output_view.end_edit(edit)
		self.output_view.run_command("do_finish_edit")
		if can_switch_to_pdf:
			self.window.active_view().run_command("jump_to_pdf", {"from_keybinding": False})


class DoOutputEditCommand(sublime_plugin.TextCommand):
    def run(self, edit, data, selection_was_at_end):
        self.view.insert(edit, self.view.size(), data)
        if selection_was_at_end:
            self.view.show(self.view.size())

class DoFinishEditCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().clear()
        reg = sublime.Region(0)
        self.view.sel().add(reg)
        self.view.show(reg)
