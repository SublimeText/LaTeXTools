# coding=utf-8

from __future__ import print_function

from collections import namedtuple

import re
import sys

if sys.version_info > (3, 0):
    strbase = str
    unicode = str
else:
    strbase = basestring

# list of known BibLaTeX fields of the type `list (name)`
NAME_FIELDS = set((
    'author',
    'bookauthor',
    'commentator',
    'editor',
    'editora',
    'editorb',
    'editorc',
    'foreword',
    'holder',
    'introduction',
    'shortauthor',
    'shorteditor',
    'translator',
    'sortname',
    'namea',
    'nameb',
    'namec'
))

# Regex to recognise if we are in a name field
#
# I've tried to simply the comprehensibility of the backwards regexes used by
# constructing them here
#
# VALUE_REGEX is a common suffix to handle the `= {<value> and <value>}` part
VALUE_REGEX = r'[\s~]*(?P<ENTRIES>(?:dna[\s~]+.+)+)?[\s~]*(?P<OPEN>\{)?(?P<EQUALS>\s*=\s*)?'

ON_NAME_FIELD_REGEX = re.compile(
    VALUE_REGEX + r'(?:' + r'|'.join((s[::-1] for s in NAME_FIELDS)) + r')' + r'\b',
    re.IGNORECASE | re.UNICODE
)

def get_text_to_cursor(view):
    cursor = view.sel()[0].b
    current_region = sublime.Region(0, cursor)
    return view.substr(current_region)

def split_tex_string(string, maxsplit=-1, sep=None):
    '''
    A variation of string.split() to support tex strings

    In particular, ignores text in brackets, no matter how deeply nested and
    defaults to breaking on any space char or ~.
    '''

    if sep is None:
        # tilde == non-breaking space
        sep = r'(?u)[\s~]+'
    sep_re = re.compile(sep)

    result = []

    # track ignore separators in braces
    brace_level = 0
    # calculate once
    string_len = len(string)
    word_start = 0
    splits = 0

    for pos, c in enumerate(string):
        if c == '{':
            brace_level += 1
        elif c == '}':
            brace_level -= 1
        elif brace_level == 0 and pos > 0:
            matcher = sep_re.match(string[pos:])
            if matcher:
                sep_len = len(matcher.group())
                if pos + sep_len <= string_len:
                    result.append(string[word_start:pos])
                    word_start = pos + sep_len

                    splits += 1
                    if splits == maxsplit:
                        break

    if word_start < string_len:
        result.append(string[word_start:])

    return [part.strip() for part in result if part]

def tokenize_list(list_str):
    return split_tex_string(list_str, sep=r'(?iu)[\s~]+and(?:[\s~]+|$)')

# namedtuple so results are a little more comprehensible
NameResult = namedtuple('NameResult', ['first', 'middle', 'prefix', 'last', 'generation'])

def tokenize_name(name_str):
    u'''
    Takes a string representing a name and returns a NameResult breaking that
    string into its component parts, as defined in the LaTeX book and BibTeXing.

    The supported formats are thus:

    First von Last
    von Last, First
    von Last, Jr, First

    We try to follow the rules in BibTeXing relatively strictly, meaning that the
    first of these formats can result in unexpected results because it is more
    ambiguous with complex names.
    '''

    def extract_middle_names(first):
        return split_tex_string(first, 1)

    def extract_name_prefix(last):
        names = split_tex_string(last, 1)
        if len(names) == 1:
            return names

        result = [names[0]]

        new_names = split_tex_string(names[1], 1)
        while len(new_names) > 1 and new_names[0].islower():
            result[0] = u' '.join((result[0], new_names[0]))
            names = new_names
            new_names = split_tex_string(names[1], 1)

        result.append(names[1])

        return result

    name_str = name_str.strip()

    parts = split_tex_string(name_str, sep=r',[\s~]*')
    if len(parts) == 1:
        # first last
        # reverse the string so split only selects the right-most instance of the token
        try:
            last, first = [part[::-1] for part in split_tex_string(parts[0][::-1], 1)]
        except ValueError:
            # we only have a single name
            return NameResult(
                parts[0],
                '', '', '', ''
            )

        # because of our splitting method, van, von, della, etc. may end up at the end of the first name field
        first_parts = split_tex_string(first)
        first_parts_len = len(first_parts)
        if first_parts_len > 1:
            lower_name_index = None
            for i, part in enumerate(first_parts[::-1], 1):
                if part.islower():
                    if lower_name_index is None or lower_name_index == i - 1:
                        lower_name_index = i
                    else:
                        break
            if lower_name_index is not None:
                last = u' '.join((
                    u' '.join(first_parts[-lower_name_index:]),
                    last
                ))
                first = u' '.join(first_parts[:-lower_name_index])

        forenames = extract_middle_names(first)
        lastnames = extract_name_prefix(last)
        return NameResult(
            forenames[0],
            forenames[1] if len(forenames) > 1 else '',
            lastnames[0] if len(lastnames) > 1 else '',
            lastnames[1] if len(lastnames) > 1 else lastnames[0],
            ''
        )
    elif len(parts) == 2:
        # last, first
        last, first = parts

        # for consistency with spaces being stripped in first last format
        first = u' '.join((s for s in split_tex_string(first)))
        last = u' '.join((s for s in split_tex_string(last)))

        forenames = extract_middle_names(first)
        lastnames = extract_name_prefix(last)

        if len(lastnames) > 1:
            name_index = 0
            for part in lastnames:
                if part.islower():
                    name_index += 1
                else:
                    break

        return NameResult(
            forenames[0],
            forenames[1] if len(forenames) > 1 else '',
            u' '.join(lastnames[:name_index]) if len(lastnames) > 1 else '',
            u' '.join(lastnames[name_index:]) if len(lastnames) > 1 else lastnames[0],
            ''
        )
    elif len(parts) == 3:
        # last, generation, first
        last, generation, first = parts
        forenames = extract_middle_names(first)
        lastnames = extract_name_prefix(last)
        return NameResult(
            forenames[0],
            forenames[1] if len(forenames) > 1 else '',
            lastnames[0] if len(lastnames) > 1 else '',
            lastnames[1] if len(lastnames) > 1 else lastnames[0],
            generation
        )
    else:
        raise ValueError(u'Unrecognised name format for "{0}"'.format(name_str))

