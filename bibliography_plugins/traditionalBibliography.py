from latextools_plugin import LaTeXToolsPlugin

from bibtex import Parser
from bibtex.names import Name
from bibtex.tex import tokenize_list

import latex_chars
from latextools_utils import cache

import codecs
from collections import Mapping
import hashlib
import os
import sublime
import traceback

# LaTeX -> Unicode decoder
latex_chars.register()

if sublime.version() < '3000':
    def _get_people_long(people):
        return u' and '.join([unicode(x) for x in people])
else:
    def _get_people_long(people):
        return u' and '.join([str(x) for x in people])

def _get_people_short(people):
    if len(people) <= 2:
        return u' & '.join([x.last for x in people])
    else:
        return people[0].last + u', et al.'

def remove_latex_commands(s):
    u'''
    Simple function to remove any LaTeX commands or brackets from the string,
    replacing it with its contents.
    '''
    chars = []
    FOUND_SLASH = False

    for c in s:
        if c == '{':
            # i.e., we are entering the contents of the command
            if FOUND_SLASH:
                FOUND_SLASH = False
        elif c == '}':
            pass
        elif c == '\\':
            FOUND_SLASH = True
        elif not FOUND_SLASH:
            chars.append(c)
        elif c.isspace():
            FOUND_SLASH = False

    return ''.join(chars)

# wrapper to implement a dict-like interface for bibliographic entries
# returning formatted value, if it is available
class EntryWrapper(Mapping):
    def __init__(self, entry):
        self.entry = entry

    def __getitem__(self, key):
        if not key:
            return u''

        key = key.lower()
        result = None

        short = False
        if key.endswith('_short'):
            short = True
            key = key[:-6]

        if key == 'keyword' or key == 'citekey':
            return self.entry.cite_key

        if key in Name.NAME_FIELDS:
            people = []
            for x in tokenize_list(self.entry[key]):
                if x.strip() == '':
                    continue

                try:
                    people.append(Name(x))
                except:
                    print(u'Error handling field "{0}" with value "{1}"'.format(
                        key, x
                    ))
                    traceback.print_exc()

            if len(people) == 0:
                return u''

            if short:
                result = _get_people_short(people)
            else:
                result = _get_people_long(people)

        if not result:
            result = self.entry[key]

        return remove_latex_commands(codecs.decode(result, 'latex'))

    def __iter__(self):
        return iter(self.entry)

    def __len__(self):
        return len(self.entry)

class TraditionalBibliographyPlugin(LaTeXToolsPlugin):
    def get_entries(self, *bib_files):
        entries = []
        parser = Parser()
        for bibfname in bib_files:
            cache_name = "bib_" + hashlib.md5(bibfname.encode("utf8")).hexdigest()
            try:
                modified_time = os.path.getmtime(bibfname)

                (cached_time, cached_entries) = cache.read_global(cache_name)
                if modified_time < cached_time:
                    entries.extend(cached_entries)
                    continue
            except:
                pass

            try:
                bibf = codecs.open(bibfname, 'r', 'UTF-8', 'ignore')  # 'ignore' to be safe
            except IOError:
                print("Cannot open bibliography file %s !" % (bibfname,))
                sublime.status_message("Cannot open bibliography file %s !" % (bibfname,))
                continue
            else:
                bib_data = parser.parse(bibf.read())

                print ('Loaded %d bibitems' % (len(bib_data)))

                for key in bib_data:
                    entry = bib_data[key]
                    if entry.entry_type in ('xdata', 'comment', 'string'):
                        continue
                    entries.append(EntryWrapper(entry))

                try:
                    cache.write_global(cache_name, (modified_time, entries))
                except:
                    print('Error occurred while trying to write to cache {0}'.format(
                        cache_name
                    ))
                    traceback.print_exc()
            finally:
                try:
                    bibf.close()
                except:
                    pass

            print("Found %d total bib entries" % (len(entries),))
        return entries

    def on_insert_citation(self, keyword):
        print('Inserted {0}'.format(keyword))
