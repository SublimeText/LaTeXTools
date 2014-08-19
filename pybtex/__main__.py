#!/usr/bin/env python

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

from pybtex.cmdline import CommandLine, make_option, standard_option


class PybtexCommandLine(CommandLine):
    prog = 'pybtex'
    args = '[options] auxfile.aux'
    description = 'BibTeX-compatible bibliography processor in Python'
    long_description = """

Pybtex reads citation information from a LaTeX .aux file and produces a
formatted bibliography. Pybtex understands BibTeX .bib and .bst style files and
can be used as a drop-in replacement for BibTeX.

Besides BibTeX .bib files, BibTeXML and YAML bibliography files are
supported.

It is also possible to define bibliography formatting styles in Python.

    """.strip()
    num_args = 1

    options = (
        (None, (
            standard_option('strict'),
            make_option(
                '--terse', dest='verbose', action='store_false',
                help='ignored for compatibility with BibTeX',
            ),
            standard_option('min_crossrefs'),
            standard_option('bib_format'),
            standard_option('output_backend'),
            standard_option('style'),
            make_option(
                '-l', '--style-language', dest='style_language',
                help='style definition language to use (bibtex or python)',
                metavar='LANGUAGE',
            ),
        )),
        ('Pythonic style options', (
            standard_option('label_style'),
            standard_option('name_style'),
            standard_option('sorting_style'),
            standard_option('abbreviate_names'),
        )),
        ('Encoding options', (
            standard_option('encoding'),
            make_option('--bibtex-encoding', dest='bib_encoding', metavar='ENCODING'),
            make_option('--bst-encoding', dest='bst_encoding', metavar='ENCODING'),
            standard_option('output_encoding'),
        )),
    )
    option_defaults = {
        'style_language': 'bibtex',
        'min_crossrefs': 2,
    }
    legacy_options = '-help', '-version', '-min-crossrefs', '-terse'

    def run(self, filename, style_language, encoding, **options):
        if style_language == 'bibtex':
            from pybtex import bibtex as engine
        elif style_language == 'python':
            import pybtex as engine
        else:
            self.opt_parser.error('unknown style language %s' % style_language)

        not_supported_by_bibtex = {
            'output_backend': 'output backends',
            'label_style': 'label styles',
            'name_style': 'name styles',
            'sorting_style': 'sorting styles',
            'abbreviate_names': 'abbreviated names',
        }
        if style_language != 'python':
            for option, what_is_not_supported in not_supported_by_bibtex.items():
                if options[option]:
                    self.opt_parser.error(
                        '%s are only supported by the Pythonic style engine (-l python)' % what_is_not_supported
                    )

        for encoding_option in 'bib_encoding', 'bst_encoding', 'output_encoding':
            if not options[encoding_option]:
                options[encoding_option] = encoding

        ext = path.splitext(filename)[1]
        if ext != '.aux':
            filename = path.extsep.join([filename, 'aux'])
        engine.make_bibliography(filename, **options)

main = PybtexCommandLine()

if __name__ == '__main__':
    main()
