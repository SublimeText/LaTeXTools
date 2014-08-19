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


"""Unicode-aware IO routines."""



import io
import sys
from os import path, environ

from pybtex.exceptions import PybtexError
from pybtex.kpathsea import kpsewhich


def get_default_encoding():
    return 'UTF-8'

    
def get_stream_encoding(stream):
    stream_encoding = getattr(stream, 'encoding', None)
    return stream_encoding or get_default_encoding()


def _open_existing(opener, filename, mode, locate, **kwargs):
    if not path.isfile(filename):
        found = locate(filename)
        if found:
            filename = found
    return opener(filename, mode, **kwargs)


def _open_or_create(opener, filename, mode, environ, **kwargs):
    try:
        return opener(filename, mode, **kwargs)
    except EnvironmentError as error:
        if 'TEXMFOUTPUT' in environ:
            new_filename = path.join(environ['TEXMFOUTPUT'], filename)
            try:
                return opener(new_filename, mode, **kwargs)
            except EnvironmentError:
                pass
        raise error


def _open(opener, filename, mode, **kwargs):
    write_mode = 'w' in mode
    try:
        if write_mode:
            return _open_or_create(opener, filename, mode, environ, **kwargs)
        else:
            return _open_existing(opener, filename, mode, locate=kpsewhich, **kwargs)
    except EnvironmentError as error:
        raise PybtexError("unable to open %s. %s" % (filename, error.strerror))


def open_raw(filename, mode='rb', encoding=None):
    return _open(io.open, filename, mode)


def open_unicode(filename, mode='r', encoding=None):
    if encoding is None:
        encoding = get_default_encoding()
    return _open(io.open, filename, mode, encoding=encoding)


def reader(stream, encoding=None, errors='strict'):
    if encoding is None:
        encoding = get_stream_encoding(stream)
    return io.TextIOWrapper(stream, encoding=encoding, errors=errors)


stdout = sys.stdout
stderr = sys.stderr
