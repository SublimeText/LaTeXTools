import shutil

import sublime


_ST3 = sublime.version() >= "3000"
if _ST3:
    from .latextools_utils import get_setting


_lt_settings = {}


def plugin_loaded():
    global _lt_settings
    _lt_settings = sublime.load_settings("LaTeXTools.sublime-settings")


def convert_installed():
    """Return whether ImageMagick/onvert is available in the PATH."""
    if hasattr(convert_installed, "result"):
        return convert_installed.result

    convert_installed.result = shutil.which("convert") is not None
    return convert_installed.result


class SettingsListener(object):
    """
    Required class attributes:
    - view: the view to listen to
    - attr_updates: these attributes are listened on the view and the
        lt settings
    - lt_attr_updates: these attributes are listened on the lt settings
    """

    def _init_list_add_on_change(self, key, view_attr, lt_attr):
        view = self.view
        _lt_settings.add_on_change(
            key, lambda: self._on_setting_change(False))
        self.view.settings().add_on_change(
            key, lambda: self._on_setting_change(True))
        self.v_attr_updates = view_attr
        self.lt_attr_updates = lt_attr

        for attr_name, d in self.v_attr_updates.items():
            settings_name = d["setting"]
            self.__dict__[attr_name] = get_setting(settings_name, view=view)

        for attr_name, d in self.lt_attr_updates.items():
            if attr_name in self.__dict__:
                continue
            settings_name = d["setting"]
            self.__dict__[attr_name] = _lt_settings.get(settings_name)

        _lt_settings.add_on_change(
            key, lambda: self._on_setting_change(False))
        self.view.settings().add_on_change(
            key, lambda: self._on_setting_change(True))

    def _on_setting_change(self, for_view):
        settings = self.view.settings() if for_view else _lt_settings
        attr_updates = (self.v_attr_updates if for_view
                        else self.lt_attr_updates)
        for attr_name in attr_updates.keys():
            attr = attr_updates[attr_name]
            settings_name = attr["setting"]
            value = settings.get(settings_name)
            if for_view and value is None:
                continue
            if self.__dict__[attr_name] == value:
                continue
            if not for_view and self.view.settings().has(settings_name):
                continue
            # update the value and call the after function
            self.__dict__[attr_name] = value
            sublime.set_timeout_async(attr["call_after"])
            break
