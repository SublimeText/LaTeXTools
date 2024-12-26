import os
import sublime
import time

from LaTeXTools.latextools.utils.external_command import check_call
from LaTeXTools.latextools.utils.external_command import check_output
from LaTeXTools.latextools.utils.external_command import external_command
from LaTeXTools.latextools.utils.settings import get_setting
from LaTeXTools.latextools.utils.sublime_utils import get_sublime_exe

from base_viewer import BaseViewer


class EvinceViewer(BaseViewer):

    PYTHON = None

    def _get_evince_folder(self):
        return os.path.join(os.path.dirname(__file__), "evince")

    def _is_evince_running(self, pdf_file):
        try:
            return ("evince {0}".format(pdf_file)) in check_output(["ps", "xv"], use_texpath=False)
        except Exception:
            return False

    def _get_settings(self):
        """
        returns evince-related settings as a tuple
        (python, sync_wait)
        """
        linux_settings = get_setting("linux", {})
        python = linux_settings.get("python")
        if python is None or python == "":
            if self.PYTHON is not None:
                python = self.PYTHON
            else:
                try:
                    check_call(["python", "-c", "import dbus"], use_texpath=False)
                    python = "python"
                except Exception:
                    try:
                        check_call(["python3", "-c", "import dbus"], use_texpath=False)
                        python = "python3"
                    except Exception:
                        sublime.error_message(
                            """Cannot find a valid Python interpreter.
                            Please set the python setting in your LaTeXTools
                            settings.""".strip()
                        )
                        # exit the viewer process
                        raise Exception("Cannot find a valid interpreter")
                self.PYTHON = python
        return (python, linux_settings.get("sync_wait") or 1.0)

    def _launch_evince(self, pdf_file):
        ev_path = self._get_evince_folder()
        py_binary, _ = self._get_settings()

        st_binary = get_sublime_exe()
        if st_binary is None:
            linux_settings = get_setting("linux", {})
            st_binary = linux_settings.get("sublime", "sublime_text")

        external_command(
            ["sh", os.path.join(ev_path, "sync"), py_binary, st_binary, pdf_file],
            cwd=ev_path,
            use_texpath=False,
        )

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)
        bring_evince_forward = get_setting("viewer_settings", {}).get("bring_evince_forward", False)

        ev_path = self._get_evince_folder()
        py_binary, sync_wait = self._get_settings()

        evince_running = self._is_evince_running(pdf_file)
        if not keep_focus or not evince_running or bring_evince_forward:
            self._launch_evince(pdf_file)
            if keep_focus:
                self.focus_st()

            time.sleep(sync_wait)

        external_command(
            [
                py_binary,
                os.path.join(ev_path, "forward_search"),
                pdf_file,
                str(line),
                tex_file,
            ],
            use_texpath=False,
        )

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)

        if not keep_focus or not self._is_evince_running(pdf_file):
            self._launch_evince(pdf_file)
            if keep_focus:
                self.focus_st()

    def supports_platform(self, platform):
        return platform == "linux"

    def supports_keep_focus(self):
        return True
