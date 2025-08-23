import re

import sublime
import sublime_plugin

from .utils.decorators import async_completions

__all__ = ["BiblatexCrossrefCompletions"]

# Regexes to detect the various types of crossref fields
# Expected field in the format:
#   <field> = {<value>,<value>}
# Should support partials approaching this format
#
# I've tried to simply the comprehensibility of the backwards regexes used by
# constructing them here
#
# VALUE_REGEX is a common suffix to hand the `= {<value>,<value>}` part
VALUE_REGEX = r"(?!.*\})\s*(?P<ENTRIES>(?:,[^,]*)+\b)?\s*(?P<OPEN>\{)?(?P<EQUALS>\s*=\s*)?"

CROSSREF_REGEX = re.compile(VALUE_REGEX + r"crossref"[::-1] + r"\b", re.IGNORECASE)

BIBLATEX_REGEX = re.compile(
    VALUE_REGEX + r"(?:" + r"|".join((s[::-1] for s in ("xref", "related"))) + r")" + r"\b",
    re.IGNORECASE,
)

ENTRY_SET_REGEX = re.compile(VALUE_REGEX + r"entryset"[::-1] + r"\b", re.IGNORECASE)

XDATA_REGEX = re.compile(VALUE_REGEX + r"xdata"[::-1] + r"\b", re.IGNORECASE)

# set indicating entries that have their own special handling...
SPECIAL_ENTRIES = set(["@xdata", "@set"])


def _get_keys_by_type(view, valid_types):
    if not valid_types:
        return []

    if callable(valid_types):
        validator = valid_types
    elif isinstance(valid_types, str):

        def validator(s):
            return s == valid_types

    else:

        def validator(s):
            return s in valid_types

    keys = []

    contents = view.substr(sublime.Region(0, view.size()))
    for entry_type, key in re.findall(
        r"(@(?!preamble|comment|string)[a-zA-Z]+)\s*\{\s*([^,]+)\b", contents, re.IGNORECASE
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
        r"\bids\s*=\s*\{([^}]+)\}", contents, re.IGNORECASE | re.UNICODE | re.DOTALL
    ):
        for key in re.findall(r"\b([^,]+)\b", ids, re.IGNORECASE | re.UNICODE):
            keys.append(key)

    return keys


def _get_cite_keys_validator(s):
    return s not in SPECIAL_ENTRIES


def get_cite_keys(view):
    return _get_keys_by_type(view, _get_cite_keys_validator) + _get_keys_from_id_field(view)


def get_xdata_keys(view):
    return _get_keys_by_type(view, "@xdata")


def get_entryset_keys(view):
    return _get_keys_by_type(view, "@set")


def get_text_to_cursor(view):
    cursor = view.sel()[0].b
    current_region = sublime.Region(0, cursor)
    return view.substr(current_region)


# builds the replacement string depending on the current context of the line
def _get_replacement(matcher, key):
    if not matcher.group("ENTRIES"):
        return "{0}{1}{2}{3}".format(
            "" if matcher.group("EQUALS") else "= ",
            "" if matcher.group("OPEN") else "{",
            key,
            "" if matcher.group("OPEN") else "}",
        )

    return "{0}{1}".format("," if matcher.group("ENTRIES")[0] != "," else "", key)


def get_completions_if_matches(regex, line, get_key_list_func, view):
    matcher = regex.match(line)
    if not matcher:
        return []

    KIND_INFO = [sublime.KIND_ID_NAVIGATION, "r", "Reference"]

    completions = [
        sublime.CompletionItem(
            trigger=name,
            completion=_get_replacement(matcher, name),
            kind=KIND_INFO
        )
        for name in get_key_list_func(view)
    ]

    return completions


class BiblatexCrossrefCompletions(sublime_plugin.EventListener):
    @async_completions
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "text.bibtex, text.biblatex"):
            return []

        current_line = get_text_to_cursor(view)[::-1]

        if current_line.startswith(prefix[::-1]):
            current_line = current_line[len(prefix) :]

        result = get_completions_if_matches(CROSSREF_REGEX, current_line, get_cite_keys, view)

        if result:
            return result

        if not view.match_selector(locations[0], "text.biblatex"):
            return []

        return (
            get_completions_if_matches(BIBLATEX_REGEX, current_line, get_cite_keys, view)
            or get_completions_if_matches(XDATA_REGEX, current_line, get_xdata_keys, view)
            or get_completions_if_matches(ENTRY_SET_REGEX, current_line, get_entryset_keys, view)
            or []
        )
