from __future__ import annotations

from ...latextools.utils.external_command import external_command

from .base_viewer import BaseViewer

__all__ = ["OkularViewer"]


class OkularViewer(BaseViewer):

    @classmethod
    def _run_okular(cls, locator=None, **kwargs):
        keep_focus: bool = kwargs.get("keep_focus", True)
        command = ["okular", "--unique"]
        if keep_focus:
            command.append("--noraise")
        if locator is not None:
            command.append(locator)

        external_command(command, use_texpath=False)
        if keep_focus:
            cls.focus_st()

    @classmethod
    def forward_sync(cls, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        cls._run_okular(f"file:{pdf_file}#src:{line}{tex_file}", **kwargs)

    @classmethod
    def view_file(cls, pdf_file: str, **kwargs) -> None:
        cls._run_okular(pdf_file, **kwargs)

    @classmethod
    def supports_keep_focus(cls) -> bool:
        return True

    @classmethod
    def supports_platform(cls, platform: str) -> bool:
        return platform == "linux"
