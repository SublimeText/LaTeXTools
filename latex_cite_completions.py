'''
This module implements the cite-completion behaviour, largely by relying on
implementations registered with latextools_plugin and configured using the
`bibliograph_plugins` configuration key.

At present, there are two supported methods on custom plugins.

`get_entries`:
    This method should take a sequence of bib_files and return a sequence of
    Mapping-like objects where the key corresponds to a Bib(La)TeX key and
    returns the matching value. We provide default fallbacks for any of the
    quick panel formatting options that might not be automatically mapped to
    a field, e.g., `author_short`, etc. or to deal with missing data, e.g.
    entries that have no `journal` but use the `journaltitle` field. Plugins
    can override this behaviour, however, by explicitly setting a value for
    whatever key they like.

`on_insert_citation`:
    This method should take a single string value indicating the citekey of the
    entry that has just been cited. This is provided to allow the plugin to
    react to the insertion event. This method will be called on a separate
    thread and should not interact with the Sublime view if possible, as this
    may cause a race condition.
'''
# ST2/ST3 compat
from __future__ import print_function
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
    from kpsewhich import kpsewhich
    from latextools_utils.is_tex_file import is_tex_file, get_tex_extensions
    from latextools_utils import get_setting
    import latextools_plugin

    # reraise implementation from 6
    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")

    strbase = basestring
else:
    _ST3 = True
    from . import getTeXRoot
    from .kpsewhich import kpsewhich
    from .latextools_utils.is_tex_file import is_tex_file, get_tex_extensions
    from .latextools_utils import get_setting
    from . import latextools_plugin

    # reraise implementation from 6
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    strbase = str


import sublime_plugin
import os, os.path
import sys
import re
import codecs

from string import Formatter
import collections

import threading

class UnrecognizedCiteFormatError(Exception): pass
class NoBibFilesError(Exception): pass

class BibParsingError(Exception):
    def __init__(self, filename=""):
        self.filename = filename

class BibPluginError(Exception): pass

