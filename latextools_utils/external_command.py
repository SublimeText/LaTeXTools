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
#   update_env() - takes two dict-like objects and updates first with the
#       values from the second. It should be OS-encoding safe on ST2 which
#       does not automatically handle this.
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

import sublime

import os
import re
import sys
from shlex import split

import subprocess
from subprocess import Popen, PIPE, STDOUT, CalledProcessError

try:
    from latextools_utils.settings import get_setting
    from latextools_utils.system import which
    from latextools_utils.utils import run_on_main_thread
except ImportError:
    from .settings import get_setting
    from .system import which
    from .utils import run_on_main_thread

if sys.version_info < (3,):
    from pipes import quote

    def expand_vars(texpath):
        return os.path.expandvars(texpath).encode(sys.getfilesystemencoding())

    def update_env(old_env, new_env):
        encoding = sys.getfilesystemencoding()
        old_env.update(
            dict((k.encode(encoding), v) for (k, v) in new_env.items())
        )

    # reraise implementation from 6
    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")

    strbase = basestring
else:
    from imp import reload
    from shlex import quote

    def expand_vars(texpath):
        return os.path.expandvars(texpath)

    def update_env(old_env, new_env):
        old_env.update(new_env)

    # reraise implementation from 6
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    strbase = str

_ST3 = sublime.version() >= '3000'

__all__ = ['external_command', 'execute_command', 'check_call', 'check_output',
           'get_texpath', 'update_env']


def get_texpath():
    '''
    Returns the texpath setting with any environment variables expanded
    '''
    def _get_texpath():
        try:
            texpath = get_setting(sublime.platform(), {}).get('texpath')
        except AttributeError:
            # hack to reload this module in case the calling module was
            # reloaded
            exc_info = sys.exc_info
            try:
                reload(sys.modules[get_texpath.__module__])
                texpath = get_setting(sublime.platform(), {}).get('texpath')
            except:
                reraise(*exc_info)

        return expand_vars(texpath) if texpath is not None else None

    # ensure _get_texpath() is run in a thread-safe manner
    return run_on_main_thread(_get_texpath, default_value=None)


# marker object used to indicate default behaviour
# (avoid overwrite while module reloads)
if "__sentinel__" not in globals():
    __sentinel__ = object()


# wrapper to handle common logic for executing subprocesses
def external_command(command, cwd=None, shell=False, env=None,
                     stdin=__sentinel__, stdout=__sentinel__,
                     stderr=__sentinel__, preexec_fn=None,
                     use_texpath=True, show_window=False):
    '''
    Takes a command object to be passed to subprocess.Popen.

    Returns a subprocess.Popen object for the corresponding process.

    Raises OSError if command not found
    '''
    if command is None:
        raise ValueError('command must be a string or list of strings')

    _env = dict(os.environ)

    if use_texpath:
        _env['PATH'] = get_texpath() or os.environ['PATH']

    if env is not None:
        update_env(_env, env)

    # if command is a string rather than a list, convert it to a list
    # unless shell is set to True on a non-Windows platform
    if (
        (shell is False or sublime.platform() == 'windows') and
        isinstance(command, strbase)
    ):
        if sys.version_info < (3,):
            command = str(command)

        command = split(command)

        if sys.version_info < (3,):
            command = [unicode(c) for c in command]
    elif (
        shell is True and sublime.platform() != 'windows' and
        (isinstance(command, list) or isinstance(command, tuple))
    ):
        command = u' '.join(command)

    # Windows-specific adjustments
    startupinfo = None
    if sublime.platform() == 'windows':
        # ensure console window doesn't show
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        if show_window:
            startupinfo.wShowWindow = 1

        if not os.path.isabs(command[0]):
            _command = which(
                command[0], path=_env['PATH'] or os.environ['PATH']
            )

            if _command:
                command[0] = _command

        # encode cwd in the file system encoding; this is necessary to support
        # some non-ASCII paths; see PR #878. Thanks to anamewing for the
        # suggested fix
        if not _ST3 and cwd:
            cwd = cwd.encode(sys.getfilesystemencoding())

    if stdin is __sentinel__:
        stdin = None

    if stdout is __sentinel__:
        stdout = None

    if stderr is __sentinel__:
        stderr = None

    try:
        print(u'Running "{0}"'.format(u' '.join([quote(s) for s in command])))
    except UnicodeError:
        try:
            print(u'Running "{0}"'.format(command))
        except:
            pass

    p = Popen(
        command,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        startupinfo=startupinfo,
        preexec_fn=preexec_fn,
        shell=shell,
        env=_env,
        cwd=cwd
    )

    return p


