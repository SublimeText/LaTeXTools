from base_viewer import BaseViewer

from latextools_utils import get_setting

import os
import sublime
import subprocess
import sys
import traceback

if sys.version_info < (3, 0):
    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")
else:
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value


class SumatraViewer(BaseViewer):
    def __init__(self, *args, **kwargs):
        super(SumatraViewer, self).__init__(*args, **kwargs)
        self._sumatra_exe = None

    def _find_sumatra_exe(self):
        for path in [
            os.path.expandvars("%PROGRAMFILES%\\SumatraPDF"),
            os.path.expandvars("%PROGRAMFILES(x86)%\\SumatraPDF")
        ]:
            if os.path.exists(path):
                exe = os.path.join(path, 'SumatraPDF.exe')
                if os.path.exists(exe):
                    return exe
        return None

    def _run_with_sumatra_exe(self, commands):
        def _no_binary():
            message = (
                'Could not find SumatraPDF.exe. '
                'Please ensure the "sumatra" setting in your '
                'LaTeXTools.sublime-settings is properly set.'
            )

            def _error_msg():
                sublime.error_message(message)

            sublime.set_timeout(_error_msg, 1)
            print(message)

        # paranoia
        if not isinstance(commands, list):
            commands = [commands]

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 4  # SHOWNOACTIVE

        # favour 'sumatra' setting under viewer_settings if
        # it exists, otherwise, use the platform setting
        sumatra_binary = get_setting('viewer_settings', {}).\
            get('sumatra', get_setting('windows', {}).
                get('sumatra', 'SumatraPDF.exe'))
        try:
            subprocess.Popen(
                [sumatra_binary] + commands,
                startupinfo=startupinfo
            )
        except OSError:
            exc_info = sys.exc_info()

            sumatra_binary = self._find_sumatra_exe()
            if sumatra_binary is not None:
                try:
                    subprocess.Popen(
                        [sumatra_binary] + commands,
                        startupinfo=startupinfo
                    )
                except OSError:
                    traceback.print_exc()
                    _no_binary()
            else:
                traceback.print_exception(*exc_info)
                _no_binary()

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        root_folder = os.path.dirname(pdf_file)
        src_file = os.path.relpath(tex_file, root_folder)

        self._run_with_sumatra_exe([
            '-reuse-instance',
            '-forward-search',
            src_file,
            str(line),
            pdf_file
        ])

    def view_file(self, pdf_file, **kwargs):
        self._run_with_sumatra_exe(['-reuse-instance', pdf_file])

    def supports_platform(self, platform):
        return platform == 'windows'
