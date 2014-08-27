# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
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

import re

from pybtex.bibtex.exceptions import BibTeXError

whitespace_re = re.compile('(\s)')
purify_special_char_re = re.compile(r'^\\[A-Za-z]+')

def wrap(string, width=79):
    def wrap_chunks(chunks, width, initial_indent='', subsequent_indent='  '):
        space_len = 1
        line = []
        lines = []
        current_width = 0
        indent = initial_indent

        def output(line, indent):
            if line:
                if line[0] == ' ':
                    line.pop(0)
                lines.append(indent + ''.join(line).rstrip())

        for chunk in chunks:
            max_width = width - len(indent)
            chunk_len = len(chunk)
            if current_width + chunk_len <= max_width:
                line.append(chunk)
                current_width += chunk_len
            else:
                output(line, indent)
                indent = subsequent_indent
                line = [chunk]
                current_width = chunk_len
        output(line, indent)
        return lines

    chunks = whitespace_re.split(string)
    return '\n'.join(wrap_chunks(chunks, width))


class BibTeXString(object):
    def __init__(self, chars, level=0):
        self.level = level
        self.is_closed = False
        self.contents = list(self.find_closing_brace(iter(chars)))

    def __iter__(self):
        return self.traverse()

    def find_closing_brace(self, chars):
        for char in chars:
            if char == '{':
                yield BibTeXString(chars, self.level + 1)
            elif char == '}' and self.level > 0:
                self.is_closed = True
                return
            else:
                yield char

    def is_special_char(self):
        return self.level == 1 and self.contents and self.contents[0] == '\\'

    def traverse(self, open=None, f=lambda char, string: char, close=None):
        if open is not None and self.level > 0:
            yield open(self)

        for child in self.contents:
            if hasattr(child, 'traverse'):
                if child.is_special_char():
                    if open is not None:
                        yield open(child)
                    yield f(child.inner_string(), child)
                    if close is not None:
                        yield close(child)
                else:
                    for result in child.traverse(open, f, close):
                        yield result
            else:
                yield f(child, self)

        if close is not None and self.level > 0 and self.is_closed:
            yield close(self)

    def __str__(self):
        return ''.join(self.traverse(open=lambda string: '{', close=lambda string: '}'))

    def inner_string(self):
        return ''.join(str(child) for child in self.contents)


def change_case(string, mode):
    r"""
    >>> print(change_case('aBcD', 'l'))
    abcd
    >>> print(change_case('aBcD', 'u'))
    ABCD
    >>> print(change_case('ABcD', 't'))
    Abcd
    >>> print(change_case(r'The {\TeX book \noop}', 'u'))
    THE {\TeX BOOK \noop}
    >>> print(change_case(r'And Now: BOOO!!!', 't'))
    And now: Booo!!!
    >>> print(change_case(r'And {Now: BOOO!!!}', 't'))
    And {Now: BOOO!!!}
    >>> print(change_case(r'And {Now: {BOOO}!!!}', 'l'))
    and {Now: {BOOO}!!!}
    >>> print(change_case(r'And {\Now: BOOO!!!}', 't'))
    And {\Now: booo!!!}
    >>> print(change_case(r'And {\Now: {BOOO}!!!}', 'l'))
    and {\Now: {booo}!!!}
    >>> print(change_case(r'{\TeX\ and databases\Dash\TeX DBI}', 't'))
    {\TeX\ and databases\Dash\TeX DBI}
    """

    def title(char, state):
        if state == 'start':
            return char
        else:
            return char.lower()

    lower = lambda char, state: char.lower()
    upper = lambda char, state: char.upper()

    convert = {'l': lower, 'u': upper, 't': title}[mode]

    def convert_special_char(special_char, state):
        # FIXME BibTeX treats some accented and foreign characterss specially
        def convert_words(words):
            for word in words:
                if word.startswith('\\'):
                    yield word
                else:
                    yield convert(word, state)

        return ' '.join(convert_words(special_char.split(' ')))

    def change_case_iter(string, mode):
        state = 'start'
        for char, brace_level in scan_bibtex_string(string):
            if brace_level == 0:
                yield convert(char, state)
                if char == ':':
                    state = 'after colon'
                elif char.isspace() and state == 'after colon':
                    state = 'start'
                else:
                    state = 'normal'
            else:
                if brace_level == 1 and char.startswith('\\'):
                    yield convert_special_char(char, state)
                else:
                    yield char

    return ''.join(change_case_iter(string, mode))


