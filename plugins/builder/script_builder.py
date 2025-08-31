from __future__ import annotations
import sublime

from functools import partial
from string import Template
from subprocess import list2cmdline
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from ...latextools.utils.external_command import external_command

from .pdf_builder import PdfBuilder

__all__ = ["ScriptBuilder"]


class ScriptBuilder(PdfBuilder):
    """
    ScriptBuilder class

    Launch a user-specified script
    """

    name = "Script Builder"

    def commands(self) -> CommandGenerator:
        cmds = self.builder_settings.get(sublime.platform(), {}).get("script_commands")
        if not cmds:
            cmds = self.builder_settings.get("script_commands")
        if not cmds:
            # Display error dialog in context of main UI thread.
            sublime.set_timeout(
                partial(
                    sublime.error_message,
                    "You MUST set a command in your LaTeXTools.sublime-settings "
                    + "file before launching the script builder.",
                )
            )
            raise ValueError("No 'script_commands' specified!")

        self.run_in_shell = True

        if isinstance(cmds, str):
            cmds = [cmds]
        if not isinstance(cmds, list):
            raise ValueError("Invalid script type! 'script_commands' must be a 'str' or 'list'!")

        for cmd in cmds:
            if isinstance(cmd, str):
                expanded_cmd = self.substitute(cmd)
                if expanded_cmd == cmd:
                    expanded_cmd += f' "{self.base_name}"'
                cmd = expanded_cmd

            elif isinstance(cmd, list):
                replaced_var = False
                for i, arg in enumerate(cmd):
                    expanded_arg = self.substitute(arg)
                    replaced_var |= expanded_arg != arg
                    cmd[i] = expanded_arg
                if not replaced_var:
                    cmd.append(self.base_name)
                cmd = list2cmdline(cmd)

            else:
                raise ValueError(f"Invalid command type! '{cmd}' must be a 'str' or 'list'!")

            yield (cmd, f"Running '{cmd}'...")

    def substitute(self, command: str) -> str:
        return Template(command).safe_substitute(
            file=self.tex_root,
            file_path=self.tex_dir,
            file_name=self.tex_name,
            file_ext=self.tex_ext,
            file_base_name=self.base_name,
            output_directory=self.output_directory_full or self.tex_dir,
            aux_directory=self.aux_directory_full or self.tex_dir,
            jobname=self.job_name,
            eol='' # a dummy to be used to prevent automatic base_name appending
        )
