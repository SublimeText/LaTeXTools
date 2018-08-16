from __future__ import print_function

import sublime
import sublime_plugin

import re
import sys

try:
    from latextools_utils import is_bib_buffer, is_biblatex_buffer
except ImportError:
    from .latextools_utils import is_bib_buffer, is_biblatex_buffer

if sys.version_info > (3, 0):
    strbase = str
else:
    strbase = basestring

# Regexes to detect the various types of crossref fields
# Expected field in the format:
#   <field> = {<value>,<value>}
# Should support partials approaching this format
#
# I've tried to simply the comprehensibility of the backwards regexes used by
# constructing them here
#
# VALUE_REGEX is a common suffix to hand the `= {<value>,<value>}` part
VALUE_REGEX = r'(?!.*\})\s*(?P<ENTRIES>(?:,[^,]*)+\b)?\s*(?P<OPEN>\{)?(?P<EQUALS>\s*=\s*)?'
CROSSREF_REGEX = re.compile(
    VALUE_REGEX + r'crossref'[::-1] + r'\b',
    re.IGNORECASE | re.UNICODE
)

BIBLATEX_REGEX = re.compile(
    VALUE_REGEX + r'(?:' + r'|'.join((s[::-1] for s in ('xref', 'related'))) + r')' + r'\b',
    re.IGNORECASE | re.UNICODE
)

ENTRY_SET_REGEX = re.compile(
    VALUE_REGEX + r'entryset'[::-1] + r'\b',
    re.IGNORECASE | re.UNICODE
)

XDATA_REGEX = re.compile(
    VALUE_REGEX + r'xdata'[::-1] + r'\b',
    re.IGNORECASE | re.UNICODE
)

# set indicating entries that have their own special handling...
SPECIAL_ENTRIES = set(['@xdata', '@set'])

def _get_keys_by_type(view, valid_types):
    if not valid_types:
        return []

    if callable(valid_types):
        validator = valid_types
    elif type(valid_types) == strbase:
        def validator(s):
            return s == valid_types
    else:
        def validator(s):
            return s in valid_types

    keys = []

    contents = view.substr(sublime.Region(0, view.size()))
    for entry_type, key in re.findall(
        r'(@(?!preamble|comment|string)[a-zA-Z]+)\s*\{\s*([^,]+)\b',
        contents,
        re.IGNORECASE | re.UNICODE
    ):
        if validator(entry_type):
            keys.append(key)

    return keys

# BibLaTeX supports custom user-defined keys specified in the `id` field
def _get_keys_from_id_field(view):
    keys = []

    contents = view.substr(sublime.Region(0, view.size()))
    # TODO: Should probably figure out how to work out the entry-type
    for ids in re.findall(
        r'\bids\s*=\s*\{([^}]+)\}',
        contents,
        re.IGNORECASE | re.UNICODE | re.DOTALL
    ):
        for key in re.findall(
            r'\b([^,]+)\b',
            ids,
            re.IGNORECASE | re.UNICODE
        ):
            keys.append(key)

    return keys

def _get_cite_keys_validator(s):
    return s not in SPECIAL_ENTRIES

def get_cite_keys(view):
    return _get_keys_by_type(view, _get_cite_keys_validator) + \
        _get_keys_from_id_field(view)

def get_xdata_keys(view):
    return _get_keys_by_type(view, '@xdata')

def get_entryset_keys(view):
    return _get_keys_by_type(view, '@set')

def get_text_to_cursor(view):
    cursor = view.sel()[0].b
    current_region = sublime.Region(0, cursor)
    return view.substr(current_region)

# builds the replacement string depending on the current context of the line
def _get_replacement(matcher, key):
    if not matcher.group('ENTRIES'):
        return u'{0}{1}{2}{3}'.format(
            u'' if matcher.group('EQUALS') else u'= ',
            u'' if matcher.group('OPEN') else u'{',
            key,
            u'' if matcher.group('OPEN') else u'}'
        )

    return '{0}{1}'.format(
        u',' if matcher.group('ENTRIES')[0] != u',' else u'',
        key
    )

def get_completions_if_matches(regex, line, get_key_list_func, view):
    matcher = regex.match(line)
    if matcher:
        return ([(key, _get_replacement(matcher, key))
                for key in sorted(set(get_key_list_func(view)))],
                sublime.INHIBIT_WORD_COMPLETIONS |
                sublime.INHIBIT_EXPLICIT_COMPLETIONS)
    else:
        return []

class BiblatexCrossrefCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not is_bib_buffer(view):
            return []

        current_line = get_text_to_cursor(view)[::-1]

        if current_line.startswith(prefix[::-1]):
            current_line = current_line[len(prefix):]

        result = get_completions_if_matches(
            CROSSREF_REGEX, current_line, get_cite_keys, view)

        if result:
            return result

        if not is_biblatex_buffer(view):
            return []

        return get_completions_if_matches(
                    BIBLATEX_REGEX, current_line, get_cite_keys, view) or \
            get_completions_if_matches(
                    XDATA_REGEX, current_line, get_xdata_keys, view) or \
            get_completions_if_matches(
                    ENTRY_SET_REGEX, current_line, get_entryset_keys, view) or \
            []