OLD_STYLE_CITE_REGEX = re.compile(r"([^_]*_)?([a-zX*]*?)etic(?:\\|\b)")
# I apoligise profusely for this regex
# forward version with explanation:
# \\
#    (?:
#       (?# 
#           first branch matches \foreigntextquote, 
#           \hypentextquote, \foreignblockquote, \hyphenblockquote,
#           \hybridblockquote and starred versions
#           syntax is:
#           \foreigntextquote{lang}[key][punct]{text}
#       )
#       (?:foreign|hyphen|hybrid(?=block))(?:text|block)quote\*?
#           \{[^}]*\}\[(?:(?:[^[\],]*,)*)?|
#       (?#
#           second branch matches \textquote, \blockquote and
#           starred versions
#           syntax is:
#           \textquote[key]{text}
#       )
#       (?:text|block)quote\*?\[(?:(?:[^[\],]*,)*)?|
#       (?#
#           third branch matches \foreigntextcquote,
#           \hyphentextcquote, \foreignblockcquote, \hypenblockcquote,
#           \hybridblockcquote and starred versions
#           syntax is:
#           \foreigntextcquote{lang}[prenote][postnote]{key}{text}
#       )
#       (?:foreign|hyphen|hybrid(?=block))(?:text|block)cquote\*?
#           \{[^}]*\}(?:\[[^\]]*\]){0,2}\{(?:(?:[^{},]*,)*)?|
#       (?#
#           fourth branch matches \textcquote, \blockcquote and 
#           starred versions
#           syntax is:
#           \textcquote[prenote][postnote]{key}{text}
#       )
#       (?:text|block)cquote\*?(?:\[[^\]]*\]){0,2}\{(?:(?:[^{},]*,)*)?|
#       (?#
#           fifth branch matches \volcite and friends
#           syntax is:
#           \volcite[prenote]{volume}[page]{key}
#       )
#       (?:p|P|f|ft|s|S|t|T|a|A)?volcite
#           (?:\[[^\]]*\])?\{[^}]*\}(?:\[[^\]]*\])?\{(?:(?:[^{},]*,)*)?|
#       (?#
#           sixth branch matches \volcites and friends
#           syntax is:
#           \volcites(multiprenote)(multipostnote)[prenote]{volume}[page]{key}
#               ...[prenote]{volume}[page]{key}
#       )
#       (?:p|P|f|ft|s|S|t|T|a|A)?volcites
#           (?:\([^)]*\)){0,2}
#               (?:(?:\[[^\]]*\])?\{[^}]*\}
#               (?:\[[^\]]*\])?\{(?:(?:[^{},]*,)*)?(?:\}(?=.*?\{))?){1,}|
#       (?#
#           seventh branch matches \cites and friends, excluding \volcite
#           syntax is:
#           \cites(multiprenote)(multipostnote)[prenote][postnote]{key}
#               ...[prenote][postnote]{key}
#       )
#       (?:(?!(?:p|P|f|ft|s|S|t|T|a|A)?volcites)
#           (?:[A-Z]?[a-z]*c)|C)ites
#           (?:\([^)]*\)){0,2}
#           (?:(?:\[[^\]]*\]){0,2}\{(?:(?:[^{},]*,)*)?(?:\}(?=.*?\{))?){1,}|
#       (?#
#           eighth branch matches most everything else, excluding \volcite,
#           \mcite, \citereset and \citestyle
#           syntax is:
#           \cite[<prenote>][<postnote>]{key}
#       )
#       (?:(?!(?:p|P|f|ft|s|S|t|T|a|A)?volcite|mcite)
#           (?:[A-Z]?[a-z]*c)|C)ite(?!reset|style)([a-zX*]*?)
#           ([.*?]){0,2}(?:\[[^\]]*\]){0,2}\{(?:(?:[^{},]*,)*)?|
#       (?#
#           ninth branch matches apacite commands
#           syntax is:
#           \citeA<prenote>[postnote]{key}
#       )
#       cite(?:(?:author|year)(?:NP)?|NP|A)?(?:<[^>]*>)?(?:\[[^\]]*\])?\{(?:(?:[^{},]*,)*)?)$
NEW_STYLE_CITE_REGEX = re.compile(
    r"""(?:
            (?# 
                first branch matches \foreigntextquote, 
                \hypentextquote, \foreignblockquote, \hyphenblockquote,
                \hybridblockquote and starred versions
                syntax is:
                \foreigntextquote{lang}[key][punct]{text}
            )
            (?:(?P<prefix1>[^\[\],]*)(?:,[^\[\],]*)*\[\}[^\{]*\{
                \*?etouq(?:kcolb|txet)(?:ngierof|nehpyh|(?<=kcolb)dirbyh))|
            (?#
                second branch matches \textquote, \blockquote and
                starred versions
                syntax is:
                \textquote[key]{text}
            )
            (?:(?P<prefix2>[^\[\],]*)(?:,[^\[\],]*)*\[\*?etouq(?:kcolb|txet))|
            (?#
                third branch matches \foreigntextcquote,
                \hyphentextcquote, \foreignblockcquote, \hypenblockcquote,
                \hybridblockcquote and starred versions
                syntax is:
                \foreigntextcquote{lang}[prenote][postnote]{key}{text}
            )
            (?:(?P<prefix3>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[){0,2}\}[^\{]*\{
                \*?etouqc(?:kcolb|txet)(?:ngierof|nehpyh|(?<=kcolb)dirbyh))|
            (?#
                fourth branch matches \textcquote, \blockcquote and 
                starred versions
                syntax is:
                \textcquote[prenote][postnote]{key}{text}
            )
            (?:(?P<prefix4>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[){0,2}
                \*?etouqc(?:kcolb|txet))|
            (?#
                fifth branch matches \volcite and friends
                syntax is:
                \volcite[prenote]{volume}[page]{key}
            )
            (?:(?P<prefix5>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[)?\}[^\{}]*\{(?:\][^\[]*\[)?
                eticlov(?:p|P|f|ft|s|S|t|T|a|A)?)|
            (?#
                sixth branch matches \volcites and friends
            )
            (?:(?P<prefix6>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[)?\}[^\{}]*\{(?:\][^\[]*\[)?
                (?:\}[^\{}]*\{(?:\][^\[]*\[)?\}[^\{}]*\{(?:\][^\[]*\[)?)*
                (?:\)[^(]*\(){0,2}
                seticlov(?:p|P|f|ft|s|S|t|T|a|A)?)|
            (?#
                seventh branch matches \cites and friends, excluding \volcite
            )
            (?:(?P<prefix7>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[){0,2}
                (?:\}[^\}]*\{(?:\][^\[]*\[){0,2})*
                (?:[\.\*\?]){0,2}(?:\)[^(]*\(){0,2}([a-zX\*]*?)
                seti(?:C|c(?!lov)[a-z]*[A-Z]?))|
            (?#
                eighth branch matches most everything else, excluding \volcite,
                \mcite, \citereset and \citestyle
                syntax is:
                \cite[prenote][postnote]{key}
            )
            (?:(?P<prefix8>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[){0,2}
                (?:[\.\*\?]){0,2}(?!teser|elyts)(?P<fancy_cite>[a-zX\*]*?)
                eti(?:C|c(?!lov|m\\)[a-z]*[A-Z]?))|
            (?#
                ninth branch matches apacite commands
            )
            (?:(?P<prefix9>[^{},]*)(?:,[^{},]*)*\{(?:\][^\[]*\[)?
                (?:>[^<]*<)?(?:(?:PN)?(?:raey|rohtua)|PN|A)?etic)
        )\\""", re.X)

