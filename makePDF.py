	# ST2/ST3 compat
from __future__ import print_function

import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
	import parseTeXlog
	from latextools_plugin import (
		add_plugin_path, get_plugin, NoSuchPluginException,
		_classname_to_internal_name
	)
	from latextools_utils.is_tex_file import is_tex_file
	from latextools_utils import get_setting
	from latextools_utils.tex_directives import parse_tex_directives
	from latextools_utils.output_directory import (
		get_aux_directory, get_output_directory, get_jobname
	)

	strbase = basestring
else:
	_ST3 = True
	from . import getTeXRoot
	from . import parseTeXlog
	from .latextools_plugin import (
		add_plugin_path, get_plugin, NoSuchPluginException,
		_classname_to_internal_name
	)
	from .latextools_utils.is_tex_file import is_tex_file
	from .latextools_utils import get_setting
	from .latextools_utils.tex_directives import parse_tex_directives
	from .latextools_utils.output_directory import (
		get_aux_directory, get_output_directory, get_jobname
	)

	strbase = str

import sublime_plugin
import sys
import os, os.path
import signal
import threading
import functools
import subprocess
import types
import traceback
import shutil

DEBUG = False

# Compile current .tex file to pdf
# Allow custom scripts and build engines!

# The actual work is done by builders, loaded on-demand from prefs

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
		self.caller.output("[Compiling " + self.caller.file_name + "]")

		# Handle custom env variables
		if self.caller.env:
			old_env = os.environ;
			if not _ST3:
				os.environ.update(dict((k.encode(sys.getfilesystemencoding()), v) for (k, v) in self.caller.env.items()))
			else:
				os.environ.update(self.caller.env.items());

		# Handle path; copied from exec.py
		if self.caller.path:
			# if we had an env, the old path is already backuped in the env
			if not self.caller.env:
				old_path = os.environ["PATH"]
			# The user decides in the build system  whether he wants to append $PATH
			# or tuck it at the front: "$PATH;C:\\new\\path", "C:\\new\\path;$PATH"
			# Handle differently in Python 2 and 3, to be safe:
			if not _ST3:
				os.environ["PATH"] = os.path.expandvars(self.caller.path).encode(sys.getfilesystemencoding())
			else:
				os.environ["PATH"] = os.path.expandvars(self.caller.path)

		# Set up Windows-specific parameters
		if self.caller.plat == "windows":
			# make sure console does not come up
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		# Now, iteratively call the builder iterator
		#
		cmd_iterator = self.caller.builder.commands()
		try:
			for (cmd, msg) in cmd_iterator:

				# If there is a message, display it
				if msg:
					self.caller.output(msg)

				# If there is nothing to be done, exit loop
				# (Avoids error with empty cmd_iterator)
				if cmd == "":
					break

				if isinstance(cmd, strbase) or isinstance(cmd, list):
					print(cmd)
					# Now create a Popen object
					try:
						if self.caller.plat == "windows":
							proc = subprocess.Popen(
								cmd,
								startupinfo=startupinfo,
								stderr=subprocess.STDOUT,
								stdout=subprocess.PIPE,
								cwd=self.caller.tex_dir
							)
						elif self.caller.plat == "osx":
							proc = subprocess.Popen(
								cmd,
								stderr=subprocess.STDOUT,
								stdout=subprocess.PIPE,
								env=os.environ,
								preexec_fn=os.setsid,
								cwd=self.caller.tex_dir
							)
						else:  # Must be linux
							proc = subprocess.Popen(
								cmd,
								stderr=subprocess.STDOUT,
								stdout=subprocess.PIPE,
								preexec_fn=os.setsid,
								cwd=self.caller.tex_dir
							)
					except:
						self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
						self.caller.output("Attempted command:")
						self.caller.output(" ".join(cmd))
						self.caller.output("\nBuild engine: " + self.caller.builder.name)
						self.caller.proc = None
						print(traceback.format_exc())
						return
				# Abundance of caution / for possible future extensions:
				elif isinstance(cmd, subprocess.Popen):
					proc = cmd
				else:
					# don't know what the command is
					continue
				
				# Now actually invoke the command, making sure we allow for killing
				# First, save process handle into caller; then communicate (which blocks)
				with self.caller.proc_lock:
					self.caller.proc = proc
				out, err = proc.communicate()
				self.caller.builder.set_output(out.decode(self.caller.encoding,"ignore"))

				
				# Here the process terminated, but it may have been killed. If so, stop and don't read log
				# Since we set self.caller.proc above, if it is None, the process must have been killed.
				# TODO: clean up?
				with self.caller.proc_lock:
					if not self.caller.proc:
						print (proc.returncode)
						self.caller.output("\n\n[User terminated compilation process]\n")
						self.caller.finish(False)	# We kill, so won't switch to PDF anyway
						return
				# Here we are done cleanly:
				with self.caller.proc_lock:
					self.caller.proc = None
				print ("Finished normally")
				print (proc.returncode)
				# At this point, out contains the output from the current command;
				# we pass it to the cmd_iterator and get the next command, until completion
		except:
			self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
			self.caller.output("\nBuild engine: " + self.caller.builder.name)
			self.caller.proc = None
			print(traceback.format_exc())
			return
		finally:
			# restore environment
			if self.caller.env:
				os.environ = old_env
			elif self.caller.path:
				os.environ['PATH'] = old_path

		# Clean up
		cmd_iterator.close()

		try:
			# Here we try to find the log file...
			# 1. Check the aux_directory if there is one
			# 2. Check the output_directory if there is one
			# 3. Assume the log file is in the same folder as the main file
			log_file_base = self.caller.tex_base + ".log"
			if self.caller.aux_directory is None:
				if self.caller.output_directory is None:
					log_file = os.path.join(
						self.caller.tex_dir,
						log_file_base
					)
				else:
					log_file = os.path.join(
						self.caller.output_directory,
						log_file_base
					)

					if not os.path.exists(log_file):
						log_file = os.path.join(
							self.caller.tex_dir,
							log_file_base
						)
			else:
				log_file = os.path.join(
					self.caller.aux_directory,
					log_file_base
				)

				if not os.path.exists(log_file):
					if (
						self.caller.output_directory is not None and
						self.caller.output_directory != self.caller.aux_directory
					):
						log_file = os.path.join(
							self.caller.output_directory,
							log_file_base
						)

					if not os.path.exists(log_file):
						log_file = os.path.join(
							self.caller.tex_dir,
							log_file_base
						)

			# CHANGED 12-10-27. OK, here's the deal. We must open in binary mode
			# on Windows because silly MiKTeX inserts ASCII control characters in
			# over/underfull warnings. In particular it inserts EOFs, which
			# stop reading altogether; reading in binary prevents that. However,
			# that's not the whole story: if a FS character is encountered,
			# AND if we invoke splitlines on a STRING, it sadly breaks the line
			# in two. This messes up line numbers in error reports. If, on the
			# other hand, we invoke splitlines on a byte array (? whatever read()
			# returns), this does not happen---we only break at \n, etc.
			# However, we must still decode the resulting lines using the relevant
			# encoding.

			# Note to self: need to think whether we don't want to codecs.open
			# this, too... Also, we may want to move part of this logic to the
			# builder...
			with open(log_file, 'rb') as f:
				data = f.read()
		except IOError:
			self.caller.output([
				"", ""
				"Could not find log file {0}!".format(log_file_base),
			])
			try:
				self.handle_std_outputs(out, err)
			except:
				# if out or err don't yet exist
				self.caller.finish(False)
		else:
			errors = []
			warnings = []
			badboxes = []

			try:
				(errors, warnings, badboxes) = parseTeXlog.parse_tex_log(
					data, self.caller.tex_dir
				)
				content = [""]
				if errors:
					content.append("Errors:")
					content.append("")
					content.extend(errors)
				else:
					content.append("No errors.")
				if warnings:
					if errors:
						content.extend(["", "Warnings:"])
					else:
						content[-1] = content[-1] + " Warnings:"
					content.append("")
					content.extend(warnings)
				else:
					if errors:
						content.append("")
						content.append("No warnings.")
					else:
						content[-1] = content[-1] + " No warnings."

				if badboxes and self.caller.display_bad_boxes:
					if warnings or errors:
						content.extend(["", "Bad Boxes:"])
					else:
						content[-1] = content[-1] + " Bad Boxes:"
					content.append("")
					content.extend(badboxes)
				else:
					if self.caller.display_bad_boxes:
						if errors or warnings:
							content.append("")
							content.append("No bad boxes.")
						else:
							content[-1] = content[-1] + " No bad boxes."

				hide_panel = {
					"always": True,
					"no_errors": not errors,
					"no_warnings": not errors and not warnings,
					"no_badboxes": not errors and not warnings and \
						(not self.caller.display_bad_boxes or not badboxes),
					"never": False
				}.get(self.caller.hide_panel_level, False)

				if hide_panel:
					# hide the build panel (ST2 api is not thread save)
					if _ST3:
						self.caller.window.run_command("hide_panel", {"panel": "output.latextools"})
					else:
						sublime.set_timeout(lambda: self.caller.window.run_command("hide_panel", {"panel": "output.latextools"}), 10)
					message = "build completed"
					if errors:
						message += " with errors"
					if warnings:
						if errors:
							if badboxes and self.caller.display_bad_boxes:
								message += ","
							else:
								message += " and"
						else:
							message += " with"
						message += " warnings"
					if badboxes and self.caller.display_bad_boxes:
						if errors or warnings:
							message += " and"
						else:
							message += " with"
						message += " bad boxes"

					if _ST3:
						sublime.status_message(message)
					else:
						sublime.set_timeout(lambda: sublime.status_message(message), 10)
			except Exception as e:
				# dumpt exception to console
				traceback.print_exc()

				content = ["", ""]
				content.append(
					"LaTeXTools could not parse the TeX log file {0}".format(
						log_file
					)
				)
				content.append("(actually, we never should have gotten here)")
				content.append("")
				content.append("Python exception: {0!r}".format(e))
				content.append("")
				content.append(
					"The full error description can be found on the console."
				)
				content.append("Please let us know on GitHub. Thanks!")

			self.caller.output(content)
			self.caller.output("\n\n[Done!]\n")
			self.caller.finish(len(errors) == 0)

	def handle_std_outputs(self, out, err):
		content = ['']
		if out is not None:
			content.extend(['Output from compilation:', '', out.decode('utf-8')])
		if err is not None:
			content.extend(['Errors from compilation:', '', err.decode('utf-8')])
		self.caller.output(content)
		# if we got here, there shouldn't be a PDF at all
		self.caller.finish(False)

