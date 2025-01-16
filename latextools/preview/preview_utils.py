import os
import re
import threading
import time
import traceback

import sublime

from shutil import which

from ..utils import cache
from ..utils.distro_utils import using_miktex
from ..utils.external_command import __sentinel__
from ..utils.external_command import check_output
from ..utils.external_command import execute_command
from ..utils.external_command import get_texpath
from ..utils.logging import logger
from ..utils.settings import get_setting

if sublime.platform() == "windows":
    import winreg
    import ctypes
    from ctypes import wintypes

    # wrapper for GetSystemDirectoryW
    def get_system_root():
        buffer = ctypes.create_unicode_buffer(wintypes.MAX_PATH + 1)
        ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
        return buffer.value


def _get_convert_command():
    if hasattr(_get_convert_command, "result"):
        return _get_convert_command.result

    texpath = get_texpath() or os.environ["PATH"]
    convert_cmd = which("magick", path=texpath) or which("convert", path=texpath) or ""

    # DO NOT RUN THE CONVERT COMMAND IN THE SYSTEM ROOT ON WINDOWS
    if sublime.platform() == "windows":
        sys_convert = os.path.join(get_system_root(), "convert.exe")
        if os.path.samefile(convert_cmd, sys_convert):
            return None

    _get_convert_command.result = convert_cmd
    return _get_convert_command.result


def convert_installed():
    """Return whether ImageMagick/convert is available in the PATH."""
    return _get_convert_command() is not None


def run_convert_command(args):
    """Executes ImageMagick convert or magick command as appropriate with the
    given args"""
    if not isinstance(args, list):
        raise TypeError("args must be a list")

    convert_command = _get_convert_command()
    if os.path.splitext(os.path.basename(convert_command))[0] == "magick":
        args.insert(0, convert_command)
        args.insert(1, "convert")
    else:
        args.insert(0, convert_command)

    execute_command(args, shell=sublime.platform() == "windows")


_GS_COMMAND = None
# on recent versions of TeXLive on Windows, the included Ghostscript
# is compiled without the necessary initiation files, so we need to make
# Ghostscript aware of the appropriate paths. This variable is used to do
# this, Any paths added to this variable will be added to the GS command
# (if GS_LIB is not set) as -I <path>
_GS_EXTRA_LIBRARY_PATHS = []
_GS_VERSION_LOCK = threading.Lock()
_GS_VERSION = None
_GS_VERSION_REGEX = re.compile(r"Ghostscript (?P<major>\d+)\.(?P<minor>\d{2})")


def _get_gs_command():
    global _GS_COMMAND, _GS_EXTRA_LIBRARY_PATHS
    if _GS_COMMAND is not None:
        return _GS_COMMAND

    # reset _GS_EXTRA_LIBRARY_PATHS as we only want to use thi
    # in limited cases
    _GS_EXTRA_LIBRARY_PATHS = []
    _GS_COMMAND = __get_gs_command()

    if _GS_COMMAND is None:
        return None

    # load the GS version on a background thread
    t = threading.Thread(target=_update_gs_version)
    t.daemon = True
    t.start()

    return _GS_COMMAND


def _update_gs_version():
    global _GS_VERSION
    with _GS_VERSION_LOCK:
        if _GS_VERSION is not None:
            return

        if _GS_COMMAND is None:
            return None

        try:
            raw_version = check_output([_GS_COMMAND, "-version"])
            m = _GS_VERSION_REGEX.search(raw_version)
            if m:
                _GS_VERSION = tuple(int(x) for x in m.groups())
        except Exception:
            logger.error("Error finding Ghostscript version for %s", _GS_COMMAND)
            traceback.print_exc()
            return None


# broken out to be called from system_check
def __get_gs_command():
    texpath = get_texpath() or os.environ["PATH"]
    if sublime.platform() == "windows":
        # use Ghostscript from the texpath if possible
        result = (
            which("gswin32c", path=texpath)
            or which("gswin64c", path=texpath)
            or which("gs", path=texpath)
        )

        # try to find Ghostscript from the registry
        if result is None:
            result = _get_gs_exe_from_registry()

        if result is None:
            if using_miktex():
                result = which("mgs", path=texpath)
            else:
                result = _get_tl_gs_path(texpath)
                if result is not None:
                    global _GS_EXTRA_LIBRARY_PATHS

                    _tlgs_path = os.path.normpath(os.path.join(os.path.dirname(result), ".."))

                    _GS_EXTRA_LIBRARY_PATHS = [
                        os.path.join(_tlgs_path, "Resource", "Init"),
                        os.path.join(_tlgs_path, "kanji"),
                    ]
    else:
        result = which("gs", path=texpath)

    return result


