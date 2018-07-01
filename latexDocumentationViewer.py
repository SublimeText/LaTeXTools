import traceback

import sublime
import sublime_plugin

from .latextools_utils.distro_utils import using_miktex
from .latextools_utils.external_command import external_command


def _view_texdoc(file):
    if file is None:
        raise Exception('File must be specified')
    if not isinstance(file, str):
        raise TypeError('File must be a string')

    command = ['texdoc']
    if using_miktex():
        command.append('--view')
    command.append(file)

    try:
        external_command(command)
    except OSError:
        traceback.print_exc()
        sublime.error_message(
            'Could not run texdoc. Please ensure that your texpath setting '
            'is configured correctly in the LaTeXTools settings.')


class LatexPkgDocCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window

        def _on_done(file):
            if (
                file is not None and
                isinstance(file, str) and
                file != ''
            ):
                window.run_command('latex_view_doc', {'file': file})

        window.show_input_panel(
            'View documentation for which package?',
            '',
            _on_done,
            None,
            None
        )


class LatexViewDocCommand(sublime_plugin.WindowCommand):
    def run(self, file):
        _view_texdoc(file)

    def is_visible(self):
        return False  # hide this from menu
