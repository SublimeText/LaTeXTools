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


class SioyekViewer(BaseViewer):

    def __init__(self, *args, **kwargs):
        super(SioyekViewer, self).__init__(*args, **kwargs)

    def _find_sioyek_exe(self):
        if hasattr(SioyekViewer, '_sioyek_exe'):
            return SioyekViewer._sioyek_exe

        # Sioyek's installer writes the location of the exe to the
        # App Paths registry key, which we can access using the winreg
        # module.
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\Microsoft\\Windows\\CurrentVersion'
                '\\App Paths\\SioyekPDF.exe'
            ) as hndl:
                SioyekViewer._sioyek_exe = winreg.QueryValue(hndl, '')
                return SioyekViewer._sioyek_exe
        except WindowsError:
            pass

        paths = [
            os.path.expandvars("%PROGRAMFILES%\\SioyekPDF"),
            os.path.expandvars("%ProgramW6432%\\SioyekPDF"),
            os.path.expandvars("%PROGRAMFILES(x86)%\\SioyekPDF")
        ]

        for path in paths:
            if os.path.exists(path):
                exe = os.path.join(path, 'sioyek.exe')
                if os.path.exists(exe):
                    SioyekViewer._sioyek_exe = exe
                    return exe

        return None

    def _run_with_sioyek_exe(self, commands):
        def _no_binary():
            message = (
                'Could not find SioyekPDF.exe. '
                'Please ensure the "sioyek" setting in your '
                'LaTeXTools settings is set and points to the location '
                'of Sioyek on your computer.'
            )

            def _error_msg():
                sublime.error_message(message)

            sublime.set_timeout(_error_msg, 1)
            print(message)

        # paranoia
        if not isinstance(commands, list):
            commands = [commands]

        # favour 'sioyek' setting under viewer_settings if
        # it exists, otherwise, use the platform setting
        sioyek_binary = get_setting('viewer_settings', {}).\
            get('sioyek', get_setting('windows', {}).
                get('sioyek', 'sioyek.exe')) or 'sioyek.exe'

        try:
            external_command(
                [sioyek_binary] + commands,
                use_texpath=False, show_window=False
            )
        except OSError:
            exc_info = sys.exc_info()

            sioyek_exe = self._find_sioyek_exe()
            if sioyek_exe is not None and sioyek_exe != sioyek_binary:
                try:
                    external_command(
                        [sioyek_exe] + commands,
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
        self._run_with_sioyek_exe([
            '--reuse-instance',
            '--forward-search-file',
            src_file,
            '--forward-search-line',
            str(line),
            pdf_file
        ])

    def view_file(self, pdf_file, **kwargs):
        self._run_with_sioyek_exe([pdf_file])

    def supports_platform(self, platform):
        return platform == 'windows'

