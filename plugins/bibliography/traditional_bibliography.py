import codecs
import re
import sublime
import traceback

from LaTeXTools.latextools.latextools_plugin import LaTeXToolsPlugin
from LaTeXTools.latextools.utils import bibcache
from LaTeXTools.latextools.utils.logging import logger
from LaTeXTools.vendor import latex_chars

kp = re.compile(r"@[^\{]+\{\s*(.+)\s*,")
# new and improved regex
# we must have "title" then "=", possibly with spaces
# then either {, maybe repeated twice, or "
# then spaces and finally the title
# # We capture till the end of the line as maybe entry is broken over several lines
# # and in the end we MAY but need not have }'s and "s
# tp = re.compile(r'\btitle\s*=\s*(?:\{+|")\s*(.+)', re.IGNORECASE)  # note no comma!
# # Tentatively do the same for author
# # Note: match ending } or " (surely safe for author names!)
# ap = re.compile(r'\bauthor\s*=\s*(?:\{|")\s*(.+)(?:\}|"),?', re.IGNORECASE)
# # Editors
# ep = re.compile(r'\beditor\s*=\s*(?:\{|")\s*(.+)(?:\}|"),?', re.IGNORECASE)
# # kp2 = re.compile(r'([^\t]+)\t*')
# # and year...
# # Note: year can be provided without quotes or braces (yes, I know...)
# yp = re.compile(r'\byear\s*=\s*(?:\{+|"|\b)\s*(\d+)[\}"]?,?', re.IGNORECASE)

# This may speed things up
# So far this captures: the tag, and the THREE possible groups
multip = re.compile(
    r"\b(author|title|year|editor|journal|eprint)\s*=\s*" r'(?:\{|"|\b)(.+?)(?:\}+|"|\b)\s*,?\s*\Z',
    re.IGNORECASE,
)

# LaTeX -> Unicode decoder
latex_chars.register()


class TraditionalBibliographyPlugin(LaTeXToolsPlugin):

    def get_entries(self, *bib_files):
        entries = []
        for bibfname in bib_files:
            bib_cache = bibcache.BibCache("trad", bibfname)
            try:
                cached_entries = bib_cache.get()
                entries.extend(cached_entries)
                continue
            except Exception:
                pass

            try:
                with open(bibfname, "r", encoding="utf-8", errors="ignore", newline="\n") as bibf:
                    bib_entries = []
                    entry = {}
                    for line in bibf.readline():
                        line = line.strip()
                        # Let's get rid of irrelevant lines first
                        if line == "" or line[0] == "%":
                            continue
                        if line.lower()[0:8] == "@comment":
                            continue
                        if line.lower()[0:7] == "@string":
                            continue
                        if line.lower()[0:9] == "@preamble":
                            continue
                        if line[0] == "@":
                            if "keyword" in entry:
                                bib_entries.append(entry)
                                entry = {}

                            kp_match = kp.search(line)
                            if kp_match:
                                entry["keyword"] = kp_match.group(1)
                            else:
                                logger.error("Cannot process this @ line: %s", line)
                                logger.error(
                                    "Previous keyword (if any): %s",
                                    entry.get("keyword", ""),
                                )
                            continue

                        # Now test for title, author, etc.
                        # Note: we capture only the first line, but that's OK for our purposes
                        multip_match = multip.search(line)
                        if multip_match:
                            key = multip_match.group(1).lower()
                            value = codecs.decode(multip_match.group(2), "latex")

                            if key == "title":
                                value = (
                                    value.replace("{\\textquoteright}", "")
                                    .replace("{", "")
                                    .replace("}", "")
                                )
                            entry[key] = value
                        continue
                    # at the end, we have a single record
                    if "keyword" in entry:
                        bib_entries.append(entry)

                    logger.info("Loaded %d bibitems", len(bib_data))

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
