import sublime, sublime_plugin
import os, os.path
import re
import getTeXRoot


def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None


# recursively search all linked tex files to find all
# included \label{} tags in the document and extract
def find_labels_in_files(rootdir, src, labels):
    if src[-4:] != ".tex":
        src = src + ".tex"

    file_path = os.path.normpath(os.path.join(rootdir, src))
    print "Searching file: " + file_path
    dir_name = os.path.dirname(file_path)

    # read src file and extract all label tags
    with open(file_path, "r") as src_file:
        src_content = re.sub("%.*", "", src_file.read())
        labels += re.findall(r'\\label\{([^\{\}]+)\}', src_content)

    # search through input tex files recursively
    for f in re.findall(r'\\(?:input|include)\{([^\{\}]+)\}', src_content):
        find_labels_in_files(dir_name, f, labels)


# Based on html_completions.py
#
# It expands references; activated by 
# ref<tab>
# refp<tab> [this adds parentheses around the ref]
# eqref<tab> [obvious]
#
# Furthermore, you can "pre-filter" the completions: e.g. use
#
# ref_sec
#
# to select all labels starting with "sec". 
#
# There is only one problem: if you have a label "sec:intro", for instance,
# doing "ref_sec:" will find it correctly, but when you insert it, this will be done
# right after the ":", so the "ref_sec:" won't go away. The problem is that ":" is a
# word boundary. Then again, TextMate has similar limitations :-)

class LatexRefCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        # Only trigger within LaTeX
        if not view.match_selector(locations[0],
                "text.tex.latex"):
            return []

        # Get the contents of line 0, from the beginning of the line to
        # the current point
        l = locations[0]
        line = view.substr(sublime.Region(view.line(l).a, l))

        # Reverse, to simulate having the regex
        # match backwards (cool trick jps btw!)
        line = line[::-1]
        #print line

        # Check the first location looks like a ref, but backward
        rex = re.compile("([^_]*_)?(p)?fer(qe)?")
        expr = match(rex, line)
        # print expr

        if expr:
            # Return the matched bits, for mangling
            prefix, has_p, has_eq = rex.match(expr).groups()
            preformatted = False
            if prefix:
                prefix = prefix[::-1]   # reverse
                prefix = prefix[1:]     # chop off #
            else:
                prefix = ""
            #print prefix, has_p, has_eq

        else:
            # Check to see if the location matches a preformatted "\ref{blah"
            rex = re.compile(r"([^{}]*)\{fer(qe)?\\(\()?")
            expr = match(rex, line)

            if not expr:
                return []

            preformatted = True
            # Return the matched bits (barely needed, in this case)
            prefix, has_eq, has_p = rex.match(expr).groups()
            if prefix:
                prefix = prefix[::-1]   # reverse
            else:
                prefix = ""
            #print prefix, has_p, has_eq

        if has_p:
            pre_snippet = "(\\ref{"
            post_snippet = "})"
        elif has_eq:
            pre_snippet = "\\eqref{"
            post_snippet = "}"
        else:
            pre_snippet = "\\ref{"
            post_snippet = "}"

        if not preformatted:
            # Replace ref_blah with \ref{blah
            expr_region = sublime.Region(l - len(expr), l)
            #print expr[::-1], view.substr(expr_region)
            ed = view.begin_edit()
            view.replace(ed, expr_region, pre_snippet + prefix)
            view.end_edit(ed)

        else:
            # Don't include post_snippet if it's already present
            suffix = view.substr(sublime.Region(l, l + len(post_snippet)))
            if post_snippet == suffix:
                post_snippet = ""

        completions = []
        # stop matching at FIRST } after \label{
        view.find_all(r'\\label\{([^\{\}]+)\}', 0, '\\1', completions)

        # first search sublime-project file settings for TEXroot
        root = view.settings().get('TEXroot')

        if not root:
            # Find tex root and search all tex source referenced
            # TEX root is the current file itself if no TEX root is specified
            root = getTeXRoot.get_tex_root(view.file_name())

        print "TEX root: " + root
        find_labels_in_files(os.path.dirname(root), root, completions)
        # remove duplicate bib files
        completions = list(set(completions))

        r = [(label + "\t\\ref{}", label + post_snippet) for label in completions]
        #print r
        return (r, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)