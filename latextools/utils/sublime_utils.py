from __future__ import annotations

import re

from pathlib import Path
from typing import cast

import sublime

from .settings import get_setting

# used by get_sublime_exe()
SUBLIME_VERSION = re.compile(r"Build (\d{4})", re.UNICODE)


def focus_st():
    """
    Bring active Sublime Text window to front and (re-)focus it.
    """
    if get_setting("disable_focus_hack", False):
        return

    platform = sublime.platform()
    plat_settings = cast(dict, get_setting(platform, {}))
    wait_time = cast(float, plat_settings.get("keep_focus_delay", 1.0))

    def focus():
        active_window = sublime.active_window()
        if active_window:
            active_window.bring_to_front()

    sublime.set_timeout(focus, int(wait_time * 1000))


def get_sublime_exe() -> Path:
    """
    Get the full path to the currently executing Sublime instance.

    Note that the value will always be overridden by the "sublime_executable"
    setting if one is provided
    """
    platform = sublime.platform()
    plat_settings = cast(dict, get_setting(platform, {}))
    sublime_executable = plat_settings.get("sublime_executable")
    if sublime_executable:
        return Path(sublime_executable)

    # we cache the results of the other checks, if possible
    if hasattr(get_sublime_exe, "result"):
        return get_sublime_exe.result

    # on linux, subl is just a script pointing to sublime_text executable,
    # hence directly use the executable to call commands
    executable = Path(sublime.executable_path())

    # on osx, the executable does not function the same as subl
    if platform == "osx":
        executable = executable.parent.parent / "SharedSupport" / "bin" / "subl"

    # on windows, subl.exe must be called to re-focuses last active window
    # calling sublime_text.exe opens a new window by default
    elif platform == "windows":
        executable = executable.parent / "subl.exe"

    get_sublime_exe.result = executable
    return get_sublime_exe.result


def get_project_file_name(view: sublime.View) -> str | None:
    window = view.window()
    if window:
        return window.project_file_name()
    return None
