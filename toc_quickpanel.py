import sublime
import sublime_plugin

_ST3 = sublime.version() >= '3000'

if _ST3:
    from .getTeXRoot import get_tex_root
    from .latextools_utils import analysis, get_setting, quickpanel
else:
    from getTeXRoot import get_tex_root
    from latextools_utils import analysis, get_setting, quickpanel


def _make_caption(toc_indentations, com, indent_offset):
    indent = toc_indentations.get(com.command, 0)
    # lower the indent with the offset
    indent = max(0, indent - indent_offset)
    short = {
        "subsubsection": "sss",
        "minisec": "msec",
        "label": "L"
    }.get(com.command, com.command[0:3])
    short = short.title()
    # special handling for koma script
    if short.lower() == "add":
        short = "+" + com.command[3:6].title()

    return ("  " * indent) + short + com.star + " " + com.args


class show_toc_quickpanel(quickpanel.CancelEntriesQuickpanel):
    __show_string = "Show Labels"
    __hide_string = "Hide Labels"
    __toggles = [__show_string, __hide_string]

    def __init__(self, ana, only_file=None):
        # retrieve the labels and the sections
        toc_section_commands = get_setting("toc_section_commands", [])
        toc_indentations = get_setting("toc_indentations", {})
        toc_labels = get_setting("toc_labels", [])

        labels = ana.filter_commands(toc_section_commands + toc_labels)
        # filter the labels and sections to only get the labels
        # (faster than an additional query)
        secs = [c for c in labels if c.command in toc_section_commands]

        if only_file:
            labels = [l for l in labels if l.file_name == only_file]
            secs = [s for s in secs if s.file_name == only_file]

        # create the user readably captions
        # get the minimal indent (to lower the minimal section indent to 0)
        max_indent_value = max(toc_indentations.values())
        indent_offset = min([
            toc_indentations.get(com.command, max_indent_value)
            for com in secs
        ] + [0])

        caption_secs = [_make_caption(toc_indentations, s, indent_offset)
                        for s in secs]

        caption_labels = [_make_caption(toc_indentations, l, indent_offset)
                          for l in labels]

        self.__only_sec = True
        # init the superclass with a copy of the section elements
        super(show_toc_quickpanel, self).__init__(
            list(caption_secs), list(secs))

        # story necessary fields
        self.__secs = secs
        self.__labels = labels
        self.__caption_secs = caption_secs
        self.__caption_labels = caption_labels

        # add a item to show the labels
        self.add_item(quickpanel.AT_END, self.__show_string,
                      done_handler=self.__show_labels)
        # register a function to hide the labels
        self.done_handler[self.__hide_string] = self.__hide_labels

        # show the quickpanel
        self.show_quickpanel()

    def __hide_labels(self):
        """Handles the toggle to hide the labels"""
        # exchange the captions after the offset (with no navigation entries)
        self.captions = self.captions[0:self._offset] + self.__caption_secs
        # change the name of the toggle from "Hide" to "Show"
        index = self.captions.index(self.__hide_string)
        self.captions[index] = self.__show_string
        # update the entries
        self.entries = self.__secs

        # show the quickpanel such that the changes take effect
        self.show_quickpanel(index)

    def __show_labels(self):
        """Handles the toggle to show the labels"""
        # exchange the captions after the offset (with no navigation entries)
        self.captions = self.captions[0:self._offset] + self.__caption_labels
        # change the name of the toggle from "Show" to "Hide"
        index = self.captions.index(self.__show_string)
        self.captions[index] = self.__hide_string
        # update the entries
        self.entries = self.__labels

        # show the quickpanel such that the changes take effect
        self.show_quickpanel(index)


def show_commands(captions, entries, show_cancel=True):
    if show_cancel:
        Quickpanel = quickpanel.CancelEntriesQuickpanel
    else:
        Quickpanel = quickpanel.EntriesQuickpanel
    Quickpanel(captions, entries).show_quickpanel()


class LatexTocQuickpanelCommand(sublime_plugin.WindowCommand):
    def run(self, only_current_file=False):
        view = self.window.active_view()
        tex_root = get_tex_root(view)
        if not tex_root:
            return
        ana = analysis.analyze_document(tex_root)

        only_file = None if not only_current_file else view.file_name()
        show_toc_quickpanel(ana, only_file=only_file)


class LatexTocQuickpanelContext(sublime_plugin.EventListener):
    def on_query_context(self, view, key, *args):
        if (key != "overwrite_goto_overlay" or
                not view.score_selector(0, "text.tex.latex")):
            return None
        return get_setting("overwrite_goto_overlay")
