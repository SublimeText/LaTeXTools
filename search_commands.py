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
    def run(self, commands):
        window = self.window
        view = window.active_view()
        tex_root = get_tex_root(view)

        ana = analysis.analyze_document(tex_root)
        entries = ana.filter_commands(commands, flags=analysis.ALL_COMMANDS)

        captions = [_make_caption(ana, e) for e in entries]
        quickpanel.show_quickpanel(captions, entries)


class LatexSearchCommandInputCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window

        def on_done(text):
            commands = [c.strip() for c in text.split(",")]
            window.run_command("latex_search_command", {"commands": commands})

        def do_nothing(text):
            pass
        caption = "Search for commands in a comma (,) separated list"
        window.show_input_panel(caption, "", on_done=on_done,
                                on_change=do_nothing, on_cancel=do_nothing)
