# ST2/ST3 compat
from __future__ import print_function

import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	from latextools_utils.is_tex_file import get_tex_extensions
	from latextools_utils.sublime import get_project_file_name
else:
	_ST3 = True
	from .latextools_utils.is_tex_file import get_tex_extensions
	from .latextools_utils.sublime import get_project_file_name

import os.path
import re

# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file or None (if there is no root file,
# and the current buffer is an unnamed unsaved file)

# Contributed by Sam Finn
def get_tex_root(view):
	texFile = view.file_name()
	root = texFile

	lines = view.substr(
		sublime.Region(0, view.size())
	).split('\n')

	for line in lines:
		# remove any leading spaces
		line = line.lstrip()
		if not line.startswith('%'):
			break
		else:
			# We have a comment match; check for a TEX root match
			tex_exts = '|'.join([re.escape(ext) for ext in get_tex_extensions()])
			mroot = re.match(
				r"(?iu)%+\s*!TEX\s+root *= *(.*({0}))\s*$".format(tex_exts),
				line
			)

			if mroot:
				# we have a TEX root match
				# Break the match into path, file and extension
				# Create TEX root file name
				# If there is a TEX root path, use it
				# If the path is not absolute and a src path exists, pre-pend it
				root = mroot.group(1)
				if not os.path.isabs(root) and texFile is not None:
					(texPath, texName) = os.path.split(texFile)
					root = os.path.join(texPath, root)
				root = os.path.normpath(root)
				break

	if root == texFile:
		root = get_tex_root_from_settings(view)
		if root is not None:
			return root
		return texFile

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
