# This module provides tools for running external commands.
# It is mainly a wrapper around subprocess calls with some defaults
# specific to LaTeXTools. In particular:
#
#  * it executes commands using the PATH defined by the texpath setting
#  * STDOUT is set to PIPE
#  * it redirects STDERR to STDOUT
#  * it hides the console window on Windows
#
# All of these, except hiding the console window, can be overridden via
# parameters passed to the method. The point is to simplify running things
# the way we normally do.
#
# All of the above can be overridden using optional parameters
#
# It provides six functions:
#   get_texpath() - returns the user configured texpath, properly encoded with
#       any environment variables expanded
#   external_command() - essentially the equivalent of subprocess.Popen()
#       provides the greatest degree of flexibility
#   execute_command() - calls external_command() and then
#       subprocess.communicate(), returning the returncode, stdout and stderr
#       output
#   check_call() - a version of subprocess.check_call() implemented on top of
#       execute_command()
#   check_output() - a version of subprocess.check_output() implemented on top
#       of execute_command()
#
# In addition to a subset of standard Popen parameters, all the functions built
# on external_command() accept a `use_texpath` parameter which indicates
# whether or not to run the executable with the PATH set to the current value
# of texpath.
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from shutil import which
from subprocess import PIPE, STDOUT, CalledProcessError, Popen, list2cmdline

import sublime

from .logging import logger
from .settings import get_setting

if TYPE_CHECKING:
    from typing import TypeAlias

    CommandLine: TypeAlias = list[str] | str

__all__ = [
    "PIPE",
    "STDOUT",
    "Popen",
    "check_call",
    "check_output",
    "execute_command",
    "external_command",
    "get_texpath",
]

__sentinel__ = object()

IS_WIN = sys.platform == "win32"


def shell_quote(s: str) -> str:
    if IS_WIN:
        s = re.sub(r"([&|<>?*])", R"^\1", s)
        return '"' + s.replace('"', '""') + '"' if " " in s else s
    return shlex.quote(s)


def get_texpath(view: sublime.View | None = None) -> str | None:
    """
    Get texpath setting with environment variables expanded.

    :param view:
        Optional `sublime.View` instance to read project-specific settings from.
        If `None` is provided, active view is used.
    """
    texpath = get_setting(sublime.platform(), {}, view).get("texpath")
    if texpath is not None:
        return os.path.expandvars(texpath)
    return None


def create_tex_env(
    env: dict[str, str] | None = None, view: sublime.View | None = None
) -> dict[str, str] | None:
    """
    Creates a tex environment.

    :param env:
        The base environment to replace $PATH in.
        If `None` is given, a copy of `os.environ` is used.

    :param view:
        Optional `sublime.View` instance to read project-specific settings from.
        If `None` is provided, active view is used.

    :returns:
        Dictionary with custom environment variables.
    """
    if texpath := get_texpath(view):
        if env is None:
            env = os.environ.copy()
        env["PATH"] = texpath
    return env


# wrapper to handle common logic for executing subprocesses
def external_command(
    cmd,
    cwd=None,
    shell=False,
    env=None,
    stdin=__sentinel__,
    stdout=__sentinel__,
    stderr=__sentinel__,
    preexec_fn=None,
    use_texpath=True,
    show_window=False,
):
    """
    Takes a command object to be passed to subprocess.Popen.

    Returns a subprocess.Popen object for the corresponding process.

    Raises OSError if command not found
    """
    if cmd is None:
        raise ValueError("command must be a string or list of strings")

    # Setup custom environment
    if use_texpath:
        env = create_tex_env(env)

    # Windows-specific adjustments
    startupinfo = None
    if IS_WIN and not show_window:
        # ensure console window doesn't show
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    if stdin is __sentinel__:
        stdin = None

    if stdout is __sentinel__:
        stdout = None

    if stderr is __sentinel__:
        stderr = None

    if shell:
        if IS_WIN:
            if isinstance(cmd, list):
                cmd = list2cmdline(cmd)
            elif not isinstance(cmd, str):
                raise TypeError(f"Invalid command type! '{cmd!r}' must be a 'str' or 'list'!")

            # make sure to run scripts with %SYSTEMROOT%\System32\cmd.exe
            comspec = os.path.join(os.environ.get("SystemRoot", ""), "System32", "cmd.exe")
            if not os.path.isabs(comspec):
                raise FileNotFoundError("cmd.exe not found!")

            cmd = f'{comspec} /c "{cmd}"'

        else:
            if isinstance(cmd, list):
                cmd = shlex.join(cmd)
            elif not isinstance(cmd, str):
                raise TypeError(f"Invalid command type! '{cmd!r}' must be a 'str' or 'list'!")

            # run scripts using bash on all platforms
            if sys.platform == "darwin":
                # use login-shell to ensure users' env variables are picked up
                # (borrowed from Default/exec.py)
                cmd = ["/usr/bin/env", "bash", "-l", "-c", cmd]
            else:
                cmd = ["/usr/bin/env", "bash", "-c", cmd]

    # If shell=False is specified, executed command is only looked up using
    # os.environ["PATH"]. Hence manually resolve location with custom env's PATH.
    elif isinstance(cmd, list) and env and not os.path.isabs(cmd[0]):
        cmd[0] = which(cmd[0], path=env.get("PATH")) or cmd[0]

    logger.debug(f"Running {cmd}")

    return Popen(
        cmd,
        cwd=cwd,
        env=env,
        bufsize=0,
        preexec_fn=preexec_fn,
        shell=False,
        startupinfo=startupinfo,
        stderr=stderr,
        stdin=stdin,
        stdout=stdout,
    )


