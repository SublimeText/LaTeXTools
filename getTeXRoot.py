import os.path, re

# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file

# Contributed by Sam Finn

def get_tex_root(texFile):
	for line in open(texFile, "rU").readlines():
		if not line.startswith('%'):
			root = texFile
			break
		else:
			# We have a comment match; check for a TEX root match
			if re.match(r"%\s*!TEX\s+root *= *",line):
				# we have a TEX root match 
				# Break the match into path, file and extension
				# Create TEX root file name
				# If there is a TEX root path, use it
				# If the path is not absolute and a src path exists, pre-pend it
				mroot = re.match(r"%\s*!TEX\s+root *= *(.*tex)\s*$",line)
				(texPath, texName) = os.path.split(texFile)
				(rootPath, rootName) = os.path.split(mroot.group(1))
				root = os.path.join(texPath,rootPath,rootName)
				root = os.path.normpath(root)
				break
	return root