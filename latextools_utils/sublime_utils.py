# This module provides some functions that handle differences between ST2 and
# ST3. For the most part, they provide ST2-compatible functionality that is
# already available in ST3.
from __future__ import print_function

import codecs
import json
import os
import re
import sublime
import sys

try:
    from latextools_utils.external_command import (
        check_output, external_command
    )
    from latextools_utils.settings import get_setting
    from latextools_utils.system import which
except ImportError:
    from .external_command import check_output, external_command
    from .settings import get_setting
    from .system import which

_ST3 = sublime.version() >= '3000'


__all__ = ['normalize_path', 'get_project_file_name']

_ST3 = sublime.version() >= '3000'

# used by get_sublime_exe()
SUBLIME_VERSION = re.compile(r'Build (\d{4})', re.UNICODE)


# normalizes the paths stored in sublime session files on Windows
# from:
# 	/c/path/to/file.ext
# to:
# 	c:\path\to\file.ext
def normalize_path(path):
    if sublime.platform() == 'windows':
        return os.path.normpath(
            path.lstrip('/').replace('/', ':/', 1)
        )
    else:
        return path


# returns the focus to ST
# NB its probably good to call this as little as possible since focus-stealing
# annoys people
def focus_st():
    if get_setting('disable_focus_hack', False):
        return

    sublime_command = get_sublime_exe()

    if sublime_command is not None:
        platform = sublime.platform()
        plat_settings = get_setting(platform, {})
        wait_time = plat_settings.get('keep_focus_delay', 0.5)

        # osx is a special snowflake
        if platform == 'osx':
            # sublime_command should be /path/to/Sublime Text.app/Contents/...
            sublime_app = sublime_command.split('/Contents/')[0]

            def keep_focus():
                external_command(
                    [
                        'osascript', '-e',
                        'tell application "{0}" to activate'.format(
                            sublime_app
                        )
                    ],
                    use_texpath=False
                )
        else:
            def keep_focus():
                external_command([sublime_command], use_texpath=False)

        if hasattr(sublime, 'set_async_timeout'):
            sublime.set_async_timeout(keep_focus, int(wait_time * 1000))
        else:
            sublime.set_timeout(keep_focus, int(wait_time * 1000))


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

                    m = SUBLIME_VERSION.search(check_output(
                        [process, '-v'],
                        use_texpath=False
                    ))
                    if m and m.group(1) == version:
                        return process
                except:
                    pass

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
                    m = SUBLIME_VERSION.search(check_output(
                        [subl, '-v'],
                        use_texpath=False
                    ))

                    if m and m.group(1) == sublime.version():
                        get_sublime_exe.result = subl
                except:
                    pass

        return get_sublime_exe.result
    # in ST2 on Windows the Python executable is actually "sublime_text"
    elif platform == 'windows' and sys.executable != 'python' and \
            os.path.isabs(sys.executable):
        get_sublime_exe.result = sys.executable
        return get_sublime_exe.result

    # guess-work for ST2
    version = sublime.version()

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
            folder = check_output(
                ['mdfind', '"kMDItemCFBundleIdentifier == com.sublimetext.2"'],
                use_texpath=False
            )

            st2_dir = os.path.join(folder, 'Contents', 'SharedSupport', 'bin')
            result = check_processes(st2_dir)
            if result is not None:
                    get_sublime_exe.result = result
                    return result
        except:
            pass

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


# tokens used to clean-up JSON files
TOKENIZER = re.compile(r'(?<![^\\]\\)"|(/\*)|(//)|(#)')
QUOTE = re.compile(r'(?<![^\\]\\)"')
NEWLINE = re.compile(r'\r?\n')


def _parse_json_with_comments(filename):
    with codecs.open(filename, 'r', 'utf-8', 'ignore') as f:
        content = f.read()

    try:
        return json.loads(content)
    except:
        pass

    # pre-process to strip comments
    new_content = []
    index = 0

    content_length = len(content) - 1

    match = TOKENIZER.search(content, index)
    while match:
        new_content.append(content[index:match.start()])

        index = match.end()
        value = match.group()

        if value == '/*':
            comment_end = content.find('*/', index)
            if comment_end == -1:
                # unbalanced comment
                break
            else:
                new_lines = len(content[index:comment_end].split('\n')) - 1
                new_content.extend(['\n'] * new_lines)
                index = comment_end + 2
        elif value == '//' or value == '#':
            comment_end = NEWLINE.search(content, index)
            if comment_end:
                index = comment_end.end()
            else:
                break
        elif value == '"':
            new_content.append('"')
            next_quote = QUOTE.search(content, index)
            if next_quote:
                new_content.append(content[index:next_quote.end()])
                index = next_quote.end()
            else:
                # unclosed quote; return to generate json error
                break

        if index < content_length:
            match = TOKENIZER.search(content, index)
        else:
            break

    if index < content_length:
        new_content.append(content[index:])

    return json.loads(''.join(new_content))


if _ST3:
    def parse_json_with_comments(filename):
        with codecs.open(filename, 'r', 'utf-8', 'ignore') as f:
            content = f.read()
        return sublime.decode_value(content)
else:
    parse_json_with_comments = _parse_json_with_comments
