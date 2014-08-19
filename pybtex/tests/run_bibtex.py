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



import sys
import re
from os import path
from tempfile import mkdtemp
from shutil import rmtree
from subprocess import Popen, PIPE

from pybtex.database.output import bibtex
from pybtex.database import BibliographyData
from pybtex.database import Person, Entry


writer = bibtex.Writer(encoding='ascii')


def write_aux(filename, citations):
    with open(filename, 'w') as aux_file:
        for citation in citations:
            aux_file.write('\\citation{%s}\n' % citation)
        aux_file.write('\\bibdata{test}\n')
        aux_file.write('\\bibstyle{test}\n')


def write_bib(filename, database):
    writer.write_file(database, filename)


def write_bst(filename, style):
    with open(filename, 'w') as bst_file:
        bst_file.write(style)
        bst_file.write('\n')


def run_bibtex(style, database, citations=None):
    if citations is None:
        citations = list(database.entries.keys())
    tmpdir = mkdtemp(prefix='pybtex_test_')
    try:
        write_bib(path.join(tmpdir, 'test.bib'), database)
        write_aux(path.join(tmpdir, 'test.aux'), citations)
        write_bst(path.join(tmpdir, 'test.bst'), style)
        bibtex = Popen(('bibtex', 'test'), cwd=tmpdir, stdout=PIPE, stderr=PIPE)
        stdout, stderr = bibtex.communicate()
        if bibtex.returncode:
            raise ValueError(stdout)
        with open(path.join(tmpdir, 'test.bbl')) as bbl_file:
            result = bbl_file.read()
        return result
    finally:
        pass
        rmtree(tmpdir)


def execute(code, database=None):
    if database is None:
        database = BibliographyData(entries={'test_entry': Entry('article')})
    bst = """
        ENTRY {name format} {} {}
        FUNCTION {article}
        {
            %s write$ newline$
        }
        READ
        ITERATE {call.type$}
    """.strip() % code
    [result] = run_bibtex(bst, database).splitlines()
    return result


def format_name(name, format):
    return execute('"%s" #1 "%s" format.name$' % (name, format))


def parse_name(name):
    space = re.compile('[\s~]+')
    formatted_name = format_name(name, '{ff}|{vv}|{ll}|{jj}')
    parts = [space.sub(' ', part.strip()) for part in formatted_name.split('|')]
    first, von, last, junior = parts
    return Person(first=first, prelast=von, last=last, lineage=junior)


def main():
    args = sys.argv[1:2]
    if len(args) != 1:
        print("usage: run_bibtex 'some bibtex code'")
        sys.exit(1)
    code = args[0]
    print(execute(code))


if __name__ == '__main__':
    main()
