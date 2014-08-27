# vim: fileencoding=utf-8
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

import re

from collections import Mapping

from pybtex.exceptions import PybtexError
from pybtex.utils import (
    deprecated,
    OrderedCaseInsensitiveDict, CaseInsensitiveDefaultDict, CaseInsensitiveSet
)
from pybtex.bibtex.utils import split_tex_string
from pybtex.errors import report_error


class BibliographyDataError(PybtexError):
    pass


class BibliographyData(object):
    def __init__(self, entries=None, preamble=None, wanted_entries=None, min_crossrefs=2):
        self.entries = OrderedCaseInsensitiveDict()
        self.crossref_count = CaseInsensitiveDefaultDict(int)
        self.min_crossrefs = min_crossrefs
        self._preamble = []
        if wanted_entries is not None:
            self.wanted_entries = CaseInsensitiveSet(wanted_entries)
            self.citations = CaseInsensitiveSet(wanted_entries)
        else:
            self.wanted_entries = None
            self.citations = CaseInsensitiveSet()
        if entries:
            if isinstance(entries, Mapping):
                entries = iter(entries.items())
            for (key, entry) in entries:
                self.add_entry(key, entry)
        if preamble:
            self._preamble.extend(preamble)

    def __eq__(self, other):
        if not isinstance(other, BibliographyData):
            return super(BibliographyData, self) == other
        return (
            self.entries == other.entries
            and self._preamble == other._preamble
        )

    def __repr__(self):
        return 'BibliographyData(entries={entries}, preamble={preamble})'.format(
            entries=repr(self.entries),
            preamble=repr(self._preamble),
        )

    def add_to_preamble(self, *values):
        self._preamble.extend(values)

    @deprecated('0.17', 'use get_preamble instead')
    def preamble(self):
        return self.get_preamble()

    def get_preamble(self):
        return ''.join(self._preamble)

    def want_entry(self, key):
        return (
            self.wanted_entries is None
            or key in self.wanted_entries
            or '*' in self.wanted_entries
        )

    def get_canonical_key(self, key):
        if key in self.citations:
            return self.citations.get_canonical_key(key)
        else:
            return key

    def add_entry(self, key, entry):
        if not self.want_entry(key):
            return
        if key in self.entries:
            report_error(BibliographyDataError('repeated bibliograhpy entry: %s' % key))
            return
        entry.collection = self
        entry.key = self.get_canonical_key(key)
        self.entries[entry.key] = entry
        try:
            crossref = entry.fields['crossref']
        except KeyError:
            pass
        else:
            if self.wanted_entries is not None:
                self.wanted_entries.add(crossref)

    def add_entries(self, entries):
        for key, entry in entries:
            self.add_entry(key, entry)

    def get_crossreferenced_citations(self, citations, min_crossrefs):
        """
        Get cititations not cited explicitly but referenced by other citations.

        >>> from pybtex.database import Entry
        >>> data = BibliographyData({
        ...     'main_article': Entry('article', {'crossref': 'xrefd_arcicle'}),
        ...     'xrefd_arcicle': Entry('article'),
        ... })
        >>> list(data.get_crossreferenced_citations([], min_crossrefs=1))
        []
        >>> list(data.get_crossreferenced_citations(['main_article'], min_crossrefs=1))
        ['xrefd_arcicle']
        >>> list(data.get_crossreferenced_citations(['Main_article'], min_crossrefs=1))
        ['xrefd_arcicle']
        >>> list(data.get_crossreferenced_citations(['main_article'], min_crossrefs=2))
        []
        >>> list(data.get_crossreferenced_citations(['xrefd_arcicle'], min_crossrefs=1))
        []

        >>> data2 = BibliographyData(data.entries, wanted_entries=list(data.entries.keys()))
        >>> list(data2.get_crossreferenced_citations([], min_crossrefs=1))
        []
        >>> list(data2.get_crossreferenced_citations(['main_article'], min_crossrefs=1))
        ['xrefd_arcicle']
        >>> list(data2.get_crossreferenced_citations(['Main_article'], min_crossrefs=1))
        ['xrefd_arcicle']
        >>> list(data2.get_crossreferenced_citations(['main_article'], min_crossrefs=2))
        []
        >>> list(data2.get_crossreferenced_citations(['xrefd_arcicle'], min_crossrefs=1))
        []
        >>> list(data2.get_crossreferenced_citations(['xrefd_arcicle'], min_crossrefs=1))
        []

        """

        crossref_count = CaseInsensitiveDefaultDict(int)
        citation_set = CaseInsensitiveSet(citations)
        for citation in citations:
            try:
                entry = self.entries[citation]
                crossref = entry.fields['crossref']
            except KeyError:
                continue
            try:
                crossref_entry = self.entries[crossref]
            except KeyError:
                report_error(BibliographyDataError(
                    'bad cross-reference: entry "{key}" refers to '
                    'entry "{crossref}" which does not exist.'.format(
                        key=citation, crossref=crossref,
                    )
                ))
                continue

            canonical_crossref = crossref_entry.key
            crossref_count[canonical_crossref] += 1
            if crossref_count[canonical_crossref] >= min_crossrefs and canonical_crossref not in citation_set:
                citation_set.add(canonical_crossref)
                yield canonical_crossref

    def expand_wildcard_citations(self, citations):
        """
        Expand wildcard citations (\citation{*} in .aux file).

        >>> from pybtex.database import Entry
        >>> data = BibliographyData((
        ...     ('uno', Entry('article')),
        ...     ('dos', Entry('article')),
        ...     ('tres', Entry('article')),
        ...     ('cuatro', Entry('article')),
        ... ))
        >>> list(data.expand_wildcard_citations([]))
        []
        >>> list(data.expand_wildcard_citations(['*']))
        ['uno', 'dos', 'tres', 'cuatro']
        >>> list(data.expand_wildcard_citations(['uno', '*']))
        ['uno', 'dos', 'tres', 'cuatro']
        >>> list(data.expand_wildcard_citations(['dos', '*']))
        ['dos', 'uno', 'tres', 'cuatro']
        >>> list(data.expand_wildcard_citations(['*', 'uno']))
        ['uno', 'dos', 'tres', 'cuatro']
        >>> list(data.expand_wildcard_citations(['*', 'DOS']))
        ['uno', 'dos', 'tres', 'cuatro']

        """

        citation_set = CaseInsensitiveSet()
        for citation in citations:
            if citation == '*':
                for key in self.entries:
                    if key not in citation_set:
                        citation_set.add(key)
                        yield key
            else:
                if citation not in citation_set:
                    citation_set.add(citation)
                    yield citation

    def add_extra_citations(self, citations, min_crossrefs):
        expanded_citations = list(self.expand_wildcard_citations(citations))
        crossrefs = list(self.get_crossreferenced_citations(expanded_citations, min_crossrefs))
        return expanded_citations + crossrefs

    def lower(self):
        """
        Return another BibliographyData with all identifiers converted to lowercase.

        >>> data = BibliographyData([
        ...     ('Obrazy', Entry('Book', [('Title', 'Obrazy z Rus')], [('Author', 'Karel Havlíček Borovský')])),
        ...     ('Elegie', Entry('BOOK', [('TITLE', 'Tirolské elegie')], [('AUTHOR', 'Karel Havlíček Borovský')])),
        ... ]).lower()
        >>> list(data.entries.keys())
        ['obrazy', 'elegie']
        >>> for entry in list(data.entries.values()):
        ...     entry.key
        ...     list(entry.persons.keys())
        ...     list(entry.fields.keys())
        'obrazy'
        ['author']
        ['title']
        'elegie'
        ['author']
        ['title']

        """

        entries_lower = ((key.lower(), entry.lower()) for key, entry in self.entries.items())
        return type(self)(
            entries=entries_lower,
            preamble=self._preamble,
            wanted_entries=self.wanted_entries,
            min_crossrefs=self.min_crossrefs,
        )