def _get_tl_gs_path(texpath):
    """Tries to find the gs installed by TeXLive"""
    pdflatex = which("pdflatex", path=texpath)
    if pdflatex is None:
        return None

    # assumed structure
    # texlive/<year>/
    tlgs_path = os.path.normpath(
        os.path.join(os.path.dirname(pdflatex), "..", "..", "tlpkg", "tlgs", "bin")
    )

    if not os.path.exists(tlgs_path):
        return None

    return which("gswin32c", path=tlgs_path) or which("gswin64c", path=tlgs_path)


def _get_gs_exe_from_registry():
    result = None
    hndl = None

    product_family = None
    major_version = -1
    minor_version = -1

    # find the most recent version of Ghostscript installed
    for product in ["GPL Ghostscript", "AFPL Ghostscript"]:
        try:
            hndl = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\{0}".format(product))

            try:
                for i in range(winreg.QueryInfoKey(hndl)[0]):
                    version = winreg.EnumKey(hndl, i)
                    try:
                        major, minor = map(int, version.split("."))
                        if major > major_version or (
                            major == major_version and minor > minor_version
                        ):
                            major_version = major
                            minor_version = minor
                            product_family = product
                    except ValueError:
                        continue
            finally:
                winreg.CloseKey(hndl)
        except OSError:
            continue

    if product_family is not None:
        try:
            hndl = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\{0}\\{1}.{2:02}".format(product_family, major_version, minor_version),
            )

            try:
                gs_path = os.path.dirname(winreg.QueryValue(hndl, "GS_DLL"))

                if gs_path is not None:
                    result = which("gswin32c", path=gs_path) or which("gswin64c", path=gs_path)
            finally:
                winreg.CloseKey(hndl)
        except OSError:
            logger.error("Could not find GS_DLL value for %s", product_family)

    return result


def ghostscript_installed():
    return _get_gs_command() is not None


def get_ghostscript_version():
    global _GS_VERSION
    with _GS_VERSION_LOCK:
        if _GS_VERSION is None:
            _update_gs_version()

        return _GS_VERSION if _GS_VERSION is not None else (-1, -1)


def run_ghostscript_command(args, stdout=__sentinel__, stderr=__sentinel__):
    """Executes a Ghostscript command with the given args"""
    if not isinstance(args, list):
        raise TypeError("args must be a list")

    # add some default args to run in quiet batch mode
    args.insert(0, _get_gs_command())
    # if there are any extra library paths to add; however, we do not want
    # to override the GS_LIB environment variable
    if "GS_LIB" not in os.environ:
        for p in _GS_EXTRA_LIBRARY_PATHS:
            args.insert(1, p)
            args.insert(1, "-I")
    args.insert(1, "-q")
    args.insert(1, "-dQUIET")
    args.insert(1, "-dNOPROMPT")
    args.insert(1, "-dNOPAUSE")
    args.insert(1, "-dBATCH")
    args.insert(1, "-dSAFER")

    return execute_command(
        args, shell=sublime.platform() == "windows", stdout=stdout, stderr=stderr
    )


_last_delete_try = {}


def try_delete_temp_files(key, temp_path):
    try:
        last_try = _last_delete_try[key]
    except KeyError:
        try:
            last_try = cache.read_global(key + "_temp_delete")
        except Exception:
            last_try = 0
        _last_delete_try[key] = time.time()

    cache_size = get_setting(key + "_temp_size", 50, view={})
    period = get_setting("preview_temp_delete_period", 24, view={})

    # if the period is negative don't clear automatically
    if period < 0:
        return

    # convert the units
    cache_size *= 10**6  # MB -> B
    period *= 60 * 60  # h -> s

    # the remaining size as tenth of the cache size
    max_remaining_size = cache_size / 10.0

    if time.time() <= last_try + period:
        return
    cache.write_global(key + "_temp_delete", last_try)

    tr = threading.Thread(
        target=lambda: delete_temp_files(temp_path, cache_size, max_remaining_size)
    )
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
    except Exception:
        mtime = 0
    return mtime


def delete_temp_files(temp_path, cache_size, max_remaining_size, total_size=None, delete_all=False):
    if total_size is None and not delete_all:
        total_size = _temp_folder_size(temp_path)
    if total_size <= cache_size:
        return

    del_files = [os.path.join(temp_path, file_name) for file_name in os.listdir(temp_path)]
    # sort the delete files by their modification time
    del_files.sort(key=_modified_time, reverse=True)

    # delete the files until the max boundary is reached
    # oldest files first
    while del_files and (delete_all or total_size > max_remaining_size):
        file_path = del_files.pop()
        if os.path.isfile(file_path):
            total_size -= os.path.getsize(file_path)
            os.remove(file_path)
