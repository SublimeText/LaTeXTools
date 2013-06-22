import os.path, re

# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file or None (if there is no root file,
# and the current buffer is an unnamed unsaved file)

# Contributed by Sam Finn

def get_tex_root(view):
	try:
		root = os.path.abspath(view.settings().get('TEXroot'))
		if os.path.isfile(root):
			print "Main file defined in project settings : " + root
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

	else:
		lines = open(texFile, "rU")

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

	if isinstance(lines, file):
		lines.close()

	return root