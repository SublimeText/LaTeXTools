from __future__ import print_function

import sublime

from functools import partial

try:
    from .utils import run_on_main_thread
except:
    from latextools_utils.utils import run_on_main_thread

__all__ = ['get_setting']


def get_setting(setting, default=None, view=None):
    if default is not None:
        return run_on_main_thread(
            partial(_get_setting, setting, default, view),
            default_value=default)
    else:
        return run_on_main_thread(
            partial(_get_setting, setting, view=view))


def _get_setting(setting, default=None, view=None):
    advanced_settings = sublime.load_settings(
        'LaTeXTools (Advanced).sublime-settings')
    global_settings = sublime.load_settings('LaTeXTools.sublime-settings')

    try:
        if view is None:
            view_settings = sublime.active_window().active_view().settings()
        elif isinstance(view, sublime.View):
            view_settings = view.settings()
        else:
            view_settings = {}
    except:
        # no view defined or view invalid
        view_settings = {}

    result = view_settings.get(setting)

    if result is None:
        result = global_settings.get(setting)

    if result is None:
        result = advanced_settings.get(setting, default)

    if result is None or '':
        result = default

    if isinstance(result, sublime.Settings) or isinstance(result, dict):
        values = {}
        for s in (
            advanced_settings.get(setting, {}),
            global_settings.get(setting, {}),
            view_settings.get(setting, {}),
            result
        ):
            # recursively load settings
            update_setting(values, s)
        result = values

    return result


def update_setting(settings, values):
    for key in values:
        if (
            key in settings and (
                isinstance(settings[key], dict) or
                isinstance(settings[key], sublime.Settings)
            )
        ):
            update_setting(settings[key], values[key])
        else:
            settings[key] = values[key]
    return settings
