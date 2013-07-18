# ST2/ST3 compat
from __future__ import print_function
import sys
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
    from latex_cite_completions import OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX
    from latex_ref_completions import OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
else:
    _ST3 = True
    from . import getTeXRoot
    from .latex_cite_completions import OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX
    from .latex_ref_completions import OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX


## Match both refs and cites, then dispatch as needed

# First stab: ideally we should do all matching here, then dispatch via Python, without
# invoking commands

import sublime_plugin
import re


class LatexRefCiteCommand(sublime_plugin.TextCommand):

    # Remember that this gets passed an edit object
    def run(self, edit, insert_char=""):
        # get view and location of first selection, which we expect to be just the cursor position
        view = self.view
        point = view.sel()[0].b
        print (point)
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
            return


        if insert_char:
#            ed = view.begin_edit()
#            point += view.insert(ed, point, insert_char)
#            view.end_edit(ed)
            # The above was roundabout and did not work on ST3!
            point += view.insert(edit, point, insert_char)
            # Get prefs and toggles to see if we are auto-triggering
            # This is only the case if we also must insert , or {, so we don't need a separate arg
            s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
            do_ref = self.view.settings().get("ref auto trigger",s.get("ref_auto_trigger", True))
            do_cite = self.view.settings().get("cite auto trigger",s.get("cite_auto_trigger", True))
        else: # if we didn't autotrigger, we must surely run
            do_ref = True
            do_cite = True

        print (do_ref,do_cite)

        # Get the contents of the current line, from the beginning of the line to
        # the current point
        line = view.substr(sublime.Region(view.line(point).a, point))
        # print line

        # Reverse
        line = line[::-1]


        if re.match(OLD_STYLE_REF_REGEX, line) or re.match(NEW_STYLE_REF_REGEX, line):
            if do_ref:
                print ("Dispatching ref")
                view.run_command("latex_ref")
            else:
                pass # Don't do anything if we match ref completion but we turned it off
        elif re.match(OLD_STYLE_CITE_REGEX, line) or re.match(NEW_STYLE_CITE_REGEX, line):
            if do_cite:
                print ("Dispatching cite")
                view.run_command("latex_cite")
            else:
                pass # ditto for cite
        else: # here we match nothing, so error out regardless of autotrigger settings
            sublime.error_message("Ref/cite: unrecognized format.")
            return

# ST3 cannot use an edit object after the TextCommand has returned; and on_done gets 
# called after TextCommand has returned. Thus, we need this work-around (works on ST2, too)
# Used by both cite and ref completion
class LatexToolsReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, a, b, replacement):
        #print("DEBUG: types of a and b are " + repr(type(a)) + " and " + repr(type(b)))
        # On ST2, a and b are passed as long, but received as floats
        # It's probably a bug. Convert to be safe.
        if _ST3:
            region = sublime.Region(a, b)
        else:
            region = sublime.Region(long(a), long(b))
        self.view.replace(edit, region, replacement)