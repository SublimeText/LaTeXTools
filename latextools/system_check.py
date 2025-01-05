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
from shutil import which

import sublime
import sublime_plugin

from .jumpto_pdf import DEFAULT_VIEWERS
from .latextools_plugin import _classname_to_internal_name
from .latextools_plugin import add_plugin_path
from .latextools_plugin import get_plugin
from .latextools_plugin import NoSuchPluginException
from .utils.activity_indicator import ActivityIndicator
from .utils.distro_utils import using_miktex
from .utils.external_command import check_output
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

__all__ = ["LatextoolsSystemCheckCommand", "LatextoolsInsertTextCommand"]


def expand_vars(texpath):
    return os.path.expandvars(texpath)


def update_environment(old, new):
    old.update(new.items())


def _get_texpath(view):
    texpath = get_setting(sublime.platform(), {}, view).get("texpath")
    return expand_vars(texpath) if texpath is not None else None


class SubprocessTimeoutThread(threading.Thread):
    """
    A thread for monitoring a subprocess to kill the subprocess after a fixed
    period of time
    """

    def __init__(self, timeout, *args, **kwargs):
        super(SubprocessTimeoutThread, self).__init__()
        self.args = args
        self.kwargs = kwargs
        # ignore the preexec_fn if specified
        if "preexec_fn" in kwargs:
            del self.kwargs["preexec_fn"]

        if "startupinfo" in kwargs:
            del self.kwargs["startupinfo"]

        if sublime.platform() == "windows":
            # ensure console window doesn't show
            self.kwargs["startupinfo"] = startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.kwargs["shell"] = True

        self.timeout = timeout

        self.returncode = None
        self.stdout = None
        self.stderr = None

    def run(self):
        if sublime.platform() != "windows":
            preexec_fn = os.setsid
        else:
            preexec_fn = None

        try:
            self._p = p = subprocess.Popen(*self.args, preexec_fn=preexec_fn, **self.kwargs)

            self.stdout, self.stderr = p.communicate()
            self.returncode = p.returncode
        except Exception as e:
            # just in case...
            self.kill_process()
            raise e

    def start(self):
        super(SubprocessTimeoutThread, self).start()
        self.join(self.timeout)

        # if the timeout occurred, kill the entire process chain
        if self.isAlive():
            self.kill_process()

    def kill_process(self):
        try:
            if sublime.platform == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.call(
                    "taskkill /t /f /pid {pid}".format(pid=self._p.pid),
                    startupinfo=startupinfo,
                    shell=True,
                )
            else:
                os.killpg(self._p.pid, signal.SIGKILL)
        except Exception:
            traceback.print_exc()


def get_version_info(executable, env=None):
    logger.info("Checking %s...", executable)

    if env is None:
        env = os.environ

    version = "--version"
    # gs / gswin32c has a different format for --version vs -version
    if os.path.splitext(os.path.basename(executable))[0] in [
        "gs",
        "gswin32c",
        "gswin64c",
    ]:
        version = "-version"

    try:
        t = SubprocessTimeoutThread(
            30,  # wait 30 seconds
            [executable, version],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            env=env,
        )

        t.start()

        stdout = t.stdout
        if stdout is None:
            return None

        return re.split(r"\r?\n", stdout.decode(encoding="utf-8", errors="ignore").strip(), 1)[
            0
        ].lstrip("Version: ")
    except Exception:
        return None


def get_tex_path_variable_texlive(variable, env=None):
    """
    Uses kpsewhich to read the value of a given TeX PATH variable, such as
    TEXINPUTS.
    """
    logger.info("Reading path for %s...", variable)

    if env is None:
        env = os.environ

    try:
        t = SubprocessTimeoutThread(
            30,  # wait up to 30 seconds
            ["kpsewhich", "--expand-path=$" + variable],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            env=env,
        )

        t.start()

        stdout = t.stdout
        if stdout is None:
            return None

        return "\n".join(re.split(r"\r?\n", stdout.decode("utf-8").strip()))
    except Exception:
        return None