def execute_command(
    command,
    cwd=None,
    shell=False,
    env=None,
    stdin=__sentinel__,
    stdout=__sentinel__,
    stderr=__sentinel__,
    preexec_fn=None,
    use_texpath=True,
    show_window=False,
):
    """
    Takes a command to be passed to subprocess.Popen and runs it. This is
    similar to subprocess.call().

    Returns a tuple consisting of
        (return_code, stdout, stderr)

    By default stderr is redirected to stdout, so stderr will normally be
    blank. This can be changed by calling execute_command with stderr set
    to subprocess.PIPE or any other valid value.

    Raises OSError if the executable is not found
    """

    def convert_stream(stream):
        if stream is None:
            return ""
        else:
            return "\n".join(re.split(r"\r?\n", stream.decode("utf-8", "ignore").rstrip()))

    if stdout is __sentinel__:
        stdout = PIPE

    if stderr is __sentinel__:
        stderr = STDOUT

    p = external_command(
        command,
        cwd=cwd,
        shell=shell,
        env=env,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        preexec_fn=preexec_fn,
        use_texpath=use_texpath,
        show_window=show_window,
    )

    stdout, stderr = p.communicate()
    return (p.returncode, convert_stream(stdout), convert_stream(stderr))


def check_call(
    command,
    cwd=None,
    shell=False,
    env=None,
    stdin=__sentinel__,
    stdout=__sentinel__,
    stderr=__sentinel__,
    preexec_fn=None,
    use_texpath=True,
    show_window=False,
):
    """
    Takes a command to be passed to subprocess.Popen.

    Raises CalledProcessError if the command returned a non-zero value
    Raises OSError if the executable is not found

    This is pretty much identical to subprocess.check_call(), but
    implemented here to take advantage of LaTeXTools-specific tooling.
    """
    # since we don't do anything with the output, by default just ignore it
    if stdout is __sentinel__:
        stdout = open(os.devnull, "w")
    if stderr is __sentinel__:
        stderr = open(os.devnull, "w")

    returncode, stdout, stderr = execute_command(
        command,
        cwd=cwd,
        shell=shell,
        env=env,
        stdin=stdin,
        stderr=stderr,
        preexec_fn=preexec_fn,
        use_texpath=use_texpath,
        show_window=show_window,
    )

    if returncode:
        e = CalledProcessError(returncode, command)
        raise e

    return 0


def check_output(
    command,
    cwd=None,
    shell=False,
    env=None,
    stdin=__sentinel__,
    stderr=__sentinel__,
    preexec_fn=None,
    use_texpath=True,
    show_window=False,
):
    """
    Takes a command to be passed to subprocess.Popen.

    Returns the output if the command was successful.

    By default stderr is redirected to stdout, so this will return any output
    to either stream. This can be changed by calling execute_command with
    stderr set to subprocess.PIPE or any other valid value.

    Raises CalledProcessError if the command returned a non-zero value
    Raises OSError if the executable is not found

    This is pretty much identical to subprocess.check_output(), but
    implemented here since it is unavailable in Python 2.6's library.
    """
    returncode, stdout, stderr = execute_command(
        command,
        cwd=cwd,
        shell=shell,
        env=env,
        stdin=stdin,
        stderr=stderr,
        preexec_fn=preexec_fn,
        use_texpath=use_texpath,
        show_window=show_window,
    )

    if returncode:
        e = CalledProcessError(returncode, command)
        e.output = stdout
        e.stderr = stderr
        raise e

    return stdout
