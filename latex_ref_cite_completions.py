## Match both refs and cites, then dispatch as needed

# First stab: ideally we should do all matching here, then dispatch via Python, without
# invoking commands

import sublime, sublime_plugin
import re

class LatexRefCiteCommand(sublime_plugin.TextCommand):

    # Remember that this gets passed an edit object
    def run(self, edit):
        # get view and location of first selection, which we expect to be just the cursor position
        view = self.view
        point = view.sel()[0].b
        print point
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point,
                "text.tex.latex"):
            return

        # Get the contents of the current line, from the beginning of the line to
        # the current point
        line = view.substr(sublime.Region(view.line(point).a, point))
        print line

        # Reverse
        line = line[::-1]

        rex_ref_new = re.compile(r"[^{]*\{fer")
        rex_ref_old = re.compile(r".*_p?fer")
        rex_cite_new = re.compile(r".*etic\\")
        rex_cite_old = re.compile(r".*_[a-zA-Z]*etic")

        if re.match(rex_ref_old, line) or re.match(rex_ref_new, line):
            print "Dispatching ref"
            view.run_command("latex_ref")
        elif re.match(rex_cite_old, line) or re.match(rex_cite_new, line):
            print "Dispatching cite"
            view.run_command("latex_cite")
        else:
            sublime.error_message("Ref/cite: unrecognized format.")
            return
