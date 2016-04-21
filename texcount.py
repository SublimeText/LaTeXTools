from __future__ import print_function
import sublime
import sublime_plugin

import subprocess
from subprocess import Popen, PIPE
import os

if sublime.version() < '3000':
    from getTeXRoot import get_tex_root
    from get_texpath import get_texpath
else:
    from .getTeXRoot import get_tex_root
    from .get_texpath import get_texpath

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

        sub_level = args.get('sub_level', 'chapter')

        command = ['texcount', '-merge', '-sub='+sub_level, '-utf8']
        cwd = os.path.dirname(tex_root)
        command.append(os.path.basename(tex_root))

        try:
            startupinfo = None
            shell = False
            if sublime.platform() == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                shell = True

            print('Running {0}'.format(' '.join(command)))
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
            # result = p.communicate()[1].decode('utf-8').strip()
            if p.returncode == 0:
                res_split = result.splitlines()
                try:
                    self.view.window().show_quick_panel(res_split[1:4] + res_split[9:], None)
                except TypeError:
                    self.view.window().show_quick_panel(res_split[1:4], None)
            else:
                sublime.error_message(
                    'Error while running TeXCount: {0}'.format(
                        str(p.stderr)
                    )
                )
        except OSError:
            sublime.error_message(
                'Could not run texcount. Please ensure that your texpath setting is configured correctly in the LaTeXTools settings.'
            )