class Name(object):
    u'''
    Represents a BibLaTeX name entry. __str__ will return a name formatted in
    the preferred format
    '''
    def __init__(self, name_str):
        self.first = None
        self.middle = None
        self.prefix = None
        self.last = None
        self.generation = None

        self.first, self.middle, self.prefix, self.last, self.generation = \
            tokenize_name(name_str)

    def __unicode__(self):
        if not self.last:
            return self.first

        result = u' '.join((self.prefix, self.last)) if self.prefix else unicode(self.last)
        if self.generation:
            result = u', '.join((result, self.generation))
        result = u', '.join((result, self.first))
        if self.middle:
            result = u' '.join((result, self.middle))
        return result

    __str__ = __unicode__
    __repr__ = __unicode__

# builds the replacement string depending on the current context of the line
def _get_replacement(matcher, key):
    if not matcher:
        return key

    match = matcher.group(0)
    if not matcher.group('ENTRIES'):
        equals = matcher.group('EQUALS')

        return u'{0}{1}{2}'.format(
            u'' if equals else u'= ' if match.startswith(u' ') else u' = ',
            u'' if matcher.group('OPEN') else u'{' if not equals or match.startswith(u' ') else u' {',
            key
        )

    if matcher.group('ENTRIES').startswith('dna'):
        if match.startswith(' '):
            return u'{0}'.format(key)
        return u' {0}'.format(key)
    else:
        return u'{0}{1}'.format(
            u' ' if matcher.group('ENTRIES').startswith(u' ') != u' ' else u'',
            key
        )

NAME_FIELD_REGEX = re.compile(
    r'(?:^|[\s~]+)(?:' + r'|'.join(NAME_FIELDS) + ')\s*=\s*\{',
    re.IGNORECASE | re.UNICODE
)

def get_names_from_view(view):
    contents = view.substr(sublime.Region(0, view.size()))
    return get_names(contents)

def get_names(contents):
    u'''
    Work-horse function to extract all the names defined in the current bib file.
    '''
    names = []

    in_entry = False
    pos = 0
    contents_length = len(contents)

    while True:
        if not in_entry:
            matcher = re.search(NAME_FIELD_REGEX, contents[pos:])
            # no more `name =` fields
            if not matcher:
                break

            pos += matcher.end()
            in_entry = True
        else:
            chars = []

            bracket_depth = 1
            for c in contents[pos:]:
                if c == '}':
                    bracket_depth -= 1

                if bracket_depth == 0:
                    break

                if c == '{':
                    bracket_depth += 1

                chars.append(c)

            names.extend([unicode(Name(s)) for s in tokenize_list(u''.join(chars))])

            pos += len(chars)
            if pos >= contents_length:
                break
            in_entry = False

    return sorted(set(names))

# isolate sublime-dependent code to allow testing with unittest
try:
    import sublime
    import sublime_plugin

    try:
        from latextools_utils import is_bib_buffer
    except ImportError:
        from .latextools_utils import is_bib_buffer

    class BiblatexNameCompletions(sublime_plugin.EventListener):
        def on_query_completions(self, view, prefix, locations):
            if not is_bib_buffer(view):
                return []

            current_line = get_text_to_cursor(view)[::-1]

            if current_line.startswith(prefix[::-1]):
                current_line = current_line[len(prefix):]

            matcher = ON_NAME_FIELD_REGEX.match(current_line)
            if matcher:
                return ([(name, _get_replacement(matcher, name))
                        for name in get_names_from_view(view)],
                        sublime.INHIBIT_WORD_COMPLETIONS |
                        sublime.INHIBIT_EXPLICIT_COMPLETIONS)

            return []
