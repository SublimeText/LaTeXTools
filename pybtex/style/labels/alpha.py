# -*- coding: utf-8 -*-

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


import sys
if sys.version_info < (2, 7):
   from counter import Counter
else:
   from collections import Counter

import re
import string
import unicodedata

from pybtex.style.labels import BaseLabelStyle

_nonalnum_pattern = re.compile('[^A-Za-z0-9]+', re.UNICODE)

def _strip_accents(s):
   return ''.join(
       (c for c in unicodedata.normalize('NFD', s)
        if not unicodedata.combining(c)))

def _strip_nonalnum(parts):
    """Strip all non-alphanumerical characters from a list of strings.

    >>> print(_strip_nonalnum(["ÅA. B. Testing 12+}[.@~_", " 3%"]))
    AABTesting123
    """
    s = ''.join(parts)
    return _nonalnum_pattern.sub('', _strip_accents(s))

class LabelStyle(BaseLabelStyle):

    def format_labels(self, sorted_entries):
        labels = [self.format_label(entry) for entry in sorted_entries]
        count = Counter(labels)
        counted = Counter()
        for label in labels:
            if count[label] == 1:
                yield label
            else:
                yield label + chr(ord('a') + counted[label])
                counted.update([label])

    # note: this currently closely follows the alpha.bst code
    # we should eventually refactor it

    def format_label(self, entry):
        # see alpha.bst calc.label
        if entry.type == "book" or entry.type == "inbook":
            label = self.author_editor_key_label(entry)
        elif entry.type == "proceedings":
            label = self.editor_key_organization_label(entry)
        elif entry.type == "manual":
            label = self.author_key_organization_label(entry)
        else:
            label = self.author_key_label(entry)
        if "year" in entry.fields:
            return label + entry.fields["year"][-2:]
        else:
            return label
        # bst additionally sets sort.label

    def author_key_label(self, entry):
        # see alpha.bst author.key.label
        if not "author" in entry.persons:
            if not "key" in entry.fields:
                return entry.key[:3] # entry.key is bst cite$
            else:
                # for entry.key, bst actually uses text.prefix$
                return entry.fields["key"][:3]
        else:
            return self.format_lab_names(entry.persons["author"])

    def author_editor_key_label(self, entry):
        # see alpha.bst author.editor.key.label
        if not "author" in entry.persons:
            if not "editor" in entry.persons:
                if not "key" in entry.fields:
                    return entry.key[:3] # entry.key is bst cite$
                else:
                    # for entry.key, bst actually uses text.prefix$
                    return entry.fields["key"][:3]
            else:
                return self.format_lab_names(entry.persons["editor"])
        else:
            return self.format_lab_names(entry.persons["author"])

    def author_key_organization_label(self, entry):
        if not "author" in entry.persons:
            if not "key" in entry.fields:
                if not "organization" in entry.fields:
                    return entry.key[:3] # entry.key is bst cite$
                else:
                    result = entry.fields["organization"]
                    if result.startswith("The "):
                        result = result[4:]
                    return result
            else:
                return entry.fields["key"][:3]
        else:
            return self.format_lab_names(entry.persons["author"])

    def editor_key_organization_label(self, entry):
        if not "editor" in entry.persons:
            if not "key" in entry.fields:
                if not "organization" in entry.fields:
                    return entry.key[:3] # entry.key is bst cite$
                else:
                    result = entry.fields["organization"]
                    if result.startswith("The "):
                        result = result[4:]
                    return result
            else:
                return entry.fields["key"][:3]
        else:
            return self.format_lab_names(entry.persons["editor"])

    def format_lab_names(self, persons):
        # see alpha.bst format.lab.names
        # s = persons
        numnames = len(persons)
        if numnames > 1:
            if numnames > 4:
                namesleft = 3
            else:
                namesleft = numnames
            result = ""
            nameptr = 1
            while namesleft:
                person = persons[nameptr - 1]
                if nameptr == numnames:
                    if str(person) == "others":
                        result += "+"
                    else:
                        result += _strip_nonalnum(
                            person.prelast(abbr=True) + person.last(abbr=True))
                else:
                    result += _strip_nonalnum(
                        person.prelast(abbr=True) + person.last(abbr=True))
                nameptr += 1
                namesleft -= 1
            if numnames > 4:
                result += "+"
        else:
            person = persons[0]
            result = _strip_nonalnum(
                person.prelast(abbr=True) + person.last(abbr=True))
            if len(result) < 2:
                result = _strip_nonalnum(person.last(abbr=False))[:3]
        return result

