from __future__ import print_function

import os
import sublime
import sys

try:
    from latextools_utils.settings import get_setting
except ImportError:
    from .settings import get_setting


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
