import os
from textwrap import dedent
from unittesting import DeferrableViewTestCase

from ..latextools.utils.tex_log import parse_log_view


class ParseTexLogTestCase(DeferrableViewTestCase):
    view_settings = {
        "auto_indent": False,
        "auto_match_enabled": False,
        "draw_indent_guides": False,
        "draw_white_space": "none",
        "detect_indentation": False,
        "disable_auto_complete": False,
        "encoding": "UTF-8",
        "gutter": False,
        "line_numbers": False,
        "rulers": [],
        "syntax": "LaTeXTools Log.sublime-syntax",
        "tab_size": 2,
        "translate_tabs_to_spaces": False,
        "word_wrap": False,
    }

    def assert_tex_log_items(self, content, expected_errors, expected_warnings, expected_badboxes):
        self.setText(dedent(content))
        errors, warnings, badboxes = parse_log_view(self.view)
        self.assertEqual(expected_errors, errors)
        self.assertEqual(expected_warnings, warnings)
        self.assertEqual(expected_badboxes, badboxes)

    def test_empty(self):
        self.assert_tex_log_items(
            # content
            R"""
            This is pdfTeX, Version 3.141592653-2.6-1.40.28 (TeX Live 2025) (preloaded format=pdflatex 2025.8.8)  12 OCT 2025 12:41
            entering extended mode
             restricted \write18 enabled.
             %&-line parsing enabled.
            **main.tex
            (./main.tex
            )
            """,
            expected_errors=[],
            expected_warnings=[],
            expected_badboxes=[],
        )

    def test_emergency_stop(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex
            )
            ! Emergency stop.
            <*> \input customize.tex
            """,
            expected_errors=[],
            expected_warnings=[],
            expected_badboxes=[],
        )

    def test_wellformed_badboxes(self):
        self.assert_tex_log_items(
            R"""
            (main.tex
            Overfull \hbox (21.7862pt too wide) in paragraph at lines 19--19
            []\OT1/cmr/bx/n/14.4 English guide-lines for pub-li-ca-tion - TI-TLE HERE
            )
            """,
            expected_errors=[],
            expected_warnings=[],
            expected_badboxes=[
                Rf"main.tex:19: Overfull \hbox (21.7862pt too wide) in paragraph at lines 19--19",
            ],
        )

    def test_wellformed_exceptions(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex

            ! Undefined control sequence.
            l.8   \newinst
                          {o}{:Rounded}

            The control sequence at the end of the top line
            of your error message was never \def'ed.

            ! LaTeX Error: \begin{document} ended by \end{sequencediagram}.

            See the LaTeX manual or LaTeX Companion for explanation.
            Type  H <return>  for immediate help.
             ...

            l.9 \end{sequencediagram}

            Your command was ignored.
            Type  I <command> <return>  to replace it with another command,
            or  <return>  to continue without it.
            )
            """,
            expected_errors=[
                R"main.tex:8: Undefined control sequence near \newinst{o}{:Rounded}",
                R"main.tex:9: LaTeX Error: \begin{document} ended by \end{sequencediagram}",
            ],
            expected_warnings=[],
            expected_badboxes=[],
        )

    def test_malformed_exceptions_without_hints(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex

            ! Undefined control sequence.
            l.8   \newinst
                          {o}{:Rounded}
            ! LaTeX Error: \begin{document} ended by \end{sequencediagram}.

            See the LaTeX manual or LaTeX Companion for explanation.
            Type  H <return>  for immediate help.
             ...

            l.9 \end{sequencediagram}
            )
            """,
            expected_errors=[
                R"main.tex:8: Undefined control sequence near \newinst{o}{:Rounded}",
                R"main.tex:9: LaTeX Error: \begin{document} ended by \end{sequencediagram}",
            ],
            expected_warnings=[],
            expected_badboxes=[],
        )

    def test_malformed_exceptions_only_titles(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex
            ! Undefined control sequence.
            ! LaTeX Error: \begin{document} ended by \end{sequencediagram}.
            )
            """,
            expected_errors=[
                R"main.tex: LaTeX Error: \begin{document} ended by \end{sequencediagram}",
                R"main.tex: Undefined control sequence",
            ],
            expected_warnings=[],
            expected_badboxes=[],
        )

    def test_nested_errors(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex
            (./chapters/chapter01.tex
            Package pkgname Error: An error message on input line 10.
            ) (./chapters/chapter02.tex
            Package pkgname Error: An error message on input line 20.
            )
            Package pkgname Error: An error message on input line 1.
            )
            """,
            expected_errors=[
                f"chapters{os.sep}chapter01.tex:10: An error message on input line 10",
                f"chapters{os.sep}chapter02.tex:20: An error message on input line 20",
                "main.tex:1: An error message on input line 1",
            ],
            expected_warnings=[],
            expected_badboxes=[],
        )

    def test_linewrapped_errors_and_warnings(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex
            LaTeX Warning: Citation `KatzShnider2008' on page 17 undefined on input line 12
            29.
            LaTeX Warning: Citation `KatzShnider2008' on page 17 undefined on input line
             1230.
            LaTeX Warning: Citation `Mickelssonâ€Ž1987' on page 18 undefined on input line
            1261.
            """,
            expected_errors=[],
            expected_warnings=[
                "main.tex:1229: Citation `KatzShnider2008' on page 17 undefined"
                " on input line 1229",
                "main.tex:1230: Citation `KatzShnider2008' on page 17 undefined"
                " on input line 1230",
                "main.tex:1261: Citation `Mickelssonâ€Ž1987' on page 18 undefined on input line1261"
            ],
            expected_badboxes=[],
        )

    def test_multiline_errors_and_warnings(self):
        self.assert_tex_log_items(
            R"""
            (./main.tex
            Package hyperref Error: Option `pdfauthor' has already been used,
            (hyperref)              setting the option has no effect
            (hyperref)              on input line 13.
            Package hyperref Warning: Option `pdfauthor' has already been used,
            (hyperref)                setting the option has no effect
            (hyperref)                on input line 33.
            )
            """,
            expected_errors=[
                "main.tex:13: Option `pdfauthor' has already been used,"
                " setting the option has no effect on input line 13",
            ],
            expected_warnings=[
                "main.tex:33: Option `pdfauthor' has already been used,"
                " setting the option has no effect on input line 33",
            ],
            expected_badboxes=[],
        )

    def test_filepath_processing(self):
        self.assert_tex_log_items(
            R"""
            (main.tex
            (/absolute/path/to/A-TeX_File.tex
            Package pkgname Error: An error message on input line 5.
            )
            (\\wsl.localhost\distro/A-TeX_File.tex
            Package pkgname Error: An error message on input line 10.
            )
            (\\wsl$\localhost\distro\A-TeX_File.tex
            Package pkgname Error: An error message on input line 20.
            )
            (D:\any\folder\name\a-file.tex
            Package pkgname Error: An error message on input line 30.
            )
            ("D:\any quoted
             folder\name\a file.tex"
            Package pkgname Error: An error message on input line 40.
            )
            )
            """,
            expected_errors=[
                f"D:{os.sep}any quoted folder{os.sep}name{os.sep}a file.tex:40: An error message on input line 40",
                f"D:{os.sep}any{os.sep}folder{os.sep}name{os.sep}a-file.tex:30: An error message on input line 30",
                f"{os.sep}{os.sep}wsl${os.sep}localhost{os.sep}distro{os.sep}A-TeX_File.tex:20: An error message on input line 20",
                f"{os.sep}{os.sep}wsl.localhost{os.sep}distro{os.sep}A-TeX_File.tex:10: An error message on input line 10",
                f"{os.sep}absolute{os.sep}path{os.sep}to{os.sep}A-TeX_File.tex:5: An error message on input line 5",
            ],
            expected_warnings=[],
            expected_badboxes=[],
        )
