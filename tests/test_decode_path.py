import os
from unittest import TestCase

from LaTeXTools.latextools.utils.analysis import decode_path


class DecodePathTest(TestCase):
    def test_relative(self):
        self.assertEqual(
            os.path.normpath("bibs/main.bib"),
            decode_path("bibs/main.bib")
        )

    def test_relative_string(self):
        self.assertEqual(
            os.path.normpath("bibs/main.bib"),
            decode_path("bibs\\string/main.bib")
        )

    def test_join_basepath(self):
        self.assertEqual(
            os.path.normpath("any/base/folder/bibs/main.bib"),
            decode_path("bibs/main.bib", "any/base/folder")
        )

    def test_expand_home(self):
        self.assertEqual(
            os.path.normpath(os.path.expanduser("~/bibs/main.bib")),
            decode_path("\\string~/bibs/main.bib")
        )

    def test_expand_home_ignores_base(self):
        self.assertEqual(
            os.path.normpath(os.path.expanduser("~/bibs/main.bib")),
            decode_path("\\string~/bibs/main.bib", "/any/path")
        )
