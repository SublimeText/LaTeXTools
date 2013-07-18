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
def find_labels_in_files(rootdir, src, labels):
    if src[-4:].lower() != ".tex":
        src = src + ".tex"

    file_path = os.path.normpath(os.path.join(rootdir, src))
    print ("Searching file: " + repr(file_path))
    # The following was a mistake:
    #dir_name = os.path.dirname(file_path)
    # THe reason is that \input and \include reference files **from the directory
    # of the master file**. So we must keep passing that (in rootdir).

    # read src file and extract all label tags

    # We open with utf-8 by default. If you use a different encoding, too bad.
    # If we really wanted to be safe, we would read until \begin{document},
    # then stop. Hopefully we wouldn't encounter any non-ASCII chars there. 
    # But for now do the dumb thing.
    try:
        src_file = codecs.open(file_path, "r", "UTF-8")
    except IOError:
        sublime.status_message("LaTeXTools WARNING: cannot find included file " + file_path)
        print ("WARNING! I can't find it! Check your \\include's and \\input's." )
        return

    src_content = re.sub("%.*", "", src_file.read())
    src_file.close()

    # If the file uses inputenc with a DIFFERENT encoding, try re-opening
    # This is still not ideal because we may still fail to decode properly, but still... 
    m = re.search(r"\\usepackage\[(.*?)\]\{inputenc\}", src_content)
    if m and (m.group(1) not in ["utf8", "UTF-8", "utf-8"]):
        print("reopening with encoding " + m.group(1))
        f = None
        try:
            f = codecs.open(file_path, "r", m.group(1))
            src_content = re.sub("%.*", "", f.read())
        except:
            print("Uh-oh, could not read file " + file_path + " with encoding " + m.group(1))
        finally:
            if f and not f.closed:
                f.close()

    labels += re.findall(r'\\label\{([^{}]+)\}', src_content)

    # search through input tex files recursively
    for f in re.findall(r'\\(?:input|include)\{([^\{\}]+)\}', src_content):
        find_labels_in_files(rootdir, f, labels)


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

    root = getTeXRoot.get_tex_root(view)
    if root:
        print ("TEX root: " + repr(root))
        find_labels_in_files(os.path.dirname(root), root, completions)

    # remove duplicates
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
        if not view.match_selector(locations[0],
                "text.tex.latex"):
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
        print (point)
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
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