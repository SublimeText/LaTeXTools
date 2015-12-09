# ST2/ST3 compat
from __future__ import print_function
import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
	from latextools_utils.is_tex_file import get_tex_extensions
else:
	_ST3 = True
	from .latextools_utils.is_tex_file import get_tex_extensions


import os.path, re
import codecs


# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file or None (if there is no root file,
# and the current buffer is an unnamed unsaved file)

# Contributed by Sam Finn

def get_tex_root(view):
	try:
		# Retrive TEX root from the project settings file.
		root = view.settings().get('TEXroot', None)

		# The TEX root must have an absolute path.
		if os.path.isabs(root):
			if os.path.isfile(root):
				return root
		else:
			try:
				# Make root relative to the current project's .sublime-project
				# file. This will thrown an exception on ST2 and when no
				# project is loaded on ST3.
				projFile = view.window().project_file_name()
				projDir = os.path.dirname(projFile)

				rootPath = os.path.join(projDir, root)
				if os.path.isfile(rootPath):
					return rootPath
			except:
				pass

			# Make root relative to the current working directory. This fails if
			# multiple instances of ST are running (issue #152).
			rootPath = os.path.abspath(root)
			if os.path.isfile(rootPath):
				return rootPath
	except:
		pass

	texFile = view.file_name()
	root = texFile
	if texFile is None:
		# We are in an unnamed, unsaved file.
		# Read from the buffer instead.
		if view.substr(0) != '%':
			return None
		reg = view.find(r"^%[^\n]*(\n%[^\n]*)*", 0)
		if not reg:
			return None
		line_regs = view.lines(reg)
		lines = map(view.substr, line_regs)
		is_file = False

	else:
		# This works on ST2 and ST3, but does not automatically convert line endings.
		# We should be OK though.
		lines = codecs.open(texFile, "r", "UTF-8")
		is_file = True

	for line in lines:
		if not line.startswith('%'):
			break
		else:
			# We have a comment match; check for a TEX root match
			tex_exts = '|'.join([re.escape(ext) for ext in get_tex_extensions()])
			mroot = re.match(r"(?i)%\s*!TEX\s+root *= *(.*({0}))\s*$".format(tex_exts), line)
			if mroot:
				# we have a TEX root match
				# Break the match into path, file and extension
				# Create TEX root file name
				# If there is a TEX root path, use it
				# If the path is not absolute and a src path exists, pre-pend it
				root = mroot.group(1)
				if not os.path.isabs(root) and texFile is not None:
					(texPath, texName) = os.path.split(texFile)
					root = os.path.join(texPath,root)
				root = os.path.normpath(root)
				break

	if is_file: # Not very Pythonic, but works...
		lines.close()

	return root