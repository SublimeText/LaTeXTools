#!/usr/bin/env python

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


from pybtex.cmdline import CommandLine, make_option, standard_option

class PybtexFormatCommandLine(CommandLine):
    prog = 'pybtex-format'
    args = '[options] in_filename out_filename'
    description = 'format bibliography database as human-readable text'
    long_description = """

pybtex-format formats bibliography database as human-readable text.
    """.strip()
    num_args = 2

    options = (
        (None, (
            standard_option('strict'),
            standard_option('bib_format'),
            standard_option('output_backend'),
            standard_option('min_crossrefs'),
            standard_option('keyless_entries'),
            standard_option('style'),
        )),
        ('Pythonic style options', (
            standard_option('label_style'),
            standard_option('name_style'),
            standard_option('sorting_style'),
            standard_option('abbreviate_names'),
        )),
        ('Encoding options', (
            standard_option('encoding'),
            standard_option('input_encoding'),
            standard_option('output_encoding'),
        )),
    )
    option_defaults = {
        'keyless_entries': False,
    }

    def run(
        self, from_filename, to_filename,
        encoding, input_encoding, output_encoding,
        keyless_entries,
        **options
    ):
        from pybtex.database.format import format_database

        format_database(
            from_filename, to_filename,
            input_encoding=input_encoding or encoding,
            output_encoding=output_encoding or encoding,
            parser_options={'keyless_entries': keyless_entries},
            **options
        )


main = PybtexFormatCommandLine()


if __name__ == '__main__':
    main()
