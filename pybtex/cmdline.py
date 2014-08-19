#!/usr/bin/env python

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

import sys
import optparse

from pybtex.__version__ import version

from pybtex import errors
from pybtex.textutils import capfirst, add_period
from pybtex.plugin import find_plugin, enumerate_plugin_names


def check_plugin(option, option_string, value):
    return find_plugin(option.plugin_group, value)


class PybtexOption(optparse.Option):
    ATTRS = optparse.Option.ATTRS + ['plugin_group']
    TYPES = optparse.Option.TYPES + ('load_plugin',)
    TYPE_CHECKER = dict(optparse.Option.TYPE_CHECKER, load_plugin=check_plugin)
    STANDARD_OPTIONS = {}


make_option = PybtexOption


def make_standard_option(*args, **kwargs):
    option = make_option(*args, **kwargs)
    PybtexOption.STANDARD_OPTIONS[option.dest] = option
    return option


def standard_option(name):
    return PybtexOption.STANDARD_OPTIONS[name]


make_standard_option(
    '--strict', dest='strict',
    help='turn warnings into errors',
    action='callback',
    callback=lambda option, opt, value, parser: errors.set_strict_mode(True)
)

make_standard_option(
    '-f', '--bibliography-format', dest='bib_format',
    help='bibliograpy format (%plugin_choices)',
    type='load_plugin',
    plugin_group='pybtex.database.input',
    metavar='FORMAT',
)

make_standard_option(
    '-b', '--output-backend', dest='output_backend',
    help='output backend (%plugin_choices)',
    type='load_plugin',
    plugin_group='pybtex.backends',
    metavar='BACKEND',
)

make_standard_option(
    '--min-crossrefs',
    type='int', dest='min_crossrefs',
    help='include item after NUMBER crossrefs; default 2',
    metavar='NUMBER',
)

make_standard_option(
    '--keyless-bibtex-entries',
    action='store_true', dest='keyless_entries',
    help='allow BibTeX entries without keys and generate unnamed-<number> keys for them'
)

make_standard_option(
    '-s', '--style',
    type='string', dest='style', help='bibliography formatting style',
)

make_standard_option(
    '--label-style', dest='label_style',
    help='label formatting style (%plugin_choices)',
    type='load_plugin',
    plugin_group='pybtex.style.labels',
    metavar='STYLE',
)

make_standard_option(
    '--name-style', dest='name_style',
    help='name formatting style (%plugin_choices)',
    type='load_plugin',
    plugin_group='pybtex.style.names',
    metavar='STYLE',
)

make_standard_option(
    '--sorting-style', dest='sorting_style',
    help='sorting style (%plugin_choices)',
    type='load_plugin',
    plugin_group='pybtex.style.sorting',
    metavar='STYLE',
)

make_standard_option(
    '--abbreviate-names',
    action='store_true', dest='abbreviate_names',
    help='use abbreviated name formatting style',
)

make_standard_option(
    '-e', '--encoding',
    action='store', type='string', dest='encoding',
    help='default encoding',
    metavar='ENCODING',
)

make_standard_option(
    '--input-encoding',
    action='store', type='string', dest='input_encoding',
    metavar='ENCODING',
)

make_standard_option(
    '--output-encoding',
    action='store', type='string', dest='output_encoding',
    metavar='ENCODING',
)


BaseHelpFormatter = optparse.IndentedHelpFormatter
class PybtexHelpFormatter(BaseHelpFormatter):
    def get_plugin_choices(self, plugin_group):
        return ', '.join(sorted(enumerate_plugin_names(plugin_group)))

    def expand_default(self, option):
        result = BaseHelpFormatter.expand_default(self, option)
        if option.plugin_group:
            plugin_choices = self.get_plugin_choices(option.plugin_group)
            result = result.replace('%plugin_choices', plugin_choices)
        return result


class CommandLine(object):
    options = ()
    option_defaults = None
    legacy_options = ()
    prog = None
    args = None
    description = ''
    num_args = 0

    def __init__(self):
        self.opt_parser = self.make_option_parser()

    def __call__(self):
        from pybtex.exceptions import PybtexError
        import pybtex.io
        try:
            self.main()
        except PybtexError as error:
            errors.print_error(error)
            sys.exit(1)

    def make_option_parser(self):
        opt_parser = optparse.OptionParser(
            prog=self.prog,
            option_class=PybtexOption,
            formatter=PybtexHelpFormatter(),
            usage='%prog ' + self.args,
            description=capfirst(add_period(self.description)),
            version='%%prog-%s' % version
        )
        for option_group, option_list in self.options:
            if option_group is None:
                container = opt_parser
            else:
                container = opt_parser.add_option_group(option_group)
            for option in option_list:
                container.add_option(option)

        if self.option_defaults:
            opt_parser.set_defaults(**self.option_defaults)

        return opt_parser

    def run(self, options, args):
        raise NotImplementedError

    def recognize_legacy_optons(self, args):
        """Grok some legacy long options starting with a single `-'."""
        return [
            '-' + arg if arg.split('=', 1)[0] in self.legacy_options else arg
            for arg in args
        ]

    def _extract_kwargs(self, options):
        return dict(
            (option.dest, getattr(options, option.dest))
            for option_group, option_list in self.options
            for option in option_list
        )

    def main(self):
        errors.set_strict_mode(False)
        argv = self.recognize_legacy_optons(sys.argv[1:])
        options, args = self.opt_parser.parse_args(argv)
        if len(args) != self.num_args:
            self.opt_parser.print_help()
            sys.exit(1)
        kwargs = self._extract_kwargs(options)
        self.run(*args, **kwargs)
        sys.exit(errors.error_code)
