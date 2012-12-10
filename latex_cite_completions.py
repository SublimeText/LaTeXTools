import sublime, sublime_plugin
import os, os.path
import re
import getTeXRoot


class UnrecognizedCiteFormatError(Exception): pass
class NoBibFilesError(Exception): pass

class BibParsingError(Exception):
    def __init__(self, filename=""):
        self.filename = filename


OLD_STYLE_CITE_REGEX = re.compile(r"([^_]*_)?([a-zX*]*?)etic(?:\\|\b)")
NEW_STYLE_CITE_REGEX = re.compile(r"([^{},]*)(?:,[^{},]*)*\{([a-zX*]*?)etic\\")


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
    print "Searching file: " + repr(file_path)
    # See latex_ref_completion.py for why the following is wrong:
    #dir_name = os.path.dirname(file_path)

    # read src file and extract all bibliography tags
    try:
        src_file = open(file_path, "r")
    except IOError:
        sublime.status_message("LaTeXTools WARNING: cannot open included file " + file_path)
        print "WARNING! I can't find it! Check your \\include's and \\input's." 
        return

    src_content = re.sub("%.*","",src_file.read())
    bibtags =  re.findall(r'\\bibliography\{[^\}]+\}', src_content)

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
    print line

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
        print prefix, fancy_cite

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
        print prefix, fancy_cite

    # Reverse back expr
    expr = expr[::-1]

    post_brace = "}"

    if not preformatted:
        # Replace cite_blah with \cite{blah
        expr_region = sublime.Region(point - len(expr), point)
        #print expr, view.substr(expr_region)
        ed = view.begin_edit()
        pre_snippet = "\cite" + fancy_cite + "{"
        view.replace(ed, expr_region, pre_snippet + prefix)
        # save prefix begin and endpoints points
        new_point_a = point - len(expr) + len(pre_snippet)
        new_point_b = new_point_a + len(prefix)
        view.end_edit(ed)

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

    print "TEX root: " + repr(root)
    bib_files = []
    find_bib_files(os.path.dirname(root), root, bib_files)
    # remove duplicate bib files
    bib_files = list(set(bib_files))
    print "Bib files found: ",
    print repr(bib_files)

    if not bib_files:
        # sublime.error_message("No bib files found!") # here we can!
        raise NoBibFilesError()

    bib_files = ([x.strip() for x in bib_files])

    print "Files:"
    print repr(bib_files)

    completions = []
    kp = re.compile(r'@[^\{]+\{(.+),')
    # new and improved regex
    # we must have "title" then "=", possibly with spaces
    # then either {, maybe repeated twice, or "
    # then spaces and finally the title
    # We capture till the end of the line as maybe entry is broken over several lines
    # and in the end we MAY but need not have }'s and "s
    tp = re.compile(r'\btitle\s*=\s*(?:\{+|")\s*(.+)', re.IGNORECASE)  # note no comma!
    # Tentatively do the same for author
    ap = re.compile(r'\bauthor\s*=\s*(?:\{+|")\s*(.+)', re.IGNORECASE)
    # kp2 = re.compile(r'([^\t]+)\t*')

    for bibfname in bib_files:
        # # THIS IS NO LONGER NEEDED as find_bib_files() takes care of it
        # if bibfname[-4:] != ".bib":
        #     bibfname = bibfname + ".bib"
        # texfiledir = os.path.dirname(view.file_name())
        # # fix from Tobias Schmidt to allow for absolute paths
        # bibfname = os.path.normpath(os.path.join(texfiledir, bibfname))
        # print repr(bibfname)
        try:
            bibf = open(bibfname)
        except IOError:
            print "Cannot open bibliography file %s !" % (bibfname,)
            sublime.status_message("Cannot open bibliography file %s !" % (bibfname,))
            continue
        else:
            bib = bibf.readlines()
            bibf.close()
        print "%s has %s lines" % (repr(bibfname), len(bib))
        # note Unicode trickery
        keywords = [kp.search(line).group(1).decode('ascii', 'ignore') for line in bib if line[0] == '@']
        titles = [tp.search(line).group(1).decode('ascii', 'ignore') for line in bib if tp.search(line)]
        authors = [ap.search(line).group(1).decode('ascii', 'ignore') for line in bib if ap.search(line)]

        # print zip(keywords,titles,authors)

        if len(keywords) != len(titles) or len(keywords) != len(authors):
            # print "Bibliography " + repr(bibfname) + " is broken!"
            raise BibParsingError(bibfname)

        print "Found %d total bib entries" % (len(keywords),)

        # Filter out }'s and ,'s at the end. Ugly!
        nobraces = re.compile(r'\s*,*\}*(.+)')
        titles = [nobraces.search(t[::-1]).group(1)[::-1] for t in titles]
        authors = [nobraces.search(a[::-1]).group(1)[::-1] for a in authors]
        completions += zip(keywords, titles, authors)

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

        r = [(prefix + " "+ title + " " + keyword, keyword + post_brace)
                        for (keyword, title, authors) in completions]

        print "%d bib entries matching %s" % (len(r), prefix)

        return r


class LatexCiteCommand(sublime_plugin.TextCommand):

    # Remember that this gets passed an edit object
    def run(self, edit, insert_comma=False):
        # get view and location of first selection, which we expect to be just the cursor position
        view = self.view
        point = view.sel()[0].b
        print point
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
            return

        if insert_comma:
            ed = view.begin_edit()
            point += view.insert(ed, point, ",")
            view.end_edit(ed)

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
            print "latex_cite_completion called with index %d" % (i,)

            # Allow user to cancel
            if i<0:
                return

            cite = completions[i][0] + post_brace

            print "selected %s:%s by %s" % completions[i]
            # Replace cite expression with citation
            expr_region = sublime.Region(new_point_a, new_point_b)
            ed = view.begin_edit()
            view.replace(ed, expr_region, cite)
            view.end_edit(ed)

        view.window().show_quick_panel([[title + " (" + keyword+ ")", author] \
                                        for (keyword, title, author) in completions], on_done)
