from __future__ import annotations
import os
import shlex
import shutil
import sublime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from .pdf_builder import PdfBuilder

__all__ = ["TraditionalBuilder"]

DEFAULT_COMMAND_LATEXMK = [
    "latexmk",
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
        cmd = self.builder_settings.get("command")
        if not cmd:
            # prefer latexmk, if available, fallback to texify
            texpath = None if self.env is None else self.env.get("PATH")
            if shutil.which("latexmk", path=texpath) and shutil.which("perl", path=texpath):
                cmd = DEFAULT_COMMAND_LATEXMK.copy()
            else:
                cmd = DEFAULT_COMMAND_TEXIFY.copy()
        elif isinstance(cmd, str):
            cmd = shlex.split(cmd)

        latexmk = cmd[0] == "latexmk"
        texify = cmd[0] == "texify"

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
            # if `-cd` is specified, `-output-directory` is required to prevent
            # latexmk changing working directory to tex root. Note, that's slower.
            if self.aux_directory and "-cd" in cmd:
                # Don't use --aux-directory as the way latexmk moves
                # final documents to a possibly defined --output-directory
                # prevents files reloading in SumatraPDF or even fails
                # if documents are opened and locked by viewer on Windows.
                cmd.append(f"-output-directory={self.aux_directory}")

            if self.job_name != self.base_name:
                cmd.append(f'-jobname="{self.job_name}"')

            cmd += map(lambda o: f"-latexoption={o}", self.options)

        elif texify:
            if self.job_name != self.base_name:
                cmd.append(f'--job-name="{self.job_name}"')

            cmd += map(lambda o: f'--tex-option="{o}"', self.options)

        # texify requires absolute path if aux-directory differs;
        # latexmk doesn't care either way
        yield (cmd + [self.tex_root], f"running {cmd[0]}...")

        # Sync compiled documents with output directory.
        self.copy_assets_to_output()
