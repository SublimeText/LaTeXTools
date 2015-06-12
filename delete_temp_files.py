# ST2/ST3 compat
from __future__ import print_function
import sublime
if sublime.version() < '3000':
	_ST3 = False
	# we are on ST2 and Python 2.X
	import getTeXRoot
else:
	_ST3 = True
	from . import getTeXRoot


import sublime_plugin
import os

class Delete_temp_filesCommand(sublime_plugin.WindowCommand):
	def run(self):
		# Retrieve file and dirname.
		view = self.window.active_view()
		self.file_name = getTeXRoot.get_tex_root(view)
		if not os.path.isfile(self.file_name):
			sublime.error_message(self.file_name + ": file not found.")
			return

		self.path = os.path.dirname(self.file_name)

		# Delete the files.
		temp_exts = set(['.blg','.bbl','.aux','.log','.brf','.nlo','.out','.dvi','.ps',
			'.lof','.toc','.fls','.fdb_latexmk','.pdfsync','.synctex.gz','.ind','.ilg','.idx'])

		for dir_path, dir_names, file_names in os.walk(self.path):
			for file_name in file_names:
				file_base, file_ext = os.path.splitext(file_name)
				if file_ext in temp_exts:
					file_name_to_del = os.path.join(dir_path, file_name)
					if os.path.exists(file_name_to_del):
						os.remove(file_name_to_del)

		sublime.status_message("Deleted temp files")