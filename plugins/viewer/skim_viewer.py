from __future__ import annotations
import stat
import sublime

from pathlib import Path

from ...latextools.utils.external_command import check_output
from ...latextools.utils.external_command import external_command

from .base_viewer import BaseViewer

__all__ = ["SkimViewer"]


class SkimViewer(BaseViewer):

    def forward_sync(self, pdf_file: str, tex_file: str, line: int, col: int, **kwargs) -> None:
        keep_focus = kwargs.get("keep_focus", True)
        skim_app = Path("/Applications/Skim.app")

        if not skim_app.exists():
            skim_app = Path(
                check_output(
                    [
                        "osascript",
                        "-e",
                        'POSIX path of (path to app id "net.sourceforge.skim-app.skim")',
                    ],
                    use_texpath=False,
                )
            )

        command = [str(skim_app / "Contents" / "SharedSupport" / "displayline"), "-r"]

        if keep_focus:
            command.append("-g")

        command += [str(line), pdf_file, tex_file]

        external_command(command, use_texpath=False)
        if keep_focus:
            self.focus_st()

    def view_file(self, pdf_file: str, **kwargs) -> None:
        keep_focus = kwargs.get("keep_focus", True)
        script_dir = Path(sublime.cache_path()) / "LaTeXTools" / "viewer" / "skim"
        script_dir.mkdir(parents=True, exist_ok=True)
        script_file = script_dir / "displayfile"
        if not script_file.exists():
            try:
                data = (
                    sublime.load_binary_resource(
                        f"Packages/LaTeXTools/plugins/viewer/skim/displayfile"
                    )
                    .replace(b"\r\n", b"\n")
                    .replace(b"\r", b"\n")
                )
            except FileNotFoundError:
                sublime.error_message(
                    "Cannot find required scripts\nfor 'skim' viewer in LaTeXTools package."
                )
                return

            script_file.write_bytes(data)
            script_file.chmod(script_file.stat().st_mode | stat.S_IXUSR)

        command = ["/bin/sh", script_file, "-r"]

        if keep_focus:
            command.append("-g")

        command.append(pdf_file)

        external_command(command, use_texpath=False)
        if keep_focus:
            self.focus_st()

    def supports_keep_focus(self) -> bool:
        return True

    def supports_platform(self, platform: str) -> bool:
        return platform == "osx"


def latextools_plugin_loaded():
    # ensure to work with up-to-date scripts after package updates
    from shutil import rmtree
    script_dir = Path(sublime.cache_path()) / "LaTeXTools" / "viewer" / "skim"
    rmtree(script_dir, ignore_errors=True)
