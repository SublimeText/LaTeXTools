from __future__ import annotations
import copy
import os
import re
import signal
import subprocess
import sys
import textwrap
import threading
import traceback

from io import StringIO
from functools import lru_cache
from functools import partial
from shutil import which
from typing import cast, Callable

import sublime
import sublime_plugin

from .jumpto_pdf import DEFAULT_VIEWERS
from .latextools_plugin import classname_to_plugin_name
from .latextools_plugin import get_plugin
from .latextools_plugin import NoSuchPluginException
from .utils.activity_indicator import ActivityIndicator
from .utils.distro_utils import using_miktex
from .utils.external_command import get_texpath
from .utils.logging import logger
from .utils.output_directory import get_aux_directory
from .utils.output_directory import get_jobname
from .utils.output_directory import get_output_directory
from .utils.settings import get_setting
from .utils.sublime_utils import get_sublime_exe
from .utils.tex_directives import get_tex_root
from .utils.tex_directives import parse_tex_directives

from .preview.preview_utils import convert_installed
from .preview.preview_utils import ghostscript_installed
from .preview.preview_utils import __get_gs_command as get_gs_command

if sublime.platform() == "windows":
    from .preview.preview_utils import get_system_root

__all__ = ["LatextoolsSystemCheckCommand"]


def get_max_width(table, column):
    return max(len(str(row[column])) for row in table)


def tabulate(table, wrap_column=0, output=sys.stdout):
    """
    Utility function to layout a table. A table is a list of list, with each
    sub-list representing a row of values. The first row in the table is taken
    to be the header row.

    Format looks like this:

    Header1  Header2
    -------  -------
    Value1   Value2

    i.e., each column is displayed at the maximum number of characters of any
    field in that column; the spacing between two columns is two spaces from
    the length of the longest entry; and each header is followed by a series
    of dashes as long as the header.

    Args:
        table: a list of lists containg the data to be formatted
        wrap_column: if a positive number, specifies the maximum number of
            characters to allow in any column
        output: the output stream to write to; defaults to sys.stdout
    """
    column_widths = [get_max_width(table, i) for i in range(len(table[0]))]
    # Ensure the *last* column is only as long as it needs to be
    # This is necessary for the syntax to work properly
    column_widths[-1] = len(table[0][-1])
    if wrap_column is not None and wrap_column > 0:
        column_widths = [width if width <= wrap_column else wrap_column for width in column_widths]

    headers = table.pop(0)

    for i in range(len(headers)):
        padding = 2 if i < len(headers) - 1 else 0
        output.write(str(headers[i]).ljust(column_widths[i] + padding))
    output.write("\n")

    for i in range(len(headers)):
        padding = 2 if i < len(headers) - 1 else 0
        if headers[i]:
            output.write(("-" * len(headers[i])).ljust(column_widths[i] + padding))
        else:
            output.write("".ljust(column_widths[i] + padding))
    output.write("\n")

    added_row = False
    for j, row in enumerate(table):
        for i in range(len(row)):
            padding = 2 if i < len(row) - 1 else 0
            column = str(row[i])
            if wrap_column is not None and wrap_column != 0 and len(column) > wrap_column:
                wrapped = textwrap.wrap(column, wrap_column)
                column = wrapped.pop(0)
                lines = "".join(wrapped)

                if added_row:
                    table[j + 1][i] = lines
                else:
                    table.insert(j + 1, [""] * len(row))
                    table[j + 1][i] = lines
                    added_row = True

            output.write(column.ljust(column_widths[i] + padding))

        added_row = False
        output.write("\n")
    output.write("\n")


