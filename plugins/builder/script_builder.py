from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

import sublime

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from ...latextools.utils.external_command import shell_quote
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
            raise TypeError("Invalid script type! 'script_commands' must be a 'str' or 'list'!")

        for cmd in cmds:
            if isinstance(cmd, str):
                expanded_cmd = self.expandvarsquoted(cmd)
                if expanded_cmd == cmd:
                    expanded_cmd += " " + shell_quote(self.base_name)
                cmd = expanded_cmd

                yield (cmd, f"Running '{cmd}'...")

            elif isinstance(cmd, list):
                replaced_var = False
                for i, arg in enumerate(cmd):
                    expanded_arg = self.expandvars(arg)
                    replaced_var |= expanded_arg != arg
                    cmd[i] = expanded_arg
                if not replaced_var:
                    cmd.append(self.base_name)

                cmd_msg = " ".join(cmd)
                yield (cmd, f"Running '{cmd_msg}'...")

            else:
                raise TypeError(f"Invalid command type! '{cmd!r}' must be a 'str' or 'list'!")
