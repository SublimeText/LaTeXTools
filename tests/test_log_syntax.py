import sublime
from pathlib import Path
from unittesting import DeferrableViewTestCase

from ._data_decorator import data_decorator, data


@data_decorator
class AssignLogSyntaxTestCase(DeferrableViewTestCase):
    """
    This class describes an assign log syntax test case.

    Verify `LatextoolsExecEventListener.on_load()` assigns `LaTeXTools Log`
    syntax definition to *.log files starting with certain lines.
    """

    @data(
        (
            (
                "luatex",
                "LuaTeX.log",
            ),
            (
                "pdftex",
                "pdfTeX.log",
            ),
            (
                "xetex",
                "XeTeX.log",
            ),
        ),
        first_param_name_suffix=True,
    )
    def assign_syntax(self, filename):
        view = self.window.open_file(
            str(Path(__file__).parent.joinpath("fixtures", "logfile", filename)),
            flags=sublime.NewFileFlags.TRANSIENT | sublime.NewFileFlags.FORCE_CLONE,
        )
        try:
            view.set_scratch(True)
            yield lambda: not view.is_loading()
            self.assertEqual(view.settings().get("syntax"), "LaTeXTools Log.sublime-syntax")
        finally:
            view.close()
