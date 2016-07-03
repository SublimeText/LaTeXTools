from base_viewer import BaseViewer

from latextools_utils import get_setting
from latextools_utils.sublime_utils import get_sublime_exe
from latextools_utils.system import which

import subprocess
import sys


class ZathuraViewer(BaseViewer):

    def _get_synctex_editor(self):
        st_binary = get_sublime_exe()
        if st_binary is None:
            st_binary = get_setting('linux', {}).get('sublime', 'sublime_text')

        return '--synctex-editor-command={0} %{{input}}:%{{line}}'.format(
            st_binary
        )

    def _get_zathura_pid(self, pdf_file):
        stdout = subprocess.Popen(
            ['ps', 'xw'], stdout=subprocess.PIPE
        ).communicate()[0]

        running_apps = stdout.decode(sys.getdefaultencoding(), 'ignore')
        for app in running_apps.splitlines():
            if 'zathura' not in app:
                continue
            if pdf_file in app:
                return app.lstrip().split(' ', 1)[0]
        return None

    def _focus_zathura(self, pid):
        if which('xdotool') is not None:
            try:
                self._focus_xdotool(pid)
                return
            except:
                pass

        if which('wmctrl') is not None:
            try:
                self._focus_wmctrl(pid)
            except:
                pass

    def _focus_wmctrl(self, pid):
        pid = ' {0} '.format(pid)
        stdout = subprocess.Popen(
            ['wmctrl', '-l', '-p'], stdout=subprocess.PIPE
        ).communicate()[0]

        window_id = None
        windows = stdout.decode(sys.getdefaultencoding(), 'ignore')
        for window in windows.splitlines():
            if pid in window:
                window_id = window.split(' ', 1)[0]
                break

        if window_id is None:
            raise Exception('Cannot find window for Zathura')

        subprocess.Popen(['wmctrl', '-a', window_id, '-i'])

    def _focus_xdotool(self, pid):
        subprocess.Popen(
            ['xdotool', 'search', '--pid', pid,
             '--class', 'Zathura', 'windowactivate', '%2']
        )

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)

        # we check for the pid here as this is only necessary if
        # we aren't otherwise creating the window
        pid = self._get_zathura_pid(pdf_file)

        if pid is None:
            pid = self._run_zathura(pdf_file)

        command = [
            'zathura', '--synctex-forward',
            '{line}:{col}:{tex_file}'.format(**locals()),
        ]

        if pid is None:
            command.append(self._get_synctex_editor())
        else:
            command.append('--synctex-pid={pid}'.format(pid=pid))

        command.append(pdf_file)

        subprocess.Popen(command)

        if pid is not None and not keep_focus:
            self._focus_zathura(pid)

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)

        pid = self._get_zathura_pid(pdf_file)
        if pid is None:
            pid = subprocess.Popen([
                'zathura',
                self._get_synctex_editor(),
                pdf_file
            ]).pid
        elif not keep_focus:
            self._focus_zathura(pid)

        return pid

    def supports_platform(self, platform):
        return platform == 'linux'
