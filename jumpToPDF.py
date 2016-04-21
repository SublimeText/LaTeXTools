# ST2/ST3 compat
from __future__ import print_function 
import sublime
import sys
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
	from latextools_utils.is_tex_file import is_tex_file
	from latextools_utils import get_setting
	from latextools_utils.sublime_utils import get_sublime_exe
	from latextools_plugin import (
		get_plugin, add_plugin_path, NoSuchPluginException,
		add_whitelist_module
	)
else:
	_ST3 = True
	from . import getTeXRoot
	from .latextools_utils.is_tex_file import is_tex_file
	from .latextools_utils import get_setting
	from .latextools_utils.sublime_utils import get_sublime_exe
	from .latextools_plugin import (
		get_plugin, add_plugin_path, NoSuchPluginException,
		add_whitelist_module
	)

import sublime_plugin, os.path, subprocess, time
import traceback
import re

SUBLIME_VERSION = re.compile(r'Build (\d{4})', re.UNICODE)
DEFAULT_VIEWERS = {
	'linux': 'evince',
	'osx': 'skim',
	'windows': 'sumatra'
}


class NoViewerException(Exception):
	pass


# common viewer logic
def get_viewer():
	default_viewer = DEFAULT_VIEWERS.get(sublime.platform(), None)
	viewer_name = get_setting('viewer', default_viewer)
	if viewer_name in ['', 'default']:
		viewer_name = default_viewer

	if viewer_name is None:
		sublime.error_message('No viewer could be found for your platform. '
				'Please configure the "viewer" setting in your LaTeXTools '
				'Preferences')
		raise NoViewerException()

	try:
		viewer = get_plugin(viewer_name + '_viewer')
	except NoSuchPluginException:
		sublime.error_message('Cannot find viewer ' + viewer_name + '.\n' +
								'Please check your LaTeXTools Preferences.')
		raise NoViewerException()

	print(repr(viewer))
	
	# assume no-args constructor
	viewer = viewer()

	if not viewer.supports_platform(sublime.platform()):
		sublime.error_message(viewer_name + ' does not support the ' +
								'current platform. Please change the viewer in ' +
								'your LaTeXTools Preferences.')
		raise NoViewerException()

	return viewer


def focus_st():
	sublime_command = get_sublime_exe()

	if sublime_command is not None:
		platform = sublime.platform()
		# TODO: this does not work on OSX
		# and I don't know why...
		if platform == 'osx':
			return

		plat_settings = get_setting(platform, {})
		wait_time = plat_settings.get('keep_focus_delay', 0.5)

		def keep_focus():
			startupinfo = None
			shell = False
			if platform == 'windows':
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				shell = _ST3

			subprocess.Popen(
				sublime_command,
				startupinfo=startupinfo,
				shell=shell,
				env=os.environ
			)

		if hasattr(sublime, 'set_async_timeout'):
			sublime.set_async_timeout(keep_focus, int(wait_time * 1000))
		else:
			sublime.set_timeout(keep_focus, int(wait_time * 1000))


# Jump to current line in PDF file
# NOTE: must be called with {"from_keybinding": <boolean>} as arg
class JumpToPdf(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		# Check prefs for PDF focus and sync
		keep_focus = args.get('keep_focus', get_setting('keep_focus', True))
		forward_sync = args.get('forward_sync', get_setting('forward_sync', True))

		# If invoked from keybinding, we sync
		# Rationale: if the user invokes the jump command, s/he wants to see the result of the compilation.
		# If the PDF viewer window is already visible, s/he probably wants to sync, or s/he would have no
		# need to invoke the command. And if it is not visible, the natural way to just bring up the
		# window without syncing is by using the system's window management shortcuts.
		# As for focusing, we honor the toggles / prefs.
		from_keybinding = args.pop("from_keybinding", False)
		if from_keybinding:
			forward_sync = True
		print (from_keybinding, keep_focus, forward_sync)

		if not is_tex_file(self.view.file_name()):
			sublime.error_message("%s is not a TeX source file: cannot jump." % (os.path.basename(view.fileName()),))
			return
		
		root = getTeXRoot.get_tex_root(self.view)
		print ("!TEX root = ", repr(root) ) # need something better here, but this works.
		rootName, rootExt = os.path.splitext(root)
		pdffile = rootName + u'.pdf'
		(line, col) = self.view.rowcol(self.view.sel()[0].end())
		print ("Jump to: ", line,col)
		# column is actually ignored up to 0.94
		# HACK? It seems we get better results incrementing line
		line += 1

		# issue #625: we need to pass the path to the file to the viewer when
		# there are files in subfolders of the main folder.
		# Thanks rstein and arahlin for this code!
		srcfile = self.view.file_name()

		try:
			viewer = get_viewer()
		except NoViewerException:
			return

		if forward_sync:
			try:
				viewer.forward_sync(pdffile, srcfile, line, col, keep_focus=keep_focus)
			except (AttributeError, NotImplementedError):
				try:
					viewer.view_file(pdffile, keep_focus=keep_focus)
				except (AttributeError, NotImplementedError):
					traceback.print_exc()
					sublime.error_message('Viewer ' + viewer_name + 
						' does not appear to be a proper LaTeXTools viewer plugin.' +
						' Please contact the plugin author.')
					return
		else:
			try:
				viewer.view_file(pdffile, keep_focus=keep_focus)
			except (AttributeError, NotImplementedError):
				traceback.print_exc()
				sublime.error_message('Viewer ' + viewer_name + 
					' does not appear to be a proper LaTeXTools viewer plugin.' +
					' Please contact the plugin author.')
				return

		if keep_focus:
			try:
				if viewer.supports_keep_focus():
					return
			except (AttributeError, NotImplementedError):
				pass

			focus_st()


class ViewPdf(sublime_plugin.WindowCommand):
	def run(self, **args):
		pdffile = None
		if 'file' in args:
			pdffile = args.pop('file', None)
		else:
			view = self.window.active_view()
			root = getTeXRoot.get_tex_root(view)
			print("!TEX root = ", repr(root))
			pdffile = os.path.splitext(root)[0] + '.pdf'

		# since we potentially accept an argument, add some extra
		# safety checks
		if pdffile is None:
			print('No PDF file found.')
			return
		elif not os.path.exists(pdffile):
			print('PDF file "' + pdffile + '" does not exist.')
			sublime.error_message(
				'PDF file "' + pdffile + '" does not exist.'
			)
			return

		try:
			viewer = get_viewer()
		except NoViewerException:
			return

		try:
			viewer.view_file(pdffile, keep_focus=False)
		except (AttributeError, NotImplementedError):
			traceback.print_exception()
			sublime.error_message('Viewer ' + viewer_name + 
					' does not appear to be a proper LaTeXTools viewer plugin.' +
					' Please contact the plugin author.')
			return
		

def plugin_loaded():
	add_whitelist_module('latextools_utils')

	viewers_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'viewers')
	# ensure that base_viewer is loaded first so that other viewers are registered
	# as plugins
	add_plugin_path(os.path.join(viewers_path, 'base_viewer.py'))
	add_plugin_path(viewers_path)

	# load any .latextools_viewer files from the Uer directory
	add_plugin_path(
		os.path.join(sublime.packages_path(), 'User'),
		'*.latextools_viewer'
	)

if not _ST3:
	plugin_loaded()
