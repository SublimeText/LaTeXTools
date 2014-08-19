# Copyright (c) 2010, 2011, 2012  Andrey Golovizin
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


import errno
import posixpath
from unittest import TestCase

from pybtex import io


class MockFile(object):
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def __repr__(self):
        return "<mock open file '%s', mode '%s'>" % (self.name, self.mode)
    

class MockFilesystem(object):
    def __init__(self, files=(), writable_dirs=(), readonly_dirs=()):
        self.files = set(files)
        self.writable_dirs = set(writable_dirs)
        self.readonly_dirs = set(readonly_dirs)

    def add_file(self, path):
        self.files.add(path)

    def chdir(self, path):
        self.pwd = path

    def locate(self, filename):
        for path in self.files:
            if path.endswith(filename):
                return path

    def open_read(self, path, mode):
        if path in self.files:
            return MockFile(path, mode)
        else:
            raise IOError(errno.ENOENT, 'No such file or directory', path)

    def open_write(self, path, mode):
        dirname = posixpath.dirname(path)
        if dirname in self.writable_dirs:
            return MockFile(path, mode)
        else:
            raise IOError(errno.EACCES, 'Permission denied', path)

    def open(self, path, mode):
        full_path = posixpath.join(self.pwd, path)
        if 'w' in mode:
            return self.open_write(full_path, mode)
        else:
            return self.open_read(full_path, mode)


class IOTest(TestCase):
    def setUp(self):
        self.fs = MockFilesystem(
            files=(
                '/home/test/foo.bib',
                '/home/test/foo.bbl',
                '/usr/share/texmf/bibtex/bst/unsrt.bst',
            ),
            writable_dirs = ('/home/test',),
            readonly_dirs = ('/'),
        )
        self.fs.chdir('/home/test')

    def test_open_existing(self):
        file = io._open_existing(self.fs.open, 'foo.bbl', 'rb', locate=self.fs.locate)
        self.assertEqual(file.name, '/home/test/foo.bbl')
        self.assertEqual(file.mode, 'rb')
        
    def test_open_missing(self):
        self.assertRaises(
            EnvironmentError,
            io._open_existing, self.fs.open, 'nosuchfile.bbl', 'rb',
            locate=self.fs.locate,
        )

    def test_locate(self):
        file = io._open_existing(
            self.fs.open, 'unsrt.bst', 'rb', locate=self.fs.locate
        )
        self.assertEqual(file.name, '/usr/share/texmf/bibtex/bst/unsrt.bst')
        self.assertEqual(file.mode, 'rb')

    def test_create(self):
        file = io._open_or_create(self.fs.open, 'foo.bbl', 'wb', {})
        self.assertEqual(file.name, '/home/test/foo.bbl')
        self.assertEqual(file.mode, 'wb')

    def test_create_in_readonly_dir(self):
        self.fs.chdir('/')
        self.assertRaises(
            EnvironmentError,
            io._open_or_create, self.fs.open, 'foo.bbl', 'wb', {},
        )

    def test_create_in_fallback_dir(self):
        self.fs.chdir('/')
        file = io._open_or_create(
            self.fs.open, 'foo.bbl', 'wb', {'TEXMFOUTPUT': '/home/test'}
        )
        self.assertEqual(file.name, '/home/test/foo.bbl')
        self.assertEqual(file.mode, 'wb')
