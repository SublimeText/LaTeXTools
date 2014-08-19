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
from pybtex.database.input import BaseParser
from pybtex.database import Entry, Person


class Parser(BaseParser):
    default_suffix = '.yaml'

    def parse_stream(self, stream):
        t = yaml.safe_load(stream)

        entries = ((key, self.process_entry(entry))
                for (key, entry) in t['entries'].items())

        try:
            self.data.add_to_preamble(t['preamble'])
        except KeyError:
            pass

        self.data.add_entries(entries)
        return self.data

    def process_entry(self, entry):
        bib_entry = Entry(entry['type']) 
        for (key, value) in entry.items():
            key_lower = key.lower()
            if key_lower in Person.valid_roles:
                for names in value:
                    bib_entry.add_person(Person(**names), key)
            elif key_lower == 'type':
                pass
            else:
                bib_entry.fields[key] = str(value)
        return bib_entry
