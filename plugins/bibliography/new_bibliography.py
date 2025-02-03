import codecs
import collections
import sublime
import traceback

from LaTeXTools.latextools.latextools_plugin import LaTeXToolsPlugin
from LaTeXTools.latextools.utils import bibcache
from LaTeXTools.latextools.utils.logging import logger

from LaTeXTools.vendor.bibtex import Parser
from LaTeXTools.vendor.bibtex.names import Name
from LaTeXTools.vendor.bibtex.tex import tokenize_list
from LaTeXTools.vendor import latex_chars

# LaTeX -> Unicode decoder
latex_chars.register()


def _get_people_long(people):
    return " and ".join([str(x) for x in people])


def _get_people_short(people):
    if len(people) <= 2:
        return " & ".join([x.last if x.last != "" else x.first for x in people])
    else:
        return people[0].last if people[0].last != "" else people[0].first + ", et al."


def remove_latex_commands(s):
    """
    Simple function to remove any LaTeX commands or brackets from the string,
    replacing it with its contents.
    """
    chars = []
    FOUND_SLASH = False

    for c in s:
        if c == "{":
            # i.e., we are entering the contents of the command
            if FOUND_SLASH:
                FOUND_SLASH = False
        elif c == "}":
            pass
        elif c == "\\":
            FOUND_SLASH = True
        elif not FOUND_SLASH:
            chars.append(c)
        elif c.isspace():
            FOUND_SLASH = False

    return "".join(chars)


# wrapper to implement a dict-like interface for bibliographic entries
# returning formatted value, if it is available
class EntryWrapper(collections.abc.Mapping):
    def __init__(self, entry):
        self.entry = entry

    def __getitem__(self, key):
        if not key:
            return ""

        key = key.lower()
        result = None

        short = False
        if key.endswith("_short"):
            short = True
            key = key[:-6]

        if key == "keyword" or key == "citekey":
            return self.entry.cite_key

        if key in Name.NAME_FIELDS:
            people = []
            for x in tokenize_list(self.entry[key]):
                if x.strip() == "":
                    continue

                try:
                    people.append(Name(x))
                except Exception:
                    logger.error('Error handling field "%s" with value "%s"', key, x)
                    traceback.print_exc()

            if len(people) == 0:
                return ""

            if short:
                result = _get_people_short(people)
            else:
                result = _get_people_long(people)

        if not result:
            result = self.entry[key]

        return remove_latex_commands(codecs.decode(result, "latex"))

    def __iter__(self):
        return iter(self.entry)

    def __len__(self):
        return len(self.entry)


class NewBibliographyPlugin(LaTeXToolsPlugin):
    def get_entries(self, *bib_files):
        entries = []
        parser = Parser()

        for bibfname in bib_files:
            bib_cache = bibcache.BibCache("new", bibfname)
            try:
                cached_entries = bib_cache.get()
                entries.extend(cached_entries)
                continue
            except Exception:
                pass

            try:
                with open(bibfname, "r", encoding="utf-8", errors="ignore", newline="\n") as bibf:
                    bib_entries = []

                    excluded_types = ("xdata", "comment", "string")
                    excluded_fields = (
                        "abstract",
                        "annotation",
                        "annote",
                        "execute",
                        "langidopts",
                        "options",
                    )

                    for key, entry in parser.parse(bibf.read()).items():
                        if entry.entry_type in excluded_types:
                            continue

                        # purge some unnecessary fields from the bib entry to save
                        # some space and time reloading
                        for k in excluded_fields:
                            if k in entry:
                                del entry[k]

                        bib_entries.append(EntryWrapper(entry))

                    logger.info("Loaded %d bibitems", len(bib_entries))

                    try:
                        bib_cache.set(bib_entries)
                        fmt_entries = bib_cache.get()
                        entries.extend(fmt_entries)
                    except Exception:
                        traceback.print_exc()
                        logger.warning("Using bibliography without caching it")
                        entries.extend(bib_entries)

            except OSError:
                msg = "Cannot open bibliography file %s !" % bibfname
                logger.error(msg)
                sublime.status_message(msg)
                continue

        logger.info("Found %d total bib entries", len(entries))

        return entries
