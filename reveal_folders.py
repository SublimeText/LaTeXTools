import os

import sublime
import sublime_plugin

from .latextools_utils.output_directory import get_aux_directory
from .latextools_utils.output_directory import get_output_directory
from .latextools_utils.logger import logger
from .latextools_utils.settings import get_setting
from .latextools_utils.tex_directives import get_tex_root


class LatextoolsRevealAuxDirectoryCommand(sublime_plugin.WindowCommand):
    """
    Reveal the aux directory of the current document in the default
    file browser.
    """

    def is_visible(self, *args):
        view = self.window.active_view()
        return (
            view and view.match_selector(0, "text.tex.latex")
            and bool(get_setting("aux_directory"))
        )

    def run(self):
        window = self.window
        view = window.active_view()
        folder = get_aux_directory(view)
        if not folder:
            message = "'aux directory' not found"
            logger.error(message)
            sublime.error_message(message)
            return
        if not os.path.isdir(folder):
            message = "'aux directory' does not exist: '{}'".format(folder)
            logger.error(message)
            sublime.error_message(message)
            return

        logger.debug("open folder '%s'", folder)
        window.run_command("open_dir", {"dir": folder})


class LatextoolsRevealOutputDirectoryCommand(sublime_plugin.WindowCommand):
    """
    Reveal the output directory of the current document in the default
    file browser.
    """

    def is_visible(self, *args):
        view = self.window.active_view()
        return (
            view and view.match_selector(0, "text.tex.latex")
            and bool(get_setting("output_directory"))
        )

    def run(self):
        window = self.window
        view = window.active_view()
        folder = get_output_directory(view)
        if not folder:
            message = "'output directory' not found"
            logger.error(message)
            sublime.error_message(message)
            return
        if not os.path.isdir(folder):
            message = "'output directory' does not exist: '{}'" .format(folder)
            logger.error(message)
            sublime.error_message(message)
            return

        logger.debug("open folder '%s'", folder)
        window.run_command("open_dir", {"dir": folder})


class LatextoolsRevealTexRootDirectoryCommand(sublime_plugin.WindowCommand):
    """
    Reveal the tex root directory of the current document in the default
    file browser.
    """

    def is_visible(self, *args):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self):
        window = self.window
        view = window.active_view()
        tex_root = get_tex_root(view)
        if not tex_root:
            return
        folder, file = os.path.split(tex_root)

        logger.debug("open folder '%s', file: %s", folder, file)
        window.run_command("open_dir", {"dir": folder, "file": file})
