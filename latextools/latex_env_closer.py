import sublime
import sublime_plugin

__all__ = ["LatextoolsLatexEnvCloserCommand"]

# Insert environment closer
# this only looks at the LAST \begin{...}
# need to extend to allow for nested \begin's


class LatextoolsLatexEnvCloserCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        view = self.view
        pattern = r"\\(begin|end)\{[^\}]+\}"
        b = []
        currpoint = view.sel()[0].b
        point = 0
        r = view.find(pattern, point)
        while r and r.end() <= currpoint:
            be = view.substr(r)
            point = r.end()
            if "\\begin" == be[0:6]:
                b.append(be[6:])
            else:
                if be[4:] == b[-1]:
                    b.pop()
                else:
                    sublime.error_message(
                        f"\\begin{b[-1]} closed with {be} on line {view.rowcol(point)[0]}"
                    )
                    return
            r = view.find(pattern, point)
        # now either b = [] or b[-1] is unmatched
        if b == []:
            sublime.error_message("Every environment is closed")
        else:
            # for some reason insert does not work
            view.run_command("insert_snippet", {"contents": f"\\\\end{b[-1]}\n"})
