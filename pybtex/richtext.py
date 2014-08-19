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

r"""(simple but) rich text formatting tools

Usage:

>>> from pybtex.backends import latex
>>> backend = latex.Backend()
>>> t = Text('this ', 'is a ', Tag('emph', 'very'), Text(' rich', ' text'))
>>> print(t.render(backend))
this is a \emph{very} rich text
>>> print(t.plaintext())
this is a very rich text
>>> t = t.capfirst().add_period()
>>> print(t.render(backend))
This is a \emph{very} rich text.
>>> print(t.plaintext())
This is a very rich text.
>>> print(Symbol('ndash').render(backend))
--
>>> t = Text('Some ', Tag('emph', Text('nested ', Tag('texttt', 'Text', Text(' objects')))), '.')
>>> print(t.render(backend))
Some \emph{nested \texttt{Text objects}}.
>>> print(t.plaintext())
Some nested Text objects.
>>> t = t.map(lambda string: string.upper())
>>> print(t.render(backend))
SOME \emph{NESTED \texttt{TEXT OBJECTS}}.
>>> print(t.plaintext())
SOME NESTED TEXT OBJECTS.

>>> t = Text(', ').join(['one', 'two', Tag('emph', 'three')])
>>> print(t.render(backend))
one, two, \emph{three}
>>> print(t.plaintext())
one, two, three
>>> t = Text(Symbol('nbsp')).join(['one', 'two', Tag('emph', 'three')])
>>> print(t.render(backend))
one~two~\emph{three}
>>> print(t.plaintext())
one<nbsp>two<nbsp>three
"""

from copy import deepcopy
from pybtex import textutils
import string

class Text(list):
    """
    Rich text is basically a list of:

    - plain strings
    - Text objects, including objects derived from Text (Tag, HRef, ...)
    - Symbol objects

    Text is used as an internal formatting language of Pybtex,
    being rendered to to HTML or LaTeX markup or whatever in the end.

    >>> Text()
    []
    >>> Text('a', '', 'c')
    ['a', 'c']
    >>> Text('a', Text(), 'c')
    ['a', 'c']
    >>> Text('a', Text('b', 'c'), Tag('emph', 'x'), Symbol('nbsp'), 'd')
    ['a', ['b', 'c'], ['x'], Symbol('nbsp'), 'd']
    >>> Text({}) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...

    """

    def __init__(self, *parts):
        """Create a Text consisting of one or more parts."""

        if not all(isinstance(part, (str, Text, Symbol))
                   for part in parts):
            raise TypeError(
                "parts must be str, Text or Symbol")
        list.__init__(self, [part for part in parts if part])

    def __len__(self):
        """Return the number of characters in this Text."""
        return sum(len(part) for part in self)

    def __add__(self, other):
        """
        Concatenate this Text with another Text or string.

        >>> t = Text('a')
        >>> print((t + 'b').plaintext())
        ab
        >>> print((t + t).plaintext())
        aa
        >>> print(t.plaintext())
        a
        """

        if isinstance(other, str):
            other = [other]
        return self.from_list(super(Text, self).__add__(other))

    def from_list(self, lst):
        return Text(*lst)

    def append(self, item):
        """Appends some text or something.
        Empty strings and similar things are ignored.
        """
        if item:
            list.append(self, item)

    def extend(self, list_):
        for item in list_:
            self.append(item)

    def render(self, backend):
        """Return backend-dependent textual representation of this Text."""

        rendered_list = []
        for item in self:
            if isinstance(item, str):
                rendered_list.append(backend.format_str(item))
            else:
                assert isinstance(item, (Text, Symbol))
                rendered_list.append(item.render(backend))
        assert all(isinstance(item, backend.RenderType)
                   for item in rendered_list)
        return backend.render_sequence(rendered_list)

    def enumerate(self):
        for n, child in enumerate(self):
            try:
                for p in child.enumerate():
                    yield p
            except AttributeError:
                yield self, n

    def reversed(self):
        for n, child in reversed(list(enumerate(self))):
            try:
                for p in child.reversed():
                    yield p
            except AttributeError:
                yield self, n

    def map(self, f, condition=None):
        if condition is None:
            condition = lambda index, length: True
        def iter_map_with_condition():
            length = len(self)
            for index, child in enumerate(self):
                if hasattr(child, 'map'):
                    yield child.map(f, condition) if condition(index, length) else child
                else:
                    yield f(child) if condition(index, length) else child
        return self.from_list(iter_map_with_condition())

    def upper(self):
        return self.map(string.upper)

    def apply_to_start(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == 0)

    def apply_to_end(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == length - 1)

    def get_beginning(self):
        try:
            l, i = next(self.enumerate())
        except StopIteration:
            pass
        else:
            return l[i]

    def get_end(self):
        try:
            l, i = next(self.reversed())
        except StopIteration:
            pass
        else:
            return l[i]

    def join(self, parts):
        """Join a list using this text (like string.join)

        >>> print(Text(' ').join([]).plaintext())
        <BLANKLINE>
        >>> print(Text(' ').join(['a', 'b', 'c']).plaintext())
        a b c
        >>> print(Text(nbsp).join(['a', 'b', 'c']).plaintext())
        a<nbsp>b<nbsp>c
        """

        joined = Text()
        if not parts:
            return joined
        for part in parts[:-1]:
            joined.extend([part, deepcopy(self)])
        joined.append(parts[-1])
        return joined

    def plaintext(self):
        return ''.join(str(l[i]) for l, i in self.enumerate())

    def capfirst(self):
        """Capitalize the first letter of the text.

        >>> Text(Text(), Text('mary ', 'had ', 'a little lamb')).capfirst()
        [['Mary ', 'had ', 'a little lamb']]

        """
        return self.apply_to_start(textutils.capfirst)

    def add_period(self, period='.'):
        """Add a period to the end of text, if necessary.

        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Backend()

        >>> text = Text("That's all, folks")
        >>> print(text.add_period().plaintext())
        That's all, folks.

        >>> text = Tag('emph', Text("That's all, folks"))
        >>> print(text.add_period().render(html))
        <em>That's all, folks.</em>
        >>> print(text.add_period().add_period().render(html))
        <em>That's all, folks.</em>

        >>> text = Text("That's all, ", Tag('emph', 'folks'))
        >>> print(text.add_period().render(html))
        That's all, <em>folks</em>.
        >>> print(text.add_period().add_period().render(html))
        That's all, <em>folks</em>.

        >>> text = Text("That's all, ", Tag('emph', 'folks.'))
        >>> print(text.add_period().render(html))
        That's all, <em>folks.</em>

        >>> text = Text("That's all, ", Tag('emph', 'folks'))
        >>> print(text.add_period('!').render(html))
        That's all, <em>folks</em>!
        >>> print(text.add_period('!').add_period('.').render(html))
        That's all, <em>folks</em>!
        """

        end = self.get_end()
        if end and not textutils.is_terminated(end):
            return self + period
        else:
            return self

