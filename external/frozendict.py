# The frozendict is originally available under the following license:
#
# Copyright (c) 2012 Santiago Lezica
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import collections
import copy

_iteritems = getattr(dict, 'iteritems', dict.items)  # py2-3 compatibility


class frozendict(collections.Mapping):
    """
    An immutable wrapper around dictionaries that implements the complete
    :py:class:`collections.Mapping` interface.

    It can be used as a drop-in replacement for dictionaries where immutability
    is desired.
    """

    dict_cls = dict

    def __init__(self, *args, **kwargs):
        self._dict = self.dict_cls(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        item = self._dict[key]
        if isinstance(item, dict):
            item = self._dict[key] = frozendict(**item)
        elif isinstance(item, list):
            item = self._dict[key] = tuple(item)
        elif isinstance(item, set):
            item = self._dict[key] = frozenset(item)
        elif hasattr(item, '__dict__') or hasattr(item, '__slots__'):
            return copy.copy(item)
        return item

    def __contains__(self, key):
        return key in self._dict

    def copy(self, **add_or_replace):
        return self.__class__(self, **add_or_replace)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._dict)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.__dict__.update(dict((
            (k, copy.deepcopy(v, memo)) for k, v in self.__dict__.items())))
        return result

    def __hash__(self):
        if self._hash is None:
            h = 0
            for key, value in _iteritems(self._dict):
                h ^= hash((key, value))
            self._hash = h
        return self._hash
