# Copyright (c) 2006, 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
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

"""BibTeX parser

>>> from io import StringIO
>>> parser = Parser()
>>> bib_data = parser.parse_stream(StringIO('''
... @String{SCI = "Science"}
... 
... @String{JFernandez = "Fernandez, Julio M."}
... @String{HGaub = "Gaub, Hermann E."}
... @String{MGautel = "Gautel, Mathias"}
... @String{FOesterhelt = "Oesterhelt, Filipp"}
... @String{MRief = "Rief, Matthias"}
... 
... @Article{rief97b,
...   author =       MRief #" and "# MGautel #" and "# FOesterhelt
...                  #" and "# JFernandez #" and "# HGaub,
...   title =        "Reversible Unfolding of Individual Titin
...                  Immunoglobulin Domains by {AFM}",
...   journal =      SCI,
...   volume =       276,
...   number =       5315,
...   pages =        "1109--1112",
...   year =         1997,
...   doi =          "10.1126/science.276.5315.1109",
...   URL =          "http://www.sciencemag.org/cgi/content/abstract/276/5315/1109",
...   eprint =       "http://www.sciencemag.org/cgi/reprint/276/5315/1109.pdf",
... }
... '''))

# entry keys are case-insensitive
>>> bib_data.entries['rief97b'] == bib_data.entries['RIEF97B']
True

>>> rief97b = bib_data.entries['rief97b']
>>> authors = rief97b.persons['author']
>>> for author in authors:
...     print(str(author))
Rief, Matthias
Gautel, Mathias
Oesterhelt, Filipp
Fernandez, Julio M.
Gaub, Hermann E.

# field names are case-insensitive
>>> print(rief97b.fields['URL'])
http://www.sciencemag.org/cgi/content/abstract/276/5315/1109
>>> print(rief97b.fields['url'])
http://www.sciencemag.org/cgi/content/abstract/276/5315/1109

"""

from string import ascii_letters, digits

import re
import pybtex.io
from pybtex.utils import CaseInsensitiveDict, CaseInsensitiveSet
from pybtex.database import Entry, Person
from pybtex.database.input import BaseParser
from pybtex.bibtex.utils import split_name_list
from pybtex.exceptions import PybtexError
from pybtex import textutils
from pybtex.scanner import (
    Scanner, Pattern, Literal,
    PrematureEOF, PybtexSyntaxError,
)

month_names = {
    'jan': 'January',
    'feb': 'February',
    'mar': 'March',
    'apr': 'April',
    'may': 'May',
    'jun': 'June',
    'jul': 'July',
    'aug': 'August',
    'sep': 'September',
    'oct': 'October',
    'nov': 'November',
    'dec': 'December'
}


class SkipEntry(Exception):
    pass


class UndefinedMacro(PybtexSyntaxError):
    error_type = 'undefined string'

