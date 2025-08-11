import sublime

from ...latextools.utils.external_command import external_command
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from .base_viewer import BaseViewer

__all__ = ["SioyekViewer"]


class SioyekViewer(BaseViewer):

    def _run_sioyek(self, *args, **kwargs):
        platform = sublime.platform()
        sioyek_binary = (
            # prefer `viewer_settings`
            get_setting("viewer_settings", {}).get("sioyek")
            # fallback to platform specific settings
            or get_setting(platform, {}).get("sioyek")
            # static binary expected to be found on $PATH
            or "sioyek.exe"
            if platform == "windows"
            else "sioyek"
        )

        command = [sioyek_binary]

        keep_focus = kwargs.pop("keep_focus", True)
        if keep_focus:
            command.append("--nofocus")

        command += args
        external_command(command, use_texpath=False, show_window=True)

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        self._run_sioyek(
            "--execute-command",
            "turn_on_synctex",
            "--forward-search-file",
            tex_file,
            "--forward-search-line",
            f"{line}",
            "--forward-search-column",
            f"{col}",
            "--inverse-search",
            f"{get_sublime_exe()} %1:%2",
            pdf_file,
            **kwargs
        )

    def view_file(self, pdf_file, **kwargs):
        self._run_sioyek("--new-window", pdf_file, **kwargs)

    def supports_keep_focus(self):
        return True

    def supports_platform(self, platform):
        return True