class SystemCheckThread(threading.Thread):

    def __init__(self, view: sublime.View, on_done: Callable[[list[list]], None]):
        super().__init__()
        self.view = view
        self.on_done = on_done
        self.platform = sublime.platform()
        self.uses_miktex = using_miktex()

        # setup system check environment
        #  CAUTION: logic must match make_pdf's logic
        self.env = os.environ.copy()

        self.builder_settings = cast(dict, get_setting("builder_settings", {}, view))
        self.builder_platform_settings = self.builder_settings.get(self.platform, {})
        build_env = self.builder_platform_settings.get("env")
        if build_env is None:
            build_env = self.builder_settings.get("env")
        if build_env is not None:
            self.env.update({k: os.path.expandvars(v) for k, v in build_env.items()})

        if (texpath := get_texpath(view)) is not None:
            self.env["PATH"] = texpath

        # prepand main tex document's location to all TeX related paths such as
        # TEXINPUTS, BIBINPUTS, BSTINPUTS, etc.
        self.tex_root = get_tex_root(self.view)
        if self.tex_root:
            tex_dir = os.path.dirname(self.tex_root)
            if self.uses_miktex:
                # MikTeX, prepends custom variables to its configuration.
                env_vars = ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS")
            else:
                # TeXLive overwrites its configuration with custom variables.
                # Hence set `TEXMFDOTDIR`, which is prepended to all of them.
                env_vars = ("TEXMFDOTDIR",)
            for key in env_vars:
                self.env[key] = os.pathsep.join(filter(None, (tex_dir, self.env.get(key))))

    def run(self):
        with ActivityIndicator("Checking system...") as activity_indicator:
            self.worker()
            activity_indicator.finish("System check complete")

    def worker(self):
        results = []

        table = [["Variable", "Value"]]

        table.append(["PATH", self.env.get("PATH", "")])

        table.extend(
            [var, self.get_tex_path_variable(var) or "missing"]
            for var in ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS")
        )

        if self.uses_miktex:
            for var in (
                "BIBTEX",
                "LATEX",
                "PDFLATEX",
                "MAKEINDEX",
                "MAKEINFO",
                "TEX",
                "PDFTEX",
                "TEXINDEX",
            ):
                value = self.env.get(var, None)
                if value is not None:
                    table.append([var, value])

        results.append(table)

        table = [["Program", "Location", "Status", "Version"]]

        # Check subl availability as it is required for backward search by viewers
        row = None
        sublime_exe = get_sublime_exe()
        if sublime_exe:
            version_info = self.get_version_info(sublime_exe)
            if version_info:
                row = ["sublime", sublime_exe, "available", version_info]
        table.append(row or ["sublime", "", "missing", "unavailable"])

        # a list of programs, each program is either a string or a list
        # of alternatives (e.g. 32/64 bit version)
        programs = [
            "perl",
            "latexmk",
            # "texify",
            "pdflatex",
            "xelatex",
            "lualatex",
            "biber",
            "bibtex",
            "bibtex8",
            "kpsewhich",
            # ImageMagick requires gs to work with PDFs
            ["magick", "convert"],
        ]
        if self.uses_miktex:
            programs.insert(2, "texify")

        for program in programs:
            if isinstance(program, list):
                program_list = program
                program = program_list[0]
                location = None
                for p in program_list:
                    location = self.which(p)
                    if location is not None:
                        program = p
                        break
            else:
                location = self.which(program)

            # convert.exe on Windows can refer to %systemroot%\convert.exe,
            # which should not be used; in that case, simple report magick.exe
            # as not existing
            if program == "convert" and self.platform == "windows":
                if os.path.samefile(location, os.path.join(get_system_root(), "convert.exe")):
                    program = "magick"
                    location = None

            available = location is not None

            if available:
                basename, extension = os.path.splitext(location)
                if extension is not None:
                    location = "".join((basename, extension.lower()))

            version_info = self.get_version_info(location) if available else None

            available_str = "available" if available and version_info is not None else "missing"

            if available and program in ["magick", "convert"] and not convert_installed():
                available_str = "restart required"

            table.append(
                [
                    program,
                    location if available and version_info is not None else "",
                    available_str,
                    version_info if version_info is not None else "unavailable",
                ]
            )

        program = "ghostscript"
        location = get_gs_command()

        available = location is not None

        if available:
            basename, extension = os.path.splitext(location)
            if extension is not None:
                location = "".join((basename, extension.lower()))

        version_info = self.get_version_info(location) if available else None

        available_str = "available" if available and version_info is not None else "missing"

        if available and not ghostscript_installed():
            available_str = "restart required"

        table.append(
            [
                program,
                location if available and version_info is not None else "",
                available_str,
                version_info if version_info is not None else "unavailable",
            ]
        )

        results.append(table)

        # This really only works for the default template
        # Note that no attempt is made to find other packages that the
        # included package depends on
        if (
            ghostscript_installed()
            and get_setting("preview_math_template_file", view=self.view) is None
            and get_setting("preview_math_mode", view=self.view) != "none"
        ):

            find_package_re = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{(?P<pkg>[^\}]*)\}")

            packages = ["standalone.cls", "preview.sty", "xcolor.sty"]

            package_settings = get_setting("preview_math_template_packages", [], view=self.view)
            # extract all packages from each package line
            for pkg_str in package_settings:
                # search for all \usepackage in the line
                for m in find_package_re.finditer(pkg_str):
                    pkg_arg = m.group("pkg")
                    # search for each package in the \usepackage argument
                    for pkg in pkg_arg.split(","):
                        pkg = pkg.strip()
                        if pkg:
                            packages.append(pkg + ".sty")

            if packages:
                table = [["Packages for equation preview", "Status"]]

                for package in packages:
                    available = bool(self.kpsewhich(package))
                    package_name = package.split(".")[0]
                    table.append([package_name, ("available" if available else "missing")])

                results.append(table)

        builder_name = get_setting("builder", "traditional", view=self.view)

        if builder_name in ["", "default"]:
            builder_name = "traditional"

        builder_name = classname_to_plugin_name(builder_name)

        try:
            get_plugin(f"{builder_name}_builder")
            builder_available = True
        except NoSuchPluginException:
            traceback.print_exc()
            builder_available = False

        results.append(
            [
                ["Builder", "Status"],
                [builder_name, "available" if builder_available else "missing"],
            ]
        )

        if self.builder_settings is not None:
            table = [["Builder Setting", "Value"]]
            table.extend(sorted(self.builder_settings.items()))
            results.append(table)

        # is current view a TeX file?
        view = self.view
        if view and view.match_selector(0, "text.tex.latex"):
            tex_directives = parse_tex_directives(
                self.tex_root, multi_values=["options"], key_maps={"ts-program": "program"}
            )

            results.append([["TeX Root"], [self.tex_root]])

            results.append(
                [
                    ["LaTeX Engine"],
                    [tex_directives.get("program", get_setting("program", "pdflatex", self.view))],
                ]
            )

            table = [["LaTeX Output Setting", "Value"]]
            output_directory = get_output_directory(view)
            if output_directory:
                table.append(["output_directory", output_directory])
            aux_directory = get_aux_directory(view)
            if aux_directory:
                table.append(["aux_directory", aux_directory])
            jobname = get_jobname(view)
            if jobname and jobname != os.path.splitext(os.path.basename(self.tex_root))[0]:
                table.append(["jobname", jobname])

            if len(table) > 1:
                results.append(table)

            options = get_setting("builder_settings", {}, self.view).get("options", [])

            if isinstance(options, str):
                options = [options]

            options.extend(tex_directives.get("options", []))

            if len(options) > 0:
                table = [["LaTeX Options"]]
                for option in options:
                    table.append([option])

                results.append(table)

        default_viewer = DEFAULT_VIEWERS.get(self.platform, None)
        viewer_name = get_setting("viewer", default_viewer, self.view)
        if viewer_name in ["", "default"]:
            viewer_name = default_viewer

        try:
            viewer_plugin = get_plugin(viewer_name + "_viewer")
            viewer_available = True
        except NoSuchPluginException:
            viewer_available = False

        viewer_location = "N/A"
        if viewer_available:
            if viewer_name == "command":
                # assume the command viewer is always valid
                viewer_location = "N/A"
            elif viewer_name in ("evince", "okular", "xreader", "zathura"):
                viewer_location = self.which(viewer_name)
                viewer_available = bool(viewer_location)
            elif viewer_name == "preview":
                viewer_location = "/Applications/Preview.app"

                if not os.path.exists(viewer_location):
                    try:
                        viewer_location = self.check_output(
                            [
                                "osascript",
                                "-e",
                                "POSIX path of " '(path to app id "com.apple.Preview")',
                            ]
                        )
                    except subprocess.CalledProcessError:
                        viewer_location = None

                viewer_available = False if not viewer_location else os.path.exists(viewer_location)
            elif viewer_name == "skim":
                viewer_location = "/Applications/Skim.app"

                if not os.path.exists(viewer_location):
                    try:
                        viewer_location = self.check_output(
                            [
                                "osascript",
                                "-e",
                                "POSIX path of " '(path to app id "net.sourceforge.skim-app.skim")',
                            ]
                        )
                    except subprocess.CalledProcessError:
                        viewer_location = None

                viewer_available = False if not viewer_location else os.path.exists(viewer_location)
            elif viewer_name == "sumatra":
                sumatra_exe = (
                    get_setting("viewer_settings", {}, self.view).get(
                        "sumatra",
                        get_setting("windows", {}, self.view).get("sumatra", "SumatraPDF.exe"),
                    )
                    or "SumatraPDF.exe"
                )

                viewer_location = self.which(sumatra_exe)
                if not bool(viewer_location):
                    viewer_location = viewer_plugin()._find_sumatra_exe()
                    viewer_available = bool(viewer_location)

        if not viewer_available:
            viewer_location = "N/A"

        results.append(
            [
                ["Viewer", "Status", "Location"],
                [
                    viewer_name,
                    "available" if viewer_available else "missing",
                    viewer_location,
                ],
            ]
        )

        if callable(self.on_done):
            # create and print output in UI thread to avoid graphical glitches
            sublime.set_timeout(partial(self.on_done, results))

    def check_output(self, cmd: list[str]) -> str | None:
        # manually lookup executable, as subprocess.run() ignores custom
        # environment's PATH, if shell=False is specified, and absolute path
        # may help analyzing debug log.
        if not os.path.isabs(cmd[0]):
            executable = self.which(cmd[0])
            if executable:
                cmd[0] = executable

        logger.debug("Executing %s...", cmd)

        result = subprocess.run(
            cmd,
            env=self.env,
            encoding="utf-8",
            shell=self.platform == "windows",
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            timeout=30,
            universal_newlines=True,
        )
        return result.stdout if result.returncode == 0 else None

    def get_version_info(self, executable: str) -> str | None:
        logger.info(f"Checking {executable}...")

        version = "--version"
        # gs / gswin32c has a different format for --version vs -version
        if os.path.splitext(os.path.basename(executable))[0] in [
            "gs",
            "gswin32c",
            "gswin64c",
        ]:
            version = "-version"

        stdout = self.check_output([executable, version])
        if stdout is None:
            return None

        return stdout.strip().split("\n", 1)[0].lstrip("Version: ")

    def get_tex_path_variable(self, variable: str) -> str | None:
        logger.info(f"Reading path for {variable}...")

        if self.uses_miktex:
            cmd = ["findtexmf", "-alias=latex", "-show-path=" + variable[:3].lower()]
        else:
            cmd = ["kpsewhich", "--expand-path=$" + variable]

        stdout = self.check_output(cmd)
        if stdout is None:
            return None

        # return platform specific normalized paths
        return os.pathsep.join(map(os.path.normpath, stdout.strip().split(os.pathsep)))

    def kpsewhich(self, file: str) -> str | None:
        return self.check_output(["kpsewhich", file])

    @lru_cache(maxsize=64)
    def which(self, file: str) -> str | None:
        return which(file, path=self.env.get("PATH"))


