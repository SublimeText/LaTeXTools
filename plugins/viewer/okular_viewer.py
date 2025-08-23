from __future__ import annotations

from ...latextools.utils.external_command import external_command

from .base_viewer import BaseViewer

__all__ = ["OkularViewer"]


class OkularViewer(BaseViewer):

    def _run_okular(self, locator=None, **kwargs):
        keep_focus: bool = kwargs.get("keep_focus", True)
        command = ["okular", "--unique"]
        if keep_focus:
            command.append("--noraise")
        if locator is not None:
            command.append(locator)

        external_command(command, use_texpath=False)
        if keep_focus:
            self.focus_st()

    def forward_sync(self, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        self._run_okular(f"file:{pdf_file}#src:{line}{tex_file}", **kwargs)

    def view_file(self, pdf_file: str, **kwargs) -> None:
        self._run_okular(pdf_file, **kwargs)

    def supports_keep_focus(self) -> bool:
        return True

    def supports_platform(self, platform: str) -> bool:
        return platform == "linux"
