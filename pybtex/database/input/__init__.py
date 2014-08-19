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



from os import path

import pybtex.io
from pybtex.plugin import Plugin
from pybtex.database import BibliographyData
from pybtex.exceptions import PybtexError


class BaseParser(Plugin):
    default_suffix = None
    filename = '<INPUT>'
    unicode_io = False

    def __init__(self, encoding=None, wanted_entries=None, min_crossrefs=2, **kwargs):
        self.encoding = encoding or pybtex.io.get_default_encoding()
        self.data = BibliographyData(
            wanted_entries=wanted_entries,
            min_crossrefs=min_crossrefs,
        )

    def parse_file(self, filename, file_suffix=None):
        if file_suffix is not None:
            filename = filename + file_suffix
        self.filename = filename
        open_file = pybtex.io.open_unicode if self.unicode_io else pybtex.io.open_raw
        with open_file(filename, encoding=self.encoding) as f:
            try:
                self.parse_stream(f)
            except UnicodeDecodeError as e:
                raise PybtexError(str(e), filename=self.filename)
        return self.data

    def parse_files(self, base_filenames, file_suffix=None):
        for filename in base_filenames:
            self.parse_file(filename, file_suffix)
        return self.data

    def parse_stream(self, stream):
        raise NotImplementedError
