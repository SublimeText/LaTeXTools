import sublime

from ...latextools.utils.external_command import external_command
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from .base_viewer import BaseViewer

__all__ = ["SioyekViewer"]


class SioyekViewer(BaseViewer):

    @classmethod
    def _run_sioyek(cls, *args, **kwargs):
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

        keep_focus = kwargs.get("keep_focus", True)
        if keep_focus:
            command.append("--nofocus")

        command += args
        external_command(command, use_texpath=False, show_window=True)
        if keep_focus:
            cls.focus_st()

    @classmethod
    def forward_sync(cls, pdf_file, tex_file, line, col, **kwargs):
        cls._run_sioyek(
            "--execute-command",
            "turn_on_synctex",
            "--forward-search-file",
            tex_file,
            "--forward-search-line",
            f"{line}",
            "--forward-search-column",
            f"{col}",
            "--inverse-search",
            f'"{get_sublime_exe()}" "%1:%2"',
            pdf_file,
            **kwargs
        )

    @classmethod
    def view_file(cls, pdf_file, **kwargs):
        cls._run_sioyek("--new-window", pdf_file, **kwargs)

    @classmethod
    def supports_keep_focus(cls):
        return True

    @classmethod
    def supports_platform(cls, platform):
        return True
