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

import yaml
from pybtex.database import Entry
from pybtex.database.output import BaseWriter


class Writer(BaseWriter):
    """Outputs YAML markup"""

    def write_stream(self, bib_data, stream):
        def process_person_roles(entry):
            for role, persons in entry.persons.items():
                yield role, list(process_persons(persons))

        def process_person(person):
            for type in ('first', 'middle', 'prelast', 'last', 'lineage'):
                name = person.get_part_as_text(type)
                if name:
                    yield type, name

        def process_persons(persons):
            for person in persons:
                yield dict(process_person(person))
                
        def process_entries(bib_data):
            for key, entry in bib_data.items():
                fields = dict(entry.fields)
                fields['type'] = entry.original_type
                fields.update(process_person_roles(entry))
                yield key, fields

        data = {'entries': dict(process_entries(bib_data.entries))}
        preamble = bib_data.get_preamble()
        if preamble:
            data['preamble'] = preamble
        yaml.safe_dump(data, stream, allow_unicode=True, encoding='UTF-8', default_flow_style=False, indent=4)