except ImportError:
    # Assume we are not in sublime
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

    class TestGetNames(unittest.TestCase):
        def test_simple(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_editor(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        editor = {Coddlington, Simon},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_translator(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        translator = {Coddlington, Simon},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_newline_before_value(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {
                            Coddlington, Simon},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_newline_after_value(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon
                            },
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_newlines_in_value(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {
                            Coddlington, Simon
                        },
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_two_authors(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon and Gary Winchester},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_two_authors_newline_before_and(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon
                            and Gary Winchester},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_two_authors_newline_after_and(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon and
                            Gary Winchester},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_three_authors(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon and Gary Winchester and Calhoun, Buck},
                        date = {2014-08-01}
                    }"""),
                [u'Calhoun, Buck', u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_two_name_fields(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon},
                        editor = {Winchester, Gary},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_three_name_fields(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon},
                        editor = {Winchester, Gary},
                        translator = {Calhoun, Buck},
                        date = {2014-08-01}
                    }"""),
                [u'Calhoun, Buck', u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_two_name_fields_same_person(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon},
                        editor = {Coddlington, Simon},
                        date = {2014-08-01}
                    }"""),
                [u'Coddlington, Simon']
            )

        def test_multiple_entries(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon},
                        date = {2014-08-01}
                    }

                    @book{
                        title = {An Even Longer Disquisition on Nothingness and Other Thoughts},
                        author = {Winchester, Gary},
                        date = {2015-06-07}
                    }"""),
                [u'Coddlington, Simon', u'Winchester, Gary']
            )

        def test_paritially_complete_entry(self):
            self.assertEqual(
                get_names(u"""
                    @article {
                        title = {A Long Disquisition on Nothing},
                        author = {Coddlington, Simon and"""),
                [u'Coddlington, Simon']
            )

    class TestFieldMatchingRegex(unittest.TestCase):
        def test_simple(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author = {'[::-1])
            )

        def test_without_spaces(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author={'[::-1])
            )

        def test_without_bracket(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author = '[::-1])
            )

        def test_with_space_after_bracket(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author = { '[::-1])
            )

        def test_alternative_field(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('editor = {'[::-1])
            )

        def test_doesnt_match_empty_field(self):
            self.assertIsNone(
                ON_NAME_FIELD_REGEX.match('author = {}'[::-1])
            )

        def test_doesnt_match_completed_field(self):
            self.assertIsNone(
                ON_NAME_FIELD_REGEX.match('author = {Coddlington, Simon}'[::-1])
            )

        def test_matches_partial_field(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author = {Coddlington, Simon and'[::-1])
            )

        def test_matches_partial_field_two_names(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author = {Coddlington, Simon and Gary Winchester and'[::-1])
            )

        def test_matches_partial_field_three_names(self):
            self.assertIsNotNone(
                ON_NAME_FIELD_REGEX.match('author = {Coddlington, Simon and Gary Winchester and Calhoun, Buck and'[::-1])
            )

    class TestGetReplacement(unittest.TestCase):
        def test_simple(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author = {'[::-1]),
                    'Coddlington, Simon'
                ),
                'Coddlington, Simon'
            )

        def test_without_spaces(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author={'[::-1]),
                    'Coddlington, Simon'
                ),
                'Coddlington, Simon'
            )

        def test_without_bracket(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author = '[::-1]),
                    'Coddlington, Simon'
                ),
                '{Coddlington, Simon'
            )

        def test_without_bracket_or_preceding_space(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author ='[::-1]),
                    'Coddlington, Simon'
                ),
                ' {Coddlington, Simon'
            )

        def test_without_equals(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author '[::-1]),
                    'Coddlington, Simon'
                ),
                '= {Coddlington, Simon'
            )

        def test_without_equals_or_space(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author'[::-1]),
                    'Coddlington, Simon'
                ),
                ' = {Coddlington, Simon'
            )

        def test_with_existing_entry(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author = {Coddlington, Simon and '[::-1]),
                    'Coddlington, Simon'
                ),
                'Coddlington, Simon'
            )

        def test_with_existing_entry_without_space(self):
            self.assertEqual(
                _get_replacement(
                    ON_NAME_FIELD_REGEX.match('author = {Coddlington, Simon and'[::-1]),
                    'Coddlington, Simon'
                ),
                ' Coddlington, Simon'
            )

    # monkey patch unittest in Python 2.6
    if sys.version_info < (2, 7) and sys.version_info >= (2, 6):
        def assertIsNone(self, obj, msg=None):
            if obj is not None:
                raise self.failureException(msg or '%r is not None' % (obj,))

        def assertIsNotNone(self, obj, msg=None):
            if obj is None:
                raise self.failureException(msg or '%r is None' % (obj,))

        unittest.TestCase.assertIsNone = assertIsNone
        unittest.TestCase.assertIsNotNone = assertIsNotNone

if __name__ == '__main__':
    unittest.main()