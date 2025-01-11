from functools import reduce
import sublime


def advanced_settings():
    try:
        return advanced_settings.cache
    except AttributeError:
        advanced_settings.cache = sublime.load_settings("LaTeXTools (Advanced).sublime-settings")
        return advanced_settings.cache


def global_settings():
    try:
        return global_settings.cache
    except AttributeError:
        global_settings.cache = sublime.load_settings("LaTeXTools.sublime-settings")
        return global_settings.cache


def subscribe_settings_change(key, callback, view=None):
    if view and view.is_valid():
        key = "{}_{}".format(key, view.id())
        view.settings().add_on_change(key, callback)

    advanced_settings().add_on_change(key, callback)
    global_settings().add_on_change(key, callback)


def unsubscribe_settings_change(key, view=None):
    if view:
        key = "{}_{}".format(key, view.id())
        view.settings().clear_on_change(key)

    advanced_settings().clear_on_change(key)
    global_settings().clear_on_change(key)


def get_setting(key, default=None, view=None):
    if view is None:
        window = sublime.active_window()
        if window:
            view = window.active_view()

    if isinstance(view, sublime.View):
        view_settings = view.settings()
    else:
        view_settings = {}

    result = view_settings.get("latextools." + key)

    if result is None:
        result = global_settings().get(key)

    if result is None:
        result = advanced_settings().get(key, default)

    if result is None or "":
        result = default

    elif isinstance(result, dict):
        result = merge_dicts(
            advanced_settings().get(key, {}),
            global_settings().get(key, {}),
            view_settings.get("latextools." + key, {}),
        )

    return result


def deep_merge(dict1, dict2):
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            deep_merge(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


def merge_dicts(*dicts):
    return reduce(deep_merge, dicts)
