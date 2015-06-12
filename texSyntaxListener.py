import sublime_plugin

try:
    from latextools_utils.is_tex_file import is_tex_file
except ImportError:
    from .latextools_utils.is_tex_file import is_tex_file

LATEX_SYNTAX = 'Packages/LaTeX/LaTeX.tmLanguage'

class TeXSyntaxListener(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.is_scratch() or not view.file_name():
            return

        current_syntax = view.settings().get('syntax')
        if current_syntax == LATEX_SYNTAX:
            return

        file_name = view.file_name()
        if is_tex_file(file_name):
            view.set_syntax_file(LATEX_SYNTAX)
