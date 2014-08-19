# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
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

"""BibTeX unnamed stack language interpreter and related stuff
"""


def make_bibliography(aux_filename,
        bib_format=None,
        bib_encoding=None,
        output_encoding=None,
        bst_encoding=None,
        min_crossrefs=2,
        style=None,
        **kwargs
    ):

    from os import path

    import pybtex.io
    from pybtex.bibtex import bst
    from pybtex.bibtex.interpreter import Interpreter
    from pybtex import auxfile


    if bib_format is None:
        from pybtex.database.input.bibtex import Parser as bib_format
    aux_data = auxfile.parse_file(aux_filename, output_encoding)
    if style is None:
        style = aux_data.style
    bst_filename = style + path.extsep + 'bst'
    bst_script = bst.parse_file(bst_filename, bst_encoding)
    base_filename = path.splitext(aux_filename)[0]
    bbl_filename = base_filename + path.extsep + 'bbl'
    bib_filenames = [filename + bib_format.default_suffix for filename in aux_data.data]
    interpreter = Interpreter(bib_format, bib_encoding)
    bbl_data = interpreter.run(bst_script, aux_data.citations, bib_filenames, min_crossrefs=min_crossrefs)
    with pybtex.io.open_unicode(bbl_filename, 'w', encoding=output_encoding) as bbl_file:
        bbl_file.write(bbl_data)
