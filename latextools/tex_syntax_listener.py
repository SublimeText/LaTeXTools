import sublime_plugin

from .utils.settings import get_setting
from .utils.is_tex_file import is_tex_file

__all__ = ["TeXSyntaxListener"]


class TeXSyntaxListener(sublime_plugin.EventListener):
    def on_load(self, view):
        self.detect_and_apply_syntax(view)

    def on_post_save(self, view):
        self.detect_and_apply_syntax(view)

    def detect_and_apply_syntax(self, view):
        if view.is_scratch() or not view.file_name():
            return

        if view.match_selector(0, "text.tex"):
            return

        if not get_setting("latextools_set_syntax", True, view):
            return

        file_name = view.file_name()
        if is_tex_file(file_name):
            view.set_syntax_file("Packages/LaTeX/LaTeX.sublime-syntax")
