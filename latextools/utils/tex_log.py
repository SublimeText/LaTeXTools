from __future__ import annotations
from itertools import chain
import os
import regex as re
import sublime
import sublime_plugin


class LogRule:
    MAX_MSG: int = 400
    selector: str

    @classmethod
    def process_text(cls, text: str) -> tuple[int, str]:
        raise NotImplementedError


class BadboxLogRule(LogRule):
    selector = "meta.warning.box.log - punctuation.terminator"

    @classmethod
    def process_text(cls, text: str) -> tuple[int, str]:
        msg = re.split(r"\.$|\[\]|\n", text, 1, re.M)[0]
        msg = re.sub(r"\s+", " ", msg, re.M)
        msg = msg.replace("\n", "")
        msg = msg.strip()
        if len(msg) > cls.MAX_MSG:
            msg = msg[: cls.MAX_MSG] + "..."

        if match := re.search(r"lines?\s*(\d+)", text.replace("\n", ""), re.M):
            line = int(match.group(1))
        else:
            line = 0

        return (line, msg)


class ExceptionLogRule(LogRule):
    selector = "meta.exception.log"

    @classmethod
    def undefined_control_sequence(cls, text) -> tuple[int, str] | None:
        R"""
        Handles messages like:

        ! Undefined control sequence.
        \imprimirautor ->\theauthor

        l.49         }

        ! Undefined control sequence.
        l.1229 ...canonical \) in \( \SO(8) \) is \( \Spin
                                                          (7) \), see~\cite[Theorem~...
        The control sequence at the end of the top line
        ...and I'll forget about whatever was undefined.
        """
        ucs = re.search(
            r"^(Undefined control sequence)\.\n"
            r"(?:.*\n)*?"             # optional details about invalid sequence
            r"l\.(\d+)"               # line number, exception was detected at
            r"[ ]+([^\n]+)\n"         # command name
            r"(?:[ ]{3,}([^\n]+))?",  # command continuation (arguments)
            text,
            re.M,
        )
        if ucs:
            msg, line, seq1, seq2 = ucs.groups()
            msg = f"{msg} near {seq1}{seq2 or ''}"
            msg = re.sub(r"\s+", " ", msg)
            return (int(line), msg)
        return None

    @classmethod
    def any_exception(cls, text: str) -> tuple[int, str]:
        msg = re.split(r"\.$", text, 1, re.M)[0]
        msg = re.sub(r"\s+", " ", msg, re.M)
        msg = msg.replace("\n", "")
        msg = msg.strip()
        if len(msg) > cls.MAX_MSG:
            msg = msg[: cls.MAX_MSG] + "..."

        if match := re.search(r"^l\.(\d+)", text, re.M):
            line = int(match.group(1))
        else:
            line = 0

        return (line, msg)

    @classmethod
    def process_text(cls, text: str) -> tuple[int, str]:
        msg = text[2:]  # skip leading `! `
        for handler in (
            cls.undefined_control_sequence,
        ):
            if result := handler(msg):
                return result

        return cls.any_exception(msg)


class ErrorLogRule(LogRule):
    selector = "meta.error.log - markup.error"

    @classmethod
    def process_text(cls, text: str) -> tuple[int, str]:
        msg = re.split(r"\.$", text, 1, re.M)[0]
        msg = re.sub(r"\n(?:\(\S+\)[^\S\n]+)", r" ", msg, re.M)
        msg = re.sub(r"\s+", " ", msg, re.M)
        msg = msg.replace("\n", "")
        msg = msg.strip()
        if len(msg) > cls.MAX_MSG:
            msg = msg[: cls.MAX_MSG] + "..."

        if match := re.search(r"line\s*(\d+)", text.replace("\n", ""), re.M):
            line = int(match.group(1))
        else:
            line = 0

        return (line, msg)


class WarningLogRule(ErrorLogRule):
    selector = "meta.warning.log - markup.warning"


