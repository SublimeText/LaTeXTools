import sublime_plugin

from .utils.settings import get_setting

__all__ = ["BibLaTeXSyntaxListener"]

BIBLATEX_SYNTAX = "Packages/LaTeXTools/BibLaTeX.sublime-syntax"


# simple listener to default bib files to BibLaTeX syntax if the
# `use_biblatex` configuration option has been set in either the user's
# LaTeXTools.sublime-settings or the current project settings
class BibLaTeXSyntaxListener(sublime_plugin.EventListener):
    def on_load(self, view):
        self.detect_and_apply_syntax(view)

    def on_post_save(self, view):
        self.detect_and_apply_syntax(view)

    def detect_and_apply_syntax(self, view):
        if view.is_scratch() or not view.file_name():
            return

        current_syntax = view.settings().get("syntax")
        if current_syntax == BIBLATEX_SYNTAX:
            return

        if not get_setting("use_biblatex", False, view):
            return

        file_name = view.file_name()
        if file_name.endswith("bib"):
            view.set_syntax_file(BIBLATEX_SYNTAX)
