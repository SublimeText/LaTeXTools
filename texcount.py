from __future__ import print_function

import sublime
import sublime_plugin

import os

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import get_setting
    from latextools_utils.external_command import (
        check_output, CalledProcessError
    )
    from getTeXRoot import get_tex_root
else:
    _ST3 = True
    from .latextools_utils import get_setting
    from .latextools_utils.external_command import (
        check_output, CalledProcessError
    )
    from .getTeXRoot import get_tex_root


class TexcountCommand(sublime_plugin.TextCommand):
    """
    Simple TextCommand to run TeXCount against the current document
    """

    def run(self, edit, **args):
        tex_root = get_tex_root(self.view)

        if not os.path.exists(tex_root):
            sublime.error_message(
                'Tried to run TeXCount on non-existent file. Please ensure '
                'all files are saved before invoking TeXCount.'
            )
            return

        sub_level = args.get(
            'sub_level',
            get_setting(
                'word_count_sub_level',
                'none'
            )
        )

        if sub_level not in ['none', 'part', 'chapter', 'section']:
            sub_level = 'none'

        if sub_level == 'none':
            command = ['texcount', '-total', '-merge', '-utf8']
        else:
            command = ['texcount', '-merge', '-sub=' + sub_level, '-utf8']
        cwd = os.path.dirname(tex_root)
        command.append(os.path.basename(tex_root))

        try:
            result = check_output(command, cwd=cwd)
            res_split = result.splitlines()
            self.view.window().show_quick_panel(
                res_split[1:4] + res_split[9:], None
            )
        except CalledProcessError as e:
            sublime.error_message(
                'Error while running TeXCount: {0}'.format(e.output or e)
            )
        except OSError:
            sublime.error_message(
                'Could not run texcount. Please ensure that TeXcount is '
                'installed and that your texpath setting includes the path '
                'containing the TeXcount executable.'
            )

    def is_visible(self, *args):
        view = self.view
        return bool(view.score_selector(0, 'text.tex.latex'))
