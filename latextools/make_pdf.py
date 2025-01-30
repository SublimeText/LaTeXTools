"""
Compile current .tex file to pdf
Allow custom scripts and build engines!

The actual work is done by builders, loaded on-demand from prefs
"""
import functools
import html
import os
import re
import shutil
import signal
import subprocess
import threading
import traceback

import sublime
import sublime_plugin

from .deprecated_command import deprecate
from .latextools_plugin import _classname_to_internal_name
from .latextools_plugin import add_plugin_path
from .latextools_plugin import get_plugin
from .latextools_plugin import NoSuchPluginException
from .utils.activity_indicator import ActivityIndicator
from .utils.external_command import execute_command
from .utils.external_command import external_command
from .utils.external_command import get_texpath
from .utils.external_command import update_env
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
    "LatextoolsDoOutputEditCommand",
    "LatextoolsDoFinishEditCommand",
    "LatextoolsExecEventListener",
]

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
        logger.debug("Welcome to thread %s", self.getName())
        self.caller.output("[Compiling " + self.caller.file_name + "]")

        env = dict(os.environ)
        if self.caller.path:
            env["PATH"] = self.caller.path

        # Handle custom env variables
        if self.caller.env:
            update_env(env, self.caller.env)

        # Now, iteratively call the builder iterator
        #
        cmd_iterator = self.caller.builder.commands()
        try:
            for cmd, msg in cmd_iterator:

                # If there is a message, display it
                if msg:
                    self.caller.output(msg)

                # If there is nothing to be done, exit loop
                # (Avoids error with empty cmd_iterator)
                if cmd == "":
                    break

                if isinstance(cmd, str) or isinstance(cmd, list):
                    logger.debug(cmd)
                    # Now create a Popen object
                    try:
                        proc = external_command(
                            cmd,
                            env=env,
                            use_texpath=False,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            preexec_fn=(os.setsid if self.caller.plat != "windows" else None),
                            cwd=self.caller.tex_dir,
                        )
                    except Exception:
                        self.caller.show_output_panel()
                        self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
                        self.caller.output("Attempted command:")
                        self.caller.output(subprocess.list2cmdline(cmd))
                        self.caller.output("\nBuild engine: " + self.caller.builder.name)
                        self.caller.proc = None
                        traceback.print_exc()
                        return
                # Abundance of caution / for possible future extensions:
                elif isinstance(cmd, subprocess.Popen):
                    proc = cmd
                else:
                    # don't know what the command is
                    continue

                # Now actually invoke the command, making sure we allow for killing
                # First, save process handle into caller; then communicate (which blocks)
                with self.caller.proc_lock:
                    self.caller.proc = proc
                out, err = proc.communicate()
                out = out.decode(self.caller.encoding, "ignore")
                out = out.replace("\r\n", "\n").replace("\r", "\n")
                self.caller.builder.set_output(out)

                # Here the process terminated, but it may have been killed. If so, stop and don't read log
                # Since we set self.caller.proc above, if it is None, the process must have been killed.
                # TODO: clean up?
                with self.caller.proc_lock:
                    if not self.caller.proc:
                        logger.info("Build canceled")
                        logger.debug("with returncode %d", proc.returncode)
                        self.caller.output("\n\n[User terminated compilation process]\n")
                        self.caller.finish(False)  # We kill, so won't switch to PDF anyway
                        return
                # Here we are done cleanly:
                with self.caller.proc_lock:
                    self.caller.proc = None
                logger.info("Finished normally")
                logger.debug("with returncode %d", proc.returncode)
                # At this point, out contains the output from the current command;
                # we pass it to the cmd_iterator and get the next command, until completion
        except Exception:
            self.caller.show_output_panel()
            self.caller.output("\n\nCOULD NOT COMPILE!\n\n")
            self.caller.output("\nBuild engine: " + self.caller.builder.name)
            self.caller.proc = None
            traceback.print_exc()
            return

        # Clean up
        cmd_iterator.close()

        try:
            # Here we try to find the log file...
            # 1. Check the aux_directory if there is one
            # 2. Check the output_directory if there is one
            # 3. Assume the log file is in the same folder as the main file
            log_file_base = self.caller.tex_base + ".log"
            if self.caller.aux_directory is None:
                if self.caller.output_directory is None:
                    log_file = os.path.join(self.caller.tex_dir, log_file_base)
                else:
                    log_file = os.path.join(self.caller.output_directory, log_file_base)

                    if not os.path.exists(log_file):
                        log_file = os.path.join(self.caller.tex_dir, log_file_base)
            else:
                log_file = os.path.join(self.caller.aux_directory, log_file_base)

                if not os.path.exists(log_file):
                    if (
                        self.caller.output_directory is not None
                        and self.caller.output_directory != self.caller.aux_directory
                    ):
                        log_file = os.path.join(self.caller.output_directory, log_file_base)

                    if not os.path.exists(log_file):
                        log_file = os.path.join(self.caller.tex_dir, log_file_base)

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

            # Note to self: need to think whether we don't want to codecs.open
            # this, too... Also, we may want to move part of this logic to the
            # builder...
            with open(log_file, "rb") as f:
                data = f.read()
        except IOError:
            traceback.print_exc()

            self.caller.show_output_panel()

            content = [
                "",
                "Could not read log file {0}.log".format(self.caller.tex_base),
                "",
            ]
            if out is not None:
                content.extend(["Output from compilation:", "", out.decode("utf-8")])
            if err is not None:
                content.extend(["Errors from compilation:", "", err.decode("utf-8")])
            self.caller.output(content)
            # if we got here, there shouldn't be a PDF at all
            self.caller.finish(False)
        else:
            errors = []
            warnings = []
            badboxes = []

            try:
                ws = re.compile(r"\s+")
                (errors, warnings, badboxes) = parse_tex_log(data, self.caller.tex_dir)
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
                content = ["", ""]
                content.append("LaTeXTools could not parse the TeX log file {0}".format(log_file))
                content.append("(actually, we never should have gotten here)")
                content.append("")
                content.append("Python exception: {0!r}".format(e))
                content.append("")
                content.append("The full error description can be found on the console.")
                content.append("Please let us know on GitHub. Thanks!")

                traceback.print_exc()

            self.caller.output(content)
            self.caller.output("\n\n[Done!]\n")

            self.caller.errors = locals().get("errors", [])
            self.caller.warnings = locals().get("warnings", [])
            self.caller.badboxes = locals().get("badboxes", [])

            self.caller.finish(len(errors) == 0)


