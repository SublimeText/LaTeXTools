from .tex import split_tex_string
from collections import namedtuple
import sys

__all__ = ["Name"]

NameResult = namedtuple("NameResult", ["first", "middle", "prefix", "last", "generation"])


def tokenize_name(name_str):
    """
    Takes a string representing a name and returns a NameResult breaking that
    string into its component parts, as defined in the LaTeX book and BibTeXing.

    The supported formats are thus:

    First von Last
    von Last, First
    von Last, Jr, First

    We try to follow the rules in BibTeXing relatively strictly, meaning that the
    first of these formats can result in unexpected results because it is more
    ambiguous with complex names.
    """

    def extract_middle_names(first):
        return split_tex_string(first, 1)

    def extract_name_prefix(last):
        names = split_tex_string(last, 1)
        if len(names) == 1:
            return names

        result = [names[0]]

        new_names = split_tex_string(names[1], 1)
        while len(new_names) > 1 and new_names[0].islower():
            result[0] = " ".join((result[0], new_names[0]))
            names = new_names
            new_names = split_tex_string(names[1], 1)

        result.append(names[1])

        return result

    name_str = name_str.strip()

    parts = split_tex_string(name_str, sep=r",[\s~]*")
    if len(parts) == 1:
        # first last
        # reverse the string so split only selects the right-most instance of the token
        try:
            last, first = [part[::-1] for part in split_tex_string(parts[0][::-1], 1)]
        except ValueError:
            # we only have a single name
            return NameResult(parts[0], "", "", "", "")

        # because of our splitting method, van, von, della, etc. may end up at the end of the first name field
        first_parts = split_tex_string(first)
        first_parts_len = len(first_parts)
        if first_parts_len > 1:
            lower_name_index = None
            for i, part in enumerate(first_parts[::-1], 1):
                if part.islower():
                    if lower_name_index is None or lower_name_index == i - 1:
                        lower_name_index = i
                    else:
                        break
            if lower_name_index is not None:
                last = " ".join((" ".join(first_parts[-lower_name_index:]), last))
                first = " ".join(first_parts[:-lower_name_index])

        forenames = extract_middle_names(first)
        lastnames = extract_name_prefix(last)
        return NameResult(
            forenames[0] if len(forenames) > 0 else "",
            forenames[1] if len(forenames) > 1 else "",
            lastnames[0] if len(lastnames) > 1 else "",
            lastnames[1] if len(lastnames) > 1 else lastnames[0],
            "",
        )
    elif len(parts) == 2:
        # last, first
        last, first = parts

        # for consistency with spaces being stripped in first last format
        first = " ".join((s for s in split_tex_string(first)))
        last = " ".join((s for s in split_tex_string(last)))

        forenames = extract_middle_names(first)
        lastnames = extract_name_prefix(last)

        if len(lastnames) > 1:
            name_index = 0
            for part in lastnames:
                if part.islower():
                    name_index += 1
                else:
                    break

        return NameResult(
            forenames[0] if len(forenames) > 0 else "",
            forenames[1] if len(forenames) > 1 else "",
            " ".join(lastnames[:name_index]) if len(lastnames) > 1 else "",
            " ".join(lastnames[name_index:]) if len(lastnames) > 1 else lastnames[0],
            "",
        )
    elif len(parts) == 3:
        # last, generation, first
        last, generation, first = parts
        forenames = extract_middle_names(first)
        lastnames = extract_name_prefix(last)
        return NameResult(
            forenames[0] if len(forenames) > 0 else "",
            forenames[1] if len(forenames) > 1 else "",
            lastnames[0] if len(lastnames) > 1 else "",
            lastnames[1] if len(lastnames) > 1 else lastnames[0],
            generation,
        )
    else:
        raise ValueError('Unrecognised name format for "{0}"'.format(name_str))


class Name:
    """
    Represents a BibLaTeX name entry. __str__ will return a name formatted in
    the preferred format
    """

    NAME_FIELDS = set(
        (
            "author",
            "bookauthor",
            "commentator",
            "editor",
            "editora",
            "editorb",
            "editorc",
            "foreword",
            "holder",
            "introduction",
            "shortauthor",
            "shorteditor",
            "translator",
            "sortname",
            "namea",
            "nameb",
            "namec",
        )
    )

    def __init__(self, name_str):
        self.first, self.middle, self.prefix, self.last, self.generation = tokenize_name(name_str)

    def __str__(self):
        if not self.last:
            return self.first

        result = " ".join((self.prefix, self.last)) if self.prefix else str(self.last)
        if self.generation:
            result = ", ".join((result, self.generation))
        result = ", ".join((result, self.first))
        if self.middle:
            result = " ".join((result, self.middle))
        return result
