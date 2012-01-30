import sublime, sublime_plugin
import re

def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

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
        #print expr
        if not expr:
            return []

        # Return the completions
        prefix, has_p, has_eq = rex.match(expr).groups()
        if prefix:
            prefix = prefix[::-1] # reverse
            prefix = prefix[1:] # chop off #
        #print prefix, has_p, has_eq

        # Reverse back expr
        expr = expr[::-1]

        # Replace ref expression with "C" to save space in drop-down menu
        expr_region = sublime.Region(l-len(expr),l)
        #print expr, view.substr(expr_region)
        ed = view.begin_edit()
        view.replace(ed, expr_region, "R")
        view.end_edit(ed)
        expr = "R"


        completions = []
        # stop matching at FIRST } after \label{
        view.find_all('\\label\{([^\{\}]*)\}',0,'\\1',completions)

        if prefix:
            completions = [comp for comp in completions if prefix in comp]

        if has_p:
            pre_snippet = "(\\ref{"
            post_snippet = "})"
        elif has_eq:
            pre_snippet = "\\eqref{"
            post_snippet = "}"
        else:
            pre_snippet = "\\ref{"
            post_snippet = "}"

        r = [(expr + " "+label, pre_snippet + label + post_snippet) for label in completions]
        #print r
        return r
