import os

import sublime

from ...latextools.utils.external_command import check_output
from ...latextools.utils.external_command import external_command

from .base_viewer import BaseViewer

__all__ = ["SkimViewer"]


class SkimViewer(BaseViewer):

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)
        path_to_skim = "/Applications/Skim.app"

        if not os.path.exists(path_to_skim):
            path_to_skim = check_output(
                [
                    "osascript",
                    "-e",
                    'POSIX path of (path to app id "net.sourceforge.skim-app.skim")',
                ],
                use_texpath=False,
            )

        command = [
            os.path.join(path_to_skim, "Contents", "SharedSupport", "displayline"),
            "-r",
        ]

        if keep_focus:
            command.append("-g")

        command += [str(line), pdf_file, tex_file]

        external_command(command, use_texpath=False)

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)
        script_dir = os.path.join(sublime.cache_path(), "LaTeXTools", "viewer", "skim")
        script_file = os.path.join(script_dir, "displayfile")
        if not os.path.exists(script_file):
            try:
                data = sublime.load_binary_resource(
                    f"Packages/LaTeXTools/plugins/viewer/skim/displayfile"
                )
            except FileNotFoundError:
                sublime.error_message(
                    "Cannot find required scripts\n"
                    "for 'skim' viewer in LaTeXTools package."
                )
            else:
                with open(script_file, "wb") as fobj:
                     fobj.write(data)

        command = ["/bin/sh", script_file, "-r"]

        if keep_focus:
            command.append("-g")

        command.append(pdf_file)

        external_command(command, use_texpath=False)

    def supports_keep_focus(self):
        return True

    def supports_platform(self, platform):
        return platform == "osx"
