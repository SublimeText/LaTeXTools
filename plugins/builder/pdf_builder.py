from __future__ import annotations
import ctypes
import os
import shutil
import sublime
import sys

from string import Template
from textwrap import indent
from typing import TYPE_CHECKING

from ...latextools.latextools_plugin import LaTeXToolsPlugin
from ...latextools.utils.external_command import external_command
from ...latextools.utils.external_command import PIPE
from ...latextools.utils.external_command import STDOUT
from ...latextools.utils.external_command import Popen
from ...latextools.utils.logging import logger

if TYPE_CHECKING:
    from typing import Any, Callable, Generator, TypeAlias
    from ...latextools.utils.external_command import CommandLine

    Command: TypeAlias = CommandLine | Popen
    CommandGenerator: TypeAlias = Generator[tuple[Command, str]]

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
        shell: bool,
        env: dict[str, str],
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

        :param env:
            A dictionary containing custom environment variables
            from sublime-build file or "platform_settings".

        """
        self.run_in_shell = shell
        """
        Specifies whether yielded commands are run within shell.

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

        self.display_log = self.builder_settings.get("display_log", False)
        """
        Specifies whether to display detailed command output in log panel.

        Value of `builder_settings: { display_log: ... }` setting
        """

        distro = self.platform_settings.get("distro", "")
        self.uses_miktex = (
            distro != "texlive" if sublime.platform() == "windows" else distro == "miktex"
        )

        # if output_directory and aux_directory can be specified as a path
        # relative to self.tex_dir, we use that instead of the absolute path
        # note that the full path for both is available as
        # self.output_directory_full and self.aux_directory_full
        if aux_directory:
            self.aux_directory_full = aux_directory
            try:
                self.aux_directory = os.path.relpath(self.aux_directory_full, self.tex_dir)
            except Exception:
                self.aux_directory = self.aux_directory_full
            if self.aux_directory:
                os.makedirs(self.aux_directory_full, exist_ok=True)
                try:
                    gitignore = os.path.join(self.aux_directory_full, ".gitignore")
                    with open(gitignore, "w+", encoding="utf-8") as fobj:
                        fobj.write("*\n")
                except FileExistsError:
                    pass
        else:
            self.aux_directory_full = self.tex_dir
            self.aux_directory = ""

        if output_directory:
            self.output_directory_full = output_directory
            try:
                self.output_directory = os.path.relpath(self.output_directory_full, self.tex_dir)
            except Exception:
                self.output_directory = self.output_directory_full
            if self.output_directory:
                os.makedirs(self.output_directory_full, exist_ok=True)
        else:
            self.output_directory_full = self.tex_dir
            self.output_directory = ""

        # Help latex toolchain find resources by prepending TeX document's location to popular
        # environment variables. Even latexmk requires it to properly build bibliography.
        if self.aux_directory or self.output_directory:
            if env is None:
                env = os.environ.copy()
            if self.uses_miktex:
                # MikTeX, prepends custom variables to its configuration.
                env_vars = ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS")
            else:
                # TeXLive overwrites its configuration with custom variables.
                # Hence set `TEXMFDOTDIR`, which is prepended to all of them.
                env_vars = ("TEXMFDOTDIR",)
            for key in env_vars:
                env[key] = os.pathsep.join(filter(None, (".", self.tex_dir, env.get(key))))

        # finally expand variables in custom environment
        self.env = {k: self.expandvars(v) for k, v in env.items()} if env else None

        logger.debug("tex directory: %s", self.tex_dir)
        logger.debug("aux directory: %s", self.aux_directory_full)
        logger.debug("out directory: %s", self.output_directory_full)

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

    def command(
        self,
        cmd: CommandLine,
        cwd: str | None = None,
        shell: bool | None = None,
        env: dict[str, str] | None = None,
        show_window: bool = False,
        message: str = "",
    ) -> Command:
        """
        Create custom command object to be yielded on builder event loop.

        Usage Example:

        ```py
            yield (
                self.command("bibtex", cwd=self.aux_directory_full),
                "running bibtex..."
            )
        ```

        :param cmd:
            The command line to execute
        :param cwd:
            The current working directory to call command in (default: tex root)
        :param shell:
            Whether to run command using login shell (default: False)
        :param env:
            The environment to use to run the command
        :param show_window:
            If `True` show window (required on Windows, primarily)

        :returns:
            Process object representing invoked command.
        """
        if isinstance(cmd, list):
            cmd = list(map(self.expandvars, cmd))
        elif isinstance(cmd, str):
            cmd = self.expandvars(cmd)

        if cwd is None:
            cwd = self.tex_dir

        if env is None:
            env = self.env

        if shell is None:
            shell = self.run_in_shell

        return external_command(
            cmd=cmd,
            cwd=cwd,
            shell=shell,
            env=env,
            stdin=None,
            stdout=PIPE,
            stderr=STDOUT,
            preexec_fn=(os.setsid if sublime.platform() != "windows" else None),
            use_texpath=False,
            show_window=show_window,
        )

    def expandvars(self, text: str, **custom_vars: str) -> str:
        """
        Expand variables in text.

        :param text:
            The text to expand `$variables` in.

        :returns:
            A string with all known variables expanded.
        """
        return Template(text).safe_substitute(
            eol="",  # a dummy to be used to prevent automatic base_name appending
            file=self.tex_root,
            file_path=self.tex_dir,
            file_name=self.tex_name,
            file_ext=self.tex_ext,
            file_base_name=self.base_name,
            output_directory=self.output_directory_full,
            aux_directory=self.aux_directory_full,
            jobname=self.job_name,
            engine=self.engine,
            **custom_vars
        )

    def copy_assets_to_output(self) -> None:
        """
        Copy final build assets from aux- to output directory.

        Only tatexmk natively supports --aux-directory, but still causes:

        - Some Linux viewers reload final PDF each time it is updated by a
          build step, causing PDF preview to flicker
        - SumatraPDF does not reload document on compile, caused by loosing
          reference due to PDF file being deleted and re-created, if latexmk
          natively moves a file from aux- to output-directory. see: issue 1373

        Those issues are solved by building document in a aux directory and use
        `shlutil.copy2`, which updates possibly existing target files, once,
        without destroying any open filehandle.

        Original PDF file is kept in place for e.g. latexmk to be able to skip
        build if nothing was changed.
        """
        if self.aux_directory_full != self.output_directory_full:
            for ext in (".synctex.gz", ".pdf"):
                asset_name = self.base_name + ext

                dst_file = os.path.join(self.output_directory_full, asset_name)
                try:
                    dst_st = os.stat(dst_file)
                except FileNotFoundError:
                    dst_st = None

                src_file = os.path.join(self.aux_directory_full, asset_name)
                try:
                    src_st = os.stat(src_file)
                except FileNotFoundError:
                    logger.debug(f"Source {src_file} does not exist, skipping!")
                    continue

                # copy if target does not exist, is older or differs in size
                if (
                    dst_st is None
                    or src_st.st_mtime > dst_st.st_mtime
                    or src_st.st_size != dst_st.st_size
                ):
                    shutil.copy2(src_file, dst_file)
                    if ext == ".synctex.gz":
                        hide_file(dst_file)
                    logger.debug(f"Updated {dst_file}")


def hide_file(file_name):
    if os.name == "nt":
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(file_name, FILE_ATTRIBUTE_HIDDEN)
        if not ret:  # There was an error.
            raise ctypes.WinError()
