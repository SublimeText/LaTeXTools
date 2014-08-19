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

from copy import deepcopy
from unittest import TestCase
from io import BytesIO, TextIOWrapper, BufferedWriter
import pickle

from .data import reference_data

from pybtex.plugin import find_plugin

class DatabaseIOTest(TestCase):
    def setUp(self):
        self.reference_data = deepcopy(reference_data)
        self.assertTrue(self.reference_data.entries)
        self.assertTrue(self.reference_data.get_preamble())

    def _test_input(self, plugin):
        parser = find_plugin('pybtex.database.input', plugin)(encoding='UTF-8')
        writer = find_plugin('pybtex.database.output', plugin)(encoding='UTF-8')
        stream = BytesIO()
        writer_stream = TextIOWrapper(stream, 'UTF-8') if writer.unicode_io else stream
        parser_stream = TextIOWrapper(stream, 'UTF-8') if parser.unicode_io else stream
        writer.write_stream(self.reference_data, writer_stream)
        writer_stream.flush()
        stream.seek(0)
        parser.parse_stream(parser_stream)
        loaded_data = parser.data
        self.assertEqual(loaded_data, self.reference_data)
        self.assertEqual(pickle.loads(pickle.dumps(loaded_data, 0)), self.reference_data)
        self.assertEqual(pickle.loads(pickle.dumps(loaded_data, 1)), self.reference_data)
        self.assertEqual(pickle.loads(pickle.dumps(loaded_data, 2)), self.reference_data)

    def test_bibtex_input(self):
        self._test_input('bibtex')

    def test_bibyaml_input(self):
        self._test_input('bibyaml')

    def test_bibtexml_input(self):
        # BibTeXML does not support TeX preambles AFAIK
        self.reference_data._preamble = []
        self._test_input('bibtexml')

    def test_repr(self):
        from pybtex.utils import OrderedCaseInsensitiveDict
        from pybtex.database import BibliographyData
        from pybtex.database import Entry, Person
        data_repr = repr(self.reference_data)
        data = eval(data_repr, {
            'OrderedCaseInsensitiveDict': OrderedCaseInsensitiveDict,
            'BibliographyData': BibliographyData,
            'Entry': Entry,
            'Person': Person,
        })
        self.assertEqual(data, self.reference_data)
