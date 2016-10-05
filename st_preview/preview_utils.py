import os
import shutil
import subprocess
import threading
import time

import sublime


from ..latextools_utils import cache, get_setting


_lt_settings = {}


def plugin_loaded():
    global _lt_settings
    _lt_settings = sublime.load_settings("LaTeXTools.sublime-settings")


def convert_installed():
    """Return whether ImageMagick/convert is available in the PATH."""
    if hasattr(convert_installed, "result"):
        return convert_installed.result

    convert_installed.result = shutil.which("convert") is not None
    return convert_installed.result


startupinfo = None
if sublime.platform() == "windows":
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def call_shell_command(command):
    """Call the command with shell=True and wait for it to finish."""
    subprocess.Popen(command,
                     shell=True,
                     startupinfo=startupinfo).wait()


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


_last_delete_try = {}


def try_delete_temp_files(key, temp_path):
    try:
        last_try = _last_delete_try[key]
    except KeyError:
        try:
            last_try = cache.read_global("preview_image_temp_delete")
        except:
            last_try = 0
        _last_delete_try[key] = last_try

    max_remaining_size = get_setting(key + "_temp_size", 50, view={})
    period = get_setting("preview_temp_delete_period", 24, view={})

    # if the period is negative don't clear automatically
    if period < 0:
        return

    # convert the units
    max_remaining_size *= 10**6  # MB -> B
    period *= 60 * 60  # h -> s

    # the remaining size as tenth of the cache size
    max_remaining_size /= 10.

    if time.time() <= last_try + period:
        return
    cache.write_global(key + "_temp_delete", last_try)

    tr = threading.Thread(
        target=lambda: delete_temp_files(temp_path, max_remaining_size))
    tr.start()


def _temp_folder_size(temp_path):
    size = 0
    for file_name in os.listdir(temp_path):
        file_path = os.path.join(temp_path, file_name)
        if os.path.isfile(file_path):
            size += os.path.getsize(file_path)
    return size


def _modified_time(file_path):
    try:
        mtime = os.path.getmtime(file_path)
    except:
        mtime = 0
    return mtime


def delete_temp_files(temp_path, max_remaining_size, total_size=None,
                      delete_all=False):
    if total_size is None and not delete_all:
        total_size = _temp_folder_size(temp_path)
    if total_size <= max_remaining_size:
        return

    del_files = [
        os.path.join(temp_path, file_name)
        for file_name in os.listdir(temp_path)
    ]
    # sort the delete files by their modification time
    del_files.sort(key=_modified_time, reverse=True)

    # delete the files until the max boundary is reached
    # oldest files first
    while del_files and (delete_all or total_size > max_remaining_size):
        file_path = del_files.pop()
        if os.path.isfile(file_path):
            total_size -= os.path.getsize(file_path)
            os.remove(file_path)