def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

# recursively search all linked tex files to find all
# included bibliography tags in the document and extract
# the absolute filepaths of the bib files
def find_bib_files(rootdir, src, bibfiles):
    if not is_tex_file(src):
        src_tex_file = None
        for ext in get_tex_extensions():
            src_tex_file = ''.join((src, ext))
            if os.path.exists(os.path.join(rootdir, src_tex_file)):
                src = src_tex_file
                break
        if src != src_tex_file:
            print("Could not find file {0}".format(src))
            return

    file_path = os.path.normpath(os.path.join(rootdir,src))
    print("Searching file: " + repr(file_path))
    # See latex_ref_completion.py for why the following is wrong:
    #dir_name = os.path.dirname(file_path)

    # read src file and extract all bibliography tags
    try:
        src_file = codecs.open(file_path, "r", 'UTF-8')
    except IOError:
        sublime.status_message("LaTeXTools WARNING: cannot open included file " + file_path)
        print ("WARNING! I can't find it! Check your \\include's and \\input's.")
        return

    src_content = re.sub("%.*","",src_file.read())
    src_file.close()

    m = re.search(r"\\usepackage\[(.*?)\]\{inputenc\}", src_content)
    if m:
        f = None
        try:
            f = codecs.open(file_path, "r", m.group(1))
            src_content = re.sub("%.*", "", f.read())
        except:
            pass
        finally:
            if f and not f.closed:
                f.close()

    # While these commands only allow a single resource as their argument...
    resources = re.findall(r'\\addbibresource(?:\[[^\]]+\])?\{([^\}]+\.bib)\}', src_content)
    resources += re.findall(r'\\addglobalbib(?:\[[^\]]+\])?\{([^\}]+\.bib)\}', src_content)
    resources += re.findall(r'\\addsectionbib(?:\[[^\]]+\])?\{([^\}]+\.bib)\}', src_content)

    # ... these can have a comma-separated list of resources as their argument.
    multi_resources = re.findall(r'\\begin\{refsection\}\[([^\]]+)\]', src_content)
    multi_resources += re.findall(r'\\bibliography\{([^\}]+)\}', src_content)
    multi_resources += re.findall(r'\\nobibliography\{([^\}]+)\}', src_content)

    for multi_resource in multi_resources:
        for res in multi_resource.split(','):
            res = res.strip()
            if res[-4:].lower() != '.bib':
                res = res + '.bib'
            resources.append(res)

    # extract absolute filepath for each bib file
    for res in resources:
        # We join with rootdir, the dir of the master file
        candidate_file = os.path.normpath(os.path.join(rootdir, res))
        # if the file doesn't exist, search the default tex paths
        if not os.path.exists(candidate_file):
            candidate_file = kpsewhich(res, 'mlbib')

        if candidate_file is not None and os.path.exists(candidate_file):
            bibfiles.append(candidate_file)

    # search through input tex files recursively
    for f in re.findall(r'\\(?:input|include)\{[^\}]+\}',src_content):
        input_f = re.search(r'\{([^\}]+)', f).group(1)
        find_bib_files(rootdir, input_f, bibfiles)

