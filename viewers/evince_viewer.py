from base_viewer import BaseViewer

from latextools_utils import get_setting
from latextools_utils.sublime_utils import get_sublime_exe

import os
import sublime
import subprocess
import sys
import time


class EvinceViewer(BaseViewer):

    PYTHON = None

    def _get_evince_folder(self):
        return os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'evince'
            )
        )

    def _is_evince_running(self, pdf_file):
        stdout = subprocess.Popen(
            ['ps', 'xw'], stdout=subprocess.PIPE
        ).communicate()[0]

        running_apps = stdout.decode(sys.getdefaultencoding(), 'ignore')
        return ('evince %s' % (pdf_file)) in running_apps

    def _get_settings(self):
        '''
        returns evince-related settings as a tuple
        (python, sync_wait)
        '''
        linux_settings = get_setting('linux', {})
        # TODO python2 should eventually be deprecated
        python = linux_settings.get('python')
        if python is None or python == '':
            python = linux_settings.get('python2')

        if python is None or python == '':
            if self.PYTHON is not None:
                python = self.PYTHON
            else:
                try:
                    subprocess.check_call(['python', '-c', 'import dbus'])
                    python = 'python'
                except subprocess.CalledProcessError:
                    try:
                        subprocess.check_call(['python3', '-c', 'import dbus'])
                        python = 'python3'
                    except subprocess.CalledProcessError:
                        sublime.error_message(
                            '''Cannot find a valid Python interpreter.
                            Please set the python setting in your LaTeXTools settings.
                            '''.strip()
                        )
                        # exit the viewer process
                        raise Exception('Cannot find a valid interpreter')
                self.PYTHON = python
        return (
            python,
            linux_settings.get('sync_wait') or 1.0
        )

    def _launch_evince(self, pdf_file):
        ev_path = self._get_evince_folder()
        py_binary, _ = self._get_settings()

        st_binary = get_sublime_exe()
        if st_binary is None:
            linux_settings = get_setting('linux', {})
            st_binary = linux_settings.get('sublime', 'sublime_text')

        subprocess.Popen([
                'sh',
                os.path.join(ev_path, 'evince_sync'),
                py_binary,
                st_binary,
                pdf_file
            ],
            cwd=ev_path
        )

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)

        ev_path = self._get_evince_folder()
        py_binary, sync_wait = self._get_settings()

        evince_running = self._is_evince_running(pdf_file)
        if not keep_focus or not evince_running:
            self._launch_evince(pdf_file)
            time.sleep(sync_wait)

        subprocess.Popen([
            py_binary,
            os.path.join(ev_path, 'evince_forward_search'),
            pdf_file,
            str(line),
            tex_file
        ])

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)

        if not keep_focus or not self._is_evince_running(pdf_file):
            self._launch_evince(pdf_file)

    def supports_platform(self, platform):
        return platform == 'linux'
