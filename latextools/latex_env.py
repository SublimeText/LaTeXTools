import sublime
import sublime_plugin
import re

from .deprecated_command import deprecate

__all__ = ["LatextoolsLatexEnvCommand"]

# Insert LaTeX environment based on current word
# Position cursor inside environment


class LatextoolsLatexEnvCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        view = self.view

        # Workaround: env* and friends trip ST2 up because * is a word boundary,
        # so we search for a word boundary

        # Code is similar to latex_cite_completions.py (should prbly factor out)
        point = view.sel()[0].b
        line = view.substr(sublime.Region(view.line(point).a, point))
        line = line[::-1]
        rex = re.compile(r"([^\s\{]*)\s?\{?")
        expr = re.match(rex, line)
        if expr:
            environment = expr.group(1)[::-1]
            if environment:
                environment_region = sublime.Region(point - len(environment), point)
                view.erase(edit, environment_region)
                snippet = "\\\\begin{" + environment + "}\n\t$0\n\\\\end{" + environment + "}"
            else:
                snippet = "\\\\begin{${1:env}}\n\t$0\n\\end{$1}"
            view.run_command("insert_snippet", {"contents": snippet})
        else:
            sublime.status_message(
                "LATEXTOOLS INTERNAL ERROR: could not find environment to expand"
            )


deprecate(globals(), "latexenvCommand", LatextoolsLatexEnvCommand)
