# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
else:
    _ST3 = True
    from . import getTeXRoot


import sublime_plugin
import os, os.path
import re
import codecs


class UnrecognizedCiteFormatError(Exception): pass
class NoBibFilesError(Exception): pass

class BibParsingError(Exception):
    def __init__(self, filename=""):
        self.filename = filename


OLD_STYLE_CITE_REGEX = re.compile(r"([^_]*_)?([a-zX*]*?)etic(?:\\|\b)")
NEW_STYLE_CITE_REGEX = re.compile(r"([^{},]*)(?:,[^{},]*)*\{(?:\].*?\[){0,2}([a-zX*]*?)etic\\")


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
    if src[-4:].lower() != ".tex":
        src = src + ".tex"

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

    bibtags =  re.findall(r'\\bibliography\{[^\}]+\}', src_content)
    bibtags += re.findall(r'\\addbibresource\{[^\}]+.bib\}', src_content)

    # extract absolute filepath for each bib file
    for tag in bibtags:
        bfiles = re.search(r'\{([^\}]+)', tag).group(1).split(',')
        for bf in bfiles:
            if bf[-4:].lower() != '.bib':
                bf = bf + '.bib'
            # We join with rootdir - everything is off the dir of the master file
            bf = os.path.normpath(os.path.join(rootdir,bf))
            bibfiles.append(bf)

    # search through input tex files recursively
    for f in re.findall(r'\\(?:input|include)\{[^\}]+\}',src_content):
        input_f = re.search(r'\{([^\}]+)', f).group(1)
        find_bib_files(rootdir, input_f, bibfiles)


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
        prefix, fancy_cite = rex.match(expr).groups()
        if prefix:
            prefix = prefix[::-1]
        else:
            prefix = ""
        if fancy_cite:
            fancy_cite = fancy_cite[::-1]
            if fancy_cite[-1] == "X":
                fancy_cite = fancy_cite[:-1] + "*"
        else:
            fancy_cite = ""
        # print prefix, fancy_cite

    # Reverse back expr
    expr = expr[::-1]

    post_brace = "}"

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

    completions = []
    kp = re.compile(r'@[^\{]+\{(.+),')
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
    multip = re.compile(r'\b(author|title|year|editor|journal|eprint)\s*=\s*(?:\{|"|\b)(.+?)(?:\}+|"|\b)\s*,?\s*\Z',re.IGNORECASE)

    for bibfname in bib_files:
        # # THIS IS NO LONGER NEEDED as find_bib_files() takes care of it
        # if bibfname[-4:] != ".bib":
        #     bibfname = bibfname + ".bib"
        # texfiledir = os.path.dirname(view.file_name())
        # # fix from Tobias Schmidt to allow for absolute paths
        # bibfname = os.path.normpath(os.path.join(texfiledir, bibfname))
        # print repr(bibfname)
        try:
            bibf = codecs.open(bibfname,'r','UTF-8', 'ignore')  # 'ignore' to be safe
        except IOError:
            print ("Cannot open bibliography file %s !" % (bibfname,))
            sublime.status_message("Cannot open bibliography file %s !" % (bibfname,))
            continue
        else:
            bib = bibf.readlines()
            bibf.close()
        print ("%s has %s lines" % (repr(bibfname), len(bib)))

        keywords = []
        titles = []
        authors = []
        years = []
        journals = []
        #
        entry = {   "keyword": "", 
                    "title": "",
                    "author": "", 
                    "year": "", 
                    "editor": "",
                    "journal": "",
                    "eprint": "" }
        for line in bib:
            line = line.strip()
            # Let's get rid of irrelevant lines first
            if line == "" or line[0] == '%':
                continue
            if line.lower()[0:8] == "@comment":
                continue
            if line.lower()[0:7] == "@string":
                continue
            if line[0] == "@":
                # First, see if we can add a record; the keyword must be non-empty, other fields not
                if entry["keyword"]:
                    keywords.append(entry["keyword"])
                    titles.append(entry["title"])
                    years.append(entry["year"])
                    # For author, if there is an editor, that's good enough
                    authors.append(entry["author"] or entry["editor"] or "????")
                    journals.append(entry["journal"] or entry["eprint"] or "????")
                    # Now reset for the next iteration
                    entry["keyword"] = ""
                    entry["title"] = ""
                    entry["year"] = ""
                    entry["author"] = ""
                    entry["editor"] = ""
                    entry["journal"] = ""
                    entry["eprint"] = ""
                # Now see if we get a new keyword
                kp_match = kp.search(line)
                if kp_match:
                    entry["keyword"] = kp_match.group(1) # No longer decode. Was: .decode('ascii','ignore')
                else:
                    print ("Cannot process this @ line: " + line)
                    print ("Previous record " + entry)
                continue
            # Now test for title, author, etc.
            # Note: we capture only the first line, but that's OK for our purposes
            multip_match = multip.search(line)
            if multip_match:
                key = multip_match.group(1).lower()     # no longer decode. Was:    .decode('ascii','ignore')
                value = multip_match.group(2)           #                           .decode('ascii','ignore')
                entry[key] = value
            continue

        # at the end, we are left with one bib entry
        keywords.append(entry["keyword"])
        titles.append(entry["title"])
        years.append(entry["year"])
        authors.append(entry["author"] or entry["editor"] or "????")
        journals.append(entry["journal"] or entry["eprint"] or "????")

        print ( "Found %d total bib entries" % (len(keywords),) )

        # # Filter out }'s at the end. There should be no commas left
        titles = [t.replace('{\\textquoteright}', '').replace('{','').replace('}','') for t in titles]

        # format author field
        def format_author(authors):
            # print(authors)
            # split authors using ' and ' and get last name for 'last, first' format
            authors = [a.split(", ")[0].strip(' ') for a in authors.split(" and ")]
            # get last name for 'first last' format (preserve {...} text)
            authors = [a.split(" ")[-1] if a[-1] != '}' or a.find('{') == -1 else re.sub(r'{|}', '', a[len(a) - a[::-1].index('{'):-1]) for a in authors]
            #     authors = [a.split(" ")[-1] for a in authors]
            # truncate and add 'et al.'
            if len(authors) > 2:
                authors = authors[0] + " et al."
            else:
                authors = ' & '.join(authors)
            # return formated string
            # print(authors)
            return authors

        # format list of authors
        authors_short = [format_author(author) for author in authors]

        # short title
        sep = re.compile(":|\.|\?")
        titles_short = [sep.split(title)[0] for title in titles]
        titles_short = [title[0:60] + '...' if len(title) > 60 else title for title in titles_short]

        # completions object
        completions += zip(keywords, titles, authors, years, authors_short, titles_short, journals)


    #### END COMPLETIONS HERE ####

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

        if prefix:
            completions = [comp for comp in completions if prefix.lower() in "%s %s" % (comp[0].lower(), comp[1].lower())]
            prefix += " "

        # get preferences for formating of autocomplete entries
        s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
        cite_autocomplete_format = s.get("cite_autocomplete_format", "{keyword}: {title}")

        r = [(prefix + cite_autocomplete_format.format(keyword=keyword, title=title, author=author, year=year, author_short=author_short, title_short=title_short, journal=journal),
                keyword + post_brace) for (keyword, title, author, year, author_short, title_short, journal) in completions]

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

        # filter against keyword, title, or author
        if prefix:
            completions = [comp for comp in completions if prefix.lower() in "%s %s %s" \
                                                    % (comp[0].lower(), comp[1].lower(), comp[2].lower())]

        # Note we now generate citation on the fly. Less copying of vectors! Win!
        def on_done(i):
            print ("latex_cite_completion called with index %d" % (i,) )

            # Allow user to cancel
            if i<0:
                return

            cite = completions[i][0] + post_brace

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
        s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
        cite_panel_format = s.get("cite_panel_format", ["{title} ({keyword})", "{author}"])

        # show quick
        view.window().show_quick_panel([[str.format(keyword=keyword, title=title, author=author, year=year, author_short=author_short, title_short=title_short, journal=journal) for str in cite_panel_format] \
                                        for (keyword, title, author, year, author_short, title_short,journal) in completions], on_done)
