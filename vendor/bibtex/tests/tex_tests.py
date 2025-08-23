from ..tex import tokenize_list

import unittest


class TestTokenizeList(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(tokenize_list("Chemicals and Entrails"), ["Chemicals", "Entrails"])

    def test_nbsp(self):
        self.assertEqual(tokenize_list("Chemicals~and~Entrails"), ["Chemicals", "Entrails"])

    def test_values_wrapped_in_brackets(self):
        self.assertEqual(tokenize_list("{Chemicals and Entrails}"), ["{Chemicals and Entrails}"])

    def test_and_wrapped_in_brackets(self):
        self.assertEqual(tokenize_list("Chemicals {and} Entrails"), ["Chemicals {and} Entrails"])

    def test_and_wrapped_in_brackets_with_whitespace(self):
        self.assertEqual(
            tokenize_list("Chemicals { and } Entrails"), ["Chemicals { and } Entrails"]
        )

    def test_partial_list(self):
        self.assertEqual(tokenize_list("Chemicals and"), ["Chemicals"])

    def test_changing_and(self):
        self.assertEqual(
            tokenize_list("Chemikalien und Eingeweide", _and="und"), ["Chemikalien", "Eingeweide"]
        )

    def test_multiple_separators_no_entry(self):
        self.assertEqual(tokenize_list("Chemicals and and Entrails"), ["Chemicals", "Entrails"])
