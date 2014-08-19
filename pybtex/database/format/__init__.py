# Copyright (c) 2013  Andrey Golovizin
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

"""
Format bibliography database as human-readable text.
"""

from pybtex.plugin import find_plugin


def format_database(from_filename, to_filename,
        bib_format=None, output_backend=None,
        input_encoding=None, output_encoding=None,
        parser_options=None,
        min_crossrefs=2,
        style=None,
        **kwargs
    ):
    if parser_options is None:
        parser_options = {}
    input_format = find_plugin('pybtex.database.input', name=bib_format, filename=from_filename)
    output_backend = find_plugin('pybtex.backends', output_backend, filename=to_filename)
    
    bib_data = input_format(input_encoding, **parser_options).parse_file(from_filename)
    style_cls = find_plugin('pybtex.style.formatting', style)
    style = style_cls(
            label_style=kwargs.get('label_style'),
            name_style=kwargs.get('name_style'),
            sorting_style=kwargs.get('sorting_style'),
            abbreviate_names=kwargs.get('abbreviate_names'),
            min_crossrefs=min_crossrefs,
    )
    formatted_bibliography = style.format_bibliography(bib_data)
    output_backend(output_encoding).write_to_file(formatted_bibliography, to_filename)
