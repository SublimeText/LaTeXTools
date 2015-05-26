from __future__ import print_function
import sublime
import sublime_plugin

import subprocess
from subprocess import Popen, PIPE
import os

from getTeXRoot import get_tex_root
from get_texpath import get_texpath

class TexcountCommand(sublime_plugin.TextCommand):
    """
    Simple TextCommand to run TeXCount against the current document
    """

    def run(self, edit, **args):
        tex_root = get_tex_root(self.view)

        if not os.path.exists(tex_root):
            sublime.error_message(
                'Tried to run TeXCount on non-existent file. Please ensure all files are saved before invoking TeXCount.'
            )
            return

        texpath = get_texpath() or os.environ['PATH']
        env = dict(os.environ)
        env['PATH'] = texpath

        command = ['texcount', '-total', '-merge', '-utf8']
        cwd = os.path.dirname(tex_root)
        command.append(os.path.basename(tex_root))

        try:
            startupinfo = None
            shell = False
            if sublime.platform() == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                shell = True

            print('Running {}'.format(' '.join(command)))
            p = Popen(
                command,
                stdout=PIPE,
                stderr=PIPE,
                startupinfo=startupinfo,
                shell=shell,
                env=env,
                cwd=cwd
            )

            result = p.communicate()[0].decode('utf-8').strip()
            if p.returncode == 0:
                self.view.window().show_quick_panel(result.split('\r')[1:-4], None)
            else:
                sublime.error_message(
                    'Error while running TeXCount: {}'.format(
                        str(p.stderr)
                    )
                )
        except OSError:
            sublime.error_message(
                'Could not run texcount. Please ensure that your texpath setting is configured correctly in the LaTeXTools settings.'
            )
