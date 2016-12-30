from base_viewer import BaseViewer

from latextools_utils import get_setting
from latextools_utils.external_command import external_command

import os
import sublime
import sys
import traceback

if sys.version_info < (3, 0):
    try:
        import _winreg as winreg
    except:
        # not on Windows
        pass

    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")
else:
    try:
        import winreg
    except:
        # not on Windows
        pass

    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value


class SumatraViewer(BaseViewer):

    def __init__(self, *args, **kwargs):
        super(SumatraViewer, self).__init__(*args, **kwargs)

    def _find_sumatra_exe(self):
        if hasattr(SumatraViewer, '_sumatra_exe'):
            return SumatraViewer._sumatra_exe

        # Sumatra's installer writes the location of the exe to the
        # App Paths registry key, which we can access using the winreg
        # module.
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\Microsoft\\Windows\\CurrentVersion'
                '\\App Paths\\SumatraPDF.exe'
            ) as hndl:
                SumatraViewer._sumatra_exe = winreg.QueryValue(hndl, '')
                return SumatraViewer._sumatra_exe
        except WindowsError:
            pass

        paths = [
            os.path.expandvars("%PROGRAMFILES%\\SumatraPDF"),
            os.path.expandvars("%ProgramW6432%\\SumatraPDF"),
            os.path.expandvars("%PROGRAMFILES(x86)%\\SumatraPDF")
        ]

        for path in paths:
            if os.path.exists(path):
                exe = os.path.join(path, 'SumatraPDF.exe')
                if os.path.exists(exe):
                    SumatraViewer._sumatra_exe = exe
                    return exe

        return None

    def _run_with_sumatra_exe(self, commands):
        def _no_binary():
            message = (
                'Could not find SumatraPDF.exe. '
                'Please ensure the "sumatra" setting in your '
                'LaTeXTools settings is set and points to the location '
                'of Sumatra on your computer.'
            )

            def _error_msg():
                sublime.error_message(message)

            sublime.set_timeout(_error_msg, 1)
            print(message)

        # paranoia
        if not isinstance(commands, list):
            commands = [commands]

        # favour 'sumatra' setting under viewer_settings if
        # it exists, otherwise, use the platform setting
        sumatra_binary = get_setting('viewer_settings', {}).\
            get('sumatra', get_setting('windows', {}).
                get('sumatra', 'SumatraPDF.exe')) or 'SumatraPDF.exe'

        try:
            external_command(
                [sumatra_binary] + commands,
                use_texpath=False, show_window=True
            )
        except OSError:
            exc_info = sys.exc_info()

            sumatra_exe = self._find_sumatra_exe()
            if sumatra_exe is not None and sumatra_exe != sumatra_binary:
                try:
                    external_command(
                        [sumatra_exe] + commands,
                        use_texpath=False, show_window=True
                    )
                except OSError:
                    traceback.print_exc()
                    _no_binary()
                    return
            else:
                traceback.print_exception(*exc_info)
                _no_binary()
                return

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        src_file = tex_file

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
