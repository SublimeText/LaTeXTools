"""
Compile current .tex file to pdf
Allow custom scripts and build engines!

The actual work is done by builders, loaded on-demand from prefs
"""
import functools
import html
import os
import re
import shlex
import shutil
import signal
import threading
import traceback

import sublime
import sublime_plugin

from ..plugins.builder import *  # register internal builder plugins
from .latextools_plugin import classname_to_plugin_name
from .latextools_plugin import get_plugin
from .latextools_plugin import NoSuchPluginException
from .utils.activity_indicator import ActivityIndicator
from .utils.external_command import execute_command
from .utils.external_command import external_command
from .utils.external_command import get_texpath
from .utils.external_command import PIPE
from .utils.external_command import Popen
from .utils.is_tex_file import is_tex_file
from .utils.logging import logger
from .utils.output_directory import get_aux_directory
from .utils.output_directory import get_jobname
from .utils.output_directory import get_output_directory
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root
from .utils.tex_directives import parse_tex_directives
from .utils.tex_log import parse_tex_log


__all__ = [
    "LatextoolsMakePdfCommand",
    "LatextoolsExecEventListener",
]

SUPPORTED_PDF_COMPILERS = ("pdflatex", "pdftex", "xelatex", "xetex", "lualatex", "luatex")


