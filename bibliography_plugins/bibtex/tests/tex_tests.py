from ..tex import tokenize_list

import unittest


class TestTokenizeList(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(
            tokenize_list(u'Chemicals and Entrails'),
            [u'Chemicals', u'Entrails']
        )

    def test_nbsp(self):
        self.assertEqual(
            tokenize_list(u'Chemicals~and~Entrails'),
            [u'Chemicals', u'Entrails']
        )

    def test_values_wrapped_in_brackets(self):
        self.assertEqual(
            tokenize_list(u'{Chemicals and Entrails}'),
            [u'{Chemicals and Entrails}']
        )

    def test_and_wrapped_in_brackets(self):
        self.assertEqual(
            tokenize_list(u'Chemicals {and} Entrails'),
            [u'Chemicals {and} Entrails']
        )

    def test_and_wrapped_in_brackets_with_whitespace(self):
        self.assertEqual(
            tokenize_list(u'Chemicals { and } Entrails'),
            [u'Chemicals { and } Entrails']
        )

    def test_partial_list(self):
        self.assertEqual(
            tokenize_list(u'Chemicals and'),
            [u'Chemicals']
        )

    def test_changing_and(self):
        self.assertEqual(
            tokenize_list(u'Chemikalien und Eingeweide', _and='und'),
            [u'Chemikalien', u'Eingeweide']
        )

    def test_multiple_separators_no_entry(self):
        self.assertEqual(
            tokenize_list(u'Chemicals and and Entrails'),
            [u'Chemicals', u'Entrails']
        )
