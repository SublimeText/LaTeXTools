from string import Formatter
import collections
import re


TITLE_SEP = re.compile(':|\.|\?')
PREFIX_MATCH_KEYS = set(["keyword", "title", "author"])

formatter = Formatter()


def _wrap(entry):
    if not isinstance(entry, CompletionWrapper):
        entry = CompletionWrapper(entry)
    return entry


def format_entry(format_string, entry):
    return formatter.vformat(format_string, (), _wrap(entry))


def format_entries(format_string, entries):
    return [formatter.vformat(format_string, (), _wrap(entry))
            for entry in entries]


def create_prefix_match_str(entry):
    prefix_str = " ".join(entry.get(key, "") for key in PREFIX_MATCH_KEYS)
    prefix_str = prefix_str.lower()
    return prefix_str


def get_title_short(title):
    title = TITLE_SEP.split(title)[0]
    if len(title) > 60:
        title = title[:60] + '...'
    return title


# default implementation that convers the author field into a short
# version of itself assumes we get a basically raw LaTeX string,
# e.g. "Lastname, Firstname and Otherlastname, Otherfirstname"
def get_author_short(authors):
    if authors == '':
        return ''

    # split authors using ' and ' and get last name for 'last, first' format
    authors = [a.split(", ")[0].strip(' ') for a in authors.split(" and ")]
    # get last name for 'first last' format (preserve {...} text)
    authors = [a.split(" ")[-1] if not('{' in a and a.endswith('}'))
               else re.sub(r'{|}', '', a[a.rindex('{') + 1:-1])
               for a in authors if len(a) > 0]

    # truncate and add 'et al.'
    if len(authors) > 2:
        authors = authors[0] + " et al."
    else:
        authors = ' & '.join(authors)

    # return formated string
    return authors


class CompletionWrapper(collections.Mapping):
    '''
    Wraps the returned completions so that we can properly handle any
    KeyErrors that occur
    '''
    def __init__(self, entry):
        self._entry = entry

    def __getitem__(self, key):
        try:
            # emulating previous behaviour of latex_cite_completions
            if key not in ('author', 'journal'):
                return self._entry[key]
            else:
                value = self._entry[key]
                return value or u'????'
        except KeyError:
            if key[0] == "<":
                raise
            elif key == 'keyword':
                try:
                    return self._entry['citekey']
                except KeyError:
                    pass
            elif key == 'author':
                try:
                    return self._entry['editor']
                except KeyError:
                    pass
            elif key == 'author_short':
                try:
                    return get_author_short(self._entry['author'])
                except KeyError:
                    pass

                return self['editor_short']
            elif key == 'editor_short':
                try:
                    return get_author_short(self._entry['editor'])
                except KeyError:
                    pass
            elif key == 'title_short':
                try:
                    return self._entry['shorttitle']
                except KeyError:
                    pass

                try:
                    return get_title_short(self._entry['title'])
                except KeyError:
                    pass
            elif key == 'journal':
                try:
                    return self._entry['journaltitle']
                except KeyError:
                    pass

                try:
                    return self._entry['eprint']
                except KeyError:
                    pass
            elif key == 'year':
                try:
                    date = self._entry['date']
                    date_matcher = re.match(r'(\d{4})', date)
                    if date_matcher:
                        return date_matcher.group(1)
                except KeyError:
                    pass
            elif key == 'month':
                try:
                    date = self._entry['date']
                    date_matcher = re.match(r'\d{4}-(\d{2})', date)
                    if date_matcher:
                        return date_matcher.group(1)
                except KeyError:
                    pass

            return u'????'

    def __iter__(self):
        return iter(self._entry)

    def __len__(self):
        return len(self._entry)
