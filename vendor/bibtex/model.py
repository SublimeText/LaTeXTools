import sys

from collections.abc import MutableMapping

from .utils import CaseInsensitiveOrderedDict

__all__ = ["Database", "Entry"]


def reraise(tp, value, tb=None):
    if value is None:
        value = tp()
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value


class Database(MutableMapping):
    def __init__(self):
        self._preamble = []
        self._macros = CaseInsensitiveOrderedDict(
            (
                ("jan", "January"),
                ("feb", "February"),
                ("mar", "March"),
                ("apr", "April"),
                ("may", "May"),
                ("jun", "June"),
                ("jul", "July"),
                ("aug", "August"),
                ("sep", "September"),
                ("oct", "October"),
                ("nov", "November"),
                ("dec", "December"),
            )
        )

        self._entries = CaseInsensitiveOrderedDict()

    def add_preamble(self, preamble):
        self._preamble.append(preamble)

    def add_macro(self, key, value):
        self._macros[key] = value

    def add_entry(self, entry):
        if not isinstance(entry, Entry):
            raise TypeError(type(entry))

        if entry.cite_key in self._entries:
            # TODO report error
            return

        self._entries[entry.cite_key] = entry
        entry.database = self

    def get_preamble(self):
        return "".join(self._preamble)

    def get_macro(self, key):
        return self._macros.get(key, key)

    def get_entries(self, *keys):
        entries = []
        for key in keys:
            try:
                entries.append(self._entries[key])
            except KeyError:
                pass
        return entries

    def __getitem__(self, key):
        return self._entries[key]

    def __setitem__(self, _, value):
        self.add_entry(value)

    def __delitem__(self, key):
        del self._entries[key]

    def __iter__(self):
        return iter(self._entries)

    def __len__(self):
        return len(self._entries)


class Entry(MutableMapping):
    def __init__(self, entry_type, cite_key, *args, **kwargs):
        self.entry_type = entry_type.lower()
        self.cite_key = cite_key
        self.database = None
        self._attributes = CaseInsensitiveOrderedDict(*args, **kwargs)

    def get_crossref(self):
        if self.database is None:
            return None

        try:
            return self.database[self["crossref"]]
        except KeyError:
            return None

    def __getitem__(self, key):
        if key is None:
            raise KeyError()

        try:
            return self._attributes[key]
        except KeyError:
            exc_info = sys.exc_info()
            if key.lower() != "crossref":
                try:
                    return self.get_crossref()[key]
                except TypeError:
                    reraise(*exc_info)
            else:
                reraise(*exc_info)

    def __setitem__(self, key, value):
        self._attributes[key] = value

    def __delitem__(self, key):
        del self._attributes[key]

    def __iter__(self):
        return iter(self._attributes)

    def __len__(self):
        return len(self._attributes)

    def __repr__(self):
        return f"<Entry [{self.cite_key}]>"
