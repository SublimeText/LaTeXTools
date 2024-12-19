from unittest import TestCase

import sublime

from LaTeXTools.context_provider import LatextoolsContextListener


class ContextTest(TestCase):
    def setUp(self):
        self.context = LatextoolsContextListener()
        self.view = sublime.active_window().new_file()
        self.view.set_syntax_file("Packages/LaTeX/LaTeX.sublime-syntax")
        self.view.settings().set("auto_indent", False)
        self.view.set_scratch(True)

    def tearDown(self):
        if self.view:
            self.view.close()
            self.view = None

    def query_context(self, key, operator=sublime.OP_EQUAL, operand=True,
                      match_all=False):
        return self.context.on_query_context(
            self.view, key, operator, operand, match_all)

    def set_content(self, content):
        self.view.run_command("select_all")
        self.view.run_command("insert", {"characters": content})

    def set_sel(self, regions):
        if not hasattr(regions, "__iter__"):
            regions = [regions]
        regions = [
            sublime.Regions(r) if isinstance(r, int) else r
            for r in regions
        ]
        self.view.sel().clear()
        self.view.sel().add_all(regions)

    def test_version(self):
        version = int(sublime.version())
        ctx = "latextools.st_version"
        self.assertTrue(
            self.query_context(ctx, operand=">={}".format(version)))
        self.assertTrue(
            self.query_context(ctx, operand="={}".format(version)))
        self.assertFalse(
            self.query_context(ctx, operand="<{}".format(version)))
        self.assertTrue(
            self.query_context(ctx, operand="<{}".format(version + 1)))
        self.assertTrue(
            self.query_context(ctx, operand="<={}".format(version + 1)))
        self.assertFalse(
            self.query_context(ctx, operand="<={}".format(version - 1)))

    def test_documentclass(self):
        ctx = "latextools.documentclass"
        self.set_content("\\documentclass{article}")
        self.assertTrue(self.query_context(
            ctx, operator=sublime.OP_REGEX_MATCH, operand="article|beamer"))
        self.assertTrue(self.query_context(ctx, operand="article"))
        self.assertFalse(self.query_context(ctx, operand="beamer"))

    def test_usepackage(self):
        ctx = "latextools.usepackage"
        content = sublime.load_resource(
            "Packages/LaTeXTools/tests/test_context_document.tex")
        self.set_content(content)
        self.assertTrue(self.query_context(ctx, operand="babel"))
        self.assertTrue(self.query_context(ctx, operand="amsmath"))
        self.assertFalse(self.query_context(ctx, operand="amsfonts"))

        operand = "\\b(mathtools|amsmath)\\b"
        self.assertTrue(self.query_context(
            ctx, operator=sublime.OP_REGEX_CONTAINS, operand=operand))

        self.assertTrue(self.query_context(ctx, operand="xcolor"))
        self.assertFalse(self.query_context(ctx, operand="color"))
        operand = "\\bx?color\\b"
        self.assertTrue(self.query_context(
            ctx, operator=sublime.OP_REGEX_CONTAINS, operand=operand))
        operand = "\\bx?color\\b"
        self.assertFalse(self.query_context(
            ctx, operator=sublime.OP_NOT_REGEX_CONTAINS, operand=operand))

    def test_env_selector(self):
        ctx = "latextools.env_selector"
        content = sublime.load_resource(
            "Packages/LaTeXTools/tests/test_context_document.tex")
        self.set_content(content)
        self.set_sel(self.view.find(r"<1>", 0))
        self.assertTrue(self.query_context(ctx, operand=""))
        self.assertTrue(self.query_context(ctx, operand=", none"))
        self.assertTrue(self.query_context(ctx, operand="document"))
        self.assertTrue(self.query_context(ctx, operand="document!"))
        self.assertTrue(self.query_context(ctx, operand="document^"))
        self.assertTrue(self.query_context(ctx, operand="-(align, equation)"))

        self.set_sel(self.view.find(r"<2>", 0))
        self.assertTrue(self.query_context(
            ctx, operand="document itemize - (align, equation)"))

        self.set_sel(self.view.find(r"<3>", 0))
        self.assertTrue(self.query_context(
            ctx, operand="(document itemize & align) - (equation)"))

        self.set_sel(self.view.find(r"<4>", 0))
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

        self.set_sel(self.view.find(r"<1>", 0))
        self.view.sel().add(self.view.find(r"<2>", 0))
        self.assertTrue(self.query_context(
            ctx, operand="document itemize", match_all=False))
        self.assertFalse(self.query_context(
            ctx, operand="document itemize", match_all=True))

    def test_command_selector(self):
        ctx = "latextools.command_selector"
        content = sublime.load_resource(
            "Packages/LaTeXTools/tests/test_context_document.tex")
        self.set_content(content)
        self.set_sel(self.view.find(r"<c1>", 0))
        self.assertTrue(self.query_context(ctx, operand=""))
        self.assertTrue(self.query_context(ctx, operand=", none"))
        self.assertTrue(self.query_context(ctx, operand="first"))
        self.assertTrue(self.query_context(ctx, operand="first second"))
        self.assertTrue(self.query_context(ctx, operand="second^"))
        self.assertTrue(self.query_context(ctx, operand="first^ second^"))

        self.set_sel(self.view.find(r"<c2>", 0))
        self.assertTrue(self.query_context(ctx, operand="first second^"))

        self.set_sel(self.view.find(r"<c3>", 0))
        self.assertTrue(self.query_context(ctx, operand="graphicspath"))

        self.set_sel(self.view.find(r"<c4>", 0))
        self.assertTrue(self.query_context(ctx, operand="ensuremath"))
        self.assertFalse(self.query_context(
            ctx, operand="ensuremath - textnormal"))

        self.set_sel(self.view.find(r"<c5>", 0))
        self.assertTrue(self.query_context(ctx, operand="starcommand"))
        self.assertTrue(self.query_context(ctx, operand="starcommand second"))
        self.assertTrue(self.query_context(ctx, operand="starcommand*"))
        self.assertFalse(self.query_context(ctx, operand="starcommand!"))

        self.set_sel(self.view.find(r"<c6>", 0))
        self.assertTrue(self.query_context(ctx, operand="cmd"))
        self.assertTrue(self.query_context(ctx, operand="cmd cmd"))
        self.assertTrue(self.query_context(ctx, operand="cmd*"))
        self.assertTrue(self.query_context(ctx, operand="cmd!"))
        self.assertTrue(self.query_context(ctx, operand="cmd!^"))
        self.assertFalse(self.query_context(ctx, operand="cmd*^"))
        self.assertTrue(self.query_context(ctx, operand="cmd*^ cmd!^"))
