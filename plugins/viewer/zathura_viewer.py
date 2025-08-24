from __future__ import annotations

from ...latextools.utils.external_command import check_output
from ...latextools.utils.external_command import external_command
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from .base_viewer import BaseViewer

__all__ = ["ZathuraViewer"]


class ZathuraViewer(BaseViewer):

    @classmethod
    def _run_zathura(cls, *args, **kwargs):
        external_command(
            [
                get_setting("viewer_settings", {}).get("zathura") or "zathura",
                f"--synctex-editor-command={get_sublime_exe()} %{{input}}:%{{line}}",
                *args,
            ],
            use_texpath=False,
        )
        if kwargs.get("keep_focus", True):
            cls.focus_st()

    @classmethod
    def _get_zathura_pid(cls, pdf_file: str) -> int:
        try:
            running_apps = check_output(["ps", "xv"], use_texpath=False)
            for app in running_apps.splitlines():
                if "zathura" in app and pdf_file in app:
                    return int(app.lstrip().split(" ", 1)[0])
        except Exception:
            pass

        return 0

    @classmethod
    def forward_sync(cls, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        cls._run_zathura("--synctex-forward", f"{line}:{col}:{tex_file}", pdf_file)

    @classmethod
    def view_file(cls, pdf_file: str, **kwargs) -> None:
        if not cls._get_zathura_pid(pdf_file):
            cls._run_zathura(pdf_file)

    @classmethod
    def supports_keep_focus(cls) -> bool:
        return True

    @classmethod
    def supports_platform(cls, platform: str) -> bool:
        return platform == "linux"
