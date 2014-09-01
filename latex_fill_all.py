from __future__ import print_function

import sublime
import sublime_plugin

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    from latex_cite_completions import OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, match
    from latex_ref_completions import OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
    from latex_input_completions import TEX_INPUT_FILE_REGEX
else:
    _ST3 = True
    from .latex_cite_completions import OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, match
    from .latex_ref_completions import OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
    from .latex_input_completions import TEX_INPUT_FILE_REGEX


class LatexFillAllCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        view = self.view
        point = view.sel()[0].b

        line = view.substr(sublime.Region(view.line(point).a, point))
        line = line[::-1]

        if match(OLD_STYLE_CITE_REGEX, line) != None or match(NEW_STYLE_CITE_REGEX, line) != None:
            prefix = match(OLD_STYLE_CITE_REGEX, line)
            prefix = prefix if prefix != None else match(NEW_STYLE_CITE_REGEX, line)

            print(prefix)
            if prefix[0] == ',':
                view.run_command("latex_cite")

            sel_str = view.substr(view.sel()[0])
            if prefix.find(sel_str[::-1]) == 0:
                startpos = point - len(sel_str)
                view.run_command("latex_tools_replace", {"a": startpos, "b": point, "replacement": ""})
                view.run_command("latex_cite")
            

        if match(OLD_STYLE_REF_REGEX, line) != None or match(NEW_STYLE_REF_REGEX, line) != None:
            prefix = match(OLD_STYLE_REF_REGEX, line)
            prefix = prefix if prefix != None else match(NEW_STYLE_REF_REGEX, line)

            sel_str = view.substr(view.sel()[0])
            if prefix.find(sel_str[::-1]) == 0:
                startpos = point - len(sel_str)
                view.run_command("latex_tools_replace", {"a": startpos, "b": point, "replacement": ""})
                view.run_command("latex_ref")

        if TEX_INPUT_FILE_REGEX.match(line) != None:
            view.run_command("latex_input_file")




