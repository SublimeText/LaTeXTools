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

		self.tex_base, self.tex_ext = os.path.splitext(self.file_name)


		# Delete the files.
		temp_exts = ['.blg','.bbl','.aux','.log','.brf','.nlo','.out','.dvi','.ps',
			'.lof','.toc','.fls','.fdb_latexmk','.pdfsync','.synctex.gz','.ind','.ilg','.idx']

		for temp_ext in temp_exts:
			file_name_to_del = self.tex_base + temp_ext
			#print file_name_to_del
			if os.path.exists(file_name_to_del):
				#print ' deleted '
				os.remove(file_name_to_del)

		sublime.status_message("Deleted the temp files")
		