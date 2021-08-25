import os

import sublime
import sublime_plugin

from .latextools_utils.settings import get_setting
from .latextools_utils.tex_directives import get_tex_root
from .latextools_utils.output_directory import (
    get_output_directory, get_aux_directory
)


class LatextoolsRevealAuxDirectoryCommand(sublime_plugin.WindowCommand):
    """
    Reveal the aux directory of the current document in the default
    file browser.
    """

    def is_visible(self, *args):
        view = self.window.active_view()
        if not view.score_selector(0, "text.tex.latex"):
            return False
        return bool(get_setting("aux_directory"))

    def run(self):
        window = self.window
        view = window.active_view()
        folder_path = get_aux_directory(view)
        if not folder_path:
            message = "'aux directory' not found"
            print(message)
            sublime.error_message(message)
            return
        if not os.path.exists(folder_path):
            message = (
                "'aux directory' does not exist: '{}'"
                .format(folder_path)
            )
            print(message)
            sublime.error_message(message)
            return

        print("open folder '{}'".format(folder_path))
        window.run_command("open_dir", {"dir": folder_path})


class LatextoolsRevealOutputDirectoryCommand(sublime_plugin.WindowCommand):
    """
    Reveal the output directory of the current document in the default
    file browser.
    """

    def is_visible(self, *args):
        view = self.window.active_view()
        if not view.score_selector(0, "text.tex.latex"):
            return False
        return bool(get_setting("output_directory"))

    def run(self):
        window = self.window
        view = window.active_view()
        folder_path = get_output_directory(view)
        if not folder_path:
            message = "'output directory' not found"
            print(message)
            sublime.error_message(message)
            return
        if not os.path.exists(folder_path):
            message = (
                "'output directory' does not exist: '{}'"
                .format(folder_path)
            )
            print(message)
            sublime.error_message(message)
            return

        print("open folder '{}'".format(folder_path))
        window.run_command("open_dir", {"dir": folder_path})


class LatextoolsRevealTexRootDirectoryCommand(sublime_plugin.WindowCommand):
    """
    Reveal the tex root directory of the current document in the default
    file browser.
    """

    def is_visible(self, *args):
        view = self.window.active_view()
        return bool(view.score_selector(0, "text.tex.latex"))

    def run(self):
        window = self.window
        view = window.active_view()
        tex_root = get_tex_root(view)
        if not tex_root:
            return
        folder_path, file_path = os.path.split(tex_root)

        print("open folder '{}', file: {}".format(folder_path, file_path))
        window.run_command("open_dir", {"dir": folder_path, "file": file_path})
