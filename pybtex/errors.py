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

from io import StringIO
from contextlib import contextmanager

import pybtex.io
from pybtex.textutils import capfirst, add_period


strict = True
error_code = 0
captured_errors = None


def set_strict_mode(enable=True):
    global strict
    strict = enable


@contextmanager
def capture():
    """Capture exceptions for debug purposes."""

    global captured_errors
    captured_errors = []
    try:
        yield captured_errors
    finally:
        captured_errors = None


def format_error(exception, prefix='ERROR: '):
    lines = []
    context = exception.get_context()
    if context:
        lines += (context.splitlines())
    lines.append('{0}{1}'.format(prefix, str(exception)))
    filename = exception.get_filename()
    if filename:
        lines = (
            '{0}: {1}'.format(filename, line)
            for line in lines
        )
    return '\n'.join(lines)


def print_error(exception, prefix='ERROR: '):
    print(format_error(exception, prefix), file=pybtex.io.stderr)


def report_error(exception):
    global error_code

    if captured_errors is not None:
        captured_errors.append(exception)
        return

    if strict:
        raise exception
    else:
        print_error(exception, 'WARNING: ')
        error_code = 2
