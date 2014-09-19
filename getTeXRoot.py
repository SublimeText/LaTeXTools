# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
	# we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True


import os.path, re
import codecs


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
			mroot = re.match(r"%\s*!TEX\s+root *= *(.*(tex|TEX))\s*$",line)
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