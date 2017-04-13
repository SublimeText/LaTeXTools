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
	from latextools_utils.external_command import (
		execute_command, external_command, get_texpath, update_env
	)
	from latextools_utils.output_directory import (
		get_aux_directory, get_output_directory, get_jobname
	)
	from latextools_utils.progress_indicator import ProgressIndicator
	from latextools_utils.sublime_utils import (
		get_project_file_name, parse_json_with_comments
	)
	from latextools_utils.utils import run_on_main_thread

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
	from .latextools_utils.external_command import (
		execute_command, external_command, get_texpath, update_env
	)
	from .latextools_utils.output_directory import (
		get_aux_directory, get_output_directory, get_jobname
	)
	from .latextools_utils.progress_indicator import ProgressIndicator
	from .latextools_utils.sublime_utils import (
		get_project_file_name, parse_json_with_comments
	)
	from .latextools_utils.utils import run_on_main_thread

	strbase = str
	long = int

import sublime_plugin
import sys
import os
import signal
import threading
import functools
import subprocess
import types
import traceback
import shutil
import glob
import re

DEBUG = False

_HAS_PHANTOMS = sublime.version() >= "3118"

if _HAS_PHANTOMS:
	import html

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


class LatextoolsBuildSelector(sublime_plugin.WindowCommand):

	# stores last settings for build
	WINDOWS = {}

	if _ST3:
		def load_build_system(self, build_system):
			build_system = sublime.load_resource(build_system)
	else:
		def load_build_system(self, build_system):
			build_system = os.path.normpath(
				build_system.replace('Packages', sublime.packages_path())
			)

			return self.parse_json_with_comments(build_system)

	def run(self, select=False):
		select = False if select not in (True, False) else select
		view = self.view = self.window.active_view()
		if not select:
			window_settings = self.WINDOWS.get(self.window.id(), {})
			build_system = window_settings.get('build_system')

			if build_system:
				build_variant = window_settings.get('build_variant', '')
				self.run_build(build_system, build_variant)
				return

		# no previously selected build system or select is True
		# find all .sublime-build files
		if _ST3:
			sublime_build_files = sublime.find_resources('*.sublime-build')
			project_settings = self.window.project_data()
		else:
			sublime_build_files = glob.glob(os.path.join(
				sublime.packages_path(), '*', '*.sublime-build'
			))
			project_file_name = get_project_file_name(view)
			if project_file_name is not None:
				try:
					project_settings = \
						parse_json_with_comments(project_file_name)
				except:
					print('Error parsing project file')
					traceback.print_exc()
					project_settings = {}
			else:
				project_settings = {}

		builders = []
		for i, build_system in enumerate(
			project_settings.get('build_systems', [])
		):
			if (
				'selector' not in build_system or
				view.score_selector(0, project_settings['selector']) > 0
			):
				try:
					build_system['name']
				except:
					print('Could not determine name for build system {0}'.format(
						build_system
					))
					continue

				build_system['index'] = i
				builders.append(build_system)

		for filename in sublime_build_files:
			try:
				sublime_build = parse_json_with_comments(filename)
			except:
				print(u'Error parsing file {0}'.format(filename))
				continue

			if (
				'selector' not in sublime_build or
				view.score_selector(0, sublime_build['selector']) > 0
			):
				sublime_build['file'] = filename.replace(
					sublime.packages_path(), 'Packages', 1
				).replace(os.path.sep, '/')

				sublime_build['name'] = os.path.splitext(
					os.path.basename(sublime_build['file'])
				)[0]

				builders.append(sublime_build)

		formatted_entries = []
		build_system_variants = []
		for builder in builders:
			build_system_name = builder['name']
			build_system_internal_name = builder.get(
				'index', builder.get('file')
			)

			formatted_entries.append(build_system_name)
			build_system_variants.append((build_system_internal_name, ''))

			for variant in builder.get('variants', []):
				try:
					formatted_entries.append(
						"{0} - {1}".format(
							build_system_name,
							variant['name']
						)
					)
				except KeyError:
					continue

				build_system_variants.append(
					(build_system_internal_name, variant['name'])
				)

		entries = len(formatted_entries)
		if entries == 0:
			self.window.run_command('build')
		elif entries == 1:
			build_system, build_variant = build_system_variants[0]
			self.WINDOWS[self.window.id()] = {
				'build_system': build_system,
				'build_variant': build_variant
			}
			self.run_build(build_system, build_variant)
		else:
			def on_done(index):
				# cancel
				if index == -1:
					return

				build_system, build_variant = build_system_variants[index]
				self.WINDOWS[self.window.id()] = {
					'build_system': build_system,
					'build_variant': build_variant
				}
				self.run_build(build_system, build_variant)

			self.window.show_quick_panel(formatted_entries, on_done)

	def run_build(self, build_system, build_variant):
		if build_system.isdigit():
			self.window.run_command(
				'set_build_system', {'index': int(build_system)}
			)
		else:
			self.window.run_command(
				'set_build_system', {'file': build_system}
			)

		if build_variant:
			self.window.run_command('build', {'variant': build_variant})
		else:
			self.window.run_command('build')


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

		env = dict(os.environ)
		if self.caller.path:
			env['PATH'] = self.caller.path

		# Handle custom env variables
		if self.caller.env:
			update_env(env, self.caller.env)

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
						proc = external_command(
							cmd,
							env=env,
							use_texpath=False,
							stdout=subprocess.PIPE,
							stderr=subprocess.STDOUT,
							preexec_fn=os.setsid if self.caller.plat != 'windows' else None,
							cwd=self.caller.tex_dir
						)
					except:
						self.caller.show_output_panel()
						self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
						self.caller.output("Attempted command:")
						self.caller.output(" ".join(cmd))
						self.caller.output("\nBuild engine: " + self.caller.builder.name)
						self.caller.proc = None
						traceback.print_exc()
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
			self.caller.show_output_panel()
			self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
			self.caller.output("\nBuild engine: " + self.caller.builder.name)
			self.caller.proc = None
			traceback.print_exc()
			return

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
			traceback.print_exc()

			self.caller.show_output_panel()

			content = ['', 'Could not read log file {0}.log'.format(
				self.caller.tex_base
			), '']
			if out is not None:
				content.extend(['Output from compilation:', '', out.decode('utf-8')])
			if err is not None:
				content.extend(['Errors from compilation:', '', err.decode('utf-8')])
			self.caller.output(content)
			# if we got here, there shouldn't be a PDF at all
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

				show_panel = {
					"always": False,
					"no_errors": bool(errors),
					"no_warnings": bool(errors or warnings),
					"no_badboxes": bool(
						errors or warnings or
						(self.caller.display_bad_boxes and badboxes)),
					"never": True
				}.get(self.caller.hide_panel_level, bool(errors or warnings))

				if show_panel:
					self.caller.progress_indicator.success_message = "Build completed"
					self.caller.show_output_panel(force=True)
				else:
					message = "Build completed"
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

					self.caller.progress_indicator.success_message = message
			except Exception as e:
				self.caller.show_output_panel()
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

				traceback.print_exc()

			self.caller.output(content)
			self.caller.output("\n\n[Done!]\n")

			if _HAS_PHANTOMS:
				self.caller.errors = locals().get("errors", [])
				self.caller.warnings = locals().get("warnings", [])
				self.caller.badboxes = locals().get("badboxes", [])

			self.caller.finish(len(errors) == 0)