class BibTeXEntryIterator(Scanner):
    NAME_CHARS = ascii_letters + '@!$&*+-./:;<>?[\\]^_`|~\x7f'
    NAME = Pattern(r'[{0}][{1}]*'.format(re.escape(NAME_CHARS), re.escape(NAME_CHARS + digits)), 'a valid name')
    KEY_PAREN = Pattern(r'[^\s\,]+', 'entry key')
    KEY_BRACE = Pattern(r'[^\s\,}]+', 'entry key')
    NUMBER = Pattern(r'[{0}]+'.format(digits), 'a number')
    LBRACE = Literal('{')
    RBRACE = Literal('}')
    LPAREN = Literal('(')
    RPAREN = Literal(')')
    QUOTE = Literal('"')
    COMMA = Literal(',')
    EQUALS = Literal('=')
    HASH = Literal('#')
    AT = Literal('@')

    command_start = None
    current_command = None
    current_entry_key = None
    current_fields = None
    current_field_name = None
    current_field_value = None

    def __init__(self, text, keyless_entries=False, macros=month_names, handle_error=None, want_entry=None, filename=None):
        super(BibTeXEntryIterator, self).__init__(text, filename)
        self.keyless_entries = keyless_entries
        self.macros = macros
        if handle_error:
            self.handle_error = handle_error
        if want_entry:
            self.want_entry = want_entry

    def __iter__(self):
        return self.parse_bibliography()

    def get_error_context_info(self):
        return self.command_start, self.lineno, self.pos

    def get_error_context(self, context_info):
        error_start, lineno, error_pos  = context_info
        before_error = self.text[error_start:error_pos]
        if not before_error.endswith('\n'):
            eol = self.NEWLINE.search(self.text, error_pos)
            error_end = eol.end() if eol else self.end_pos
        else:
            error_end = error_pos
        context = self.text[error_start:error_end].rstrip('\r\n')
        colno = len(before_error.splitlines()[-1])
        return context, lineno, colno

    def handle_error(self, error):
        raise error

    def want_entry(self, key):
        return True

    def want_current_entry(self):
        return self.current_entry_key is None or self.want_entry(self.current_entry_key)

    def parse_bibliography(self):
        while True:
            if not self.skip_to([self.AT]):
                return
            self.command_start = self.pos - 1
            try:
                yield tuple(self.parse_command())
            except PybtexSyntaxError as error:
                self.handle_error(error)
            except SkipEntry:
                pass

    def parse_command(self):
        self.current_entry_key = None
        self.current_fields = []
        self.current_field_name = None
        self.current_value = []

        name = self.required([self.NAME])
        command = name.value
        body_start = self.required([self.LPAREN, self.LBRACE])
        body_end = self.RBRACE if body_start.pattern == self.LBRACE else self.RPAREN

        command_lower = command.lower()
        if command_lower == 'string':
            parse_body = self.parse_string_body
            make_result = lambda: (command, (self.current_field_name, self.current_value))
        elif command_lower == 'preamble':
            parse_body = self.parse_preamble_body
            make_result = lambda: (command, (self.current_value,))
        elif command_lower == 'comment':
            raise SkipEntry
        else:
            parse_body = self.parse_entry_body
            make_result = lambda: (command, (self.current_entry_key, self.current_fields))
        try:
            parse_body(body_end)
            self.required([body_end])
        except PybtexSyntaxError as error:
            self.handle_error(error)
        return make_result()

    def parse_preamble_body(self, body_end):
        self.parse_value()

    def parse_string_body(self, body_end):
        self.current_field_name = self.required([self.NAME]).value
        self.required([self.EQUALS])
        self.parse_value()
        self.macros[self.current_field_name] = ''.join(self.current_value)

    def parse_entry_body(self, body_end):
        if not self.keyless_entries:
            key_pattern = self.KEY_PAREN if body_end == self.RPAREN else self.KEY_BRACE
            self.current_entry_key = self.required([key_pattern]).value
        self.parse_entry_fields()
        if not self.want_current_entry():
            raise SkipEntry

    def parse_entry_fields(self):
        while True:
            self.current_field_name = None
            self.current_value = []
            self.parse_field()
            if self.current_field_name and self.current_value:
                self.current_fields.append((self.current_field_name, self.current_value))
            comma = self.optional([self.COMMA])
            if not comma:
                return

    def parse_field(self):
        name = self.optional([self.NAME])
        if not name:
            return
        self.current_field_name = name.value
        self.required([self.EQUALS])
        self.parse_value()

    def parse_value(self):
        start = True
        concatenation = False
        value_parts = []
        while True:
            if not start:
                concatenation = self.optional([self.HASH])
            if not (start or concatenation):
                break
            value_parts.append(self.parse_value_part())
            start = False
        self.current_value = value_parts

    def parse_value_part(self):
        token = self.required(
            [self.QUOTE, self.LBRACE, self.NUMBER, self.NAME],
            description='field value',
        )
        if token.pattern is self.QUOTE:
            value_part = self.flatten_string(self.parse_string(string_end=self.QUOTE))
        elif token.pattern is self.LBRACE:
            value_part = self.flatten_string(self.parse_string(string_end=self.RBRACE))
        elif token.pattern is self.NUMBER:
            value_part = token.value
        else:
            value_part = self.substitute_macro(token.value)
        return value_part

    def flatten_string(self, parts):
        return ''.join(part.value for part in parts)[:-1]

    def substitute_macro(self, name):
        try:
            return self.macros[name]
        except KeyError:
            if self.want_current_entry():
                self.handle_error(UndefinedMacro(name, self))
            return ''

    def parse_string(self, string_end, level=0):
        special_chars = [self.RBRACE, self.LBRACE]
        if string_end is self.QUOTE:
            special_chars = [self.QUOTE] + special_chars
        while True:
            part = self.skip_to(special_chars)
            if not part:
                raise PrematureEOF(self)
            if part.pattern is string_end:
                yield part
                break
            elif part.pattern is self.LBRACE:
                yield part
                for subpart in self.parse_string(self.RBRACE, level + 1):
                    yield subpart
            elif part.pattern is self.RBRACE and level == 0:
                raise PybtexSyntaxError('unbalanced braces', self)


class Parser(BaseParser):
    default_suffix = '.bib'
    unicode_io = True

    macros = None

    def __init__(self,
            encoding=None,
            macros=month_names,
            person_fields=Person.valid_roles,
            keyless_entries=False,
            **kwargs
        ):
        BaseParser.__init__(self, encoding, **kwargs)

        self.macros = CaseInsensitiveDict(macros)
        self.person_fields = CaseInsensitiveSet(person_fields)
        self.keyless_entries = keyless_entries

    def process_entry(self, entry_type, key, fields):
        entry = Entry(entry_type)

        if key is None:
            key = 'unnamed-%i' % self.unnamed_entry_counter
            self.unnamed_entry_counter += 1

        for field_name, field_value_list in fields:
            field_value = textutils.normalize_whitespace(self.flatten_value_list(field_value_list))
            if field_name in self.person_fields:
                for name in split_name_list(field_value):
                    entry.add_person(Person(name), field_name)
            else:
                entry.fields[field_name] = field_value
        self.data.add_entry(key, entry)

    def process_preamble(self, value_list):
        value = textutils.normalize_whitespace(self.flatten_value_list(value_list))
        self.data.add_to_preamble(value)

    def flatten_value_list(self, value_list):
        return ''.join(value_list)

    def handle_error(self, error):
        from pybtex.errors import report_error
        report_error(error)

    def parse_stream(self, stream):
        self.unnamed_entry_counter = 1
        text = stream.read()
        self.command_start = 0

        entry_iterator = BibTeXEntryIterator(
            text,
            keyless_entries=self.keyless_entries,
            handle_error=self.handle_error,
            want_entry=self.data.want_entry,
            filename=self.filename,
            macros=self.macros,
        )
        for entry in entry_iterator:
            entry_type = entry[0]
            entry_type_lower = entry_type.lower()
            if entry_type_lower == 'string':
                pass
            elif entry_type_lower == 'preamble':
                self.process_preamble(*entry[1])
            else:
                self.process_entry(entry_type, *entry[1])
        return self.data

