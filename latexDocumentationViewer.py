from __future__ import print_function

import sublime
import sublime_plugin

import os
import subprocess
from subprocess import Popen, PIPE

try:
    from latextools_utils import get_setting
except ImportError:
    from .latextools_utils import get_setting

if sublime.version() < '3000':
    _ST3 = False
    strbase = basestring
    import sys
else:
    _ST3 = True
    strbase = str

def get_texpath():
    platform_settings = get_setting(sublime.platform(), {})
    texpath = platform_settings.get('texpath', '')

    if not _ST3:
        return os.path.expandvars(texpath).encode(sys.getfilesystemencoding())
    else:
        return os.path.expandvars(texpath)

def using_miktex():
    if sublime.platform() != 'windows':
        return False

    platform_settings = get_setting(sublime.platform(), {})

    try:
        distro = platform_settings.get('distro', 'miktex')
        return distro in ['miktex', '']
    except KeyError:
        return True  # assumed

def _view_texdoc(file):
    if file is None:
        raise Exception('File must be specified')
    if not isinstance(file, strbase):
        raise TypeError('File must be a string')

    command = ['texdoc']

    texpath = get_texpath() or os.environ['PATH']
    env = dict(os.environ)
    env['PATH'] = texpath

    try:
        # Windows-specific adjustments
        startupinfo = None
        shell = False
        if sublime.platform() == 'windows':
            # ensure console window doesn't show
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            shell = True

            if using_miktex():
                command.append('--view')

        command.append(file)

        print('Running %s' % (' '.join(command)))
        p = Popen(
            command,
            stdout=None,
            stdin=None,
            startupinfo=startupinfo,
            shell=shell,
            env=env
        )

        if not using_miktex():  # see http://sourceforge.net/p/miktex/bugs/2367/
            p.communicate()     # cannot rely on texdoc --view from MiKTeX returning
            if p.returncode != 0:
                sublime.error_message('An error occurred while trying to run texdoc.')
    except OSError:
        sublime.error_message('Could not run texdoc. Please ensure that your texpath setting is configured correctly in the LaTeXTools settings.')

class LatexPkgDocCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        def _on_done(file):
            if (
                file is not None and
                isinstance(file, strbase) and
                file != ''
            ):
                window.run_command('latex_view_doc',
                    {'file': file})

        window.show_input_panel(
            'View documentation for which package?',
            '',
            _on_done,
            None,
            None
        )

class LatexViewDocCommand(sublime_plugin.WindowCommand):
    def run(self, file):
        _view_texdoc(file)

    def is_visible(self):
        return False  # hide this from menu
