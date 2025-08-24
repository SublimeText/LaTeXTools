from __future__ import annotations
from typing import cast

from ...latextools.latextools_plugin import LaTeXToolsPlugin
from ...latextools.utils import sublime_utils as st_utils
from ...latextools.utils.settings import get_setting

__all__ = ["BaseViewer"]


class BaseViewer(LaTeXToolsPlugin):
    """
    This class describes a base viewer.

    Note: Most methods take a kwargs variable, which currently only consists
          of the `keep_focus` setting
    """

    @classmethod
    def forward_sync(cls, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
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

    @classmethod
    def view_file(cls, pdf_file: str, **kwargs) -> None:
        """
        command to open a file

        :params:
            pdf_file - full path to the generated pdf
        """
        raise NotImplementedError()

    @classmethod
    def supports_keep_focus(cls) -> bool:
        """
        return True to indicate that this plugin supports the keep_focus
        setting or False (the default) to use the default refocus
        implementation
        """
        return False

    @classmethod
    def supports_platform(cls, platform: str) -> bool:
        """
        return True to indicate that this plugin supports the reported
        platform or False to indicate that it is not supported in the
        current platform / environment
        """
        return True

    @staticmethod
    def focus_st() -> None:
        st_utils.focus_st()

    @staticmethod
    def viewer_settings() -> dict:
        return cast(dict, get_setting("viewer_settings", {}))
