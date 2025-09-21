from __future__ import annotations
from unittesting import ViewTestCase

import sublime

from LaTeXTools.latextools.context_provider import LatextoolsContextListener


class ContextTest(ViewTestCase):
    view_settings = {
        "auto_indent": False,
        "syntax": "Packages/LaTeX/LaTeX.sublime-syntax",
    }

    def setUp(self):
        self.context = LatextoolsContextListener()
        super().setUp()

    def query_context(
        self,
        key: str,
        operator=sublime.OP_EQUAL,
        operand: bool | float | int | str = True,
        match_all=False,
    ):
        return self.context.on_query_context(self.view, key, operator, operand, match_all)

    def set_sel(self, regions):
        if not hasattr(regions, "__iter__"):
            regions = [regions]
        self.view.sel().clear()
        self.view.sel().add_all(regions)

    def test_version(self):
        ctx = "latextools.st_version"
        ver = int(sublime.version())
        self.assertTrue(self.query_context(ctx, operand=f">={ver}"))
        self.assertTrue(self.query_context(ctx, operand=f"={ver}"))
        self.assertFalse(self.query_context(ctx, operand=f"<{ver}"))
        self.assertTrue(self.query_context(ctx, operand=f"<{ver + 1}"))
        self.assertTrue(self.query_context(ctx, operand=f"<={ver + 1}"))
        self.assertFalse(self.query_context(ctx, operand=f"<={ver - 1}"))

    def test_documentclass(self):
        ctx = "latextools.documentclass"
        yield self.setText("\\documentclass{article}")

        self.assertTrue(
            self.query_context(ctx, operator=sublime.OP_REGEX_MATCH, operand="article|beamer")
        )
        self.assertTrue(self.query_context(ctx, operand="article"))
        self.assertFalse(self.query_context(ctx, operand="beamer"))

    def test_usepackage(self):
        ctx = "latextools.usepackage"
        content = sublime.load_resource("Packages/LaTeXTools/tests/fixtures/context/main.tex")
        yield self.setText(content)
        self.assertTrue(self.query_context(ctx, operand="babel"))
        self.assertTrue(self.query_context(ctx, operand="amsmath"))
        self.assertFalse(self.query_context(ctx, operand="amsfonts"))

        operand = "\\b(mathtools|amsmath)\\b"
        self.assertTrue(
            self.query_context(ctx, operator=sublime.OP_REGEX_CONTAINS, operand=operand)
        )

        self.assertTrue(self.query_context(ctx, operand="xcolor"))
        self.assertFalse(self.query_context(ctx, operand="color"))
        operand = "\\bx?color\\b"
        self.assertTrue(
            self.query_context(ctx, operator=sublime.OP_REGEX_CONTAINS, operand=operand)
        )
        operand = "\\bx?color\\b"
        self.assertFalse(
            self.query_context(ctx, operator=sublime.OP_NOT_REGEX_CONTAINS, operand=operand)
        )

    def test_env_selector(self):
        ctx = "latextools.env_selector"
        content = sublime.load_resource("Packages/LaTeXTools/tests/fixtures/context/main.tex")
        self.setText(content)
        yield self.set_sel(self.view.find(r"<1>", 0))
        self.assertTrue(self.query_context(ctx, operand=""))
        self.assertTrue(self.query_context(ctx, operand=", none"))
        self.assertTrue(self.query_context(ctx, operand="document"))
        self.assertTrue(self.query_context(ctx, operand="document!"))
        self.assertTrue(self.query_context(ctx, operand="document^"))
        self.assertTrue(self.query_context(ctx, operand="-(align, equation)"))

        yield self.set_sel(self.view.find(r"<2>", 0))
        self.assertTrue(self.query_context(ctx, operand="document itemize - (align, equation)"))

        yield self.set_sel(self.view.find(r"<3>", 0))
        self.assertTrue(self.query_context(ctx, operand="(document itemize & align) - (equation)"))

        yield self.set_sel(self.view.find(r"<4>", 0))
        operand = "document itemize & itemize itemize"
        self.assertTrue(self.query_context(ctx, operand=operand))
        operand = "document itemize & itemize itemize itemize"
        self.assertFalse(self.query_context(ctx, operand=operand))
        operand = "document itemize & itemize itemize - enumerate"
        self.assertFalse(self.query_context(ctx, operand=operand))
        operand = "document itemize env, itemize itemize - enumerate itemize"
        self.assertTrue(self.query_context(ctx, operand=operand))

        operand = "description^"
        self.assertTrue(self.query_context(ctx, operand=operand))
        operand = "description!^"
        self.assertTrue(self.query_context(ctx, operand=operand))
        operand = "document enumerate^ description^"
        self.assertTrue(self.query_context(ctx, operand=operand))
        operand = "itemize^ enumerate"
        self.assertTrue(self.query_context(ctx, operand=operand))
        operand = "itemize^ enumerate^"
        self.assertFalse(self.query_context(ctx, operand=operand))

        yield self.set_sel(self.view.find(r"<1>", 0))
        yield self.view.sel().add(self.view.find(r"<2>", 0))

        self.assertTrue(self.query_context(ctx, operand="document itemize", match_all=False))
        self.assertFalse(self.query_context(ctx, operand="document itemize", match_all=True))

    def test_command_selector(self):
        ctx = "latextools.command_selector"
        content = sublime.load_resource("Packages/LaTeXTools/tests/fixtures/context/main.tex")
        self.setText(content)
        yield self.set_sel(self.view.find(r"<c1>", 0))
        self.assertTrue(self.query_context(ctx, operand=""))
        self.assertTrue(self.query_context(ctx, operand=", none"))
        self.assertTrue(self.query_context(ctx, operand="first"))
        self.assertTrue(self.query_context(ctx, operand="first second"))
        self.assertTrue(self.query_context(ctx, operand="second^"))
        self.assertTrue(self.query_context(ctx, operand="first^ second^"))

        yield self.set_sel(self.view.find(r"<c2>", 0))
        self.assertTrue(self.query_context(ctx, operand="first second^"))

        yield self.set_sel(self.view.find(r"<c3>", 0))
        self.assertTrue(self.query_context(ctx, operand="graphicspath"))

        yield self.set_sel(self.view.find(r"<c4>", 0))
        self.assertTrue(self.query_context(ctx, operand="ensuremath"))
        self.assertFalse(self.query_context(ctx, operand="ensuremath - textnormal"))

        yield self.set_sel(self.view.find(r"<c5>", 0))
        self.assertTrue(self.query_context(ctx, operand="starcommand"))
        self.assertTrue(self.query_context(ctx, operand="starcommand second"))
        self.assertTrue(self.query_context(ctx, operand="starcommand*"))
        self.assertFalse(self.query_context(ctx, operand="starcommand!"))

        yield self.set_sel(self.view.find(r"<c6>", 0))
        self.assertTrue(self.query_context(ctx, operand="cmd"))
        self.assertTrue(self.query_context(ctx, operand="cmd cmd"))
        self.assertTrue(self.query_context(ctx, operand="cmd*"))
        self.assertTrue(self.query_context(ctx, operand="cmd!"))
        self.assertTrue(self.query_context(ctx, operand="cmd!^"))
        self.assertFalse(self.query_context(ctx, operand="cmd*^"))
        self.assertTrue(self.query_context(ctx, operand="cmd*^ cmd!^"))
