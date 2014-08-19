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

"""name formatting styles
"""

from pybtex.plugin import Plugin
from pybtex.richtext import Symbol, Text, nbsp
from pybtex.style.template import join, together, node, _format_list


class BaseNameStyle(Plugin):
    def format(self, person, abbr=False):
        raise NotImplementedError


def tie_or_space(word, tie='~', space = ' ', enough_chars=3):
    if len(word) < enough_chars:
        return tie
    else:
        return space
    

@node
def name_part(children, data, before='', tie=False):
    parts = together [children].format_data(data)
    if not parts:
        return Text()
    if tie:
        return Text(before, parts, tie_or_space(parts, nbsp, ' '))
    else:
        return Text(before, parts)
