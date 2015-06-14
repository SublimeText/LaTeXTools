import sublime
import sublime_plugin

try:
    from latextools_utils.is_tex_file import is_tex_file
except ImportError:
    from .latextools_utils.is_tex_file import is_tex_file

LATEX_SYNTAX = 'Packages/LaTeX/LaTeX.tmLanguage'

class TeXSyntaxListener(sublime_plugin.EventListener):
    def on_load(self, view):
        self.detect_and_apply_syntax(view)

    def on_post_save(self, view):
        self.detect_and_apply_syntax(view)

    def detect_and_apply_syntax(self, view):
        if view.is_scratch() or not view.file_name():
            return

        current_syntax = view.settings().get('syntax')
        if current_syntax == LATEX_SYNTAX:
            return

        global_settings = sublime.load_settings('LaTeXTools.sublime-settings')
        if not view.settings().get('latextools_set_syntax',
            global_settings.get('latextools_set_syntax', True)):
            return

        file_name = view.file_name()
        if is_tex_file(file_name):
            view.set_syntax_file(LATEX_SYNTAX)