def execute_command(command, cwd=None, shell=False, env=None,
                    stdin=__sentinel__, stdout=__sentinel__,
                    stderr=__sentinel__, preexec_fn=None,
                    use_texpath=True, show_window=False):
    '''
    Takes a command to be passed to subprocess.Popen and runs it. This is
    similar to subprocess.call().

    Returns a tuple consisting of
        (return_code, stdout, stderr)

    By default stderr is redirected to stdout, so stderr will normally be
    blank. This can be changed by calling execute_command with stderr set
    to subprocess.PIPE or any other valid value.

    Raises OSError if the executable is not found
    '''
    def convert_stream(stream):
        if stream is None:
            return u''
        else:
            return u'\n'.join(
                re.split(r'\r?\n', stream.decode('utf-8', 'ignore').rstrip())
            )

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
        show_window=show_window
    )

    stdout, stderr = p.communicate()
    return (
        p.returncode,
        convert_stream(stdout),
        convert_stream(stderr)
    )


def check_call(command, cwd=None, shell=False, env=None,
               stdin=__sentinel__, stdout=__sentinel__,
               stderr=__sentinel__, preexec_fn=None,
               use_texpath=True, show_window=False):
    '''
    Takes a command to be passed to subprocess.Popen.

    Raises CalledProcessError if the command returned a non-zero value
    Raises OSError if the executable is not found

    This is pretty much identical to subprocess.check_call(), but
    implemented here to take advantage of LaTeXTools-specific tooling.
    '''
    # since we don't do anything with the output, by default just ignore it
    if stdout is __sentinel__:
        stdout = open(os.devnull, 'w')
    if stderr is __sentinel__:
        stderr = open(os.devnull, 'w')

    returncode, stdout, stderr = execute_command(
        command,
        cwd=cwd,
        shell=shell,
        env=env,
        stdin=stdin,
        stderr=stderr,
        preexec_fn=preexec_fn,
        use_texpath=use_texpath,
        show_window=show_window
    )

    if returncode:
        e = CalledProcessError(
            returncode,
            command
        )
        raise e

    return 0


def check_output(command, cwd=None, shell=False, env=None,
                 stdin=__sentinel__, stderr=__sentinel__,
                 preexec_fn=None, use_texpath=True,
                 show_window=False):
    '''
    Takes a command to be passed to subprocess.Popen.

    Returns the output if the command was successful.

    By default stderr is redirected to stdout, so this will return any output
    to either stream. This can be changed by calling execute_command with
    stderr set to subprocess.PIPE or any other valid value.

    Raises CalledProcessError if the command returned a non-zero value
    Raises OSError if the executable is not found

    This is pretty much identical to subprocess.check_output(), but
    implemented here since it is unavailable in Python 2.6's library.
    '''
    returncode, stdout, stderr = execute_command(
        command,
        cwd=cwd,
        shell=shell,
        env=env,
        stdin=stdin,
        stderr=stderr,
        preexec_fn=preexec_fn,
        use_texpath=use_texpath,
        show_window=show_window
    )

    if returncode:
        e = CalledProcessError(
            returncode,
            command
        )
        e.output = stdout
        e.stderr = stderr
        raise e

    return stdout