def parse_log_view(view: sublime.View) -> tuple[list[str], list[str], list[str]]:
    """
    Extract errors, warnings and badbox messages from a `sublime.View`.

    This function relies on log file already being tokenized by
    `LaTeXTools Log.sublime-syntax` syntax.

    :param view:
        The view to extract log items from.

    :returns:
        3-tuple of lists of strings, containing results
    """
    # gather all blocks
    blocks = []
    selector = "meta.block.log"
    while regs := view.find_by_selector(selector):
        blocks.extend(regs)
        selector += " meta.block.log"

    # associate blocks with file names and sort by starting position
    # assumption: each `meta.block` starts with an `entity.name.section.filename`.
    blocks = [
        (block, os.path.normpath(view.substr(filename).replace("\n", "").strip()))
        for block, filename in zip(
            sorted(blocks),
            view.find_by_selector(
                "entity.name.section.filename.log - punctuation.definition.entity"
            ),
        )
    ]

    def extract_items(rule: type[LogRule]) -> list[str]:
        items = []
        for reg in view.find_by_selector(rule.selector):
            for sreg, fname in reversed(blocks):
                if reg in sreg:
                    item = (fname, *rule.process_text(view.substr(reg)))
                    if item not in items:
                        items.append(item)
                    break

        return items

    def format_items(items):
        return [
            f"{fname}:{line}: {msg}" if line > 0 else f"{fname}: {msg}"
            for fname, line, msg in sorted(items)
        ]

    # gather log items
    return (
        format_items(chain(*map(extract_items, (ExceptionLogRule, ErrorLogRule)))),
        format_items(extract_items(WarningLogRule)),
        format_items(extract_items(BadboxLogRule)),
    )


def parse_log_file(logfile: str | os.PathLike[str]) -> tuple[list[str], list[str], list[str]]:
    """
    Extract errors, warnings and badbox messages from tex build log.

    :param logfile:
        The logfile

    :returns:
        3-tuple of lists of strings, containing results
    """

    # find a proper window
    window = sublime.active_window()
    if window is None:
        if not (windows := sublime.windows()):
            return ([], [], [])
        window = windows[0]

    # create a hidden panel as scratch pad
    panel = window.create_output_panel("latextools_logfile", unlisted=True)
    panel_settings = panel.settings()
    panel_settings.set("auto_indent", False)
    panel_settings.set("auto_match_enabled", False)
    panel_settings.set("draw_indent_guides", False)
    panel_settings.set("draw_white_space", "none")
    panel_settings.set("detect_indentation", False)
    panel_settings.set("disable_auto_complete", False)
    panel_settings.set("encoding", "UTF-8")
    panel_settings.set("gutter", False)
    panel_settings.set("line_numbers", False)
    panel_settings.set("rulers", [])
    panel_settings.set("tab_size", 2)
    panel_settings.set("translate_tabs_to_spaces", False)
    panel_settings.set("word_wrap", False)
    panel.assign_syntax("Packages/LaTeXTools/LaTeXTools Log.sublime-syntax")

    # open logfile into panel
    try:
        with open(logfile, encoding="utf-8") as fobj:
            text = fobj.read()
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        panel.run_command("append", {"characters": text})
        return parse_log_view(panel)
    finally:
        window.destroy_output_panel("latextools_logfile")


class LatextoolsDumpTexLog(sublime_plugin.WindowCommand):
    """
    This class implements the `latextools_dump_tex_log` command.

    The debug command dumps all log entries, found in a tex log to ST's console.
    """

    def run(self):
        view = self.window.active_view()
        if not view:
            print("Not a view, cancelling!")
            return
        syntax = view.syntax()
        if not syntax:
            print("View has no syntax assigned, cancelling!")
            return
        if syntax.name != "LaTeXTools Log":
            print("View has wrong syntax assigned, cancelling!")
            return
        for item in chain(*parse_log_view(view)):
            print(item)
