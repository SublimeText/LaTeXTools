# vim:fileencoding=utf-8

# Copyright (c) 2009, 2010, 2011, 2012  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Test routines for the BibTeX .bib parser.

Some tests were adopted from Babybib - another BibTeX parser by Matthew Brett.
https://github.com/matthew-brett/babybib

"""


from pybtex.database import BibliographyData
from pybtex.database import Entry, Person
from pybtex.database.input.bibtex import Parser
from io import StringIO
from itertools import zip_longest

from unittest import TestCase


class TestParser(Parser):
    def __init__(self, *args, **kwargs):
        super(TestParser, self).__init__(*args, **kwargs)
        self.errors = []

    def handle_error(self, error):
        self.errors.append(error)


class ParserTest(object):
    input_string = None
    input_strings = []
    correct_result = None
    parser_options = {}
    errors = []

    def setUp(self):
        if not self.input_strings:
            self.input_strings = [self.input_string]

    def test_parser(self):
        parser = TestParser(encoding='UTF-8', **self.parser_options)
        for input_string in self.input_strings:
            parser.parse_stream(StringIO(input_string))
        result = parser.data
        correct_result = self.correct_result
        assert result == correct_result
        for error, correct_error in zip_longest(parser.errors, self.errors):
            actual_error = str(error)
            assert actual_error == correct_error
    

class EmptyDataTest(ParserTest, TestCase):
    input_string = ''
    correct_result = BibliographyData()


class BracesTest(ParserTest, TestCase):
    input_string = """@ARTICLE{
                test,
                title={Polluted
                    with {DDT}.
            },
    }"""
    correct_result = BibliographyData({'test': Entry('article', {'title': 'Polluted with {DDT}.'})})


class BracesAndQuotesTest(ParserTest, TestCase):
    input_string = '''@ARTICLE{
                test,
                title="Nested braces  and {"quotes"}",
        }'''
    correct_result =BibliographyData({'test': Entry('article', {'title': 'Nested braces and {"quotes"}'})})


class EntryInStringTest(ParserTest, TestCase):
    input_string = """
        @article{Me2010, author="Brett, Matthew", title="An article
        @article{something, author={Name, Another}, title={not really an article}}
        "}
        @article{Me2009,author={Nom de Plume, My}, title="A short story"}
    """
    correct_result = BibliographyData(
        entries={
            'Me2010': Entry('article',
                fields={
                    'title': 'An article @article{something, author={Name, Another}, title={not really an article}}'
                },
                persons={'author': [Person('Brett, Matthew')]}
            ),
            'Me2009': Entry('article',
                fields={'title': 'A short story'},
                persons={'author': [Person('Nom de Plume, My')]}
            )
        }
    )


class EntryInCommentTest(ParserTest, TestCase):
    input_string = """
        Both the articles register despite the comment block
        @Comment{
        @article{Me2010, title="An article"}
        @article{Me2009, title="A short story"}
        }
        These all work OK without errors
        @Comment{and more stuff}

        Last article to show we can get here
        @article{Me2011, }
    """
    correct_result = BibliographyData({
        'Me2011': Entry('article'),
        'Me2010': Entry('article', fields={'title': 'An article'}),
        'Me2009': Entry('article', fields={'title': 'A short story'}),
    })


class AtTest(ParserTest, TestCase):
    # FIXME: check warnings
    input_string = """
        The @ here parses fine in both cases
        @article{Me2010,
            title={An @tey article}}
        @article{Me2009, title="A @tey short story"}
    """
    correct_result = BibliographyData({
        'Me2010': Entry('article', {'title': 'An @tey article'}),
        'Me2009': Entry('article', {'title': 'A @tey short story'}),
    })
    errors = [
        "syntax error in line 2: '(' or '{' expected",
    ]

class EntryTypesTest(ParserTest, TestCase):
    input_string = """
        Testing what are allowed for entry types

        These are OK
        @somename{an_id,}
        @t2{another_id,}
        @t@{again_id,}
        @t+{aa1_id,}
        @_t{aa2_id,}

        These ones not
        @2thou{further_id,}
        @some name{id3,}
        @some#{id4,}
        @some%{id4,}
    """
    correct_result = BibliographyData({
        'an_id': Entry('somename'),
        'another_id': Entry('t2'),
        'again_id': Entry('t@'),
        'aa1_id': Entry('t+'),
        'aa2_id': Entry('_t'),
    })
    errors = [
        "syntax error in line 12: a valid name expected",
        "syntax error in line 13: '(' or '{' expected",
        "syntax error in line 14: '(' or '{' expected",
        "syntax error in line 15: '(' or '{' expected",
    ]


class FieldNamesTest(ParserTest, TestCase):
    input_string = """
        Check for characters allowed in field names
        Here the cite key is fine, but the field name is not allowed:
        ``You are missing a field name``
        @article{2010, 0author="Me"}

        Underscores allowed (no error)
        @article{2011, _author="Me"}

        Not so for spaces obviously (``expecting an '='``)
        @article{2012, author name = "Myself"}

        Or hashes (``missing a field name``)
        @article{2013, #name = "Myself"}

        But field names can start with +-.
        @article{2014, .name = "Myself"}
        @article{2015, +name = "Myself"}
        @article{2016, -name = "Myself"}
        @article{2017, @name = "Myself"}
    """
    correct_result = BibliographyData({
        '2010': Entry('article'),
        '2011': Entry('article', {'_author': 'Me'}),
        '2012': Entry('article'),
        '2013': Entry('article'),
        '2014': Entry('article', {'.name': 'Myself'}),
        '2015': Entry('article', {'+name': 'Myself'}),
        '2016': Entry('article', {'-name': 'Myself'}),
        '2017': Entry('article', {'@name': 'Myself'}),
    })
    errors = [
        "syntax error in line 5: '}' expected",
        "syntax error in line 11: '=' expected",
        'syntax error in line 14: \'}\' expected',
    ]


class InlineCommentTest(ParserTest, TestCase):
    input_string = """
        "some text" causes an error like this
        ``You're missing a field name---line 6 of file bibs/inline_comment.bib``
        for all 3 of the % some text occurences below; in each case the parser keeps
        what it has up till that point and skips, so that it correctly gets the last
        entry.
        @article{Me2010,}
        @article{Me2011,
            author="Brett-like, Matthew",
        % some text
            title="Another article"}
        @article{Me2012, % some text
            author="Real Brett"}
        This one correctly read
        @article{Me2013,}
    """
    correct_result = BibliographyData({
        'Me2010': Entry('article'),
        'Me2011': Entry('article', persons={'author': [
            Person(first='Matthew', last='Brett-like'),
        ]}),
        'Me2012': Entry('article'),
        'Me2013': Entry('article'),
    })
    errors = [
        "syntax error in line 10: '}' expected",
        "syntax error in line 12: '}' expected",
    ]


class SimpleEntryTest(ParserTest, TestCase):
    input_string = """
        % maybe the simplest possible
        % just a comment and one reference

        @ARTICLE{Brett2002marsbar,
        author = {Matthew Brett and Jean-Luc Anton and Romain Valabregue and Jean-Baptise
            Poline},
        title = {{Region of interest analysis using an SPM toolbox}},
        journal = {Neuroimage},
        institution = {},
        year = {2002},
        volume = {16},
        pages = {1140--1141},
        number = {2}
        }
    """
    correct_result = BibliographyData({
        'Brett2002marsbar': Entry('article',
            fields={
                'title': '{Region of interest analysis using an SPM toolbox}',
                'journal': 'Neuroimage',
                'institution': '',
                'year': '2002',
                'volume': '16',
                'pages': '1140--1141',
                'number': '2',
            },
            persons={
                'author': [
                    Person(first='Matthew', last='Brett'),
                    Person(first='Jean-Luc', last='Anton'),
                    Person(first='Romain', last='Valabregue'),
                    Person(first='Jean-Baptise', last='Poline'),
                ],
            },
        )
    })


class KeyParsingTest(ParserTest, TestCase):
    input_string = """
        # will not work as expected
        @article(test(parens1))

        # works fine
        @article(test(parens2),)

        # works fine
        @article{test(braces1)}

        # also works
        @article{test(braces2),}
    """
    correct_result = BibliographyData({
        'test(parens1))': Entry('article'),
        'test(parens2)': Entry('article'),
        'test(braces1)': Entry('article'),
        'test(braces2)': Entry('article'),
    })
    errors = [
        "syntax error in line 5: ')' expected",
    ]


class KeylessEntriesTest(ParserTest, TestCase):
    parser_options = {'keyless_entries': True}
    input_string = """
        @BOOK(
            title="I Am Jackie Chan: My Life in Action",
            year=1999
        )
        @BOOK()
        @BOOK{}

        @BOOK{
            title = "Der deutsche Jackie Chan Filmführer",
        }

    """
    correct_result = BibliographyData({
        'unnamed-1': Entry('book', {'title': 'I Am Jackie Chan: My Life in Action', 'year': '1999'}),
        'unnamed-2': Entry('book'),
        'unnamed-3': Entry('book'),
        'unnamed-4': Entry('book', {'title': 'Der deutsche Jackie Chan Filmführer'}),
    })


class MacrosTest(ParserTest, TestCase):
    input_string = """
        @String{and = { and }}
        @String{etal = and # { {et al.}}}
        @Article(
            unknown,
            author = nobody,
        )
        @Article(
            gsl,
            author = "Gough, Brian"#etal,
        )
    """
    correct_result = BibliographyData({
        'unknown': Entry('article'),
        'gsl': Entry('article', persons={'author': [Person('Gough, Brian'), Person('{et al.}')]}),
    })
    errors = [
        'undefined string in line 6: nobody',
    ]


class WantedEntriesTest(ParserTest, TestCase):
    parser_options = {'wanted_entries': ['GSL']}
    input_string = """
        @Article(
            gsl,
        )
    """
    correct_result = BibliographyData(entries={
        'GSL': Entry('article'),
    })


class CrossrefTest(ParserTest, TestCase):
    parser_options = {'wanted_entries': ['GSL', 'GSL2']}
    input_string = """
        @Article(gsl, crossref="the_journal")
        @Article(gsl2, crossref="The_Journal")
        @Journal{the_journal,}
    """
    correct_result = BibliographyData(entries={
        'GSL': Entry('article', {'crossref': 'the_journal'}),
        'GSL2': Entry('article', {'crossref': 'The_Journal'}),
        'the_journal': Entry('journal'),
    })


class CrossrefWantedTest(ParserTest, TestCase):
    """When cross-referencing an explicitly cited, the key from .aux file should be used."""

    parser_options = {'wanted_entries': ['GSL', 'GSL2', 'The_Journal']}
    input_string = """
        @Article(gsl, crossref="the_journal")
        @Article(gsl2, crossref="The_Journal")
        @Journal{the_journal,}
    """
    correct_result = BibliographyData(entries={
        'GSL': Entry('article', {'crossref': 'the_journal'}),
        'GSL2': Entry('article', {'crossref': 'The_Journal'}),
        'The_Journal': Entry('journal'),
    })


class UnusedEntryTest(ParserTest, TestCase):
    parser_options = {'wanted_entries': []}
    input_string = """
        @Article(
            gsl,
            author = nobody,
        )
    """
    correct_result = BibliographyData()


class CrossFileMacrosTest(ParserTest, TestCase):
    input_strings = [
        '@string{jackie = "Jackie Chan"}',
        """,
            @Book{
                i_am_jackie,
                author = jackie,
                title = "I Am " # jackie # ": My Life in Action",
            }
        """,
    ]
    correct_result = BibliographyData({
        'i_am_jackie': Entry('book', 
            fields={'title': 'I Am Jackie Chan: My Life in Action'},
            persons={'author': [Person('Chan, Jackie')]}
        ),
    })


class AtCharacterTest(ParserTest, TestCase):
    input_strings = [
        r""",
            @proceedings{acc,
                title = {Proc.\@ of the American Control Conference},
                notes = "acc@example.org"
            }
        """,
    ]
    correct_result = BibliographyData({
        'acc': Entry('proceedings', 
            fields={
                'title': r'Proc.\@ of the American Control Conference',
                'notes': 'acc@example.org'
            },
        ),
    })


class AtCharacterInUnwantedEntryTest(ParserTest, TestCase):
    parser_options = {'wanted_entries': []}
    input_strings = [
        r""",
            @proceedings{acc,
                title = {Proc.\@ of the American Control Conference},
                notes = "acc@example.org"
            }
        """,
    ]
    correct_result = BibliographyData()


class CaseSensitivityTest(ParserTest, TestCase):
    input_strings = [
        r""",
            @Article{CamelCase,
                Title = {To CamelCase or Under score},
                year = 2009,
                NOTES = "none"
            }
        """,
    ]
    correct_result = BibliographyData({
        'CamelCase': Entry('article', 
            fields={
                'Title': 'To CamelCase or Under score',
                'year': '2009',
                'NOTES': 'none',
            },
        ),
    })
