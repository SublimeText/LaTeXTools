import sublime
import sublime_plugin

import re

_WHITESPACE = re.compile('^\s*$')


class LatextoolsWrapInText(sublime_plugin.TextCommand):

    def run(self, edit, command=None):
        if command is None:
            return

        view = self.view

        new_sels = []
        for sel in view.sel():
            if sel.empty():
                replace_region = view.word(sel)
            else:
                replace_region = sel

            replace_selection = view.substr(replace_region)

            if sel.empty():
                # view.word() captures surrounding whitespace if there is no
                # current word, so we elminiate it
                if _WHITESPACE.match(replace_selection):
                    replace_region = sel
                    replace_selection = _WHITESPACE.sub(u'', replace_selection)

            replace_string = \
                u'\\{command}{{{replace_selection}}}'.format(
                    **locals())

            view.replace(edit, replace_region, replace_string)

            if replace_region.empty():
                start_point = end_point = \
                    replace_region.begin() + len(replace_string) - 1
            else:
                start_point = replace_region.begin() + len(command) + 2
                end_point = replace_region.begin() + len(replace_string) - 1

            new_sels.append(sublime.Region(start_point, end_point))

        view.sel().clear()
        view.sel().add_all(new_sels)
