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

"""bibliography processor
"""


def make_bibliography(aux_filename,
        bib_format=None,
        bib_encoding=None,
        output_encoding=None,
        output_backend=None,
        min_crossrefs=2,
        style=None,
        **kwargs
        ):
    """This functions extracts all nessessary information from .aux file
    and writes the bibliography.
    """

    from os import path
    from pybtex import auxfile
    from pybtex.plugin import find_plugin

    filename = path.splitext(aux_filename)[0]
    aux_data = auxfile.parse_file(aux_filename, output_encoding)

    bib_parser = find_plugin('pybtex.database.input', bib_format)
    bib_data = bib_parser(
        encoding=bib_encoding,
        wanted_entries=aux_data.citations,
        min_crossrefs=min_crossrefs,
    ).parse_files(aux_data.data, bib_parser.default_suffix)

    if style is None:
        style = aux_data.style
    style_cls = find_plugin('pybtex.style.formatting', style)
    style = style_cls(
            label_style=kwargs.get('label_style'),
            name_style=kwargs.get('name_style'),
            sorting_style=kwargs.get('sorting_style'),
            abbreviate_names=kwargs.get('abbreviate_names'),
            min_crossrefs=min_crossrefs,
    )
    formatted_bibliography = style.format_bibliography(bib_data, aux_data.citations)

    output_backend = find_plugin('pybtex.backends', output_backend)
    output_filename = filename + output_backend.default_suffix
    output_backend(output_encoding).write_to_file(formatted_bibliography, output_filename)
