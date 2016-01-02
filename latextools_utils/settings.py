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
    def __init__(self, key, values, parent=None):
        self.key = key

        if parent is None:
            self.values = values
        else:
            settings = sublime.load_settings('LaTeXTools.sublime-settings').\
                get(parent.key).get(self.key)
            if settings is not None and isinstance(settings, dict):
                self.values = dict(settings)
                self.values.update(values)
            else:
                self.values = values

    def get(self, key, default=None):
        try:
            result = self.values.get(key)
        except KeyError:
            result = None

        if result is None:
            settings = sublime.load_settings('LaTeXTools.sublime-settings').\
                get(self.key)
            if settings:
                result = settings.get(key)

        if result is None:
            result = default

        if isinstance(result, sublime.Settings) or isinstance(result, dict):
            result = SettingsWrapper(key, result, self)

        return result

    def __getitem__(self, key):
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)


def get_raw_setting(setting, default=None):
    global_settings = sublime.load_settings('LaTeXTools.sublime-settings')

    try:
        result = sublime.active_window().active_view().settings().get(setting)
    except AttributeError:
        # no view defined
        result = None

    if result is None:
        result = global_settings.get(setting, default)

    if result is None:
        result = default

    if isinstance(result, sublime.Settings) or isinstance(result, dict):
        result = SettingsWrapper(setting, result)

    return result


class PlatformSettingsWrapper(Mapping):
    '''
    Wrapper object for nested settings, to allow us to refer to keys
    defined in the global settings but not overridden by, e.g.,
    project or buffer-specific settings.

    This is done so that, e.g., platform-specific settings can be
    overridden per-project or per-buffer without needing to override
    all settings that might be globally set (e.g., changing the texpath
    setting for a project without changing viewer-specific settings)
    '''
    def __init__(self, key, values, view_settings, parent=None):
        self.key = key
        self.view_settings = view_settings
        global_settings = sublime.load_settings('LaTeXTools.sublime-settings')

        if parent is not None:
            self.values = parent.values
            self.values.update(values)
        else:
            values = {}
            for s in (
                global_settings.get(self.key, {}),
                global_settings.get(sublime.platform(), {}).get(self.key, {}),
                global_settings.get(self.key, {}).get(sublime.platform(), {}),
                view_settings.get(self.key, {}),
                view_settings.get(sublime.platform(), {}).get(self.key, {}),
                view_settings.get(self.key, {}).get(sublime.platform(), {}),
                values
            ):
                if isinstance(s, dict) or isinstance(s, sublime.Settings):
                    for key in s:
                        if key not in ('windows', 'linux', 'osx') or \
                                not isinstance(s[key], dict):
                            values[key] = s[key]
            self.values = values

    def get(self, key, default=None):
        try:
            result = self.values.get(key)
        except KeyError:
            result = None

        if result is None:
            result = default

        if isinstance(result, dict) or isinstance(result, sublime.Settings):
            result = PlatformSettingsWrapper(key, result, self.view_settings, self)

        return result

    def __getitem__(self, key):
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return repr(self.values)


def get_platform_setting(setting, default=None):
    global_settings = sublime.load_settings('LaTeXTools.sublime-settings')
    try:
        view_settings = sublime.active_window().active_view().settings()
    except AttributeError:
        # no view defined
        view_settings = {}

    platform = sublime.platform()

    result = None

    platform_settings = view_settings.get(platform, {})
    result = platform_settings.get(setting)

    if result is None:
        result = view_settings.get(setting)

    if result is None:
        platform_settings = global_settings.get(platform, {})
        result = platform_settings.get(setting)

        if result is None:
            result = global_settings.get(setting)

    if result is None:
        result = default

    if isinstance(result, sublime.Settings) or isinstance(result, dict):
        result = PlatformSettingsWrapper(setting, result, view_settings)

    return result

# define get_setting
get_setting = get_platform_setting