# Actual Command

class make_pdfCommand(sublime_plugin.WindowCommand):

	def __init__(self, *args, **kwargs):
		sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)
		self.proc = None
		self.proc_lock = threading.Lock()

	def run(self, cmd="", file_regex="", path=""):
		
		# Try to handle killing
		with self.proc_lock:
			if self.proc: # if we are running, try to kill running process
				self.output("\n\n### Got request to terminate compilation ###")
				if sublime.platform() == 'windows':
					startupinfo = subprocess.STARTUPINFO()
					startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
					subprocess.call(
						'taskkill /t /f /pid {pid}'.format(pid=self.proc.pid),
						startupinfo=startupinfo,
						shell=True
					)
				else:
					os.killpg(self.proc.pid, signal.SIGTERM)
				self.proc = None
				return
			else: # either it's the first time we run, or else we have no running processes
				self.proc = None

		view = self.view = self.window.active_view()

		if view.is_dirty():
			print ("saving...")
			view.run_command('save')  # call this on view, not self.window

		if view.file_name() is None:
			sublime.error_message('Please save your file before attempting to build.')
			return

		self.file_name = getTeXRoot.get_tex_root(view)
		if not os.path.isfile(self.file_name):
			sublime.error_message(self.file_name + ": file not found.")
			return

		self.tex_base = get_jobname(view)
		self.tex_dir = os.path.dirname(self.file_name)

		if not is_tex_file(self.file_name):
			sublime.error_message("%s is not a TeX source file: cannot compile." % (os.path.basename(view.file_name()),))
			return

		# Output panel: from exec.py
		if not hasattr(self, 'output_view'):
			self.output_view = self.window.get_output_panel("latextools")

		output_view_settings = self.output_view.settings()
		output_view_settings.set("result_file_regex", file_regex)
		output_view_settings.set("result_base_dir", self.tex_dir)
		output_view_settings.set("line_numbers", False)
		output_view_settings.set("gutter", False)
		output_view_settings.set("scroll_past_end", False)

		if get_setting("highlight_build_panel", True):
			self.output_view.set_syntax_file(
				"Packages/LaTeXTools/LaTeXTools Console.hidden-tmLanguage"
			)
			output_view_settings.set(
				"color_scheme",
				sublime.load_settings('Preferences.sublime-settings').
				get('color_scheme')
			)

		self.output_view.set_read_only(True)

		# Dumb, but required for the moment for the output panel to be picked
        # up as the result buffer
		self.window.get_output_panel("latextools")

		self.hide_panel_level = get_setting("hide_build_panel", "never")
		if self.hide_panel_level != "always":
			self.window.run_command("show_panel", {"panel": "output.latextools"})

		self.plat = sublime.platform()
		if self.plat == "osx":
			self.encoding = "UTF-8"
		elif self.plat == "windows":
			self.encoding = getOEMCP()
		elif self.plat == "linux":
			self.encoding = "UTF-8"
		else:
			sublime.error_message("Platform as yet unsupported. Sorry!")
			return

		# Get platform settings, builder, and builder settings
		platform_settings  = get_setting(self.plat, {})
		builder_name = get_setting("builder", "traditional")
		self.display_bad_boxes = get_setting("display_bad_boxes", False)
		# This *must* exist, so if it doesn't, the user didn't migrate
		if builder_name is None:
			sublime.error_message("LaTeXTools: you need to migrate your preferences. See the README file for instructions.")
			self.window.run_command('hide_panel', {"panel": "output.latextools"})
			return

		# Default to 'traditional' builder
		if builder_name in ['', 'default']:
			builder_name = 'traditional'

		# this is to convert old-style names (e.g. AReallyLongName)
		# to new style plugin names (a_really_long_name)
		builder_name = _classname_to_internal_name(builder_name)

		builder_settings = get_setting("builder_settings", {})

		# parse root for any %!TEX directives
		tex_directives = parse_tex_directives(
			self.file_name,
			multi_values=['options'],
			key_maps={'ts-program': 'program'}
		)

		# determine the engine
		engine = tex_directives.get('program',
			builder_settings.get("program", "pdflatex"))

		engine = engine.lower()

		# Sanity check: if "strange" engine, default to pdflatex (silently...)
		if engine not in [
			'pdflatex', "pdftex", 'xelatex', 'xetex', 'lualatex', 'luatex'
		]:
			engine = 'pdflatex'

		options = builder_settings.get("options", [])
		if isinstance(options, strbase):
			options = [options]

		if 'options' in tex_directives:
			options.extend(tex_directives['options'])

		# filter out --aux-directory and --output-directory options which are
		# handled separately
		options = [opt for opt in options if (
			not opt.startswith('--aux-directory') and
			not opt.startswith('--output-directory') and
			not opt.startswith('--jobname')
		)]

		self.aux_directory = get_aux_directory(self.file_name)
		self.output_directory = get_output_directory(self.file_name)

		# Read the env option (platform specific)
		builder_platform_settings = builder_settings.get(self.plat)
		if builder_platform_settings:
			self.env = builder_platform_settings.get("env", None)
		else:
			self.env = None

		# Now actually get the builder
		builder_path = get_setting("builder_path", "")  # relative to ST packages dir!

		# Safety check: if we are using a built-in builder, disregard
		# builder_path, even if it was specified in the pref file
		if builder_name in ['simple', 'traditional', 'script', 'basic']:
			builder_path = None

		if builder_path:
			bld_path = os.path.join(sublime.packages_path(), builder_path)
			add_plugin_path(bld_path)

		try:
			builder = get_plugin('{0}_builder'.format(builder_name))
		except NoSuchPluginException:
			sublime.error_message("Cannot find builder " + builder_name + ".\n" \
							      "Check your LaTeXTools Preferences")
			self.window.run_command('hide_panel', {"panel": "output.latextools"})
			return

		print(repr(builder))
		self.builder = builder(
			self.file_name,
			self.output,
			engine,
			options,
			self.aux_directory,
			self.output_directory,
			self.tex_base,
			tex_directives,
			builder_settings,
			platform_settings
		)

		# Now get the tex binary path from prefs, change directory to
		# that of the tex root file, and run!
		self.path = platform_settings['texpath']
		CmdThread(self).start()
		print(threading.active_count())


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
		self.output_view.run_command("do_finish_edit")
		# can_switch_to_pdf indicates a pdf should've been created
		if can_switch_to_pdf:
			# if using output_directory, follow the copy_output_on_build setting
			# files are copied to the same directory as the main tex file
			if self.output_directory is not None:
				copy_on_build = get_setting('copy_output_on_build', True) or True
				if copy_on_build is True:
					shutil.copy2(
						os.path.join(
							self.output_directory,
							self.tex_base + u'.pdf'
						),
						os.path.dirname(self.file_name)
					)
				elif isinstance(copy_on_build, list):
					for ext in copy_on_build:
						shutil.copy2(
							os.path.join(
								self.output_directory,
								self.tex_base + ext
							),
							os.path.dirname(self.file_name)
						)

			if get_setting('open_pdf_on_build', True):
				self.view.run_command("jump_to_pdf", {"from_keybinding": False})


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

def plugin_loaded():
	# load the plugins from the builders dir
	ltt_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'builders')
	# ensure that pdfBuilder is loaded first as otherwise, the other builders
	# will not be registered as plugins
	add_plugin_path(os.path.join(ltt_path, 'pdfBuilder.py'))
	add_plugin_path(ltt_path)

	# load any .latextools_builder files from User directory
	add_plugin_path(
		os.path.join(sublime.packages_path(), 'User'),
		'*.latextools_builder'
	)

if not _ST3:
	plugin_loaded()
