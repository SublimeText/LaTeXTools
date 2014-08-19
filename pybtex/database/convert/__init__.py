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

"""convert bibliography database from one format to another
"""
from os import path
from pybtex.exceptions import PybtexError
from pybtex.plugin import find_plugin

class ConvertError(PybtexError):
    pass


def convert(from_filename, to_filename,
        from_format=None, to_format=None,
        input_encoding=None, output_encoding=None,
        parser_options=None,
        preserve_case=True,
        **kwargs
        ):
    if parser_options is None:
        parser_options = {}
    input_format = find_plugin('pybtex.database.input', name=from_format, filename=from_filename)
    output_format = find_plugin('pybtex.database.output', name=to_format, filename=to_filename)
    
    if from_filename == to_filename:
        raise ConvertError('input and output file can not be the same')

    bib_data = input_format(input_encoding, **parser_options).parse_file(from_filename)
    if not preserve_case:
        bib_data = bib_data.lower()
    output_format(output_encoding).write_file(bib_data, to_filename)