class FieldDict(OrderedCaseInsensitiveDict):
    def __init__(self, parent, *args, **kwargw):
        self.parent = parent
        super(FieldDict, self).__init__(*args, **kwargw)

    def __getitem__(self, key):
        try:
            return super(FieldDict, self).__getitem__(key)
        except KeyError:
            if key in self.parent.persons:
                persons = self.parent.persons[key]
                return ' and '.join(str(person) for person in persons)
            elif 'crossref' in self:
                return self.parent.get_crossref().fields[key]
            else:
                raise KeyError(key)
    
    def lower(self):
        lower_dict = super(FieldDict, self).lower()
        return type(self)(self.parent, self.iteritems_lower())


class Entry(object):
    """Bibliography entry. Important members are:
    - persons (a dict of Person objects)
    - fields (all dict of string)
    """

    def __init__(self, type_, fields=None, persons=None, collection=None):
        if fields is None:
            fields = {}
        if persons is None:
            persons = {}
        self.type = type_.lower()
        self.original_type = type_
        self.fields = FieldDict(self, fields)
        self.persons = OrderedCaseInsensitiveDict(persons)
        self.collection = collection

        # for BibTeX interpreter
        self.vars = {}

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return super(Entry, self) == other
        return (
                self.type == other.type
                and self.fields == other.fields
                and self.persons == other.persons
        )

    def __repr__(self):
        return 'Entry({type_}, fields={fields}, persons={persons})'.format(
            type_=repr(self.type),
            fields=repr(self.fields),
            persons=repr(self.persons),
        )

    def get_crossref(self):
        return self.collection.entries[self.fields['crossref']]

    def add_person(self, person, role):
        self.persons.setdefault(role, []).append(person)

    def lower(self):
        return type(self)(
            self.type,
            fields=self.fields.lower(),
            persons=self.persons.lower(),
            collection=self.collection,
        )



