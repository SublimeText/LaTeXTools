import sublime_plugin

try:
    _ST3 = True
    from .getTeXRoot import get_tex_root
    from .latextools_utils import analysis, ana_utils, quickpanel
except:
    _ST3 = False
    from getTeXRoot import get_tex_root
    from latextools_utils import analysis, ana_utils, quickpanel


def _make_caption(ana, entry):
    text = entry.text
    file_pos_str = ana_utils.create_rel_file_str(ana, entry)
    return "{text} ({file_pos_str})".format(**locals())


class LatexSearchCommandCommand(sublime_plugin.WindowCommand):
    def run(self, commands, only_current_file=False):
        window = self.window
        view = window.active_view()
        tex_root = get_tex_root(view)

        ana = analysis.analyze_document(tex_root)
        entries = ana.filter_commands(commands, flags=analysis.ALL_COMMANDS)

        if only_current_file:
            file_name = view.file_name()
            entries = [e for e in entries if e.file_name == file_name]

        captions = [_make_caption(ana, e) for e in entries]
        quickpanel.show_quickpanel(captions, entries)


class LatexSearchCommandInputCommand(sublime_plugin.WindowCommand):
    def is_visible(self, *args):
        view = self.window.active_view()
        return bool(view.score_selector(0, "text.tex"))

    def run(self, only_current_file=False):
        window = self.window

        def on_done(text):
            commands = [c.strip() for c in text.split(",")]
            kwargs = {
                "commands": commands,
                "only_current_file": only_current_file
            }
            window.run_command("latex_search_command", kwargs)

        def do_nothing(text):
            pass
        caption = "Search for commands in a comma (,) separated list"
        window.show_input_panel(caption, "", on_done, do_nothing, do_nothing)