# Actual Command

class make_pdfCommand(sublime_plugin.WindowCommand):

	errs_by_file = {}
	phantom_sets_by_buffer = {}
	show_errors_inline = True
	errors = []
	warnings = []
	badboxes = []


	def __init__(self, *args, **kwargs):
		sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)
		self.proc = None
		self.proc_lock = threading.Lock()

	# **kwargs is unused but there so run can safely ignore any unknown
	# parameters
	def run(
		self, file_regex="", program=None, builder=None, command=None,
		env=None, path=None, script_commands=None, update_phantoms_only=False,
		hide_phantoms_only=False, **kwargs
	):
		if update_phantoms_only:
			if self.show_errors_inline:
				self.update_phantoms()
			return

		if hide_phantoms_only:
			self.hide_phantoms()
			return

		# Try to handle killing
		with self.proc_lock:
			if self.proc:  # if we are running, try to kill running process
				self.output("\n\n### Got request to terminate compilation ###")
				try:
					if sublime.platform() == 'windows':
						execute_command(
							'taskkill /t /f /pid {pid}'.format(pid=self.proc.pid),
							use_texpath=False
						)
					else:
						os.killpg(self.proc.pid, signal.SIGTERM)
				except:
					print('Exception occurred while killing build')
					traceback.print_exc()

				self.proc = None
				return
			else: # either it's the first time we run, or else we have no running processes
				self.proc = None

		view = self.view = self.window.active_view()

		if _HAS_PHANTOMS:
			self.hide_phantoms()
			pref_settings = sublime.load_settings("Preferences.sublime-settings")
			self.show_errors_inline = pref_settings.get("show_errors_inline", True)

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

		if get_setting("highlight_build_panel", True, view=view):
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

		self.hide_panel_level = get_setting(
			"hide_build_panel", "no_warnings", view=view)
		if self.hide_panel_level == "never":
			self.show_output_panel(force=True)

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
		platform_settings = get_setting(self.plat, {}, view=view)
		self.display_bad_boxes = get_setting(
			"display_bad_boxes", False, view=view)

		if builder is not None:
			builder_name = builder
		else:
			builder_name = get_setting("builder", "traditional", view=view)

		# Default to 'traditional' builder
		if builder_name in ['', 'default']:
			builder_name = 'traditional'

		# this is to convert old-style names (e.g. AReallyLongName)
		# to new style plugin names (a_really_long_name)
		builder_name = _classname_to_internal_name(builder_name)

		builder_settings = get_setting("builder_settings", {}, view=view)

		# override the command
		if command is not None:
			builder_settings.set("command", command)

		# parse root for any %!TEX directives
		tex_directives = parse_tex_directives(
			self.file_name,
			multi_values=['options'],
			key_maps={'ts-program': 'program'}
		)

		# determine the engine
		if program is not None:
			engine = program
		else:
			engine = tex_directives.get(
				'program',
				builder_settings.get("program", "pdflatex")
			)

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

		self.aux_directory = get_aux_directory(view)
		self.output_directory = get_output_directory(view)

		# Read the env option (platform specific)
		builder_platform_settings = builder_settings.get(self.plat, {})

		if env is not None:
			self.env = env
		elif builder_platform_settings:
			self.env = builder_platform_settings.get("env", None)
		else:
			self.env = None

		# Safety check: if we are using a built-in builder, disregard
		# builder_path, even if it was specified in the pref file
		if builder_name in ['simple', 'traditional', 'script', 'basic']:
			builder_path = None
		else:
			# relative to ST packages dir!
			builder_path = get_setting("builder_path", "", view=view)

		if builder_path:
			bld_path = os.path.join(sublime.packages_path(), builder_path)
			add_plugin_path(bld_path)

		try:
			builder = get_plugin('{0}_builder'.format(builder_name))
		except NoSuchPluginException:
			try:
				builder = get_plugin(builder_name)
			except NoSuchPluginException:
				sublime.error_message(
					"Cannot find builder {0}.\n"
					"Check your LaTeXTools Preferences".format(builder_name)
				)
				self.window.run_command(
					'hide_panel', {"panel": "output.latextools"})
				return

		if builder_name == 'script' and script_commands:
			builder_platform_settings['script_commands'] = script_commands
			builder_settings[self.plat] = builder_platform_settings

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
		if path is not None:
			self.path = path
		else:
			self.path = get_texpath() or os.environ['PATH']

		thread = CmdThread(self)
		thread.start()
		print(threading.active_count())

		# setup the progress indicator
		display_message_length = long(
			get_setting(
				'build_finished_message_length', 2.0, view=view) * 1000)
		# NB CmdThread will change the success message
		self.progress_indicator = ProgressIndicator(
			thread, 'Building', 'Build failed',
			display_message_length=display_message_length
		)


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

	def show_output_panel(self, force=False):
		if force or self.hide_panel_level != 'always':
			f = functools.partial(
				self.window.run_command,
				"show_panel", {"panel": "output.latextools"}
			)
			run_on_main_thread(f, default_value=None)

	# Also from exec.py
	# Set the selection to the start of the output panel, so next_result works
	# Then run viewer

	def finish(self, can_switch_to_pdf):
		sublime.set_timeout(functools.partial(self.do_finish, can_switch_to_pdf), 0)

	def do_finish(self, can_switch_to_pdf):
		self.output_view.run_command("do_finish_edit")

		if _HAS_PHANTOMS and self.show_errors_inline:
			self.create_errs_by_file()
			self.update_phantoms()

		# can_switch_to_pdf indicates a pdf should've been created
		if can_switch_to_pdf:
			# if using output_directory, follow the copy_output_on_build setting
			# files are copied to the same directory as the main tex file
			if self.output_directory is not None:
				copy_on_build = get_setting(
					'copy_output_on_build', True, view=self.view)
				if copy_on_build is None or copy_on_build is True:
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

			if get_setting('open_pdf_on_build', True, view=self.view):
				self.view.run_command("jump_to_pdf", {"from_keybinding": False})

	if _HAS_PHANTOMS:
		def _find_errors(self, errors, error_class):
			for line in errors:
				m = self.file_regex.search(line)
				if not m:
					continue
				groups = m.groups()
				if len(groups) == 4:
					file, line, column, text = groups
				else:
					continue
				if line is None:
					continue
				line = int(line)
				column = int(column) if column else 0
				if file not in self.errs_by_file:
					self.errs_by_file[file] = []
				self.errs_by_file[file].append((line, column, text, error_class))

		def create_errs_by_file(self):
			file_regex = self.output_view.settings().get("result_file_regex")
			if not file_regex:
				return
			self.errs_by_file = {}
			try:
				self.file_regex = re.compile(file_regex, re.MULTILINE)
			except:
				print("Cannot compile file regex.")
				return
			lt_settings = sublime.load_settings("LaTeXTools.sublime-settings")
			level_name = lt_settings.get("show_error_phantoms")
			level = {
				"none": 0,
				"errors": 1,
				"warnings": 2,
				"badboxes": 3
			}.get(level_name, 2)

			if level >= 1:
				self._find_errors(self.errors, "error")
			if level >= 2:
				self._find_errors(self.warnings, "warning")
			if level >= 3:
				self._find_errors(self.badboxes, "warning badbox")

		def update_phantoms(self):
			stylesheet = """
				<style>
					div.lt-error {
						padding: 0.4rem 0 0.4rem 0.7rem;
						margin: 0.2rem 0;
						border-radius: 2px;
					}
					div.lt-error span.message {
						padding-right: 0.7rem;
					}
					div.lt-error a {
						text-decoration: inherit;
						padding: 0.35rem 0.7rem 0.45rem 0.8rem;
						position: relative;
						bottom: 0.05rem;
						border-radius: 0 2px 2px 0;
						font-weight: bold;
					}
					html.dark div.lt-error a {
						background-color: #00000018;
					}
					html.light div.lt-error a {
						background-color: #ffffff18;
					}
				</style>
			"""

			for file, errs in self.errs_by_file.items():
				view = self.window.find_open_file(file)
				if view:

					buffer_id = view.buffer_id()
					if buffer_id not in self.phantom_sets_by_buffer:
						phantom_set = sublime.PhantomSet(view, "lt_exec")
						self.phantom_sets_by_buffer[buffer_id] = phantom_set
					else:
						phantom_set = self.phantom_sets_by_buffer[buffer_id]

					phantoms = []

					for line, column, text, error_class in errs:
						pt = view.text_point(line - 1, column - 1)
						html_text = html.escape(text, quote=False)
						phantom_content = """
							<body id="inline-error">
								{stylesheet} 
								<div class="lt-error {error_class}">
									<span class="message">{html_text}</span>
									<a href="hide">{cancel_char}</a>
								</div>
							</body>
						""".format(cancel_char=chr(0x00D7), **locals())
						phantoms.append(sublime.Phantom(
							sublime.Region(pt, view.line(pt).b),
							phantom_content, sublime.LAYOUT_BELOW,
							on_navigate=self.on_phantom_navigate))

					phantom_set.update(phantoms)

		def hide_phantoms(self):
			for file, errs in self.errs_by_file.items():
				view = self.window.find_open_file(file)
				if view:
					view.erase_phantoms("lt_exec")

			self.errs_by_file = {}
			self.phantom_sets_by_buffer = {}
			self.show_errors_inline = False

		def on_phantom_navigate(self, href):
			self.hide_phantoms()


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

if _HAS_PHANTOMS:
	class BuildPhantomEventListener(sublime_plugin.EventListener):
		def on_load(self, view):
			if not view.score_selector(0, "text.tex"):
				return
			w = view.window()
			if w is not None:
				w.run_command("make_pdf", {"update_phantoms_only": True})


def plugin_loaded():
	# load the plugins from the builders dir
	ltt_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'builders')
	# ensure that pdfBuilder is loaded first as otherwise, the other builders
	# will not be registered as plugins
	add_plugin_path(os.path.join(ltt_path, 'pdfBuilder.py'))
	add_plugin_path(ltt_path)


if not _ST3:
	plugin_loaded()