def bibtex_substring(string, start, length):
    """
    Return a substring of the given length, starting from the given position.

    start and length are 1-based. If start is < 0, it is counted from the end
    of the string. If start is 0, an empty string is returned.

    >>> print(bibtex_substring('abcdef', 1, 3))
    abc
    >>> print(bibtex_substring('abcdef', 2, 3))
    bcd
    >>> print(bibtex_substring('abcdef', 2, 1000))
    bcdef
    >>> print(bibtex_substring('abcdef', 0, 1000))
    <BLANKLINE>
    >>> print(bibtex_substring('abcdef', -1, 1))
    f
    >>> print(bibtex_substring('abcdef', -1, 2))
    ef
    >>> print(bibtex_substring('abcdef', -2, 3))
    cde
    >>> print(bibtex_substring('abcdef', -2, 1000))
    abcde
    """

    if start > 0:
        start0 = start - 1
        end0 = start0 + length
    elif start < 0:
        end0 = len(string) + start + 1
        start0 = end0 - length
    else: # start == 0:
        return ''
    return string[start0:end0]


def bibtex_len(string):
    r"""Return the number of characters in the string.

    Braces are ignored. "Special characters" are ignored. A "special character"
    is a substring at brace level 1, if the first character after the opening
    brace is a backslash, like in "de la Vall{\'e}e Poussin".

    >>> print(bibtex_len(r"de la Vall{\'e}e Poussin"))
    20
    >>> print(bibtex_len(r"de la Vall{e}e Poussin"))
    20
    >>> print(bibtex_len(r"de la Vallee Poussin"))
    20
    >>> print(bibtex_len(r'\ABC 123'))
    8
    >>> print(bibtex_len(r'{\abc}'))
    1
    >>> print(bibtex_len(r'{\abc'))
    1
    >>> print(bibtex_len(r'}\abc'))
    4
    >>> print(bibtex_len(r'\abc}'))
    4
    >>> print(bibtex_len(r'\abc{'))
    4
    >>> print(bibtex_len(r'level 0 {1 {2}}'))
    11
    >>> print(bibtex_len(r'level 0 {\1 {2}}'))
    9
    >>> print(bibtex_len(r'level 0 {1 {\2}}'))
    12
    """
    length = 0
    for char, brace_level in scan_bibtex_string(string):
        if char not in '{}':
            length += 1
    return length


def bibtex_width(string):
    r"""
    Determine the width of the given string, in relative units.

    >>> bibtex_width('')
    0
    >>> bibtex_width('abc')
    1500
    >>> bibtex_width('ab{c}')
    2500
    >>> bibtex_width(r"ab{\'c}")
    1500
    >>> bibtex_width(r"ab{\'c{}}")
    1500
    >>> bibtex_width(r"ab{\'c{}")
    1500
    >>> bibtex_width(r"ab{\'c{d}}")
    2056
    """

    from pybtex.charwidths import charwidths
    width = 0
    for token, brace_level in scan_bibtex_string(string):
        if brace_level == 1 and token.startswith('\\'):
            for char in token[2:]:
                if char not in '{}':
                    width += charwidths.get(char, 0)
            width -= 1000  # two braces
        else:
            width += charwidths.get(token, 0)
    return width


def bibtex_prefix(string, num_chars):
    """Return the firxt num_char characters of the string.

    Braces and "special characters" are ignored, as in bibtex_len.  If the
    resulting prefix ends at brace level > 0, missing closing braces are
    appended.

    >>> print(bibtex_prefix('abc', 1))
    a
    >>> print(bibtex_prefix('abc', 5))
    abc
    >>> print(bibtex_prefix('ab{c}d', 3))
    ab{c}
    >>> print(bibtex_prefix('ab{cd}', 3))
    ab{c}
    >>> print(bibtex_prefix('ab{cd', 3))
    ab{c}
    >>> print(bibtex_prefix(r'ab{\cd}', 3))
    ab{\cd}
    >>> print(bibtex_prefix(r'ab{\cd', 3))
    ab{\cd}

    """
    def prefix():
        length = 0
        for char, brace_level in scan_bibtex_string(string):
            yield char
            if char not in '{}':
                length += 1
            if length >= num_chars:
                break
        for i in range(brace_level):
            yield '}'
    return ''.join(prefix())


def bibtex_purify(string):
    r"""Strip special characters from the string.

    >>> print(bibtex_purify('Abc 1234'))
    Abc 1234
    >>> print(bibtex_purify('Abc  1234'))
    Abc  1234
    >>> print(bibtex_purify('Abc-Def'))
    Abc Def
    >>> print(bibtex_purify('Abc-~-Def'))
    Abc   Def
    >>> print(bibtex_purify('{XXX YYY}'))
    XXX YYY
    >>> print(bibtex_purify('{XXX {YYY}}'))
    XXX YYY
    >>> print(bibtex_purify(r'XXX {\YYY} XXX'))
    XXX  XXX
    >>> print(bibtex_purify(r'{XXX {\YYY} XXX}'))
    XXX YYY XXX
    >>> print(bibtex_purify(r'\\abc def'))
    abc def
    >>> print(bibtex_purify('a@#$@#$b@#$@#$c'))
    abc
    >>> print(bibtex_purify(r'{\noopsort{1973b}}1973'))
    1973b1973
    >>> print(bibtex_purify(r'{sort{1973b}}1973'))
    sort1973b1973
    >>> print(bibtex_purify(r'{sort{\abc1973b}}1973'))
    sortabc1973b1973
    >>> print(bibtex_purify(r'{\noopsort{1973a}}{\switchargs{--90}{1968}}'))
    1973a901968
    """

    # FIXME BibTeX treats some accented and foreign characterss specially
    def purify_iter(string):
        for token, brace_level in scan_bibtex_string(string):
            if brace_level == 1 and token.startswith('\\'):
                for char in purify_special_char_re.sub('', token):
                    if char.isalnum():
                        yield char
            else:
                if token.isalnum():
                    yield token
                elif token.isspace() or token in '-~':
                    yield ' '

    return ''.join(purify_iter(string))


