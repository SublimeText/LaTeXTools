from __future__ import annotations

from ...latextools.utils.external_command import check_output
from ...latextools.utils.external_command import external_command
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from .base_viewer import BaseViewer

__all__ = ["ZathuraViewer"]


class ZathuraViewer(BaseViewer):

    def _run_zathura(self, *args, **kwargs):
        external_command(
            [
                get_setting("viewer_settings", {}).get("zathura") or "zathura",
                f"--synctex-editor-command={get_sublime_exe()} %{{input}}:%{{line}}",
                *args,
            ],
            use_texpath=False,
        )
        if kwargs.get("keep_focus", True):
            self.focus_st()

    def _get_zathura_pid(self, pdf_file: str) -> int:
        try:
            running_apps = check_output(["ps", "xv"], use_texpath=False)
            for app in running_apps.splitlines():
                if "zathura" in app and pdf_file in app:
                    return int(app.lstrip().split(" ", 1)[0])
        except Exception:
            pass

        return 0

    def forward_sync(self, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        self._run_zathura("--synctex-forward", f"{line}:{col}:{tex_file}", pdf_file)

    def view_file(self, pdf_file: str, **kwargs) -> None:
        if not self._get_zathura_pid(pdf_file):
            self._run_zathura(pdf_file)

    def supports_keep_focus(self) -> bool:
        return True

    def supports_platform(self, platform: str) -> bool:
        return platform == "linux"
