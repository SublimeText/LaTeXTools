from __future__ import print_function

import sublime


__all__ = ['get_setting']


def get_setting(setting, default=None, view=None):
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

    result = view_settings.get('latextools.{}'.format(setting))

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
            view_settings.get('latextools.{}'.format(setting), {}),
            result
        ):
            # recursively load settings
            _update_setting(values, s)
        result = values

    return result


def _update_setting(settings, values):
    for key in values:
        if (
            key in settings and (
                isinstance(settings[key], dict) or
                isinstance(settings[key], sublime.Settings)
            )
        ):
            _update_setting(settings[key], values[key])
        else:
            settings[key] = values[key]
    return settings