def scan_bibtex_string(string):
    """ Yield (char, brace_level) tuples.

    "Special characters", as in bibtex_len, are treated as a single character

    """
    return BibTeXString(string).traverse(
        open=lambda string: ('{', string.level),
        f=lambda char, string: (char, string.level),
        close=lambda string: ('}', string.level - 1),
    )


def split_name_list(string):
    """
    Split a list of names, separated by ' and '.

    >>> split_name_list('Johnson and Peterson')
    ['Johnson', 'Peterson']
    >>> split_name_list('Armand and Peterson')
    ['Armand', 'Peterson']
    >>> split_name_list('Armand and anderssen')
    ['Armand', 'anderssen']
    >>> split_name_list('What a Strange{ }and Bizzare Name! and Peterson')
    ['What a Strange{ }and Bizzare Name!', 'Peterson']
    >>> split_name_list('What a Strange and{ }Bizzare Name! and Peterson')
    ['What a Strange and{ }Bizzare Name!', 'Peterson']
    """
    return split_tex_string(string, ' and ')


def split_tex_string(string, sep=None, strip=True, filter_empty=False):
    """Split a string using the given separator (regexp).

    Everything at brace level > 0 is ignored.
    Separators at the edges of the string are ignored.

    >>> split_tex_string('')
    []
    >>> split_tex_string('     ')
    []
    >>> split_tex_string('   ', ' ', strip=False, filter_empty=False)
    [' ', ' ']
    >>> split_tex_string('.a.b.c.', r'\.')
    ['.a', 'b', 'c.']
    >>> split_tex_string('.a.b.c.{d.}.', r'\.')
    ['.a', 'b', 'c', '{d.}.']
    >>> split_tex_string('Matsui      Fuuka')
    ['Matsui', 'Fuuka']
    >>> split_tex_string('{Matsui      Fuuka}')
    ['{Matsui      Fuuka}']
    >>> split_tex_string('a')
    ['a']
    >>> split_tex_string('on a')
    ['on', 'a']
    """

    if sep is None:
        sep = '[\s~]+'
        filter_empty = True
    sep_re = re.compile(sep)
    brace_level = 0
    name_start = 0
    result = []
    string_len = len(string)
    pos = 0
    for pos, char in enumerate(string):
        if char == '{':
            brace_level += 1
        elif char == '}':
            brace_level -= 1
        elif brace_level == 0 and pos > 0:
            match = sep_re.match(string[pos:])
            if match:
                sep_len = len(match.group())
                if pos + sep_len < string_len:
                    result.append(string[name_start:pos])
                    name_start = pos + sep_len
    if name_start < string_len:
        result.append(string[name_start:])
    if strip:
        result = [part.strip() for part in result]
    if filter_empty:
        result = [part for part in result if part]
    return result


def bibtex_first_letter(string):
    """ Return the first letter or special character of the string.

    >>> print(bibtex_first_letter('Andrew Blake'))
    A
    >>> print(bibtex_first_letter('{Andrew} Blake'))
    A
    >>> print(bibtex_first_letter('1Andrew'))
    A
    >>> print(bibtex_first_letter('{\TeX} markup'))
    {\TeX}
    >>> print(bibtex_first_letter(''))
    <BLANKLINE>
    >>> print(bibtex_first_letter('123 123 123 {}'))
    <BLANKLINE>
    >>> print(bibtex_first_letter('\LaTeX Project Team'))
    L

    """

    for char in BibTeXString(string):
        if char.startswith('\\') and char != '\\':
            return '{{{0}}}'.format(char)
        elif char.isalpha():
            return char
    return ''


def bibtex_abbreviate(string, delimiter=None, separator='-'):
    """
    Abbreviate string.

    >>> print(bibtex_abbreviate('Andrew Blake'))
    A
    >>> print(bibtex_abbreviate('Jean-Pierre'))
    J.-P
    >>> print(bibtex_abbreviate('Jean--Pierre'))
    J.-P
    
    """

    def _bibtex_abbreviate():
        for token in split_tex_string(string, sep=separator):
            letter = bibtex_first_letter(token)
            if letter:
                yield letter

    if delimiter is None:
        delimiter = '.-'
    return delimiter.join(_bibtex_abbreviate())

