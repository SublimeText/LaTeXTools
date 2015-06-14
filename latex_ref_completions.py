# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
    from latextools_utils import is_tex_buffer
    from latextools_utils.subfiles import walk_subfiles
else:
    _ST3 = True
    from . import getTeXRoot
    from .latextools_utils import is_tex_buffer
    from .latextools_utils.subfiles import walk_subfiles

import sublime_plugin
import os, os.path
import re
import codecs


class UnrecognizedRefFormatError(Exception): pass

_ref_special_commands = "|".join(["", "eq", "page", "v", "V", "auto", "name", "c", "C", "cpage"])[::-1]

OLD_STYLE_REF_REGEX = re.compile(r"([^_]*_)?(p)?fer(" + _ref_special_commands + r")?(?:\\|\b)")
NEW_STYLE_REF_REGEX = re.compile(r"([^{}]*)\{fer(" + _ref_special_commands + r")?\\(\()?")


def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

# recursively search all linked tex files to find all
# included \label{} tags in the document and extract
def find_labels_in_files(rootdir, src):
    completions = []
    for content in walk_subfiles(rootdir, src):
        for label in re.findall(r'\\label\{([^{}]+)\}', content):
            completions.append(label)

    return completions

# get_ref_completions forms the guts of the parsing shared by both the
# autocomplete plugin and the quick panel command
def get_ref_completions(view, point, autocompleting=False):
    # Get contents of line from start up to point
    line = view.substr(sublime.Region(view.line(point).a, point))
    # print line

    # Reverse, to simulate having the regex
    # match backwards (cool trick jps btw!)
    line = line[::-1]
    #print line

    # Check the first location looks like a ref, but backward
    rex = OLD_STYLE_REF_REGEX
    expr = match(rex, line)
    # print expr

    if expr:
        # Do not match on plain "ref" when autocompleting,
        # in case the user is typing something else
        if autocompleting and re.match(r"p?fer(?:" + _ref_special_commands + r")?\\?", expr):
            raise UnrecognizedRefFormatError()
        # Return the matched bits, for mangling
        prefix, has_p, special_command = rex.match(expr).groups()
        preformatted = False
        if prefix:
            prefix = prefix[::-1]   # reverse
            prefix = prefix[1:]     # chop off "_"
        else:
            prefix = ""
        #print prefix, has_p, special_command

    else:
        # Check to see if the location matches a preformatted "\ref{blah"
        rex = NEW_STYLE_REF_REGEX
        expr = match(rex, line)

        if not expr:
            raise UnrecognizedRefFormatError()

        preformatted = True
        # Return the matched bits (barely needed, in this case)
        prefix, special_command, has_p = rex.match(expr).groups()
        if prefix:
            prefix = prefix[::-1]   # reverse
        else:
            prefix = ""
        #print prefix, has_p, special_command

    pre_snippet = "\\" + special_command[::-1] + "ref{"
    post_snippet = "}"

    if has_p:
        pre_snippet = "(" + pre_snippet
        post_snippet = post_snippet + ")"

    if not preformatted:
        # Replace ref_blah with \ref{blah
        # The "latex_tools_replace" command is defined in latex_ref_cite_completions.py
        view.run_command("latex_tools_replace", {"a": point-len(expr), "b": point, "replacement": pre_snippet + prefix})
        # save prefix begin and endpoints points
        new_point_a = point - len(expr) + len(pre_snippet)
        new_point_b = new_point_a + len(prefix)
#        view.end_edit(ed)

    else:
        # Don't include post_snippet if it's already present
        suffix = view.substr(sublime.Region(point, point + len(post_snippet)))
        new_point_a = point - len(prefix)
        new_point_b = point
        if post_snippet == suffix:
            post_snippet = ""

    completions = []
    # Check the file buffer first:
    #    1) in case there are unsaved changes
    #    2) if this file is unnamed and unsaved, get_tex_root will fail
    view.find_all(r'\\label\{([^\{\}]+)\}', 0, '\\1', completions)
    print(completions)

    root = getTeXRoot.get_tex_root(view)
    if root:
        print ("TEX root: " + repr(root))
        completions.extend(find_labels_in_files(os.path.dirname(root), root))

    # remove duplicates
    print(completions)
    completions = list(set(completions))

    return completions, prefix, post_snippet, new_point_a, new_point_b

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
        if not is_tex_buffer(view):
            return []

        point = locations[0]

        try:
            completions, prefix, post_snippet, new_point_a, new_point_b = get_ref_completions(view, point, autocompleting=True)
        except UnrecognizedRefFormatError:
            return []

        # r = [(label + "\t\\ref{}", label + post_snippet) for label in completions]
        r = [(label, label + post_snippet) for label in completions]
        #print r
        return (r, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


### Ref completions using the quick panel

class LatexRefCommand(sublime_plugin.TextCommand):

    # Remember that this gets passed an edit object
    def run(self, edit):
        # get view and location of first selection, which we expect to be just the cursor position
        view = self.view
        point = view.sel()[0].b
        # Only trigger within LaTeX
        if not is_tex_buffer(view, point):
            return

        try:
            completions, prefix, post_snippet, new_point_a, new_point_b = get_ref_completions(view, point)
        except UnrecognizedRefFormatError:
            sublime.error_message("Not a recognized format for reference completion")
            return

        # filter! Note matching is "less fuzzy" than ST2. Room for improvement...
        completions = [c for c in completions if prefix in c]

        if not completions:
            sublime.error_message("No label matches %s !" % (prefix,))
            return

        # Note we now generate refs on the fly. Less copying of vectors! Win!
        def on_done(i):
            print ("latex_ref_completion called with index %d" % (i,))
            
            # Allow user to cancel
            if i<0:
                return

            ref = completions[i] + post_snippet
            

            # Replace ref expression with reference and possibly post_snippet
            # The "latex_tools_replace" command is defined in latex_ref_cite_completions.py
            view.run_command("latex_tools_replace", {"a": new_point_a, "b": new_point_b, "replacement": ref})
            # Unselect the replaced region and leave the caret at the end
            caret = view.sel()[0].b
            view.sel().subtract(view.sel()[0])
            view.sel().add(sublime.Region(caret, caret))
        
        view.window().show_quick_panel(completions, on_done)