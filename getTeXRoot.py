import os.path, re, sublime

# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file

# Contributed by Sam Finn

def get_tex_root(view):
	# Try to get the TEX root from the current open folder
	rootDirName = sublime.active_window().folders()[0]
	files = [each for each in os.listdir(rootDirName) if each.endswith('.tex')]
	for file in files:
		fileName = os.path.join(rootDirName, file)
		with open(fileName, 'r') as f:
			for line in f:
				if '\\begin{document}' in line and not line.startswith('%'):
					return fileName

	try:
		root = os.path.abspath(view.settings().get('TEXroot'))
		if os.path.isfile(root):
			print "Main file defined in project settings : " + root
			return root
	except:
		pass


	texFile = view.file_name()
	for line in open(texFile, "rU").readlines():
		if not line.startswith('%'):
			root = texFile
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
				(texPath, texName) = os.path.split(texFile)
				(rootPath, rootName) = os.path.split(mroot.group(1))
				root = os.path.join(texPath,rootPath,rootName)
				root = os.path.normpath(root)
				break
	return root