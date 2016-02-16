import json
import os.path
import sublime

try:
	from latextools_utils.settings import get_setting
except ImportError:
	from .settings import get_setting


__all__ = ['normalize_path', 'get_project_file_name']


# normalizes the paths stored in sublime session files on Windows
# from:
#     /c/path/to/file.ext
# to:
#     c:\path\to\file.ext
def normalize_path(path):
	if sublime.platform() == 'windows':
		return os.path.normpath(
			path.lstrip('/').replace('/', ':/', 1)
		)
	else:
		return path


# returns the path to the sublime executable
def get_sublime_exe():
    '''
    Utility function to get the full path to the currently executing
    Sublime instance.
    '''
    plat_settings = get_setting(sublime.platform(), {})
    sublime_executable = plat_settings.get('sublime_executable', None)

    if sublime_executable:
        return sublime_executable

    # we cache the results of the other checks, if possible
    if hasattr(get_sublime_exe, 'result'):
        return get_sublime_exe.result

    # are we on ST3
    if hasattr(sublime, 'executable_path'):
        get_sublime_exe.result = sublime.executable_path()
    # in ST2 the Python executable is actually "sublime_text"
    elif sys.executable != 'python' and os.path.isabs(sys.executable):
        get_sublime_exe.result = sys.executable

    # on osx, the executable does not function the same as subl
    if sublime.platform() == 'osx':
        get_sublime_exe.result = os.path.normpath(
            os.path.join(
                os.path.dirname(get_sublime_exe.result),
                '..',
                'SharedSupport',
                'bin',
                'subl'
            )
        )

    return get_sublime_exe.result

    print(
        'Cannot determine the path to your Sublime installation. Please ' +
        'set the "sublime_executable" setting in your settings.'
    )

    return None


def get_project_file_name(view):
	try:
		return view.window().project_file_name()
	except AttributeError:
		return _get_project_file_name(view)


# long, complex hack for ST2 to load the project file from the current session
def _get_project_file_name(view):
	try:
		window_id = view.window().id()
	except AttributeError:
		print('Could not determine project file as view does not seem to have an associated window.')
		return None

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

			project_file = normalize_path(project_file)
			try:
				with open(project_file, 'r') as fd:
					project_json = json.loads(fd.read(), strict=False)

				if 'folders' in project_json:
					project_folders = project_json['folders']
					for directory in view.window().folders():
						found = False
						for folder in project_folders:
							folder_path = normalize_path(folder['path'])
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
