import sublime
import sublime_plugin

_ST3 = sublime.version() >= '3000'

if _ST3:
    from .getTeXRoot import get_tex_root
    from .latextools_utils import analysis, get_setting, quickpanel
else:
    from getTeXRoot import get_tex_root
    from latextools_utils import analysis, get_setting, quickpanel


_section_commands = [
    "chapter",
    "section",
    "subsection",
    "subsubsection",
    "paragraph"
]

_label_commands = [
    "label"
]

_indentations = {
    "chapter": 0,
    "section": 1,
    "subsection": 2,
    "subsubsection": 3,
    "paragraph": 4,
    "label": 0
}


def _make_caption(com):
    indent = _indentations.get(com.command, 0)
    short = {
        "subsubsection": "sss",
        "label": "L"
    }.get(com.command, com.command[0:3])
    short = short.title()

    return ("  " * indent) + short + com.star + " " + com.args


class show_toc_quickpanel(quickpanel.CancelEntriesQuickpanel):
    __show_string = "Show Labels"
    __hide_string = "Hide Labels"
    __toggles = [__show_string, __hide_string]

    def __init__(self, ana):
        # retrieve the labels and the sections
        labels = ana.filter_commands(_section_commands + _label_commands)
        # filter the labels and sections to only get the labels
        # (faster than an additional query)
        secs = [c for c in labels if c.command in _section_commands]

        # create the user readably captions
        caption_secs = list(map(_make_caption, secs))
        caption_labels = list(map(_make_caption, labels))

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
    def run(self):
        view = self.window.active_view()
        tex_root = get_tex_root(view)
        if not tex_root:
            return
        ana = analysis.analyze_document(tex_root)

        show_toc_quickpanel(ana)


class LatexTocQuickpanelContext(sublime_plugin.EventListener):
    def on_query_context(self, view, key, *args):
        if (key != "overwrite_goto_overlay" or
                not view.score_selector(0, "text.tex.latex")):
            return None
        return get_setting("overwrite_goto_overlay")
