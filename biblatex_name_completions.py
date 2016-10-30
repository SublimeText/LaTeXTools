# coding=utf-8

from __future__ import print_function

import sublime
import sublime_plugin

import re
import sys

try:
    from external.bibtex.names import Name
    from external.bibtex.tex import tokenize_list
    from latextools_utils import is_bib_buffer
except ImportError:
    from .external.bibtex.names import Name
    from .external.bibtex.tex import tokenize_list
    from .latextools_utils import is_bib_buffer

if sys.version_info > (3, 0):
    strbase = str
    unicode = str
else:
    strbase = basestring

NAME_FIELDS = Name.NAME_FIELDS

# Regex to recognise if we are in a name field
#
# I've tried to simply the comprehensibility of the backwards regexes used by
# constructing them here
#
# VALUE_REGEX is a common suffix to handle the `= {<value> and <value>}` part
VALUE_REGEX = r'[\s~]*(?P<ENTRIES>(?:dna[\s~]+.+)+)?[\s~]*' \
              r'(?P<OPEN>\{)?(?P<EQUALS>\s*=\s*)?'

ON_NAME_FIELD_REGEX = re.compile(
    VALUE_REGEX + r'(?:' + r'|'.join((s[::-1] for s in NAME_FIELDS)) + r')\b',
    re.IGNORECASE | re.UNICODE
)


def get_text_to_cursor(view):
    cursor = view.sel()[0].b
    current_region = sublime.Region(0, cursor)
    return view.substr(current_region)


# builds the replacement string depending on the current context of the line
def _get_replacement(matcher, key):
    if not matcher:
        return key

    match = matcher.group(0)
    if not matcher.group('ENTRIES'):
        equals = matcher.group('EQUALS')

        return u'{0}{1}{2}'.format(
            u'' if equals else u'= ' if match.startswith(u' ') else u' = ',
            u'' if matcher.group('OPEN') else u'{' if not equals or match.startswith(u' ') else u' {',
            key
        )

    if matcher.group('ENTRIES').startswith('dna'):
        if match.startswith(' '):
            return u'{0}'.format(key)
        return u' {0}'.format(key)
    else:
        return u'{0}{1}'.format(
            u' ' if matcher.group('ENTRIES').startswith(u' ') != u' ' else u'',
            key
        )

NAME_FIELD_REGEX = re.compile(
    r'(?:^|[\s~]+)(?:' + r'|'.join(NAME_FIELDS) + ')\s*=\s*\{',
    re.IGNORECASE | re.UNICODE
)


def get_names_from_view(view):
    contents = view.substr(sublime.Region(0, view.size()))
    return get_names(contents)


def get_names(contents):
    u'''
    Work-horse function to extract all the names defined in the current bib file.
    '''
    names = []

    in_entry = False
    pos = 0
    contents_length = len(contents)

    while True:
        if not in_entry:
            matcher = re.search(NAME_FIELD_REGEX, contents[pos:])
            # no more `name =` fields
            if not matcher:
                break

            pos += matcher.end()
            in_entry = True
        else:
            chars = []

            bracket_depth = 1
            for c in contents[pos:]:
                if c == '}':
                    bracket_depth -= 1

                if bracket_depth == 0:
                    break

                if c == '{':
                    bracket_depth += 1

                chars.append(c)

            names.extend([
                unicode(Name(s)) for s in tokenize_list(u''.join(chars))
            ])

            pos += len(chars)
            if pos >= contents_length:
                break
            in_entry = False

    return sorted(set(names))


class BiblatexNameCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if not is_bib_buffer(view):
            return []

        current_line = get_text_to_cursor(view)[::-1]

        if current_line.startswith(prefix[::-1]):
            current_line = current_line[len(prefix):]

        matcher = ON_NAME_FIELD_REGEX.match(current_line)
        if matcher:
            return ([
                (name, _get_replacement(matcher, name))
                for name in get_names_from_view(view)
            ],
                sublime.INHIBIT_WORD_COMPLETIONS |
                sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        return []
