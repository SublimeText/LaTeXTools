import os

import sublime
import sublime_plugin

from .deprecated_command import deprecate
from .utils.external_command import CalledProcessError
from .utils.external_command import check_output
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

__all__ = ["LatextoolsTexcountCommand"]


class LatextoolsTexcountCommand(sublime_plugin.WindowCommand):
    """
    Simple WindowCommand to run TeXCount against the current document
    """

    def is_visible(self):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self, **args):
        view = self.window.active_view()
        tex_root = get_tex_root(view)

        if not tex_root or not os.path.exists(tex_root):
            sublime.error_message(
                "Tried to run TeXCount on non-existent file. Please ensure "
                "all files are saved before invoking TeXCount."
            )
            return

        sub_level = args.get("sub_level", get_setting("word_count_sub_level", "none", view))

        if sub_level not in ["none", "part", "chapter", "section"]:
            sub_level = "none"

        if sub_level == "none":
            command = ["texcount", "-total", "-merge", "-utf8"]
        else:
            command = ["texcount", "-merge", "-sub=" + sub_level, "-utf8"]
        cwd = os.path.dirname(tex_root)
        command.append(os.path.basename(tex_root))

        try:
            result = check_output(command, cwd=cwd)
            res_split = result.splitlines()
            self.window.show_quick_panel(res_split[1:4] + res_split[9:], lambda _: None)
        except CalledProcessError as e:
            sublime.error_message("Error while running TeXCount: {0}".format(e.output or e))
        except OSError:
            sublime.error_message(
                "Could not run texcount. Please ensure that TeXcount is "
                "installed and that your texpath setting includes the path "
                "containing the TeXcount executable."
            )


deprecate(globals(), "TexcountCommand", LatextoolsTexcountCommand)
