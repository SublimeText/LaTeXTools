from __future__ import annotations
import os
import shlex
import shutil
import sublime

from logging import DEBUG
from typing import TYPE_CHECKING

from ...latextools.utils.distro_utils import using_miktex
from ...latextools.utils.logging import logger

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from .pdf_builder import PdfBuilder

__all__ = ["TraditionalBuilder"]

DEFAULT_COMMAND_LATEXMK = [
    "latexmk",
    "-cd",
    "-f",
    "-%E",
    "-interaction=nonstopmode",
    "-synctex=1",
]

DEFAULT_COMMAND_TEXIFY = [
    "texify",
    "-b",
    "-p",
    "--engine=%E",
    '--tex-option="--synctex=1"',
]

TEXIFY_TO_LATEXMK_ENGINES = {"pdftex": "pdflatex", "xetex": "xelatex", "luatex": "lualatex"}

LATEXMK_TO_TEXIFY_ENGINES = {"pdflatex": "pdftex", "xelatex": "xetex", "lualatex": "luatex"}


class TraditionalBuilder(PdfBuilder):
    """
    TraditionalBuilder class

    Implement existing functionality, more or less
    NOTE: move this to a different file, too
    """

    name = "Traditional Builder"

    def commands(self) -> CommandGenerator:
        self.run_in_shell = False
        # Build command, with reasonable defaults
        cmd = self.builder_settings.get(sublime.platform(), {}).get("command")
        if not cmd:
            cmd = self.builder_settings.get("command")
            if not cmd:
                if using_miktex():
                    cmd = DEFAULT_COMMAND_TEXIFY.copy()
                else:
                    cmd = DEFAULT_COMMAND_LATEXMK.copy()

        if isinstance(cmd, str):
            cmd = shlex.split(cmd)

        latexmk = cmd[0] == "latexmk"
        texify = cmd[0] == "texify"

        # use default command line arguments, if only compiler is configured
        if len(cmd) == 1:
            if latexmk:
                cmd = DEFAULT_COMMAND_LATEXMK.copy()
            if texify:
                cmd = DEFAULT_COMMAND_TEXIFY.copy()

        # check if the command even wants the engine selected
        if not any("%E" in c for c in cmd):
            self.display("Your custom command does not allow the engine to be selected\n\n")
        else:
            engine = self.engine
            self.display(f"Engine: {engine}.\n")

            if latexmk:
                # latexmk options only supports latex-specific versions
                engine = TEXIFY_TO_LATEXMK_ENGINES.get(engine, engine)
            elif texify:
                # texify's --engine option takes pdftex/xetex/luatex as acceptable values
                engine = LATEXMK_TO_TEXIFY_ENGINES.get(engine, engine)

            flag = f"-{engine}" if texify or engine != "pdflatex" else "-pdf"
            for i, c in enumerate(cmd):
                cmd[i] = c.replace("-%E", flag).replace("%E", engine)

        if latexmk:
            # no need to output messages, if they are not consumed
            if logger.getEffectiveLevel() == DEBUG or self.display_log:
                cmd.append("-verbose")
            else:
                cmd.append("-silent")

            if sublime.platform() == "windows":
                cmd.append("-MSWinBackSlash")

            if self.aux_directory:
                # Don't use --aux-directory as the way latexmk moves
                # final documents to a possibly defined --output-directory
                # prevents files reloading in SumatraPDF or even fails
                # if documents are opened and locked by viewer on Windows.
                cmd.append(f"-output-directory={self.aux_directory_full}")

            if self.job_name != self.base_name:
                cmd.append(f'-jobname="{self.job_name}"')

            cmd += map(lambda o: f"-latexoption={o}", self.options)

        elif texify:
            # no need to output messages, if they are not consumed
            if logger.getEffectiveLevel() == DEBUG or self.display_log:
                cmd.append("--verbose")
            else:
                cmd.append("--quiet")

            if self.job_name != self.base_name:
                cmd.append(f'--job-name="{self.job_name}"')

            cmd += map(lambda o: f'--tex-option="{o}"', self.options)

        # texify wants the .tex extension; latexmk doesn't care either way
        yield (cmd + [self.tex_name], f"running {cmd[0]}...")

        # Sync compiled documents with output directory.
        if latexmk and self.aux_directory:
            self.copy_assets_to_output()
