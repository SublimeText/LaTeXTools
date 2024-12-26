import traceback

import sublime
import sublime_plugin

from .deprecated_command import deprecate
from .utils.distro_utils import using_miktex
from .utils.external_command import external_command

__all__ = ["LatextoolsPkgDocCommand", "LatextoolsViewDocCommand"]


def _view_texdoc(file):
    if file is None:
        raise Exception("File must be specified")
    if not isinstance(file, str):
        raise TypeError("File must be a string")

    command = ["texdoc"]
    if using_miktex():
        command.append("--view")
    command.append(file)

    try:
        external_command(command)
    except OSError:
        traceback.print_exc()
        sublime.error_message(
            "Could not run texdoc. Please ensure that your texpath setting "
            "is configured correctly in the LaTeXTools settings."
        )


class LatextoolsPkgDocCommand(sublime_plugin.WindowCommand):
    def run(self):
        def _on_done(file):
            if file and isinstance(file, str):
                self.window.run_command("latextools_view_doc", {"file": file})

        self.window.show_input_panel(
            "View documentation for which package?", "", _on_done, None, None
        )


class LatextoolsViewDocCommand(sublime_plugin.WindowCommand):
    def run(self, file):
        _view_texdoc(file)

    def is_visible(self):
        return False  # hide this from menu


deprecate(globals(), "LatexPkgDocCommand", LatextoolsPkgDocCommand)
deprecate(globals(), "LatexViewDocCommand", LatextoolsViewDocCommand)
