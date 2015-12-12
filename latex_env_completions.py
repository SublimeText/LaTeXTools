import sublime
import sublime_plugin


try:
    _ST3 = True
    from .latextools_utils import get_setting
    from .latex_input_completions import add_closing_bracket
    from .latex_cwl_completions import parse_cwl_file, parse_line_as_environment, is_cwl_available
    from .latexFillAll import get_current_word
except:
    _ST3 = False
    from latextools_utils import get_setting
    from latex_input_completions import add_closing_bracket
    from latex_cwl_completions import parse_cwl_file, parse_line_as_environment, is_cwl_available
    from latexFillAll import get_current_word


class LatexFillEnvCommand(sublime_plugin.TextCommand):
    def run(self, edit, insert_char=""):
        view = self.view
        point = view.sel()[0].b
        # Only trigger within LaTeX
        # Note using score_selector rather than match_selector
        if not view.score_selector(point, "text.tex.latex"):
            return

        if not is_cwl_available():
            if insert_char:
                view.insert(edit, point, insert_char)
                add_closing_bracket(view, edit)
            return

        if insert_char:
            # append the insert_char to the end of the current line if it
            # is given so this works when being triggered by pressing "{"
            point += view.insert(edit, point, insert_char)

            do_completion = get_setting("env_auto_trigger", False)

            if not do_completion:
                add_closing_bracket(view, edit)
                return

        if not insert_char:
            # only use the prefix if all cursors have the same
            prefix = get_current_word(view, point)[0]
            for sel in view.sel():
                other_prefix = get_current_word(view, sel.b)[0]
                if other_prefix != prefix:
                    prefix = ""
                    break
        else:
            prefix = ""

        completions = parse_cwl_file(parse_line_as_environment)
        if prefix:
            completions = [c for c in completions if c[1].startswith(prefix)]

        show_entries = [c[0].split("\t") for c in completions]

        def on_done(index):
            if index < 0:
                return
            key = completions[index][1]
            # close bracket
            if insert_char:
                key += "}"

            if prefix:
                for sel in view.sel():
                    point = sel.b
                    startpoint = point - len(prefix)
                    endpoint = point
                    view.run_command('latex_tools_replace', {'a': startpoint, 'b': endpoint, 'replacement': key})
            else:
                view.run_command("insert", {"characters": key})

        # autocomplete bracket if we aren't doing anything
        if not show_entries and insert_char:
            add_closing_bracket(view, edit)
        else:
            view.window().show_quick_panel(show_entries, on_done)
