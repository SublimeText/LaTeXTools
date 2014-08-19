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
from pybtex.database import Entry
from pybtex.database.output import BaseWriter


doctype = """<!DOCTYPE bibtex:file PUBLIC
    "-//BibTeXML//DTD XML for BibTeX v1.0//EN"
        "bibtexml.dtd" >
"""

class PrettyTreeBuilder(object):
    def __init__(self):
        self.tree_builder = ET.TreeBuilder()
        self.close = self.tree_builder.close
        self.data = self.tree_builder.data
        self.stack = []

    def newline(self):
        self.data('\n')

    def indent_line(self):
        self.data(' ' * len(self.stack) * 4)

    def start(self, tag, attrs=None, newline=True):
        if attrs is None:
            attrs = {}
        self.indent_line()
        self.stack.append(tag)
        self.tree_builder.start(tag, attrs)
        if newline:
            self.newline()

    def end(self, indent=True):
        tag = self.stack.pop()
        if indent:
            self.indent_line()
        self.tree_builder.end(tag)
        self.newline()

    def element(self, tag, data):
        self.start(tag, newline=False)
        self.data(data)
        self.end(indent=False)


class Writer(BaseWriter):
    """Outputs BibTeXML markup"""

    def write_stream(self, bib_data, stream):
        def write_persons(persons, role):
            if persons:
                w.start('bibtex:' + role)
                for person in persons:
                    w.start('bibtex:person')
                    for type in ('first', 'middle', 'prelast', 'last', 'lineage'):
                        name = person.get_part_as_text(type)
                        if name:
                            w.element('bibtex:' + type, name)
                    w.end()
                w.end()

        w = PrettyTreeBuilder()
        bibtex_file = w.start('bibtex:file', {'xmlns:bibtex': 'http://bibtexml.sf.net/'})
        w.newline()

        for key, entry in bib_data.entries.items():
            w.start('bibtex:entry', dict(id=key))
            w.start('bibtex:' + entry.original_type)
            for field_name, field_value in entry.fields.items():
                w.element('bibtex:' + field_name, field_value)
            for role, persons in entry.persons.items():
                write_persons(persons, role)
            w.end()
            w.end()
            w.newline()
        w.end()

        tree = ET.ElementTree(w.close())
        tree.write(stream, self.encoding)
        stream.write(b'\n')
