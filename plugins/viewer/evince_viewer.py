from __future__ import annotations
import stat
import sublime

from pathlib import Path
from typing import cast

from ...latextools.utils.external_command import check_call
from ...latextools.utils.external_command import check_output
from ...latextools.utils.external_command import external_command
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from .base_viewer import BaseViewer

__all__ = ["EvinceViewer"]


class EvinceViewer(BaseViewer):

    _cached_python = None

    @property
    def _evince_folder(self) -> Path:
        script_dir = Path(sublime.cache_path()) / "LaTeXTools" / "viewer" / "evince"
        script_dir.mkdir(parents=True, exist_ok=True)

        # extract scripts to cache dir and run them from there
        for script_name in ("backward_search", "forward_search", "sync"):
            script_file = script_dir / script_name
            if not script_file.exists():
                try:
                    data = (
                        sublime.load_binary_resource(
                            f"Packages/LaTeXTools/plugins/viewer/evince/{script_name}"
                        )
                        .replace(b"\r\n", b"\n")
                        .replace(b"\r", b"\n")
                    )
                except FileNotFoundError:
                    sublime.error_message(
                        f"Cannot find required script '{script_name}'\n"
                        "for 'evince' viewer in LaTeXTools package."
                    )
                    continue

                script_file.write_bytes(data)
                script_file.chmod(script_file.stat().st_mode | stat.S_IXUSR)

        return script_dir

    def _is_evince_running(self, pdf_file: str) -> bool:
        try:
            return f"evince {pdf_file}" in check_output(["ps", "xv"], use_texpath=False)
        except Exception:
            return False

    @property
    def _python_binary(self) -> str:
        linux_settings = cast(dict, get_setting("linux", {}))
        python = linux_settings.get("python")
        if python and isinstance(python, str):
            return python

        if self._cached_python is None:
            try:
                check_call(["python3", "-c", "import dbus"], use_texpath=False)
                self._cached_python = "python3"
            except Exception:
                try:
                    check_call(["python", "-c", "import dbus"], use_texpath=False)
                    self._cached_python = "python"
                except Exception:
                    sublime.error_message(
                        "Cannot find a valid Python interpreter.\n"
                        "Please set the python setting in your LaTeXTools settings."
                    )
                    # exit the viewer process
                    raise RuntimeError("Cannot find a valid python interpreter!")

        return self._cached_python

    def forward_sync(self, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        viewer_settings = cast(dict, get_setting("viewer_settings", {}))
        bring_evince_forward = viewer_settings.get("bring_evince_forward", False)
        keep_focus = kwargs.get("keep_focus", True)
        evince_folder = self._evince_folder
        python_binary = self._python_binary

        def forward_search():
            external_command(
                [python_binary, "./forward_search", pdf_file, str(line), tex_file],
                cwd=evince_folder,
                use_texpath=False,
            )

        if bring_evince_forward or not keep_focus or not self._is_evince_running(pdf_file):
            external_command(
                ["/bin/sh", "./sync", python_binary, get_sublime_exe(), pdf_file],
                cwd=evince_folder,
                use_texpath=False,
            )
            if keep_focus:
                self.focus_st()

            linux_settings = cast(dict, get_setting("linux", {}))
            sync_wait = linux_settings.get("sync_wait", 1.0)
            sublime.set_timeout(forward_search, int(1000 * sync_wait))

        else:
            forward_search()

    def view_file(self, pdf_file: str, **kwargs) -> None:
        keep_focus = kwargs.get("keep_focus", True)
        if keep_focus and self._is_evince_running(pdf_file):
            return

        external_command(
            ["/bin/sh", "./sync", self._python_binary, get_sublime_exe(), pdf_file],
            cwd=self._evince_folder,
            use_texpath=False,
        )
        if keep_focus:
            self.focus_st()

    def supports_platform(self, platform: str) -> bool:
        return platform == "linux"

    def supports_keep_focus(self) -> bool:
        return True
