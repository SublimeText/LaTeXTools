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

        # split at space, get last contiguous string
        cmd = line.split()[-1]

        rex_ref = re.compile(r"\(?\\?(eq)?ref")
        rex_cite = re.compile(r"\\?cite")

        if re.match(rex_ref, cmd):
            view.run_command("latex_ref")
        elif re.match(rex_cite, cmd):
            view.run_command("latex_cite")
        else:
            return
