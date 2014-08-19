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


from pybtex.style.template import join
from pybtex.style.names import BaseNameStyle, name_part


class NameStyle(BaseNameStyle):

    def format(self, person, abbr=False):
        r"""
        Format names similarly to {ff~}{vv~}{ll}{, jj} in BibTeX.  

        >>> from pybtex.database import Person
        >>> name = Person(string=r"Charles Louis Xavier Joseph de la Vall{\'e}e Poussin")
        >>> plain = NameStyle().format
        >>> print(plain(name).format().plaintext())
        Charles Louis Xavier<nbsp>Joseph de<nbsp>la Vall{\'e}e<nbsp>Poussin
        >>> print(plain(name, abbr=True).format().plaintext())
        C.<nbsp>L. X.<nbsp>J. de<nbsp>la Vall{\'e}e<nbsp>Poussin

        >>> name = Person(first='First', last='Last', middle='Middle')
        >>> print(plain(name).format().plaintext())
        First<nbsp>Middle Last
        >>> print(plain(name, abbr=True).format().plaintext())
        F.<nbsp>M. Last
        >>> print(plain(Person('de Last, Jr., First Middle')).format().plaintext())
        First<nbsp>Middle de<nbsp>Last, Jr.
        """
        return join [
            name_part(tie=True) [person.first(abbr) + person.middle(abbr)],
            name_part(tie=True) [person.prelast()],
            name_part [person.last()],
            name_part(before=', ') [person.lineage()]
        ]


