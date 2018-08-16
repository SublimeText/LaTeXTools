# coding=utf-8
from ..names import tokenize_name, Name, NameResult

import unittest


class TestTokenizeName(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(
            tokenize_name(u'Coddlington, Simon'),
            NameResult(first='Simon', middle='', prefix='', last='Coddlington', generation='')
        )

    def test_with_nbsp(self):
        self.assertEqual(
            tokenize_name(u'Coddlington,~Simon'),
            NameResult(first='Simon', middle='', prefix='', last='Coddlington', generation='')
        )

    def test_without_comma(self):
        self.assertEqual(
            tokenize_name(u'Simon Coddlington'),
            NameResult(first='Simon', middle='', prefix='', last='Coddlington', generation='')
        )

    def test_without_comma_with_nbsp(self):
        self.assertEqual(
            tokenize_name(u'Simon~Coddlington'),
            NameResult(first='Simon', middle='', prefix='', last='Coddlington', generation='')
        )

    def test_middle_name(self):
        self.assertEqual(
            tokenize_name(u'Coddlington, Simon P.'),
            NameResult(first='Simon', middle='P.', prefix='', last='Coddlington', generation='')
        )

    def test_middle_name_without_comma(self):
        self.assertEqual(
            tokenize_name(u'Simon P. Coddlington'),
            NameResult(first='Simon', middle='P.', prefix='', last='Coddlington', generation='')
        )

    def test_middle_name_with_nbsp(self):
        self.assertEqual(
            tokenize_name(u'Coddlington, Simon~P.'),
            NameResult(first='Simon', middle='P.', prefix='', last='Coddlington', generation='')
        )

    def test_multiple_middle_names(self):
        self.assertEqual(
            tokenize_name(u'Quine, Willard van Orman'),
            NameResult(first='Willard', middle='van Orman', prefix='', last='Quine', generation='')
        )

    def test_multiple_middle_names_without_comma(self):
        self.assertEqual(
            tokenize_name(u'Willard van Orman Quine'),
            NameResult(first='Willard', middle='', prefix='van', last='Orman Quine', generation='')
        )

    def test_single_name_only(self):
        self.assertEqual(
            tokenize_name(u'Augustine'),
            NameResult(first='Augustine', middle='', prefix='', last='', generation='')
        )

    def test_generation(self):
        # NB as with Bib(La)TeX, generations are only supported using commas
        self.assertEqual(
            tokenize_name(u'Jones, Jr, James Earl'),
            NameResult(first='James', middle='Earl', prefix='', last='Jones', generation='Jr')
        )

    def test_hyphenated_first_name(self):
        self.assertEqual(
            tokenize_name(u'Sartre, Jean-Paul'),
            NameResult(first='Jean-Paul', middle='', prefix='', last='Sartre', generation='')
        )

    def test_hyphenated_surname(self):
        self.assertEqual(
            tokenize_name(u'Jean Charles-Gabriel'),
            NameResult(first='Jean', middle='', prefix='', last='Charles-Gabriel', generation='')
        )

    def test_prefixed_surname(self):
        self.assertEqual(
            tokenize_name(u'van Houten, James'),
            NameResult(first='James', middle='', prefix='van', last='Houten', generation='')
        )

    def test_prefixed_surname_without_comma(self):
        self.assertEqual(
            tokenize_name(u'James van Houten'),
            NameResult(first='James', middle='', prefix='van', last='Houten', generation='')
        )

    def test_long_prefixed_surname(self):
        self.assertEqual(
            tokenize_name(u'van auf der Rissen, Gloria'),
            NameResult(first='Gloria', middle='', prefix='van auf der', last='Rissen', generation='')
        )

    def test_long_prefixed_surname_without_comma(self):
        self.assertEqual(
            tokenize_name(u'Gloria van auf der Rissen'),
            NameResult(first='Gloria', middle='', prefix='van auf der', last='Rissen', generation='')
        )

    def test_compound_last_name(self):
        self.assertEqual(
            tokenize_name(u'Pedro {Almodóvar Caballero}'),
            NameResult(first='Pedro', middle='', prefix='', last=u'{Almodóvar Caballero}', generation='')
        )

    def test_compound_last_name_with_comma(self):
        self.assertEqual(
            tokenize_name(u'{Almodóvar Caballero}, Pedro'),
            NameResult(first='Pedro', middle='', prefix='', last=u'{Almodóvar Caballero}', generation='')
        )

    def test_compound_last_name_with_comma_without_brackets(self):
        self.assertEqual(
            tokenize_name(u'Almodóvar Caballero, Pedro'),
            NameResult(first='Pedro', middle='', prefix='', last=u'Almodóvar Caballero', generation='')
        )

    def test_complex_name(self):
        self.assertEqual(
            tokenize_name(u'de la Vall{\\\'e}e~Poussin, Jean Charles~Gabriel'),
            NameResult(first='Jean', middle='Charles Gabriel', prefix='de la', last="Vall{\\'e}e Poussin", generation='')
        )

    def test_complex_name_without_comma(self):
        self.assertEqual(
            tokenize_name(u'Jean Charles~Gabriel de la Vall{\\\'e}e~Poussin'),
            NameResult(first='Jean', middle='Charles Gabriel', prefix='de la', last="Vall{\\'e}e Poussin", generation='')
        )

    def test_complex_name_with_unicode(self):
        self.assertEqual(
            tokenize_name(u'Jean Charles~Gabriel de la Vallée~Poussin'),
            NameResult(first='Jean', middle='Charles Gabriel', prefix='de la', last=u'Vallée Poussin', generation='')
        )

    def test_another_complex_name(self):
        self.assertEqual(
            tokenize_name(u'von Berlichingen zu Hornberg, Johann Gottfried'),
            NameResult(first='Johann', middle='Gottfried', prefix='von', last='Berlichingen zu Hornberg', generation='')
        )

    def test_name_with_brackets(self):
        self.assertEqual(
            tokenize_name(u'{Robert and Sons, Inc.}'),
            NameResult(first='{Robert and Sons, Inc.}', middle='', prefix='', last='', generation='')
        )

    def test_name_with_initial(self):
        self.assertEqual(
            tokenize_name(u'T. Hobbes'),
            NameResult(first='T.', middle='', prefix='', last='Hobbes', generation='')
        )


class TestNameClass(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(
            str(Name('Simon~Coddlington')),
            'Coddlington, Simon'
        )

    def test_hyphenation(self):
        self.assertEqual(
            str(Name('Jean-Paul Sartre')),
            'Sartre, Jean-Paul'
        )

    def test_prefixed_surname(self):
        self.assertEqual(
            str(Name('Gloria van auf der Rissen')),
            'van auf der Rissen, Gloria'
        )

    def test_complex_name(self):
        self.assertEqual(
            str(Name('de la Vall{\\\'e}e~Poussin, Jean Charles~Gabriel')),
            "de la Vall{\\'e}e Poussin, Jean Charles Gabriel"
        )
