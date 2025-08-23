from __future__ import annotations

from ...latextools.latextools_plugin import LaTeXToolsPlugin
from ...latextools.utils import sublime_utils as st_utils

__all__ = ["BaseViewer"]


class BaseViewer(LaTeXToolsPlugin):
    """
    This class describes a base viewer.

    Note: Most methods take a kwargs variable, which currently only consists
          of the `keep_focus` setting
    """

    def forward_sync(self, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        """
        command to jump to the file at a specified line and column

        if this raises a NotImplementedError, we will fallback to
        invoking view_file

        :params:
            pdf_file - full path to the generated pdf
            tex_file - full path to the tex file of the active view
            line - indicates the line number in the tex file (1-based)
            col - incidates the column number in the tex file (1-based)
            **kwargs:
                keep_focus - if true, focus should return to ST
        """
        raise NotImplementedError()

    def view_file(self, pdf_file: str, **kwargs) -> None:
        """
        command to open a file

        :params:
            pdf_file - full path to the generated pdf
        """
        raise NotImplementedError()

    def supports_keep_focus(self) -> bool:
        """
        return True to indicate that this plugin supports the keep_focus
        setting or False (the default) to use the default refocus
        implementation
        """
        return False

    def supports_platform(self, platform: str) -> bool:
        """
        return True to indicate that this plugin supports the reported
        platform or False to indicate that it is not supported in the
        current platform / environment
        """
        return True

    def focus_st(self) -> None:
        st_utils.focus_st()
