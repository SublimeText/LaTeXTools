# This module provides utilities for working with Sublime Text
# orignally, it existed to map difference between ST2 and ST3, but some of
# the functionality is still useful
import os
import re
from shutil import which

import sublime

from .external_command import check_output
from .external_command import external_command
from .logging import logger
from .settings import get_setting

# used by get_sublime_exe()
SUBLIME_VERSION = re.compile(r"Build (\d{4})", re.UNICODE)


# returns the focus to ST
# NB its probably good to call this as little as possible since focus-stealing
# annoys people
def focus_st():
    if get_setting("disable_focus_hack", False):
        return

    sublime_command = get_sublime_exe()

    if sublime_command is not None:
        platform = sublime.platform()
        plat_settings = get_setting(platform, {})
        wait_time = plat_settings.get("keep_focus_delay", 0.5)

        # osx is a special snowflake
        if platform == "osx":
            # sublime_command should be /path/to/Sublime Text.app/Contents/...
            sublime_app = sublime_command.split("/Contents/")[0]

            def keep_focus():
                external_command(
                    [
                        "osascript",
                        "-e",
                        'tell application "{0}" to activate'.format(sublime_app),
                    ],
                    use_texpath=False,
                )

        else:

            def keep_focus():
                external_command([sublime_command], use_texpath=False)

        sublime.set_timeout_async(keep_focus, int(wait_time * 1000))


# returns the path to the sublime executable
def get_sublime_exe():
    """
    Utility function to get the full path to the currently executing
    Sublime instance.

    Note that the value will always be overridden by the "sublime_executable"
    setting if one is provided
    """
    platform = sublime.platform()

    sublime_executable = get_setting(platform, {}).get("sublime_executable")
    if sublime_executable:
        return sublime_executable

    # we cache the results of the other checks, if possible
    if hasattr(get_sublime_exe, "result"):
        return get_sublime_exe.result

    executable = sublime.executable_path()

    # on osx, the executable does not function the same as subl
    if platform == "osx":
        executable = os.path.normpath(
            os.path.join(os.path.dirname(executable), "..", "SharedSupport", "bin", "subl")
        )

    # on linux, it is preferable to use subl if it points to the
    # correct version see issue #710 for a case where this is useful
    elif platform == "linux":
        if not executable.endswith("subl"):
            subl = which("subl")
            if subl is not None:
                try:
                    m = SUBLIME_VERSION.search(check_output("subl -v", use_texpath=False))

                    if m and m.group(1) == sublime.version():
                        executable = subl
                except Exception:
                    pass

    # on windows, subl.exe must be called to re-focuses last active window
    # calling sublime_text.exe opens a new window by default
    elif platform == "windows":
        executable = os.path.join(os.path.dirname(executable), "subl.exe")

    if executable is None:
        logger.error(
            "Cannot determine the path to your Sublime installation. Please "
            'set the "sublime_executable" setting in your settings for your '
            "platform."
        )

    get_sublime_exe.result = executable
    return get_sublime_exe.result


def get_project_file_name(view):
    return view.window().project_file_name()
