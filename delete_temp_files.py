# ST2/ST3 compat
from __future__ import print_function
import sublime
if sublime.version() < '3000':
	_ST3 = False
	# we are on ST2 and Python 2.X
	import getTeXRoot
	from latextools_utils import cache, get_setting, is_bib_buffer
	from latextools_utils.output_directory import (
		get_aux_directory, get_output_directory
	)
	from latextools_utils.six import get_self
else:
	_ST3 = True
	from . import getTeXRoot
	from .latextools_utils import cache, get_setting, is_bib_buffer
	from .latextools_utils.output_directory import (
		get_aux_directory, get_output_directory
	)
	from .latextools_utils.six import get_self

import sublime_plugin
import os
import shutil

import traceback


class ClearLocalLatexCacheCommand(sublime_plugin.WindowCommand):

	def is_visible(self, *args):
		view = self.window.active_view()
		return bool(view.score_selector(0, "text.tex.latex"))

	def run(self):
		view = self.window.active_view()

		if view is None or not bool(view.score_selector(0, "text.tex.latex")):
			return

		tex_root = getTeXRoot.get_tex_root(view)
		if tex_root:
			# clear the cache
			try:
				cache.LocalCache(tex_root).invalidate()
			except:
				print('Error while trying to delete local cache')
				traceback.print_exc()


class ClearBibliographyCacheCommand(sublime_plugin.WindowCommand):

	def is_visible(self, *args):
		view = self.window.active_view()
		return (
			bool(view.score_selector(0, "text.tex.latex")) or
			is_bib_buffer(view)
		)

	def run(self):
		view = self.window.active_view()

		if view is None:
			return

		is_tex_file = bool(view.score_selector(0, "text.tex.latex"))
		if not (is_tex_file or is_bib_buffer(view)):
			return

		# find the instance of LatextoolsCacheUpdateListener, if any
		cache_listener = None
		for callback in sublime_plugin.all_callbacks['on_close']:
			try:
				instance = get_self(callback)
			except:
				continue

			if instance.__class__.__name__ == 'LatextoolsCacheUpdateListener':
				cache_listener = instance
				break

		if cache_listener is None:
			return

		# if run from a TeX file, clear all bib caches associated with this
		# document
		if is_tex_file:
			tex_root = getTeXRoot.get_tex_root(view)
			for bib_cache in cache_listener._BIB_CACHES.get(tex_root, []):
				bib_cache.invalidate()
		# if run from a bib file, clear all bib caches that reflect this
		# document
		else:
			file_name = view.file_name()
			if not file_name:
				return

			for bib_caches in cache_listener._BIB_CACHES.values():
				for bib_cache in bib_caches:
					if bib_cache.bib_file == file_name:
						bib_cache.invalidate()


class DeleteTempFilesCommand(sublime_plugin.WindowCommand):

	def is_visible(self, *args):
		view = self.window.active_view()
		return bool(view.score_selector(0, "text.tex.latex"))

	def run(self):
		# Retrieve root file and dirname.
		view = self.window.active_view()

		root_file = getTeXRoot.get_tex_root(view)
		if root_file is None:
			msg = \
				'Could not find TEX root. Please ensure that either you ' + \
				'have configured a TEX root in your project settings or ' + \
				'have a LaTeX document open.'
			sublime.status_message(msg)
			print(msg)
			return

		if not os.path.isfile(root_file):
			message = "Could not find TEX root {0}.".format(root_file)
			sublime.status_message(message)
			print(message)
			return

		# clear the cache
		try:
			cache.LocalCache(root_file).invalidate()
		except:
			print('Error while trying to delete local cache')
			traceback.print_exc()

		aux_directory, aux_directory_setting = get_aux_directory(
			view, return_setting=True
		)

		output_directory, output_directory_setting = get_output_directory(
			view, return_setting=True
		)

		if aux_directory is not None:
			# we cannot delete the output directory on Windows in case
			# Sumatra is holding a reference to it
			if (
				sublime.platform() != 'windows' or
				aux_directory != output_directory
			):
				if aux_directory_setting.startswith('<<'):
					self._rmtree(aux_directory)
				else:
					self.delete_temp_files(aux_directory)

		if output_directory is not None:
			if output_directory_setting.startswith('<<'):
				# we cannot delete the output directory on Windows in case
				# Sumatra is holding a reference to it
				if sublime.platform() == 'windows':
					self._clear_dir(output_directory)
				else:
					self._rmtree(output_directory)
			else:
				self.delete_temp_files(output_directory)
		else:
			# if there is no output directory, we may need to clean files
			# in the main directory, even if aux_directory is used
			self.delete_temp_files(os.path.dirname(root_file))

		sublime.status_message("Deleted temp files")

	def delete_temp_files(self, path):
		# Load the files to delete from the settings
		temp_files_exts = get_setting(
			'temp_files_exts',
			['.blg', '.bbl', '.aux', '.log', '.brf', '.nlo', '.out', '.dvi',
				'.ps', '.lof', '.toc', '.fls', '.fdb_latexmk', '.pdfsync',
				'.synctex.gz', '.ind', '.ilg', '.idx']
		)

		ignored_folders = get_setting(
			'temp_files_ignored_folders',
			['.git', '.svn', '.hg']
		)

		ignored_folders = set(ignored_folders)

		for dir_path, dir_names, file_names in os.walk(path):
			dir_names[:] = [d for d in dir_names if d not in ignored_folders]
			for file_name in file_names:
				for ext in temp_files_exts:
					if file_name.endswith(ext):
						self._rmfile(os.path.join(dir_path, file_name))
						# exit extension
						break

	def _rmtree(self, path):
		if os.path.exists(path):
			try:
				shutil.rmtree(path)
			except OSError:
				if os.path.exists(path):
					# report the exception if the folder didn't end up deleted
					traceback.print_exc()

	def _rmfile(self, path):
		if os.path.exists(path):
			try:
				os.remove(path)
			except OSError:
				if os.path.exists(path):
					# basically here for locked files in Windows,
					# but who knows what we might find?
					print('Error while trying to delete {0}'.format(path))
					traceback.print_exc()

	def _clear_dir(self, path):
		for root, directories, file_names in os.walk(path):
			for directory in directories:
				self._rmtree(os.path.join(root, directory))
			for file_name in file_names:
				self._rmfile(os.path.join(root, file_name))
