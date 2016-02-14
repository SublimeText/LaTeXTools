# ST2/ST3 compat
from __future__ import print_function

import os
import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	from latextools_utils.is_tex_file import is_tex_file
	from latextools_utils.sublime_utils import get_project_file_name
	from latextools_utils import parse_tex_directives
else:
	_ST3 = True
	from .latextools_utils.is_tex_file import is_tex_file
	from .latextools_utils.sublime_utils import get_project_file_name
	from .latextools_utils import parse_tex_directives


# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file or None (if there is no root file,
# and the current buffer is an unnamed unsaved file)

# Contributed by Sam Finn
def get_tex_root(view):
	view_file = view.file_name()
	root = view_file
	directives = parse_tex_directives(view, only_for=['root'])
	try:
		root = directives['root']
	except KeyError:
		pass
	else:
		if not is_tex_file(root):
			root = view_file

		if not os.path.isabs(root) and view_file is not None:
			file_path, _ = os.path.split(view_file)
			root = os.path.normpath(os.path.join(file_path, root))

	if root == view_file:
		root = get_tex_root_from_settings(view)
		if root is not None:
			return root
		return view_file

	return root


def get_tex_root_from_settings(view):
	root = view.settings().get('TEXroot', None)

	if root is not None:
		if os.path.isabs(root):
			if os.path.isfile(root):
				return root
		else:
			proj_file = get_project_file_name(view)

			if proj_file:
				project_dir = os.path.dirname(proj_file)
				root_path = os.path.normpath(os.path.join(project_dir, root))
				if os.path.isfile(root_path):
					return root_path

	return root