class Tag(Text):
    """A tag is somethins like <foo>some text</foo> in HTML
    or \\foo{some text} in LaTeX. 'foo' is the tag's name, and
    'some text' is tag's text.

    >>> emph = Tag('emph', 'emphasized text')
    >>> from pybtex.backends import latex, html
    >>> print(emph.render(latex.Backend()))
    \emph{emphasized text}
    >>> print(emph.render(html.Backend()))
    <em>emphasized text</em>
    """

    def from_list(self, lst):
        return Tag(self.name, *lst)

    def __init__(self, name, *args):
        if not isinstance(name, (str, Text)):
            raise TypeError(
                "name must be str or Text (got %s)" % name.__class__.__name__)
        if isinstance(name, Text):
            name = name.plaintext()
        self.name = name
        Text.__init__(self, *args)

    def render(self, backend):
        text = super(Tag, self).render(backend)
        return backend.format_tag(self.name, text)

class HRef(Text):
    """A href is somethins like <href url="URL">some text</href> in HTML
    or \href{URL}{some text} in LaTeX.

    >>> href = HRef('http://www.example.com', 'hyperlinked text')
    >>> from pybtex.backends import latex, html, plaintext
    >>> print(href.render(latex.Backend()))
    \href{http://www.example.com}{hyperlinked text}
    >>> print(href.render(html.Backend()))
    <a href="http://www.example.com">hyperlinked text</a>
    >>> print(href.render(plaintext.Backend()))
    hyperlinked text
    """

    def __init__(self, url, *args):
        if not isinstance(url, (str, Text)):
            raise TypeError(
                "url must be str or Text (got %s)" % url.__class__.__name__)
        if isinstance(url, Text):
            url = url.plaintext()
        self.url = url
        Text.__init__(self, *args)

    def render(self, backend):
        text = super(HRef, self).render(backend)
        return backend.format_href(self.url, text)

class Symbol(object):
    """A special symbol.

    Examples of special symbols are non-breaking spaces and dashes.

    >>> nbsp = Symbol('nbsp')
    >>> from pybtex.backends import latex, html
    >>> print(nbsp.render(latex.Backend()))
    ~
    >>> print(nbsp.render(html.Backend()))
    &nbsp;
    """

    def __init__(self, name):
        self.name = name

    def __len__(self):
        return 1

    def __repr__(self):
        return "Symbol('%s')" % self.name

    def __str__(self):
        return '<%s>' % self.name

    def render(self, backend):
        return backend.symbols[self.name]

nbsp = Symbol('nbsp')

