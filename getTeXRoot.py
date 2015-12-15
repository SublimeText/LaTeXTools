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


import os.path
import re
import json


# normalizes the paths stored in sublime session files on Windows
# from:
#     /c/path/to/file.ext
# to:
#     c:\path\to\file.ext
def normalize_sublime_path(path):
	if sublime.platform() == 'windows':
		return os.path.normpath(
			path.lstrip('/').replace('/', ':/', 1)
		)
	else:
		return path


# long, complex hack for ST2 to load the project file from the current session
def get_project_file_name(view):
	window_id = view.window().id()
	if window_id is None:
		return None

	session = os.path.normpath(
		os.path.join(
			sublime.packages_path(),
			'..',
			'Settings',
			'Session.sublime_session'
		)
	)

	auto_save_session = os.path.normpath(
		os.path.join(
			sublime.packages_path(),
			'..',
			'Settings',
			'Auto Save Session.sublime_session'
		)
	)

	session = auto_save_session if os.path.exists(auto_save_session) else session

	if not os.path.exists(session):
		return None

	project_file = None

	# we tell that we have found the current project's project file by
	# looking at the folders registered for that project and comparing it
	# to the open directorys in the current window
	found_all_folders = False
	try:
		with open(session, 'r') as f:
			session_data = f.read().replace('\t', ' ')
		j = json.loads(session_data, strict=False)
		projects = j.get('workspaces', {}).get('recent_workspaces', [])

		for project_file in projects:
			found_all_folders = True

			project_file = normalize_sublime_path(project_file)
			try:
				with open(project_file, 'r') as fd:
					project_json = json.loads(fd.read(), strict=False)

				if 'folders' in project_json:
					project_folders = project_json['folders']
					for directory in view.window().folders():
						found = False
						for folder in project_folders:
							folder_path = normalize_sublime_path(folder['path'])
							# handle relative folder paths
							if not os.path.isabs(folder_path):
								folder_path = os.path.normpath(
									os.path.join(os.path.dirname(project_file), folder_path)
								)

							if folder_path == directory:
								found = True
								break

						if not found:
							found_all_folders = False
							break

					if found_all_folders:
						break
			except:
				found_all_folders = False
	except:
		pass

	if not found_all_folders:
		project_file = None

	if (
		project_file is None or
		not project_file.endswith('.sublime-project') or
		not os.path.exists(project_file)
	):
		return None

	print('Using project file: %s' % project_file)
	return project_file


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
			try:
				proj_file = view.window().project_file_name()
			except AttributeError:
				proj_file = get_project_file_name(view)

			if proj_file:
				project_dir = os.path.dirname(proj_file)
				root_path = os.path.normpath(os.path.join(project_dir, root))
				if os.path.isfile(root_path):
					return root_path

	return root