class CmdThread(threading.Thread):

    # Use __init__ to pass things we need
    # in particular, we pass the caller in teh main thread, so we can display stuff!
    def __init__(self, caller):
        self.caller = caller
        threading.Thread.__init__(self)

    def run(self):
        with ActivityIndicator("Building...") as activity_indicator:
            self.worker(activity_indicator)

    def worker(self, activity_indicator):
        logger.debug(f"Welcome to thread {self.name}")
        self.caller.output(
            f"[Compiling '{self.caller.builder.tex_root}' with '{self.caller.builder.name}']\n"
        )

        # Remove old log-file to prevent displaying out-dated error information
        # on pre-mature build termination.
        log_filename = f"{self.caller.builder.base_name}.log"
        for log_dir in (self.caller.builder.aux_directory_full, self.caller.builder.tex_dir):
            if log_dir:
                try:
                    os.remove(os.path.join(log_dir, log_filename))
                except OSError:
                    pass

        # Now, iteratively call the builder iterator
        aborted = False
        pending = False
        cmd_coroutine = self.caller.builder.commands()
        try:
            cmd, msg = next(cmd_coroutine)
            while True:
                if msg:
                    self.caller.output(msg)
                    pending = True

                if cmd and isinstance(cmd, (list, str)):
                    proc = self.caller.builder.command(cmd)
                elif cmd and isinstance(cmd, Popen):
                    proc = cmd
                else:
                    # don't know what the command is
                    pending = False
                    continue

                # Now actually invoke the command, making sure we allow for
                # killing First, save process handle into caller; then
                # communicate (which blocks)
                with self.caller.proc_lock:
                    self.caller.proc = proc

                out, _ = proc.communicate()
                if out is not None:
                    out = out.decode(self.caller.encoding, "ignore")
                    out = out.replace("\r\n", "\n").replace("\r", "\n")

                # Here the process terminated, but it may have been killed. If
                # so, stop and don't read log Since we set self.caller.proc
                # above, if it is None, the process must have been killed.
                with self.caller.proc_lock:
                    if not self.caller.proc:
                        logger.info("Build canceled")
                        msg = "\n[Build cancelled by user!]"
                        if pending:
                            msg = "cancelled\n" + msg
                        self.caller.show_output_panel()
                        self.caller.output(msg)
                        self.caller.finish(False)
                        pending = False
                        return

                    self.caller.proc = None

                self.caller.builder.set_output(out)

                # print and handle command exit status
                logger.info(f"Finished with status {proc.returncode}.")
                if pending:
                    self.caller.output("error\n" if proc.returncode else "done\n")
                    pending = False
                if self.caller.builder.abort_on_error and proc.returncode != 0:
                    # abort and parse logfile or command output for details
                    aborted = True
                    break

                # acknowledge coroutine's yield with process's return code
                # it allows statements like: `result = yield (cmd, msg)`
                cmd, msg = cmd_coroutine.send(proc.returncode)

        except StopIteration:
            with self.caller.proc_lock:
                self.caller.proc = None
            pending = False

        except Exception as exc:
            with self.caller.proc_lock:
                self.caller.proc = None
            msg = f"\nError: {exc}\n\n[Build failed!]"
            if pending:
                msg = "aborted\n" + msg
            self.caller.show_output_panel()
            self.caller.output(msg)
            self.caller.finish(False)
            traceback.print_exc()
            pending = False
            return

        finally:
            cmd_coroutine.close()

        try:
            if self.caller.builder.aux_directory_full:
                log_file = os.path.join(self.caller.builder.aux_directory_full, log_filename)
                if not os.path.exists(log_file):
                    log_file = os.path.join(self.caller.builder.tex_dir, log_filename)
            else:
                log_file = os.path.join(self.caller.builder.tex_dir, log_filename)

            # CHANGED 12-10-27. OK, here's the deal. We must open in binary mode
            # on Windows because silly MiKTeX inserts ASCII control characters in
            # over/underfull warnings. In particular it inserts EOFs, which
            # stop reading altogether; reading in binary prevents that. However,
            # that's not the whole story: if a FS character is encountered,
            # AND if we invoke splitlines on a STRING, it sadly breaks the line
            # in two. This messes up line numbers in error reports. If, on the
            # other hand, we invoke splitlines on a byte array (? whatever read()
            # returns), this does not happen---we only break at \n, etc.
            # However, we must still decode the resulting lines using the relevant
            # encoding.
            with open(log_file, "rb") as f:
                data = f.read()

        except FileNotFoundError:
            # If no log file was created, and all processes finished with exit code 0,
            # build steps were skipped most likely due to PDF still being up-to-date.
            # Note: At least latexmk is known to behave like that.
            self.caller.show_output_panel()
            self.caller.output("\n[Build failed!]" if aborted else "\n[Build skipped!]")
            self.caller.finish(aborted == False)

        except OSError:
            self.caller.show_output_panel()
            self.caller.output(f"\nCould not read log file {log_filename}\n\n[Build failed!]")
            self.caller.finish(False)

        else:
            errors = []
            warnings = []
            badboxes = []

            try:
                ws = re.compile(r"\s+")
                (errors, warnings, badboxes) = parse_tex_log(data, self.caller.builder.tex_dir)
                content = [""]
                if errors:
                    content.append("Errors:")
                    content.append("")
                    content.extend((ws.sub(" ", e) for e in errors))
                else:
                    content.append("No errors.")
                if warnings:
                    if errors:
                        content.extend(["", "Warnings:"])
                    else:
                        content[-1] = content[-1] + " Warnings:"
                    content.append("")
                    content.extend((ws.sub(" ", w) for w in warnings))
                else:
                    if errors:
                        content.append("")
                        content.append("No warnings.")
                    else:
                        content[-1] = content[-1] + " No warnings."

                if badboxes and self.caller.display_bad_boxes:
                    if warnings or errors:
                        content.extend(["", "Bad Boxes:"])
                    else:
                        content[-1] = content[-1] + " Bad Boxes:"
                    content.append("")
                    content.extend(badboxes)
                else:
                    if self.caller.display_bad_boxes:
                        if errors or warnings:
                            content.append("")
                            content.append("No bad boxes.")
                        else:
                            content[-1] = content[-1] + " No bad boxes."

                content.append("")
                content.append(log_file + ":1: Double-click here to open the full log.")

                show_panel = {
                    "always": False,
                    "no_errors": bool(errors),
                    "no_warnings": bool(errors or warnings),
                    "no_badboxes": bool(
                        errors or warnings or (self.caller.display_bad_boxes and badboxes)
                    ),
                    "never": True,
                }.get(self.caller.hide_panel_level, bool(errors or warnings))

                if show_panel:
                    activity_indicator.finish("Build completed")
                    self.caller.show_output_panel(force=True)
                else:
                    message = "Build completed"
                    if errors:
                        message += " with errors"
                    if warnings:
                        if errors:
                            if badboxes and self.caller.display_bad_boxes:
                                message += ","
                            else:
                                message += " and"
                        else:
                            message += " with"
                        message += " warnings"
                    if badboxes and self.caller.display_bad_boxes:
                        if errors or warnings:
                            message += " and"
                        else:
                            message += " with"
                        message += " bad boxes"

                    activity_indicator.finish(message)
            except Exception as e:
                activity_indicator.finish("Build failed!")
                self.caller.show_output_panel()
                content = [
                    "",
                    "",
                    f"LaTeXTools could not parse the TeX log file {log_file}",
                    "(actually, we never should have gotten here)",
                    "",
                    f"Python exception: {e!r}",
                    "",
                    "The full error description can be found on the console.",
                    "Please let us know on GitHub. Thanks!",
                ]

                traceback.print_exc()

            self.caller.output(content)
            self.caller.output("\n\n[Build failed!]" if aborted else "\n\n[Done!]")

            self.caller.errors = errors
            self.caller.warnings = warnings
            self.caller.badboxes = badboxes

            self.caller.finish(aborted == False and len(errors) == 0)


