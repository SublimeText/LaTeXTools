import sublime_plugin

from .latextools_utils import get_setting
from .latextools_utils.is_tex_file import is_tex_file

LATEX_SYNTAX = 'Packages/LaTeX/LaTeX.sublime-syntax'


class TeXSyntaxListener(sublime_plugin.EventListener):
    def on_load(self, view):
        self.detect_and_apply_syntax(view)

    def on_post_save(self, view):
        self.detect_and_apply_syntax(view)

    def detect_and_apply_syntax(self, view):
        if view.is_scratch() or not view.file_name():
            return

        if view.score_selector(0, "text.tex"):
            return

        if not get_setting('latextools_set_syntax', True):
            return

        file_name = view.file_name()
        if is_tex_file(file_name):
            view.set_syntax_file(LATEX_SYNTAX)
