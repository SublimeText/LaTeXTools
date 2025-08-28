from __future__ import annotations
from pathlib import Path
from typing import cast
import shutil
import stat
import sublime
import sublime_plugin

from ...latextools.utils import sublime_utils as st_utils
from ...latextools.utils.external_command import external_command, check_call, Popen
from ...latextools.utils.logging import logger
from ...latextools.utils.settings import get_setting

from .base_viewer import BaseViewer

__all__ = ["LatextoolsDbusViewerListener", "EvinceViewer", "XreaderViewer"]


# let registered processes survife module reloading
if "_monitor_processes" not in globals():
    _monitor_processes = {}


class BaseDBusViewer(BaseViewer):
    _app_dbus_name = ""
    _app_command = ""
    _cached_python = None

    @classmethod
    def get_python_exe(cls) -> str:
        """
        Gets the python executable which can import `dbus` module.

        :returns:   The python executable.
        """
        if cls._cached_python is None:
            python = shutil.which("python3")
            try:
                check_call([python, "-c", "import dbus"], use_texpath=False)
            except Exception:
                python = shutil.which("python")
                try:
                    check_call([python, "-c", "import dbus"], use_texpath=False)
                except Exception:
                    sublime.error_message(
                        "Cannot find a valid Python interpreter with 'dbus' support.\n"
                        "Please set the python setting in your LaTeXTools settings."
                    )
                    # exit the viewer process
                    raise RuntimeError("Cannot find a valid python interpreter!")

            cls._cached_python = python

        return cls._cached_python

    @classmethod
    def bring_to_front(cls, pdf_file: str) -> None:
        """
        Bring viewer application to front by executing it.

        :param pdf_file:
            The pdf file the displaying window to bring to front for.
        """
        if cls.viewer_settings().get("bring_to_front", False):
            logger.debug(f"Bring {cls._app_command} to front.")
            external_command(
                [cls._app_command, pdf_file],
                shell=False,
                stdin=None,
                stdout=None,
                stderr=None,
                use_texpath=False,
            )

    @classmethod
    def run_sync(
        cls,
        pdf_file: str,
        spawn: bool = False,
        forward_sync: str | None = None,
        backward_sync: bool = False,
    ) -> Popen | None:
        """
        Run dbus sync script.

        Starts dbus server for backward sync or passes forward sync command to viewer backend
        via `Packages/LaTeXTools/plugins/viewer/dbus/sync` script.

        :param pdf_file:
            Path to the pdf file to open
        :param spawn:
            If True, the pdf file will be opened if it wasn't already.
        :param forward_sync:
            If specified, path to the source tex file, optionally including line and column, to
            perform a forward synchronization (e.g. `my_tex_file.tex:42:1`)
        :param backward_sync:
            If True, the process will stay alive and monitor for backward sync from the viewer

        :returns:
            Popen object.
        """
        linux_settings = cast(dict, get_setting("linux", {}))

        # Determine python binary
        python = linux_settings.get("python")
        if not python:
            python = cls.get_python_exe()

        # Find the sync script
        script_dir = Path(sublime.cache_path(), "LaTeXTools", "viewer", "dbus")
        script_dir.mkdir(parents=True, exist_ok=True)
        script_file = script_dir / "sync"
        if not script_file.exists():
            try:
                data = (
                    sublime.load_binary_resource(f"Packages/LaTeXTools/plugins/viewer/dbus/sync")
                    .replace(b"\r\n", b"\n")
                    .replace(b"\r", b"\n")
                )
            except FileNotFoundError:
                sublime.error_message(
                    "Cannot find required scripts\nfor 'dbus' viewer in LaTeXTools package."
                )
                return None

            script_file.write_bytes(data)
            script_file.chmod(script_file.stat().st_mode | stat.S_IXUSR)

        command = [
            python,
            str(script_file),
            "--document",
            pdf_file,
            "--dbus-name",
            cls._app_dbus_name,
        ]
        if spawn:
            command.append("--spawn")
        if forward_sync is not None:
            command += [
                "--sync-wait",
                str(linux_settings.get("sync_wait", 0.5)),
                "--forward",
                str(forward_sync),
            ]
        if backward_sync:
            command += ["--backward", st_utils.get_sublime_exe(), "%f:%l:%c"]
        proc = external_command(
            command, shell=False, use_texpath=False, stdin=None, stdout=None, stderr=None
        )
        return proc

    @classmethod
    def is_monitor_process_running(cls, pdf_file: str) -> bool:
        """
        Determines if dbus server process for backward sync is running.

        :param pdf_file:
            The pdf file to search a running backward sync server process for.

        :returns:
            True if monitor process running, False otherwise.
        """
        proc = _monitor_processes.get(pdf_file, None)
        # Poll the return code, if None, the process is still running
        result = proc is not None and proc.poll() is None
        if result:
            logger.debug(f"{cls._app_command} monitoring process is running at {proc.pid}.")
        else:
            logger.debug(f"{cls._app_command} monitoring process is not running.")
        return result

    @classmethod
    def run_monitor_process(cls, pdf_file: str, forward_sync: str | None = None) -> None:
        """
        Replaces the existing monitor process (if present) with a new one, launched in such a way
        to have backward sync enabled. Optionally performs also a forward sync.

        :param pdf_file:
            Path to the pdf file
        :param forward_sync:
            If specified, path to the source tex file, optionally including line and column,
            to perform a forward synchronization (e.g. `my_tex_file.tex:42:1`)
        """
        logger.debug(f"Start {cls._app_command} monitoring process.")

        # Terminate existing monitor process
        old_process = cls.terminate_monitor_process(pdf_file)
        # Run and replace the monitor process
        _monitor_processes[pdf_file] = cls.run_sync(
            pdf_file,
            spawn=True,
            forward_sync=forward_sync,
            backward_sync=True,
        )

    @classmethod
    def terminate_monitor_process(cls, pdf_file: str) -> Popen | None:
        """
        Terminate monitoring process for specified pdf file.

        :param pdf_file:
            The pdf file to terminate a possibly running monitoring process for.

        :returns:
            A `subprocess.Popen` object of terminated process or `None`.
        """
        proc = _monitor_processes.get(pdf_file, None)
        if proc is not None and proc.poll() is None:
            proc.terminate()
        else:
            proc = None

        return proc

    @classmethod
    def terminate_monitor_processes(cls) -> None:
        """
        Terminate all remaining monitoring processes.
        """
        procs = tuple(_monitor_processes.values())
        _monitor_processes.clear()

        for proc in procs:
            if proc is not None and proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass

    @classmethod
    def forward_sync(cls, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        forward_sync_target = f"{tex_file}:{line}:{col}"

        if not cls.is_monitor_process_running(pdf_file):
            # start new dbus monitoring process for backward sync
            cls.run_monitor_process(pdf_file, forward_sync_target)
        else:
            cls.bring_to_front(pdf_file)
            # call into running dbus process to navigate to desired location in PDF
            cls.run_sync(pdf_file, spawn=True, forward_sync=forward_sync_target)

        if kwargs.get("keep_focus", True):
            cls.focus_st()

    @classmethod
    def view_file(cls, pdf_file: str, **kwargs) -> None:
        if not cls.is_monitor_process_running(pdf_file):
            cls.run_monitor_process(pdf_file)
        else:
            cls.bring_to_front(pdf_file)
        if kwargs.get("keep_focus", True):
            cls.focus_st()

    @classmethod
    def supports_platform(cls, platform: str) -> bool:
        return platform == "linux"

    @classmethod
    def supports_keep_focus(cls) -> bool:
        return True


class EvinceViewer(BaseDBusViewer):
    _app_dbus_name = "org.gnome.evince"
    _app_command = shutil.which("evince")
    if _app_command is not None:
        if Path(_app_command).resolve().name == "xreader":
            logger.info("On this platform, Xreader provides Evince, will use Xreader DBus name")
            _app_dbus_name = "org.x.reader"


class XreaderViewer(BaseDBusViewer):
    _app_dbus_name = "org.x.reader"
    _app_command = shutil.which("xreader")


class LatextoolsDbusViewerListener(sublime_plugin.EventListener):
    """
    Terminate all monitoring processes if ST is being exited.
    """

    def on_exit(self):
        BaseDBusViewer.terminate_monitor_processes()


def latextools_plugin_loaded():
    # ensure to work with up-to-date scripts after package updates
    script_dir = Path(sublime.cache_path(), "LaTeXTools", "viewer", "dbus")
    shutil.rmtree(script_dir, ignore_errors=True)


def latextools_plugin_unloaded():
    """
    Terminate all monitoring processes if plugin is being disabled.
    """
    BaseDBusViewer.terminate_monitor_processes()
