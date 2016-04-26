from __future__ import print_function

from collections import Mapping

import sublime

class SettingsWrapper(Mapping):
    '''
    Wrapper object for nested settings, to allow us to refer to keys
    defined in the global settings but not overridden by, e.g.,
    project or buffer-specific settings.

    This is done so that, e.g., platform-specific settings can be
    overridden per-project or per-buffer without needing to override
    all settings that might be globally set (e.g., changing the texpath
    setting for a project without changing viewer-specific settings)
    '''
    def __init__(self, key, values, view_settings=None, parent=None):
        self.key = key

        if parent is not None:
            self._values = parent._values
            self._values.update(values)
        else:
            values = {}
            if view_settings is None:
                view_settings = {}

            advanced_settings = sublime.load_settings('LaTeXTools (Advanced).sublime-settings')
            global_settings = sublime.load_settings('LaTeXTools.sublime-settings')

            for s in (
                advanced_settings.get(self.key, {}),
                global_settings.get(self.key, {}),
                view_settings.get(self.key, {}),
                values
            ):
                if isinstance(s, dict) or isinstance(s, sublime.Settings):
                    for key in s:
                        values[key] = s[key]
            self._values = values

    def get(self, key, default=None):
        try:
            result = self._values.get(key)
        except KeyError:
            result = None

        if result is None:
            result = default

        if isinstance(result, sublime.Settings) or isinstance(result, dict):
            result = SettingsWrapper(key, result, parent=self)

        return result

    def __getitem__(self, key):
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)


def get_setting(setting, default=None, view=None):
    advanced_settings = sublime.load_settings('LaTeXTools (Advanced).sublime-settings')
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
        result = SettingsWrapper(setting, result, view_settings)

    return result