def run_plugin_command(command, *args, **kwargs):
    '''
    This function is intended to run a command against a user-configurable list
    of bibliography plugins set using the `bibliography` setting.

    Parameters:
        `command`: a string representing the command to invoke, which should
            generally be the name of a function to be called on the plugin
                class.
        `*args`: the args to pass to the function
        `**kwargs`: the keyword args to pass to the function

    Additionally, the following keyword parameters can be specified to control
    how this function works:
        `stop_on_first`: if True (default), no more attempts will be made to
            run the command after the first plugin that returns a non-None
            result
        `expect_result`: if True (default), a BibPluginError will be raised if
            no plugin returns a non-None result

    Example:
        run_plugin_command('get_entries', *bib_files)
        This will attempt to invoke the `get_entries` method of any configured
        plugin, passing in the discovered bib_files, and returning the result.

    The general assumption of this function is that we only care about the
    first valid result returned from a plugin and that plugins that should not
    handle a request will either not implement the method or implement a
    version of the method which raises a NotImplementedError if that plugin
    should not handle the current situation.
    '''
    stop_on_first = kwargs.pop('stop_on_first', True)
    expect_result = kwargs.pop('expect_result', True)

    def _run_command(plugin_name):
        plugin = None
        try:
            plugin = latextools_plugin.get_plugin(plugin_name)
        except latextools_plugin.NoSuchPluginException:
            pass

        if not plugin:
            error_message = 'Could not find bibliography plugin named {0}. Please ensure your LaTeXTools.sublime-settings is configured correctly.'.format(
                plugin_name)
            print(error_message)
            raise BibPluginError(error_message)

        # instantiate plugin
        try:
            plugin = plugin()
        except:
            error_message = 'Could not instantiate {0}. {0} must have a no-args __init__ method'.format(
                type(plugin).__name__,
            )

            print(error_message)
            raise BibPluginError(error_message)

        try:
            result = getattr(plugin, command)(*args, **kwargs)
        except TypeError as e:
            if "'{0}()'".format(command) in str(e):
                error_message = '{1} is not properly implemented by {0}.'.format(
                    type(plugin).__name__,
                    command
                )

                print(error_message)
                raise BibPluginError(error_message)
            else:
                reraise(*sys.exc_info())
        except AttributeError as e:
            if "'{0}'".format(command) in str(e):
                error_message = '{0} does not implement `{1}`'.format(
                    type(plugin).__name__,
                    command
                )

                print(error_message)
                raise BibPluginError(error_message)
            else:
                reraise(*sys.exc_info())
        except NotImplementedError:
            return None

        return result

    plugins = get_setting('bibliography', ['traditional_bibliography'])
    if not plugins:
        print('bibliography setting is blank. Loading traditional plugin.')
        plugins = 'traditional_bibliography'

    result = None
    if isinstance(plugins, strbase):
        result = _run_command(plugins)
    else:
        for plugin_name in plugins:
            try:
                result = _run_command(plugin_name)
            except BibPluginError:
                continue
            if stop_on_first and result is not None:
                break

    if expect_result and result is None:
        raise BibPluginError("Could not find a plugin to handle '{0}'. See the console for more details".format(command))

    return result

TITLE_SEP = re.compile(':|\.|\?')
def get_title_short(title):
    title = TITLE_SEP.split(title)[0]
    if len(title) > 60:
        title = title[:60] + '...'
    return title


# default implementation that convers the author field into a short version of itself
# assumes we get a basically raw LaTeX string, e.g. "Lastname, Firstnamd and Otherlastname, Otherfirstname"
def get_author_short(authors):
    if authors == '':
        return ''

    # split authors using ' and ' and get last name for 'last, first' format
    authors = [a.split(", ")[0].strip(' ') for a in authors.split(" and ")]
    # get last name for 'first last' format (preserve {...} text)
    authors = [a.split(" ")[-1] if a[-1] != '}' or a.find('{') == -1 else re.sub(r'{|}', '', a[len(a) - a[::-1].index('{'):-1]) for a in authors]

    # truncate and add 'et al.'
    if len(authors) > 2:
        authors = authors[0] + " et al."
    else:
        authors = ' & '.join(authors)

    # return formated string
    return authors