annotation_sets_by_buffer = {}


class LatextoolsMakePdfCommand(sublime_plugin.WindowCommand):
    errs_by_file = {}
    show_errors_inline = True
    errors = []
    warnings = []
    badboxes = []

    def __init__(self, *args, **kwargs):
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)
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
        env=None,
        path=None,
        script_commands=None,
        update_annotations_only=False,
        hide_annotations_only=False,
        **kwargs
    ):
        if update_annotations_only:
            if self.show_errors_inline:
                self.update_annotations()
            return

        if hide_annotations_only:
            self.hide_annotations()
            return

        # Try to handle killing
        with self.proc_lock:
            if self.proc:  # if we are running, try to kill running process
                self.output("\n\n### Got request to terminate compilation ###")
                try:
                    if sublime.platform() == "windows":
                        execute_command(
                            "taskkill /t /f /pid {pid}".format(pid=self.proc.pid),
                            use_texpath=False,
                            shell=True,
                        )
                    else:
                        os.killpg(self.proc.pid, signal.SIGTERM)
                except Exception:
                    logger.error("Exception occurred while killing build")
                    traceback.print_exc()

                self.proc = None
                return
            else:  # either it's the first time we run, or else we have no running processes
                self.proc = None

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

        self.file_name = get_tex_root(view)
        if not os.path.isfile(self.file_name):
            sublime.error_message(self.file_name + ": file not found.")
            return

        self.tex_base = get_jobname(view)
        self.tex_dir = os.path.dirname(self.file_name)

        if not is_tex_file(self.file_name):
            sublime.error_message(
                "%s is not a TeX source file: cannot compile."
                % (os.path.basename(view.file_name()),)
            )
            return

        # Output panel: from exec.py
        if not hasattr(self, "output_view"):
            self.output_view = self.window.get_output_panel("latextools")

        output_view_settings = self.output_view.settings()
        output_view_settings.set("result_file_regex", file_regex)
        output_view_settings.set("result_base_dir", self.tex_dir)
        output_view_settings.set("line_numbers", False)
        output_view_settings.set("gutter", False)
        output_view_settings.set("scroll_past_end", False)

        if get_setting("highlight_build_panel", True, view):
            output_view_settings.set(
                "syntax", "Packages/LaTeXTools/LaTeXTools Console.sublime-syntax"
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
        builder_name = _classname_to_internal_name(builder_name)

        builder_settings = get_setting("builder_settings", {}, view)

        # override the command
        if command is not None:
            builder_settings.set("command", command)

        # parse root for any %!TEX directives
        tex_directives = parse_tex_directives(
            self.file_name, multi_values=["options"], key_maps={"ts-program": "program"}
        )

        # determine the engine
        if program is not None:
            engine = program
        else:
            engine = tex_directives.get("program", builder_settings.get("program", "pdflatex"))

        engine = engine.lower()

        # Sanity check: if "strange" engine, default to pdflatex (silently...)
        if engine not in [
            "pdflatex",
            "pdftex",
            "xelatex",
            "xetex",
            "lualatex",
            "luatex",
        ]:
            engine = "pdflatex"

        options = builder_settings.get("options", [])
        if isinstance(options, str):
            options = [options]

        if "options" in tex_directives:
            options.extend(tex_directives["options"])

        # filter out --aux-directory and --output-directory options which are
        # handled separately
        options = [
            opt
            for opt in options
            if (
                not opt.startswith("--aux-directory")
                and not opt.startswith("--output-directory")
                and not opt.startswith("--jobname")
            )
        ]

        self.aux_directory = get_aux_directory(view)
        self.output_directory = get_output_directory(view)

        # Read the env option (platform specific)
        builder_platform_settings = builder_settings.get(self.plat, {})

        if env is not None:
            self.env = env
        elif builder_platform_settings:
            self.env = builder_platform_settings.get("env", None)
        else:
            self.env = None

        # Safety check: if we are using a built-in builder, disregard
        # builder_path, even if it was specified in the pref file
        if builder_name in ["simple", "traditional", "script", "basic"]:
            builder_path = None
        else:
            # relative to ST packages dir!
            builder_path = get_setting("builder_path", "", view)

        if builder_path:
            bld_path = os.path.join(sublime.packages_path(), builder_path)
            add_plugin_path(bld_path)

        try:
            builder = get_plugin("{0}_builder".format(builder_name))
        except NoSuchPluginException:
            try:
                builder = get_plugin(builder_name)
            except NoSuchPluginException:
                sublime.error_message(
                    "Cannot find builder {0}.\n"
                    "Check your LaTeXTools Preferences".format(builder_name)
                )
                self.window.run_command("hide_panel", {"panel": "output.latextools"})
                return

        if builder_name == "script" and script_commands:
            builder_platform_settings["script_commands"] = script_commands
            builder_settings[self.plat] = builder_platform_settings

        logger.debug(repr(builder))
        self.builder = builder(
            self.file_name,
            self.output,
            engine,
            options,
            self.aux_directory,
            self.output_directory,
            self.tex_base,
            tex_directives,
            builder_settings,
            platform_settings,
        )

        # Now get the tex binary path from prefs, change directory to
        # that of the tex root file, and run!
        if path is not None:
            self.path = path
        else:
            self.path = get_texpath() or os.environ["PATH"]

        thread = CmdThread(self)
        thread.start()
        logger.debug(threading.active_count())

    def output(self, data):
        if isinstance(data, list) or isinstance(data, tuple):
            data = "\n".join(data)
        data = data.replace("\r\n", "\n").replace("\r", "\n")
        self.output_view.run_command("latextools_do_output_edit", {"data": data})

    def show_output_panel(self, force=False):
        if force or self.hide_panel_level != "always":
            self.window.run_command("show_panel", {"panel": "output.latextools"})

    # Also from exec.py
    # Set the selection to the start of the output panel, so next_result works
    # Then run viewer

    def finish(self, can_switch_to_pdf):
        sublime.set_timeout(functools.partial(self.do_finish, can_switch_to_pdf), 0)

    def do_finish(self, can_switch_to_pdf):
        self.output_view.run_command("latextools_do_finish_edit")

        if self.show_errors_inline:
            self.create_errs_by_file()
            self.update_annotations()

        # can_switch_to_pdf indicates a pdf should've been created
        if can_switch_to_pdf:
            # if using output_directory, follow the copy_output_on_build setting
            # files are copied to the same directory as the main tex file
            if self.output_directory is not None:
                copy_on_build = get_setting("copy_output_on_build", True, self.view)
                if copy_on_build is None or copy_on_build is True:
                    shutil.copy2(
                        os.path.join(self.output_directory, self.tex_base + ".pdf"),
                        os.path.dirname(self.file_name),
                    )
                elif isinstance(copy_on_build, list):
                    for ext in copy_on_build:
                        copy_file = os.path.join(self.output_directory, self.tex_base + ext)
                        if os.path.isfile(copy_file):
                            shutil.copy2(copy_file, os.path.dirname(self.file_name))

            if get_setting("open_pdf_on_build", True, self.view):
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
                    phantom_content = """
                        <body id="inline-error">
                            {stylesheet}
                            <div class="lt-error {error_class}">
                                <span class="message">{html_text}</span>
                                <a href="hide">{cancel_char}</a>
                            </div>
                        </body>
                    """.format(
                        cancel_char=chr(0x00D7), **locals()
                    )
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


class LatextoolsDoOutputEditCommand(sublime_plugin.TextCommand):
    def run(self, edit, data):
        view = self.view
        sel = view.sel()
        sel_at_end = len(sel) == 1 and sel[0].end() == view.size()
        view.set_read_only(False)
        view.insert(edit, view.size(), data)
        view.set_read_only(True)
        if sel_at_end:
            view.show(view.size())


class LatextoolsDoFinishEditCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().clear()
        reg = sublime.Region(0)
        self.view.sel().add(reg)
        self.view.show(reg)


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


def latextools_plugin_loaded():
    # load the plugins from the builders dir
    ltt_path = os.path.join(sublime.packages_path(), "LaTeXTools", "plugins", "builder")
    # ensure that pdfBuilder is loaded first as otherwise, the other builders
    # will not be registered as plugins
    add_plugin_path(os.path.join(ltt_path, "pdf_builder.py"))
    add_plugin_path(ltt_path)


deprecate(globals(), "make_pdfCommand", LatextoolsMakePdfCommand)
deprecate(globals(), "DoOutputEditCommand", LatextoolsDoOutputEditCommand)
deprecate(globals(), "DoFinishEditCommand", LatextoolsDoFinishEditCommand)
