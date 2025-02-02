# coding=utf-8
import re

import sublime
import sublime_plugin

from ..vendor.bibtex.names import Name
from ..vendor.bibtex.tex import tokenize_list
from .utils.decorators import async_completions

__all__ = ["BiblatexNameCompletions"]

NAME_FIELDS = Name.NAME_FIELDS

# Regex to recognise if we are in a name field
#
# I've tried to simply the comprehensibility of the backwards regexes used by
# constructing them here
#
# VALUE_REGEX is a common suffix to handle the `= {<value> and <value>}` part
VALUE_REGEX = r"[\s~]*(?P<ENTRIES>(?:dna[\s~]+.+)+)?[\s~]*(?P<OPEN>\{)?(?P<EQUALS>\s*=\s*)?"

ON_NAME_FIELD_REGEX = re.compile(
    VALUE_REGEX + r"(?:" + r"|".join((s[::-1] for s in NAME_FIELDS)) + r")\b", re.IGNORECASE
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
    if not matcher.group("ENTRIES"):
        equals = matcher.group("EQUALS")

        return "{0}{1}{2}".format(
            "" if equals else "= " if match.startswith(" ") else " = ",
            "" if matcher.group("OPEN") else "{" if not equals or match.startswith(" ") else " {",
            key,
        )

    if matcher.group("ENTRIES").startswith("dna"):
        if match.startswith(" "):
            return "{0}".format(key)
        return " {0}".format(key)
    else:
        return "{0}{1}".format(" " if matcher.group("ENTRIES").startswith(" ") != " " else "", key)


NAME_FIELD_REGEX = re.compile(
    r"(?:^|[\s~]+)(?:" + r"|".join(NAME_FIELDS) + r")\s*=\s*\{", re.IGNORECASE
)


def get_names_from_view(view):
    contents = view.substr(sublime.Region(0, view.size()))
    return get_names(contents)


def get_names(contents):
    """
    Work-horse function to extract all the names defined in the current bib
    file.
    """
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
                if c == "}":
                    bracket_depth -= 1

                if bracket_depth == 0:
                    break

                if c == "{":
                    bracket_depth += 1

                chars.append(c)

            names.extend([str(Name(s)) for s in tokenize_list("".join(chars))])

            pos += len(chars)
            if pos >= contents_length:
                break
            in_entry = False

    return set(names)


class BiblatexNameCompletions(sublime_plugin.EventListener):
    @async_completions
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "text.bibtex, text.biblatex"):
            return []

        current_line = get_text_to_cursor(view)[::-1]

        if current_line.startswith(prefix[::-1]):
            current_line = current_line[len(prefix) :]

        matcher = ON_NAME_FIELD_REGEX.match(current_line)
        if not matcher:
            return []

        KIND_INFO = [sublime.KIND_ID_VARIABLE, "n", "Name"]

        return [
            sublime.CompletionItem(
                trigger=name,
                completion=_get_replacement(matcher, name),
                kind=KIND_INFO,
                details=" ",
            )
            for name in get_names_from_view(view)
        ]
