import sublime
import sublime_plugin

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import get_setting
else:
    _ST3 = True
    from .latextools_utils import get_setting

_toggle_settings = [
    "keep_focus",
    "forward_sync",
    "open_pdf_on_build",
    "ref_auto_trigger",
    "cite_auto_trigger",
    "fill_auto_trigger",
    "env_auto_trigger",
    "glossary_auto_trigger",
    "tex_directive_auto_trigger",
    "smart_bracket_auto_trigger"
]


def _make_panel_entry(t):
    return [t[0].replace("_", " "), "{0}  (default: {1})".format(t[1], t[2])]


class ToggleShowCommand(sublime_plugin.TextCommand):
    def is_visible(self, *args):
        view = sublime.active_window().active_view()
        return bool(view.score_selector(0, "text.tex"))

    def run(self, edit, **args):
        view = self.view
        window = view.window()
        default_settings = sublime.load_settings("LaTeXTools.sublime-settings")

        _current_settings = [[s, get_setting(s), default_settings.get(s)]
                             for s in _toggle_settings]

        _panel_entries = [_make_panel_entry(t) for t in _current_settings]

        def toggle_setting(index):
            if index == -1:
                return
            name, value = _current_settings[index][0:2]
            new_value = not value
            message = "Set '{0}' to {1}".format(name, new_value)
            print(message)
            sublime.status_message(message)
            _current_settings[index][1] = new_value
            view.settings().set(name, new_value)
            _panel_entries[index] = _make_panel_entry(_current_settings[index])

            # keep the index (only possible with ST3)
            flags = {"selected_index": index} if _ST3 else {}
            window.show_quick_panel(_panel_entries, toggle_setting, **flags)

        window.show_quick_panel(_panel_entries, toggle_setting)
