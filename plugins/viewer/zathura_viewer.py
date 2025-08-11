from shutil import which

from ...latextools.utils.external_command import check_output
from ...latextools.utils.external_command import external_command
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from .base_viewer import BaseViewer

__all__ = ["ZathuraViewer"]


class ZathuraViewer(BaseViewer):

    def _run_zathura(self, pdf_file):
        return external_command(
            ["zathura", self._get_synctex_editor(), pdf_file], use_texpath=False
        ).pid

    def _get_synctex_editor(self):
        return f"--synctex-editor-command={get_sublime_exe()} %{{input}}:%{{line}}"

    def _get_zathura_pid(self, pdf_file):
        try:
            running_apps = check_output(["ps", "xv"], use_texpath=False)
            for app in running_apps.splitlines():
                if "zathura" not in app:
                    continue
                if pdf_file in app:
                    return app.lstrip().split(" ", 1)[0]
        except Exception:
            pass

        return None

    def _focus_zathura(self, pid):
        if which("xdotool") is not None:
            try:
                self._focus_xdotool(pid)
                return
            except Exception:
                pass

        if which("wmctrl") is not None:
            try:
                self._focus_wmctrl(pid)
            except Exception:
                pass

    def _focus_wmctrl(self, pid):
        window_id = None
        try:
            windows = check_output(["wmctrl", "-l", "-p"], use_texpath=False)
        except Exception:
            pass
        else:
            pid = f" {pid} "
            for window in windows.splitlines():
                if pid in window:
                    window_id = window.split(" ", 1)[0]
                    break

        if window_id is None:
            raise Exception("Cannot find window for Zathura")

        external_command(["wmctrl", "-a", window_id, "-i"], use_texpath=False)

    def _focus_xdotool(self, pid):
        external_command(
            [
                "xdotool",
                "search",
                "--pid",
                pid,
                "--class",
                "Zathura",
                "windowactivate",
                "%2",
            ],
            use_texpath=False,
        )

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)

        # we check for the pid here as this is only necessary if
        # we aren't otherwise creating the window
        pid = self._get_zathura_pid(pdf_file)

        if pid is None:
            pid = self._run_zathura(pdf_file)
            if keep_focus:
                self.focus_st()

        command = [
            "zathura",
            "--synctex-forward",
            f"{line}:{col}:{tex_file}",
        ]

        if pid is None:
            command.append(self._get_synctex_editor())
        else:
            command.append(f"--synctex-pid={pid}")

        command.append(pdf_file)

        external_command(command, use_texpath=False)

        if pid is not None and not keep_focus:
            self._focus_zathura(pid)

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)

        pid = self._get_zathura_pid(pdf_file)
        if pid is None:
            pid = self._run_zathura(pdf_file)
            if keep_focus:
                self.focus_st()
        elif not keep_focus:
            self._focus_zathura(pid)

        return pid

    def supports_platform(self, platform):
        return platform == "linux"

    def supports_keep_focus(self):
        return True