class Person(object):
    """Represents a person (usually human).

    >>> p = Person('Avinash K. Dixit')
    >>> print(p.first())
    ['Avinash']
    >>> print(p.middle())
    ['K.']
    >>> print(p.prelast())
    []
    >>> print(p.last())
    ['Dixit']
    >>> print(p.lineage())
    []
    >>> print(str(p))
    Dixit, Avinash K.
    >>> p == Person(str(p))
    True
    >>> p = Person('Dixit, Jr, Avinash K. ')
    >>> print(p.first())
    ['Avinash']
    >>> print(p.middle())
    ['K.']
    >>> print(p.prelast())
    []
    >>> print(p.last())
    ['Dixit']
    >>> print(p.lineage())
    ['Jr']
    >>> print(str(p))
    Dixit, Jr, Avinash K.
    >>> p == Person(str(p))
    True

    >>> p = Person('abc')
    >>> print(p.first(), p.middle(), p.prelast(), p.last(), p.lineage())
    [] [] [] ['abc'] []
    >>> p = Person('Viktorov, Michail~Markovitch')
    >>> print(p.first(), p.middle(), p.prelast(), p.last(), p.lineage())
    ['Michail'] ['Markovitch'] [] ['Viktorov'] []
    """
    valid_roles = ['author', 'editor'] 
    style1_re = re.compile('^(.+),\s*(.+)$')
    style2_re = re.compile('^(.+),\s*(.+),\s*(.+)$')

    def __init__(self, string="", first="", middle="", prelast="", last="", lineage=""):
        self._first = []
        self._middle = []
        self._prelast = []
        self._last = []
        self._lineage = []
        string = string.strip()
        if string:
            self.parse_string(string)
        self._first.extend(split_tex_string(first))
        self._middle.extend(split_tex_string(middle))
        self._prelast.extend(split_tex_string(prelast))
        self._last.extend(split_tex_string(last))
        self._lineage.extend(split_tex_string(lineage))

    def parse_string(self, name):
        """Extract various parts of the name from a string.
        Supported formats are:
         - von Last, First
         - von Last, Jr, First
         - First von Last
        (see BibTeX manual for explanation)
        """
        def process_first_middle(parts):
            try:
                self._first.append(parts[0])
                self._middle.extend(parts[1:])
            except IndexError:
                pass

        def process_von_last(parts):
            von, last = rsplit_at(parts, lambda part: part.islower())
            if von and not last:
                last.append(von.pop())
            self._prelast.extend(von)
            self._last.extend(last)

        def find_pos(lst, pred):
            for i, item in enumerate(lst):
                if pred(item):
                    return i
            return i + 1

        def split_at(lst, pred):
            """Split the given list into two parts.

            The second part starts with the first item for which the given
            predicate is True.
            """
            pos = find_pos(lst, pred)
            return lst[:pos], lst[pos:]

        def rsplit_at(lst, pred):
            rpos = find_pos(reversed(lst), pred)
            pos = len(lst) - rpos
            return lst[:pos], lst[pos:]

        parts = split_tex_string(name, ',')
        if len(parts) == 3: # von Last, Jr, First
            process_von_last(split_tex_string(parts[0]))
            self._lineage.extend(split_tex_string(parts[1]))
            process_first_middle(split_tex_string(parts[2]))
        elif len(parts) == 2: # von Last, First
            process_von_last(split_tex_string(parts[0]))
            process_first_middle(split_tex_string(parts[1]))
        elif len(parts) == 1: # First von Last
            parts = split_tex_string(name)
            first_middle, von_last = split_at(parts, lambda part: part.islower())
            if not von_last and first_middle:
                last = first_middle.pop()
                von_last.append(last)
            process_first_middle(first_middle)
            process_von_last(von_last)
        else:
            raise PybtexError('Invalid name format: %s' % name)

    def __eq__(self, other):
        if not isinstance(other, Person):
            return super(Person, self) == other
        return (
                self._first == other._first
                and self._middle == other._middle
                and self._prelast == other._prelast
                and self._last == other._last
                and self._lineage == other._lineage
        )

    def __str__(self):
        # von Last, Jr, First
        von_last = ' '.join(self._prelast + self._last)
        jr = ' '.join(self._lineage)
        first = ' '.join(self._first + self._middle)
        return ', '.join(part for part in (von_last, jr, first) if part)

    def __repr__(self):
        return 'Person({0})'.format(repr(str(self)))

    def get_part_as_text(self, type):
        names = getattr(self, '_' + type)
        return ' '.join(names)

    def get_part(self, type, abbr=False):
        names = getattr(self, '_' + type)
        if abbr:
            from pybtex.textutils import abbreviate
            names = [abbreviate(name) for name in names]
        return names

    #FIXME needs some thinking and cleanup
    def bibtex_first(self):
        """Return first and middle names together.
        (BibTeX treats all middle names as first)
        """
        return self._first + self._middle

    def first(self, abbr=False):
        return self.get_part('first', abbr)
    def middle(self, abbr=False):
        return self.get_part('middle', abbr)
    def prelast(self, abbr=False):
        return self.get_part('prelast', abbr)
    def last(self, abbr=False):
        return self.get_part('last', abbr)
    def lineage(self, abbr=False):
        return self.get_part('lineage', abbr)