annotation_sets_by_buffer = {}


class LatextoolsMakePdfCommand(sublime_plugin.WindowCommand):
    errs_by_file = {}
    show_errors_inline = True
    errors = []
    warnings = []
    badboxes = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proc = None
        self.proc_lock = threading.Lock()

    # **kwargs is unused but there so run can safely ignore any unknown
    # parameters
    def run(
        self,
        file_regex="",
        program=None,
        builder=None,
        command=None,
        options=None,
        shell=False,
        env=None,
        path=None,
        script_commands=None,
        update_annotations_only=False,
        hide_annotations_only=False,
        kill=False,
        **kwargs
    ):
        if update_annotations_only:
            if self.show_errors_inline:
                self.update_annotations()
            return

        if hide_annotations_only:
            self.hide_annotations()
            return

        # kill running build process
        with self.proc_lock:
            if self.proc:
                proc = self.proc
                self.proc = None
                try:
                    # On Windows use taskkill, to make sure all child processes
                    # are terminated as well.
                    if sublime.platform() == "windows":
                        execute_command(
                            f"taskkill /t /f /pid {proc.pid}",
                            use_texpath=False,
                            shell=True,
                        )
                    else:
                        proc.terminate()
                except Exception:
                    logger.error("Exception occurred while killing build")
                    traceback.print_exc()

        # cancel_build command was invoked to just terminate running build
        if kill:
            return

        view = self.view = self.window.active_view()

        self.hide_annotations()
        pref_settings = sublime.load_settings("Preferences.sublime-settings")
        self.show_errors_inline = pref_settings.get("show_errors_inline", True)

        if view.file_name() is None:
            sublime.error_message("Please save your file before attempting to build.")
            return

        if view.is_dirty():
            logger.info("saving...")
            view.run_command("save")  # call this on view, not self.window

        tex_root = get_tex_root(view)
        if not tex_root:
            sublime.error_message(f"Main TeX file not found.")
            return
        if not os.path.isfile(tex_root):
            sublime.error_message(f"{tex_root}: file not found.")
            return

        tex_dir, tex_name = os.path.split(tex_root)

        if not is_tex_file(tex_root):
            sublime.error_message(f"{tex_name} is not a TeX source file: cannot compile.")
            return

        # Output panel: from exec.py
        if not hasattr(self, "output_view"):
            self.output_view = self.window.get_output_panel("latextools")

        output_view_settings = self.output_view.settings()
        output_view_settings.set("result_file_regex", file_regex)
        output_view_settings.set("result_base_dir", tex_dir)
        output_view_settings.set("auto_match_enabled", False)
        output_view_settings.set("draw_indent_guides", False)
        output_view_settings.set("draw_white_space", "none")
        output_view_settings.set("detect_indentation", False)
        output_view_settings.set("disable_auto_complete", False)
        output_view_settings.set("gutter", False)
        output_view_settings.set("scroll_past_end", False)
        output_view_settings.set("tab_size", 2)
        output_view_settings.set("word_wrap", get_setting("build_panel_word_wrap", False, view))

        if get_setting("highlight_build_panel", True, view):
            output_view_settings.set(
                "syntax", "Packages/LaTeXTools/LaTeXTools Build Output.sublime-syntax"
            )

        self.output_view.set_read_only(True)

        # Dumb, but required for the moment for the output panel to be picked
        # up as the result buffer
        self.window.get_output_panel("latextools")

        self.hide_panel_level = get_setting("hide_build_panel", "no_warnings", view)
        if self.hide_panel_level == "never":
            self.show_output_panel(force=True)

        self.plat = sublime.platform()
        if self.plat == "osx":
            self.encoding = "UTF-8"
        elif self.plat == "windows":
            self.encoding = "oem"
        elif self.plat == "linux":
            self.encoding = "UTF-8"
        else:
            sublime.error_message("Platform as yet unsupported. Sorry!")
            return

        # Get platform settings, builder, and builder settings
        platform_settings = get_setting(self.plat, {}, view)
        self.display_bad_boxes = get_setting("display_bad_boxes", False, view)

        if builder is not None:
            builder_name = builder
        else:
            builder_name = get_setting("builder", "traditional", view)

        # Default to 'traditional' builder
        if builder_name in ["", "default"]:
            builder_name = "traditional"

        # this is to convert old-style names (e.g. AReallyLongName)
        # to new style plugin names (a_really_long_name)
        builder_name = classname_to_plugin_name(builder_name)

        builder_settings = get_setting("builder_settings", {}, view)
        builder_platform_settings = builder_settings.get(self.plat, {})

        # override the command
        if command is not None:
            builder_settings.set("command", command)

        # parse root for any %!TEX directives
        tex_directives = parse_tex_directives(
            tex_root, multi_values=["options"], key_maps={"ts-program": "program"}
        )

        # determine the engine
        if program is None:
            program = tex_directives.get("program")
            if not program:
                program = builder_platform_settings.get("program")
                if not program:
                    program = builder_settings.get("program")
        if program and isinstance(program, str):
            program = program.lower()
            # Sanity check: if "strange" engine, default to pdflatex (silently...)
            if program not in SUPPORTED_PDF_COMPILERS:
                program = "pdflatex"
        else:
            program = "pdflatex"

        # Collect and merge options
        if options is None:
            options = builder_platform_settings.get("options")
            if options is None:
                options = builder_settings.get("options", [])
        if isinstance(options, str):
            options = shlex.split(options)
        elif not isinstance(options, list):
            options = []

        tex_options = tex_directives.pop("options", [])
        if isinstance(tex_options, str):
            tex_options = shlex.split(tex_options)
        elif not isinstance(tex_options, list):
            tex_options = []

        options = set(options) | set(tex_options)
        # filter out separately handled options
        options -= set(("--aux-directory", "--output-directory", "--jobname"))
        options = sorted(options)

        # Create custom environmnent with "env" from sublime-build or
        # platform-specific "builder_settings" merged in.
        if env is None:
            env = builder_platform_settings.get("env")
            if env is None:
                env = builder_settings.get("env")
        if env is not None:
            _env = os.environ.copy()
            _env.update({k: os.path.expandvars(v) for k, v in env.items()})
            env = _env

        # Replace $PATH in environment with "path" from sublime-build or
        # "texpath" from project-specific, or platform-specifig "builder_settings".
        if (path is not None) or (path := get_texpath(self.view)):
            if env is None:
                env = os.environ.copy()
            env["PATH"] = path

        try:
            builder = get_plugin(f"{builder_name}_builder")
        except NoSuchPluginException:
            try:
                builder = get_plugin(builder_name)
            except NoSuchPluginException:
                sublime.error_message(
                    f"Cannot find builder {builder_name}.\n"
                    "Check your LaTeXTools Preferences"
                )
                self.window.run_command("hide_panel", {"panel": "output.latextools"})
                return

        if builder_name == "script" and script_commands:
            builder_platform_settings["script_commands"] = script_commands
            builder_settings[self.plat] = builder_platform_settings

        self.builder = builder(
            tex_root,
            self.output,
            program,
            options,
            get_aux_directory(view),
            get_output_directory(view),
            get_jobname(view),
            tex_directives,
            builder_settings,
            platform_settings,
            shell,
            env,
        )

        thread = CmdThread(self)
        thread.start()

    def output(self, data):
        if isinstance(data, (list, tuple)):
            data = "\n".join(data)
        self.output_view.run_command(
            "append", {"characters": data, "force": True, "scroll_to_end": True}
        )

    def show_output_panel(self, force=False):
        if force or self.hide_panel_level != "always":
            self.window.run_command("show_panel", {"panel": "output.latextools"})

    # Also from exec.py
    # Set the selection to the start of the output panel, so next_result works
    # Then run viewer

    def finish(self, can_switch_to_pdf):
        sublime.set_timeout(functools.partial(self.do_finish, can_switch_to_pdf), 0)

    def do_finish(self, can_switch_to_pdf):
        if get_setting("scroll_build_panel_to_top", False, self.view) is True:
            self.output_view.show(0, show_surrounds=False, keep_to_left=True, animate=False)

        if self.show_errors_inline:
            self.create_errs_by_file()
            self.update_annotations()

        # can_switch_to_pdf indicates a pdf should've been created
        if can_switch_to_pdf and get_setting("open_pdf_on_build", True, self.view):
            self.window.run_command("latextools_jumpto_pdf", {"from_keybinding": False})

    def _find_errors(self, errors, error_class):
        for line in errors:
            m = self.file_regex.search(line)
            if not m:
                continue
            groups = m.groups()
            if len(groups) == 4:
                file, line, column, text = groups
            else:
                continue
            if line is None:
                continue
            line = int(line)
            column = int(column) if column else 0
            if file not in self.errs_by_file:
                self.errs_by_file[file] = []
            self.errs_by_file[file].append((line, column, text, error_class))

    def create_errs_by_file(self):
        file_regex = self.output_view.settings().get("result_file_regex")
        if not file_regex:
            return
        self.errs_by_file = {}
        try:
            self.file_regex = re.compile(file_regex, re.MULTILINE)
        except Exception:
            logger.error("Cannot compile file regex.")
            return
        level_name = get_setting("show_error_phantoms", "warnings", {})
        level = {"none": 0, "errors": 1, "warnings": 2, "badboxes": 3}.get(level_name, 2)

        if level >= 1:
            self._find_errors(self.errors, "error")
        if level >= 2:
            self._find_errors(self.warnings, "warning")
        if level >= 3:
            self._find_errors(self.badboxes, "warning badbox")

    def update_annotations(self):
        stylesheet = """
            <style>
                div.lt-error {
                    padding: 0.4rem 0 0.4rem 0.7rem;
                    margin: 0.2rem 0;
                    border-radius: 2px;
                }
                div.lt-error span.message {
                    padding-right: 0.7rem;
                }
                div.lt-error a {
                    text-decoration: inherit;
                    padding: 0.35rem 0.7rem 0.45rem 0.8rem;
                    position: relative;
                    bottom: 0.05rem;
                    border-radius: 0 2px 2px 0;
                    font-weight: bold;
                }
                html.dark div.lt-error a {
                    background-color: #00000018;
                }
                html.light div.lt-error a {
                    background-color: #ffffff18;
                }
            </style>
        """

        def on_navigate(href):
            if href == "hide":
                self.hide_annotations()

        for file, errs in self.errs_by_file.items():
            view = self.window.find_open_file(file)
            if view:

                buffer_id = view.buffer_id()
                if buffer_id not in annotation_sets_by_buffer:
                    phantom_set = sublime.PhantomSet(view, "lt_exec")
                    annotation_sets_by_buffer[buffer_id] = phantom_set
                else:
                    phantom_set = annotation_sets_by_buffer[buffer_id]

                phantoms = []

                for line, column, text, error_class in errs:
                    pt = view.text_point(line - 1, column - 1)
                    html_text = html.escape(text, quote=False)
                    phantom_content = f"""
                        <body id="inline-error">
                            {stylesheet}
                            <div class="lt-error {error_class}">
                                <span class="message">{html_text}</span>
                                <a href="hide">{chr(0x00D7)}</a>
                            </div>
                        </body>
                    """
                    phantoms.append(
                        sublime.Phantom(
                            sublime.Region(pt, view.line(pt).b),
                            phantom_content,
                            sublime.LAYOUT_BELOW,
                            on_navigate=on_navigate,
                        )
                    )

                phantom_set.update(phantoms)

    def hide_annotations(self):
        global annotation_sets_by_buffer
        for file, errs in self.errs_by_file.items():
            view = self.window.find_open_file(file)
            if view:
                del annotation_sets_by_buffer[view.buffer_id()]

        self.errs_by_file = {}
        self.show_errors_inline = False


class LatextoolsExecEventListener(sublime_plugin.EventListener):
    def on_load(self, view):
        # assign latex log syntax based on view's first line
        if view.match_selector(0, "text.plain"):
            first_line = view.substr(sublime.Region(0, 40))
            if re.search(r"^This is (?:LuaHB|pdfe?|Xe)?(?:La)?TeXk?, Version ", first_line):
                view.assign_syntax("LaTeXTools Log.sublime-syntax")
            return

        # update build result annotations
        if view.match_selector(0, "text.tex"):
            w = view.window()
            if w is not None:
                w.run_command("latextools_make_pdf", {"update_annotations_only": True})

    def on_query_context(self, view, key, operator, operand, match_all):
        # provide context for conditional key bindings
        if key != "latextools_inline_errors_visible":
            return False

        result = bool(annotation_sets_by_buffer.get(view.buffer_id(), False))

        if operator == sublime.OP_EQUAL:
            return result == operand

        if operator == sublime.OP_NOT_EQUAL:
            return result != operand

        raise Exception(
            "latextools_inline_errors_visible; " "Invalid operator must be EQUAL or NOT_EQUAL."
        )
