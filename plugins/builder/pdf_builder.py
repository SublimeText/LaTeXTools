from __future__ import annotations
import os
import shutil
import sublime
import sys

from textwrap import indent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Generator, TypeAlias
    from subprocess import Popen

    CommandGenerator: TypeAlias = Generator[tuple[list[str] | str | Popen, str]]

from ...latextools.latextools_plugin import LaTeXToolsPlugin
from ...latextools.utils.logging import logger

__all__ = ["PdfBuilder"]


class PdfBuilder(LaTeXToolsPlugin):
    """
    Base class for build engines

    Build engines subclass PdfBuilder

    Your __init__ method *must* call this (via super) to ensure that
    tex_root is properly split into the root tex file's directory,
    its base name, and extension, etc.
    """

    def __init__(
        self,
        tex_root: str,
        output: Callable[[list[str] | tuple[str] | str], None],
        engine: str,
        options: list[str],
        aux_directory: str,
        output_directory: str,
        job_name: str,
        tex_directives: dict[str, Any],
        builder_settings: dict[str, Any],
        platform_settings: dict[str, Any],
    ):
        """
        Constructs a new pdf builder engine instance.

        :param tex_root:
            The absolute path of the root tex document.

        :param output:
            A collable object taking a string to be writing to output panel.

        :param engine:
            The latex engine to use to compile the document.
            One of "pdflatex", "pdftex", "xelatex", "xetex", "lualatex", "luatex".

        :param options:
            The list of merged options from root document's tex directives
            and builder settings.

        :param aux_directory:
            The auxiliary directory, used to store intermediate build files.

        :param output_directory:
            The output directory to write final build assets to.
            Assets are the generated pdf document and associated synctex file.

        :param job_name:
            The job name

        :param tex_directives:
            A dictionary containing the tex directives parsed from root tex document.

        :param builder_settings:
            A dictionary containing the "builder_settings"
            from LaTeXTools.sublime-settings

        :param platform_settings:
            A dictionary containing the "platform_settings"
            from LaTeXTools.sublime-settings

        """
        self.run_in_shell = None
        """
        Specifies whether yielded commands are run within shell.

        `None` - automatic
        `True` - run commands via login shell
        `False` - run commands directly
        """
        self.abort_on_error = True
        """
        If `True`, batch execution is aborted, if called subprocess returns
        non-zero returncode.
        """
        self.out = ""
        """
        Output of most recently called command.
        """

        self.display = output
        self.tex_root = tex_root
        self.tex_dir, self.tex_name = os.path.split(tex_root)
        self.base_name, self.tex_ext = os.path.splitext(self.tex_name)
        self.engine = engine
        self.options = options
        self.job_name = job_name
        self.tex_directives = tex_directives
        self.builder_settings = builder_settings
        self.platform_settings = platform_settings

        # if output_directory and aux_directory can be specified as a path
        # relative to self.tex_dir, we use that instead of the absolute path
        # note that the full path for both is available as
        # self.output_directory_full and self.aux_directory_full
        self.aux_directory = (
            os.path.relpath(aux_directory, self.tex_dir)
            if aux_directory and aux_directory.startswith(self.tex_dir)
            else aux_directory
        )
        self.aux_directory_full = aux_directory
        if self.aux_directory_full:
            os.makedirs(self.aux_directory_full, exist_ok=True)

        self.output_directory = (
            os.path.relpath(output_directory, self.tex_dir)
            if output_directory and output_directory.startswith(self.tex_dir)
            else output_directory
        )
        self.output_directory_full = output_directory
        if self.output_directory_full:
            os.makedirs(self.output_directory_full, exist_ok=True)

        self.display_log = self.builder_settings.get("display_log", False)
        """
        Specifies whether to display detailed command output in log panel.

        Value of `builder_settings: { display_log: ... }` setting
        """

    def set_output(self, out: str) -> None:
        """
        Save command output.

        Called by command executor to display command results

        It assumes command message to look like "Running command..." so it will
        be finished with "done." on the same line, optionally followed by
        command's log output
        """
        self.out = out.strip()
        if self.display_log:
            self.display(f"command output:\n{indent(self.out, '  ')}\n{'-' * 80}\n")

        logger.debug("command output:\n%s", self.out)

    def commands(self) -> CommandGenerator:
        """
        Build command generator

        This is where the real work is done. This generator yields (cmd, msg)
        tuples, as function of parameters and output from previous commands
        (via send()).

        Note: Current working directory is root file's directory.

        :yields:
            (cmd, msg) tuples

            cmd - the list of command line arguments to execute
            msg - the message to be displayed (or None)

            The generator *must* yield at least *one* tuple.
            If no command is to be executed, yield ("","").
        """
        raise NotImplementedError

    def move_assets_to_output(self) -> None:
        """
        Move final build assets from aux- to output directory.

        Only tatexmk natively supports --aux-directory, but still causes issues
        in case final pdf document is opened in a viewer, already. This method
        is part of a strategy to work around known limitations and provide
        consistent behavior accross supporting builders.
        """
        dest_dir = self.output_directory_full or self.tex_dir
        if self.aux_directory and self.aux_directory_full != dest_dir:
            for ext in (".synctex.gz", ".pdf"):
                name = self.base_name + ext
                shutil.move(
                    src=os.path.join(self.aux_directory_full, name),
                    dst=os.path.join(dest_dir, name),
                )
