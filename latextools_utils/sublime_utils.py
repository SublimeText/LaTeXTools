from __future__ import print_function

import json
import os
import re
import sublime
import subprocess
import sys

try:
	from latextools_utils.settings import get_setting
	from latextools_utils.system import which
except ImportError:
	from .settings import get_setting
	from .system import which


__all__ = ['normalize_path', 'get_project_file_name']

# used by get_sublime_exe()
SUBLIME_VERSION = re.compile(r'Build (\d{4})', re.UNICODE)

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
    processes = ['subl', 'sublime_text']

    def check_processes(st2_dir=None):
        if st2_dir is None or os.path.exists(st2_dir):
            for process in processes:
                try:
                    if st2_dir is not None:
                        process = os.path.join(st2_dir, process)

                    p = subprocess.Popen(
                        [process, '-v'],
                        stdout=subprocess.PIPE,
                        startupinfo=startupinfo,
                        shell=shell,
                        env=os.environ
                    )
                except:
                    pass
                else:
                    stdout, _ = p.communicate()

                    if p.returncode == 0:
                        m = SUBLIME_VERSION.search(stdout.decode('utf8'))
                        if m and m.group(1) == version:
                            return process
        return None

    platform = sublime.platform()

    plat_settings = get_setting(platform, {})
    sublime_executable = plat_settings.get('sublime_executable', None)

    if sublime_executable:
        return sublime_executable

    # we cache the results of the other checks, if possible
    if hasattr(get_sublime_exe, 'result'):
        return get_sublime_exe.result

    # are we on ST3
    if hasattr(sublime, 'executable_path'):
        get_sublime_exe.result = sublime.executable_path()
        # on osx, the executable does not function the same as subl
        if platform == 'osx':
            get_sublime_exe.result = os.path.normpath(
                os.path.join(
                    os.path.dirname(get_sublime_exe.result),
                    '..',
                    'SharedSupport',
                    'bin',
                    'subl'
                )
            )
        # on linux, it is preferable to use subl if it points to the
        # correct version see issue #710 for a case where this is useful
        elif (
            platform == 'linux' and
            not get_sublime_exe.result.endswith('subl')
        ):
            subl = which('subl')
            if subl is not None:
                try:
                    p = subprocess.Popen(
                        [subl, '-v'],
                        stdout=subprocess.PIPE,
                        env=os.environ
                    )
                except:
                    pass
                else:
                    stdout, _ = p.communicate()

                    if p.returncode == 0:
                        m = SUBLIME_VERSION.search(stdout.decode('utf8'))
                        if m and m.group(1) == sublime.version():
                            get_sublime_exe.result = subl

        return get_sublime_exe.result
    # in ST2 on Windows the Python executable is actually "sublime_text"
    elif platform == 'windows' and sys.executable != 'python' and \
            os.path.isabs(sys.executable):
        get_sublime_exe.result = sys.executable
        return get_sublime_exe.result

    # guess-work for ST2
    version = sublime.version()

    startupinfo = None
    shell = False
    if platform == 'windows':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        shell = sublime.version() >= '3000'

    # hope its on the path
    result = check_processes()
    if result is not None:
        get_sublime_exe.result = result
        return result

    # guess the default location
    if platform == 'windows':
        st2_dir = os.path.expandvars('%PROGRAMFILES%\\Sublime Text 2')
        result = check_processes(st2_dir)
        if result is not None:
            get_sublime_exe.result = result
            return result
    elif platform == 'linux':
        for path in [
            '$HOME/bin',
            '$HOME/sublime_text_2',
            '$HOME/sublime_text',
            '/opt/sublime_text_2',
            '/opt/sublime_text',
            '/usr/local/bin',
            '/usr/bin'
        ]:
            st2_dir = os.path.expandvars(path)
            result = check_processes(st2_dir)
            if result is not None:
                get_sublime_exe.result = result
                return result
    else:
        st2_dir = '/Applications/Sublime Text 2.app/Contents/SharedSupport/bin'
        result = check_processes(st2_dir)
        if result is not None:
            get_sublime_exe.result = result
            return result
        try:
            p = subprocess.Popen(
                ['mdfind', '"kMDItemCFBundleIdentifier == com.sublimetext.2"'],
                stdout=subprocess.PIPE,
                env=os.environ
            )
        except:
            pass
        else:
            stdout, _ = p.communicate()
            if p.returncode == 0:
                st2_dir = os.path.join(
                    stdout.decode('utf8'),
                    'Contents',
                    'SharedSupport',
                    'bin'
                )
                result = check_processes(st2_dir)
                if result is not None:
                    get_sublime_exe.result = result
                    return result

    print(
        'Cannot determine the path to your Sublime installation. Please '
        'set the "sublime_executable" setting in your settings for your '
        'platform.'
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
