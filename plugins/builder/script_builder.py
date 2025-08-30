from __future__ import annotations
import os
import re
import sublime
import subprocess

from shlex import quote
from string import Template
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from ...latextools.utils.external_command import external_command
from ...latextools.utils.external_command import get_texpath

from .pdf_builder import PdfBuilder

__all__ = ["ScriptBuilder"]


class ScriptBuilder(PdfBuilder):
    """
    ScriptBuilder class

    Launch a user-specified script
    """
    name = "Script Builder"

    FILE_VARIABLES = r"file|file_path|file_name|file_ext|file_base_name"

    CONTAINS_VARIABLE = re.compile(
        r"\$\{?(?:" + FILE_VARIABLES + r"|output_directory|aux_directory|jobname)\}?\b",
        re.IGNORECASE | re.UNICODE,
    )

    def __init__(self, *args):
        # Sets the file name parts, plus internal stuff
        super().__init__(*args)
        plat = sublime.platform()
        self.cmd = self.builder_settings.get(plat, {}).get("script_commands", None)

    # Very simple here: we yield a single command
    # Also add environment variables
    def commands(self) -> CommandGenerator:
        if self.cmd is None:
            sublime.error_message(
                "You MUST set a command in your LaTeXTools.sublime-settings "
                + "file before launching the script builder."
            )
            # I'm not sure this is the best way to handle things...
            raise StopIteration()

        if isinstance(self.cmd, str):
            self.cmd = [self.cmd]

        for cmd in self.cmd:
            replaced_var = False
            if isinstance(cmd, str):
                cmd, replaced_var = self.substitute(cmd)
            else:
                for i, component in enumerate(cmd):
                    cmd[i], replaced = self.substitute(component)
                    replaced_var = replaced_var or replaced

            if not replaced_var:
                if isinstance(cmd, str):
                    cmd += " " + self.base_name
                else:
                    cmd.append(self.base_name)

            if not isinstance(cmd, str):
                cmd = " ".join(map(quote, cmd))
            self.display(f"Invoking '{cmd}'...")

            yield (cmd, "")

    def substitute(self, command: str) -> tuple[str, bool]:
        replaced_var = False
        if self.CONTAINS_VARIABLE.search(command):
            replaced_var = True

            template = Template(command)
            command = template.safe_substitute(
                file=self.tex_root,
                file_path=self.tex_dir,
                file_name=self.tex_name,
                file_ext=self.tex_ext,
                file_base_name=self.base_name,
                output_directory=self.output_directory_full or self.tex_dir,
                aux_directory=self.aux_directory_full or self.tex_dir,
                jobname=self.job_name,
            )

        return (command, replaced_var)
