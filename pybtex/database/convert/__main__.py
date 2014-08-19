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


from pybtex.cmdline import CommandLine, make_option, standard_option

class PybtexConvertCommandLine(CommandLine):
    prog = 'pybtex-convert'
    args = '[options] in_filename out_filename' 
    description = 'convert between bibliography database formats'
    long_description = """

pybtex-convert converts bibliography database files between supported formats
(currently BibTeX, BibTeXML and YAML).

    """.strip()

    num_args = 2

    options = (
        (None, (
            standard_option('strict'),
            make_option(
                '-f', '--from', dest='from_format',
                help='input format (%plugin_choices)', metavar='FORMAT',
                type='load_plugin', plugin_group='pybtex.database.input',
            ),
            make_option(
                '-t', '--to', dest='to_format',
                help='output format (%plugin_choices)', metavar='FORMAT',
                type='load_plugin', plugin_group='pybtex.database.output',
            ),
            standard_option('keyless_entries'),
            make_option(
                '--preserve-case', dest='preserve_case',
                action='store_true',
                help='do not convert identifiers to lower case',
            ),
        )),
        ('Encoding options', (
            standard_option('encoding'),
            standard_option('input_encoding'),
            standard_option('output_encoding'),
        )),
    )
    option_defaults = {
        'keyless_entries': False,
        'preserve_case': False,
    }

    def run(
        self, from_filename, to_filename,
        encoding, input_encoding, output_encoding,
        keyless_entries,
        **options
    ):
        from pybtex.database.convert import convert, ConvertError

        convert(from_filename, to_filename,
            input_encoding=input_encoding or encoding,
            output_encoding=output_encoding or encoding,
            parser_options = {'keyless_entries': keyless_entries},
            **options
        )

main = PybtexConvertCommandLine()

if __name__ == '__main__':
    main()