def get_tex_path_variable_miktex(variable, env=None):
    """
    Uses findtexmf to find the values of a given TeX PATH variable, such as
    TEXINPUTS
    """
    logger.info("Reading path for %s...", variable)

    if env is None:
        env = os.environ

    try:
        command = ["findtexmf", "-alias=latex"]
        command.append(
            ("-show-path={" + variable + "}").format(
                TEXINPUTS="tex", BIBINPUTS="bib", BSTINPUTS="bst"
            )
        )

        t = SubprocessTimeoutThread(
            30,  # wait up to 30 seconds
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            env=env,
        )

        t.start()

        stdout = t.stdout
        if stdout is None:
            return None

        output = "\n".join(re.split(r"\r?\n", stdout.decode("utf-8").strip()))
        return os.pathsep.join([os.path.normpath(p) for p in output.split(os.pathsep)])
    except Exception:
        return None


def kpsewhich(file):
    try:
        return check_output(["kpsewhich", file])
    except Exception:
        return None


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

    def __init__(
        self,
        sublime_exe=None,
        uses_miktex=False,
        texpath=None,
        build_env=None,
        view=None,
        on_done=None,
    ):
        super(SystemCheckThread, self).__init__()
        self.sublime_exe = sublime_exe
        self.uses_miktex = uses_miktex
        self.texpath = texpath
        self.build_env = build_env
        self.view = view
        self.on_done = on_done

    def run(self):
        with ActivityIndicator("Checking system...") as activity_indicator:
            self.worker()
            activity_indicator.finish("System check complete")

    def worker(self):
        texpath = self.texpath
        results = []

        env = copy.deepcopy(os.environ)

        if texpath is not None:
            env["PATH"] = texpath
        if self.build_env is not None:
            update_environment(env, self.build_env)

        table = [["Variable", "Value"]]

        table.append(["PATH", env.get("PATH", "")])

        if self.uses_miktex:
            get_tex_path_variable = get_tex_path_variable_miktex
            should_run = which("findtexmf", path=texpath) is not None
        else:
            get_tex_path_variable = get_tex_path_variable_texlive
            should_run = which("kpsewhich", path=texpath) is not None

        if should_run:
            for var in ["TEXINPUTS", "BIBINPUTS", "BSTINPUTS"]:
                table.append([var, get_tex_path_variable(var, env)])

        if self.uses_miktex:
            for var in [
                "BIBTEX",
                "LATEX",
                "PDFLATEX",
                "MAKEINDEX",
                "MAKEINFO",
                "TEX",
                "PDFTEX",
                "TEXINDEX",
            ]:
                value = env.get(var, None)
                if value is not None:
                    table.append([var, value])

        results.append(table)

        table = [["Program", "Location", "Status", "Version"]]

        # skip sublime_exe on OS X
        # we only use this for the hack to re-focus on ST
        # which doesn't work on OS X anyway
        if sublime.platform() != "osx":
            sublime_exe = self.sublime_exe
            available = sublime_exe is not None

            if available:
                if not os.path.isabs(sublime_exe):
                    sublime_exe = which(sublime_exe)

                basename, extension = os.path.splitext(sublime_exe)
                if extension is not None:
                    sublime_exe = "".join((basename, extension.lower()))

            version_info = get_version_info(sublime_exe, env=env) if available else None

            table.append(
                [
                    "sublime",
                    sublime_exe if available and version_info is not None else "",
                    ("available" if available and version_info is not None else "missing"),
                    version_info if version_info is not None else "unavailable",
                ]
            )

        # a list of programs, each program is either a string or a list
        # of alternatives (e.g. 32/64 bit version)
        programs = [
            "latexmk" if not self.uses_miktex else "texify",
            "pdflatex",
            "xelatex",
            "lualatex",
            "biber",
            "bibtex",
            "bibtex8",
            "kpsewhich",
        ]

        # ImageMagick requires gs to work with PDFs
        programs += [["magick", "convert"]]

        for program in programs:
            if isinstance(program, list):
                program_list = program
                program = program_list[0]
                location = None
                for p in program_list:
                    location = which(p, path=texpath)
                    if location is not None:
                        program = p
                        break
            else:
                location = which(program, path=texpath)

            # convert.exe on Windows can refer to %systemroot%\convert.exe,
            # which should not be used; in that case, simple report magick.exe
            # as not existing
            if program == "convert" and sublime.platform() == "windows":
                if os.path.samefile(location, os.path.join(get_system_root(), "convert.exe")):
                    program = "magick"
                    location = None

            available = location is not None

            if available:
                basename, extension = os.path.splitext(location)
                if extension is not None:
                    location = "".join((basename, extension.lower()))

            version_info = get_version_info(location, env=env) if available else None

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

        version_info = get_version_info(location, env=env) if available else None

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
                    available = kpsewhich(package) is not None
                    package_name = package.split(".")[0]
                    table.append([package_name, ("available" if available else "missing")])

                results.append(table)

        builder_name = get_setting("builder", "traditional", view=self.view)

        if builder_name in ["", "default"]:
            builder_name = "traditional"

        builder_settings = get_setting("builder_settings", view=self.view)
        builder_path = get_setting("builder_path", view=self.view)

        if builder_name in ["simple", "traditional", "script"]:
            builder_path = None
        else:
            bld_path = os.path.join(sublime.packages_path(), builder_path)
            add_plugin_path(bld_path)

        builder_name = _classname_to_internal_name(builder_name)

        try:
            get_plugin("{0}_builder".format(builder_name))
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

        if builder_path:
            results.append([["Builder Path"], [builder_path]])

        if builder_settings is not None:
            table = [["Builder Setting", "Value"]]
            for key in sorted(builder_settings.keys()):
                value = builder_settings[key]
                table.append([key, value])
            results.append(table)

        # is current view a TeX file?
        view = self.view
        if view and view.match_selector(0, "text.tex.latex"):
            tex_root = get_tex_root(view)
            tex_directives = parse_tex_directives(
                tex_root, multi_values=["options"], key_maps={"ts-program": "program"}
            )

            results.append([["TeX Root"], [tex_root]])

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
            if jobname and jobname != os.path.splitext(os.path.basename(tex_root))[0]:
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

        default_viewer = DEFAULT_VIEWERS.get(sublime.platform(), None)
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
            elif viewer_name in ("evince", "okular", "zathura"):
                viewer_location = which(viewer_name)
                viewer_available = bool(viewer_location)
            elif viewer_name == "preview":
                viewer_location = "/Applications/Preview.app"

                if not os.path.exists(viewer_location):
                    try:
                        viewer_location = check_output(
                            [
                                "osascript",
                                "-e",
                                "POSIX path of " '(path to app id "com.apple.Preview")',
                            ],
                            use_texpath=False,
                        )
                    except subprocess.CalledProcessError:
                        viewer_location = None

                viewer_available = False if not viewer_location else os.path.exists(viewer_location)
            elif viewer_name == "skim":
                viewer_location = "/Applications/Skim.app"

                if not os.path.exists(viewer_location):
                    try:
                        viewer_location = check_output(
                            [
                                "osascript",
                                "-e",
                                "POSIX path of " '(path to app id "net.sourceforge.skim-app.skim")',
                            ],
                            use_texpath=False,
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

                viewer_location = which(sumatra_exe)
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
            self.on_done(results)


class LatextoolsSystemCheckCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        view = sublime.active_window().active_view()

        t = SystemCheckThread(
            sublime_exe=get_sublime_exe(),
            uses_miktex=using_miktex(),
            texpath=_get_texpath(view) or os.environ["PATH"],
            build_env=get_setting("builder_settings", {}, view).get(sublime.platform(), {}).get("env"),
            view=view,
            on_done=self.on_done,
        )

        t.start()

    def on_done(self, results):
        def _on_done():
            buf = StringIO()
            for item in results:
                tabulate(item, output=buf)

            new_view = sublime.active_window().new_file()
            new_view.set_scratch(True)
            new_view.set_name("LaTeXTools System Check")
            new_view.set_encoding("UTF-8")

            settings = new_view.settings()
            settings.set("word_wrap", False)
            settings.set("line_numbers", False)
            settings.set("gutter", False)
            settings.set("syntax", "Packages/LaTeXTools/system_check.sublime-syntax")

            new_view.run_command("latextools_insert_text", {"text": buf.getvalue().rstrip()})

            new_view.set_read_only(True)

            buf.close()

        sublime.set_timeout(_on_done, 0)


class LatextoolsInsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, text=""):
        view = self.view
        view.insert(edit, 0, text)
