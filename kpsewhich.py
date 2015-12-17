from __future__ import print_function
import subprocess
from subprocess import Popen, PIPE
import os
import sublime
import sys

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import get_setting
else:
    _ST3 = True
    from .latextools_utils import get_setting

__all__ = ['kpsewhich']

def get_texpath():
    platform_settings = get_setting(sublime.platform(), {})
    texpath = platform_settings.get('texpath', '')

    if not _ST3:
        return os.path.expandvars(texpath).encode(sys.getfilesystemencoding())
    else:
        return os.path.expandvars(texpath)

def kpsewhich(filename, file_format=None):
    # build command
    command = ['kpsewhich']
    if file_format is not None:
        command.append('-format=%s' % (file_format))
    command.append(filename)

    # setup the environment to run the subprocess in
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

        print('Running %s' % (' '.join(command)))
        p = Popen(
            command,
            stdout=PIPE,
            stdin=PIPE,
            startupinfo=startupinfo,
            shell=shell,
            env=env
        )
        path = p.communicate()[0].decode('utf-8').rstrip()
        if p.returncode == 0:
            return path
        else:
            sublime.error_message('An error occurred while trying to run kpsewhich. TEXMF tree could not be accessed.')
    except OSError:
        sublime.error_message('Could not run kpsewhich. Please ensure that your texpath setting is configured correctly in the LaTeXTools settings.')

    return None
