# Copyright (c) 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
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

from xml.sax.saxutils import escape
from pybtex.backends import BaseBackend
import pybtex.io


PROLOGUE = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head><meta name="generator" content="Pybtex">
<meta http-equiv="Content-Type" content="text/html; charset=%s">
<title>Bibliography</title>
</head>
<body>
<dl>
"""

class Backend(BaseBackend):
    default_suffix = '.html'
    symbols = {
        'ndash': '&ndash;',
        'newblock': '\n',
        'nbsp': '&nbsp;'
    }
    tags = {
         'emph': 'em',
    }
    
    def format_text(self, text):
        return escape(text)

    def format_tag(self, tag_name, text):
        tag = self.tags[tag_name]
        return r'<%s>%s</%s>' % (tag, text, tag)
    
    def format_href(self, url, text):
        return r'<a href="%s">%s</a>' % (url, text)

    def write_prologue(self):
        encoding = self.encoding or pybtex.io.get_default_encoding()
        self.output(PROLOGUE % encoding)

    def write_epilogue(self):
        self.output('</dl></body></html>\n')

    def write_entry(self, key, label, text):
        self.output('<dt>%s</dt>\n' % label)
        self.output('<dd>%s</dd>\n' % text)