class LatextoolsSystemCheckCommand(sublime_plugin.ApplicationCommand):

    def run(self) -> None:
        window = sublime.active_window() or sublime.windows()[0]
        view = window.active_view() or window.views()[0]
        SystemCheckThread(view=view, on_done=self.on_done).start()

    def on_done(self, results: list[list]) -> None:
        with StringIO() as buf:
            for item in results:
                tabulate(item, output=buf)

            view = None
            view_name = "LaTeXTools System Check"
            window = sublime.active_window()

            for _view in window.views():
                if _view.name() == view_name and _view.is_scratch():
                    view = _view
                    break

            if view is None:
                view = window.new_file()
                view.set_scratch(True)
                view.set_name("LaTeXTools System Check")
                view.set_encoding("UTF-8")

                view_settings = view.settings()
                view_settings.set("auto_indent", False)
                view_settings.set("auto_match_enabled", False)
                view_settings.set("draw_indent_guides", False)
                view_settings.set("draw_white_space", "none")
                view_settings.set("detect_indentation", False)
                view_settings.set("disable_auto_complete", False)
                view_settings.set("gutter", False)
                view_settings.set("line_numbers", False)
                view_settings.set("rulers", [])
                view_settings.set("scroll_past_end", False)
                view_settings.set("tab_size", 2)
                view_settings.set("word_wrap", False)
                view.assign_syntax("Packages/LaTeXTools/system_check.sublime-syntax")

            view.set_read_only(False)
            view.run_command("select_all")  # ensure to replace existing text
            view.run_command("insert", {"characters": buf.getvalue().rstrip()})
            view.set_read_only(True)
            view.show(0, keep_to_left=True, animate=False)
            window.focus_view(view)
