# ST2/ST3 compat
from __future__ import print_function
import os
import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	from latextools_utils.is_tex_file import is_tex_file
	from latextools_utils import parse_tex_directives
else:
	_ST3 = True
	from .latextools_utils.is_tex_file import is_tex_file
	from .latextools_utils import parse_tex_directives

# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file or None (if there is no root file,
# and the current buffer is an unnamed unsaved file)

# Contributed by Sam Finn


def get_tex_root(view):
	try:
		root = os.path.abspath(view.settings().get('TEXroot'))
		if os.path.isfile(root):
			print("Main file defined in project settings : " + root)
			return root
	except:
		pass

	view_file = view.file_name()
	root = view_file
	directives = parse_tex_directives(view, only_for=['root'])
	try:
		root = directives['root']
	except KeyError:
		pass
	else:
		if not is_tex_file(root):
			return view_file

		if not os.path.isabs(root) and view_file is not None:
			file_path, _ = os.path.split(view_file)
			root = os.path.normpath(os.path.join(file_path, root))

	return root