class CompletionWrapper(collections.Mapping):
    '''
    Wraps the returned completions so that we can properly handle any KeyErrors that
    occur
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
            if key == 'author':
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
            elif key == 'keyword':
                try:
                    return self._entry['citekey']
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

def get_cite_completions(view, point, autocompleting=False):
    line = view.substr(sublime.Region(view.line(point).a, point))
    # print line

    # Reverse, to simulate having the regex
    # match backwards (cool trick jps btw!)
    line = line[::-1]
    #print line

    # Check the first location looks like a cite_, but backward
    # NOTE: use lazy match for the fancy cite part!!!
    # NOTE2: restrict what to match for fancy cite
    rex = OLD_STYLE_CITE_REGEX
    expr = match(rex, line)

    # See first if we have a cite_ trigger
    if expr:
        # Do not match on plain "cite[a-zX*]*?" when autocompleting,
        # in case the user is typing something else
        if autocompleting and re.match(r"[a-zX*]*etic\\?", expr):
            raise UnrecognizedCiteFormatError()
        # Return the completions
        prefix, fancy_cite = rex.match(expr).groups()
        preformatted = False
        if prefix:
            prefix = prefix[::-1]  # reverse
            prefix = prefix[1:]  # chop off _
        else:
            prefix = ""  # because this could be a None, not ""
        if fancy_cite:
            fancy_cite = fancy_cite[::-1]
            # fancy_cite = fancy_cite[1:] # no need to chop off?
            if fancy_cite[-1] == "X":
                fancy_cite = fancy_cite[:-1] + "*"
        else:
            fancy_cite = ""  # again just in case
        # print prefix, fancy_cite

    # Otherwise, see if we have a preformatted \cite{}
    else:
        rex = NEW_STYLE_CITE_REGEX
        expr = match(rex, line)

        if not expr:
            raise UnrecognizedCiteFormatError()

        preformatted = True
        m = rex.match(expr)
        prefix =   (m.group('prefix1') or
                    m.group('prefix2') or
                    m.group('prefix3') or
                    m.group('prefix4') or
                    m.group('prefix5') or
                    m.group('prefix6') or
                    m.group('prefix7') or
                    m.group('prefix8') or
                    m.group('prefix9'))
        if prefix:
            prefix = prefix[::-1]
        else:
            prefix = ""
        fancy_cite = m.group('fancy_cite')
        if fancy_cite:
            fancy_cite = fancy_cite[::-1]
            if fancy_cite[-1] == "X":
                fancy_cite = fancy_cite[:-1] + "*"
        else:
            fancy_cite = ""
        # print prefix, fancy_cite

    # if the key is an optional parameter, ensure we close the optional parameter
    post_brace = "}" if not re.match(r'(?:[^\[\],]*)\[', expr) else ']'

    # Reverse back expr
    expr = expr[::-1]

    if not preformatted:
        # Replace cite_blah with \cite{blah
        pre_snippet = "\cite" + fancy_cite + "{"
        # The "latex_tools_replace" command is defined in latex_ref_cite_completions.py
        view.run_command("latex_tools_replace", {"a": point-len(expr), "b": point, "replacement": pre_snippet + prefix})        
        # save prefix begin and endpoints points
        new_point_a = point - len(expr) + len(pre_snippet)
        new_point_b = new_point_a + len(prefix)

    else:
        # Don't include post_brace if it's already present
        suffix = view.substr(sublime.Region(point, point + len(post_brace)))
        new_point_a = point - len(prefix)
        new_point_b = point
        if post_brace == suffix:
            post_brace = ""

    #### GET COMPLETIONS HERE #####

    root = getTeXRoot.get_tex_root(view)

    if root is None:
        # This is an unnamed, unsaved file
        # FIXME: should probably search the buffer instead of giving up
        raise NoBibFilesError()

    print ("TEX root: " + repr(root))
    bib_files = []
    find_bib_files(os.path.dirname(root), root, bib_files)
    # remove duplicate bib files
    bib_files = list(set(bib_files))
    print ("Bib files found: ")
    print (repr(bib_files))

    if not bib_files:
        # sublime.error_message("No bib files found!") # here we can!
        raise NoBibFilesError()

    bib_files = ([x.strip() for x in bib_files])

    print ("Files:")
    print (repr(bib_files))

    completions = run_plugin_command('get_entries', *bib_files)

    #### END COMPLETIONS HERE ####

    completions = [CompletionWrapper(completion) for completion in completions]

    return completions, prefix, post_brace, new_point_a, new_point_b


# Based on html_completions.py
# see also latex_ref_completions.py
#
# It expands citations; activated by 
# cite<tab>
# citep<tab> and friends
#
# Furthermore, you can "pre-filter" the completions: e.g. use
#
# cite_sec
#
# to select all citation keywords starting with "sec". 
#
# There is only one problem: if you have a keyword "sec:intro", for instance,
# doing "cite_intro:" will find it correctly, but when you insert it, this will be done
# right after the ":", so the "cite_intro:" won't go away. The problem is that ":" is a
# word boundary. Then again, TextMate has similar limitations :-)
#
# There is also another problem: * is also a word boundary :-( So, use e.g. citeX if
# what you want is \cite*{...}; the plugin handles the substitution

class LatexCiteCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        # Only trigger within LaTeX
        if not view.match_selector(locations[0],
                "text.tex.latex"):
            return []

        point = locations[0]

        try:
            completions, prefix, post_brace, new_point_a, new_point_b = get_cite_completions(view, point, autocompleting=True)
        except UnrecognizedCiteFormatError:
            return []
        except NoBibFilesError:
            sublime.status_message("No bib files found!")
            return []
        except BibParsingError as e:
            sublime.status_message("Bibliography " + e.filename + " is broken!")
            return []

        # filter against keyword or title
        if prefix:
            completions = [comp for comp in completions if prefix.lower() in "%s %s" %
                                                    (
                                                        comp['keyword'].lower(),
                                                        comp['title'].lower())]
            prefix += " "

        # get preferences for formating of autocomplete entries
        cite_autocomplete_format = get_setting('cite_autocomplete_format',
            "{keyword}: {title}")

        formatter = Formatter()
        r = [(prefix + formatter.vformat(cite_autocomplete_format, (), completion),
              completion['keyword'] + post_brace) for completion in completions]

        # print "%d bib entries matching %s" % (len(r), prefix)

        return r


class LatexCiteCommand(sublime_plugin.TextCommand):

    # Remember that this gets passed an edit object
    def run(self, edit):
        # get view and location of first selection, which we expect to be just the cursor position
        view = self.view
        point = view.sel()[0].b
        print (point)
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
            return

        try:
            completions, prefix, post_brace, new_point_a, new_point_b = get_cite_completions(view, point)
        except UnrecognizedCiteFormatError:
            sublime.error_message("Not a recognized format for citation completion")
            return
        except NoBibFilesError:
            sublime.error_message("No bib files found!")
            return
        except BibParsingError as e:
            sublime.error_message("Bibliography " + e.filename + " is broken!")
            return
        except BibParsingError as e:
            sublime.error_message(e.message)
            return

        # filter against keyword, title, or author
        if prefix:
            completions = [comp for comp in completions if prefix.lower() in "%s %s %s" % 
                                                    (
                                                        comp['keyword'].lower(),
                                                        comp['title'].lower(),
                                                        comp['author'].lower())]

        # Note we now generate citation on the fly. Less copying of vectors! Win!
        def on_done(i):
            print ("latex_cite_completion called with index %d" % (i,) )

            # Allow user to cancel
            if i < 0:
                return

            keyword = completions[i]['keyword']
            # notify any plugins
            notification_thread = threading.Thread(
                target=run_plugin_command,
                args=(
                    'on_insert_citation',
                    keyword
                ),
                kwargs={
                    'stop_on_first': False,
                    'expect_result': False
                }
            )

            notification_thread.daemon = True
            notification_thread.start()

            cite = completions[i]['keyword'] + post_brace

            #print("DEBUG: types of new_point_a and new_point_b are " + repr(type(new_point_a)) + " and " + repr(type(new_point_b)))
            # print "selected %s:%s by %s" % completions[i][0:3]
            # Replace cite expression with citation
            # the "latex_tools_replace" command is defined in latex_ref_cite_completions.py
            view.run_command("latex_tools_replace", {"a": new_point_a, "b": new_point_b, "replacement": cite})
            # Unselect the replaced region and leave the caret at the end
            caret = view.sel()[0].b
            view.sel().subtract(view.sel()[0])
            view.sel().add(sublime.Region(caret, caret))

        # get preferences for formating of quick panel
        cite_panel_format = get_setting('cite_panel_format',
            ["{title} ({keyword})", "{author}"])

        completions_length = len(completions)
        if completions_length == 0:
            return
        elif completions_length == 1:
            # only one entry, so insert entry
            view.run_command("latex_tools_replace",
                {
                    "a": new_point_a,
                    "b": new_point_b,
                    "replacement": completions[0]['keyword'] + post_brace
                }
            )

            # Unselect the replaced region and leave the caret at the end
            caret = view.sel()[0].b
            view.sel().subtract(view.sel()[0])
            view.sel().add(sublime.Region(caret, caret))
        else:
            # show quick
            formatter = Formatter()
            view.window().show_quick_panel([[formatter.vformat(s, (), completion) for s in cite_panel_format] \
                                        for completion in completions], on_done)

def plugin_loaded():
    latextools_plugin.add_whitelist_module('latex_chars')
    # load plugins from the bibliography_plugins dir of LaTeXTools if it exists
    # this allows us to have pre-packaged plugins that won't require any user
    # setup
    os_path = os.path
    latextools_plugin.add_plugin_path(
        os_path.join(os_path.dirname(__file__), 'bibliography_plugins'))

# ensure plugin_loaded() called on ST2
if not _ST3:
    plugin_loaded()
