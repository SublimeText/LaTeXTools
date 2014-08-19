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

import pybtex.io
from pybtex.bibtex.exceptions import BibTeXError
from pybtex.bibtex.utils import scan_bibtex_string
from pybtex.database.output import BaseWriter


class Writer(BaseWriter):
    """Outputs BibTeX markup"""

    unicode_io = True

    def quote(self, s):
        """
        >>> w = Writer()
        >>> print(w.quote('The World'))
        "The World"
        >>> print(w.quote(r'The \emph{World}'))
        "The \emph{World}"
        >>> print(w.quote(r'The "World"'))
        {The "World"}
        >>> try:
        ...     print(w.quote(r'The {World'))
        ... except BibTeXError as error:
        ...     print(error)
        String has unmatched braces: The {World
        """

        self.check_braces(s)
        if '"' not in s:
            return '"%s"' % s
        else:
            return '{%s}' % s

    def check_braces(self, s):
        """
        Raise an exception if the given string has unmatched braces.

        >>> w = Writer()
        >>> w.check_braces('Cat eats carrots.')
        >>> w.check_braces('Cat eats {carrots}.')
        >>> w.check_braces('Cat eats {carrots{}}.')
        >>> w.check_braces('')
        >>> w.check_braces('end}')
        >>> try:
        ...     w.check_braces('{')
        ... except BibTeXError as error:
        ...     print(error)
        String has unmatched braces: {
        >>> w.check_braces('{test}}')
        >>> try:
        ...     w.check_braces('{{test}')
        ... except BibTeXError as error:
        ...     print(error)
        String has unmatched braces: {{test}

        """

        tokens = list(scan_bibtex_string(s))
        if tokens:
            end_brace_level = tokens[-1][1]
            if end_brace_level != 0:
                raise BibTeXError('String has unmatched braces: %s' % s)

    def write_stream(self, bib_data, stream):
        def write_field(type, value):
            stream.write(',\n    %s = %s' % (type, self.quote(value)))
        def format_name(person):
            def join(l):
                return ' '.join([name for name in l if name])
            first = person.get_part_as_text('first')
            middle = person.get_part_as_text('middle')
            prelast = person.get_part_as_text('prelast')
            last = person.get_part_as_text('last')
            lineage = person.get_part_as_text('lineage')
            s = '' 
            if last:
                s += join([prelast, last])
            if lineage:
                s += ', %s' % lineage
            if first or middle:
                s += ', '
                s += join([first, middle])
            return s
        def write_persons(persons, role):
#            persons = getattr(entry, role + 's')
            if persons:
                write_field(role, ' and '.join([format_name(person) for person in persons]))
        def write_preamble(preamble):
            if preamble:
                stream.write('@preamble{%s}\n\n' % self.quote(preamble))

        write_preamble(bib_data.get_preamble())
        for key, entry in bib_data.entries.items():
            stream.write('@%s' % entry.original_type)
            stream.write('{%s' % key)
#            for role in ('author', 'editor'):
            for role, persons in entry.persons.items():
                write_persons(persons, role)
            for type, value in entry.fields.items():
                write_field(type, value)
            stream.write('\n}\n\n')

