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

from xml.etree import cElementTree as ET
from pybtex.database import Entry, Person
from pybtex.database.input import BaseParser


bibtexns = '{http://bibtexml.sf.net/}'


def remove_ns(s):
    if s.startswith(bibtexns):
        return s[len(bibtexns):]

class Parser(BaseParser):
    default_suffix = '.xml'

    def parse_stream(self, stream):
        t = ET.parse(stream)
        entries = t.findall(bibtexns + 'entry')
        self.data.add_entries(self.process_entry(entry) for entry in entries)
        return self.data

    def process_entry(self, entry):
        def process_person(person_entry, role):
            persons = person_entry.findall(bibtexns + 'person')
            if persons:
                for person in persons:
                    process_person(person, role)
            else:
                text = person_entry.text.strip()
                if text:
                    e.add_person(Person(text), role)
                else:
                    names = {}
                    for name in person_entry.getchildren():
                        names[remove_ns(name.tag)] = name.text
                    e.add_person(Person(**names), role)
                        

        id_ = entry.get('id')
        item = entry.getchildren()[0]
        type = remove_ns(item.tag)
        e = Entry(type)
        for field in item.getchildren():
            field_name = remove_ns(field.tag)
            if field_name in Person.valid_roles:
                process_person(field, field_name)
            else:
                field_text = field.text if field.text is not None else ''
                e.fields[field_name] = field_text
        return id_, e
