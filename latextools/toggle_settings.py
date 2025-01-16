import sublime
import sublime_plugin

from .utils.logging import logger
from .utils.settings import get_setting
from .utils.settings import global_settings

__all__ = ["LatextoolsToggleKeysCommand"]


def _make_panel_entry(t, prefix_map):
    entry_info = prefix_map.get(t[0], [])
    kbd = next(iter(entry_info or []), "")
    key_name = t[0].replace("_", " ")
    default_value = "{0}  (default: {1})".format(t[1], t[2])
    trigger = "Trigger: C-l,t,{0}".format(",".join(kbd)) if kbd else ""
    try:
        description = entry_info[1][0]
    except IndexError:
        description = ""
    return [key_name, default_value + ("; " + trigger if trigger else ""), description]


def _toggle_setting(setting_name, view):
    new_value = not get_setting(setting_name, True, view=view)
    view.settings().set("latextools.{}".format(setting_name), new_value)
    message = "Set '{0}' to '{1}'.".format(setting_name, new_value)
    sublime.status_message(message)
    logger.info(message)


def _show_toggle_overlay(window, view, prefix, setting_keys):
    default_settings = global_settings()
    setting_keys = [t for t in setting_keys if t[1].startswith(prefix)]
    prefix_map = {k: [v, rest] for k, v, *rest in setting_keys}

    current_settings = [[s, get_setting(s), default_settings.get(s)] for s, *_ in setting_keys]

    panel_entries = [_make_panel_entry(t, prefix_map) for t in current_settings]

    def toggle_setting(index):
        if index == -1:
            return
        name, value = current_settings[index][0:2]
        new_value = not value
        message = "Set '{0}' to {1}".format(name, new_value)
        sublime.status_message(message)
        logger.info(message)
        current_settings[index][1] = new_value
        view.settings().set("latextools.{}".format(name), new_value)
        panel_entries[index] = _make_panel_entry(current_settings[index], prefix_map)

        window.show_quick_panel(panel_entries, toggle_setting, selected_index=index)

    window.show_quick_panel(panel_entries, toggle_setting)


class LatextoolsToggleKeysCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self, character="", prefix=""):
        view = self.window.active_view()
        if not view:
            return

        if not view.match_selector(0, "text.tex.latex"):
            return

        setting_keys = get_setting("toggle_setting_keys", [], view={})
        for v, k, *_ in setting_keys:
            if prefix:
                if not k.startswith(prefix):
                    continue
                k = k[len(prefix) :]

            if character and k == character:
                # change the settings value
                _toggle_setting(v, view)
                return

        # show the overlay with all settings
        _show_toggle_overlay(self.window, view, prefix, setting_keys)
