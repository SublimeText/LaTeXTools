import os
import re

import sublime
import sublime_plugin

from .utils import analysis
from .utils import ana_utils
from .utils import quickpanel
from .utils import utils
from .utils.logging import logger
from .utils.tex_directives import get_tex_root
from .utils.tex_directives import TEX_DIRECTIVE
from .latex_cite_completions import NEW_STYLE_CITE_REGEX
from .latex_glossary_completions import ACR_LINE_RE
from .latex_glossary_completions import GLO_LINE_RE
from .latex_ref_completions import NEW_STYLE_REF_REGEX
from .jumpto_tex_file import INPUT_REG, IMPORT_REG, BIB_REG, IMAGE_REG
from . import jumpto_tex_file

__all__ = ["LatextoolsJumptoAnywhereCommand", "LatextoolsJumptoAnywhereByMouseCommand"]

INPUT_REG_EXPS = [INPUT_REG, IMPORT_REG, BIB_REG, IMAGE_REG]

COMMAND_REG = re.compile(
    r"\\(?P<command>[\w]+)\*?\s*(?:\[[^\]]*\]\s*)?\{(?P<args>[^}]*)\}",
    re.UNICODE,
)


def _get_selected_arg(view, com_reg, pos):
    """
    Retrieves the selected argument in a comma separated list,
    returns None if there are several entries and no entry is selected
    directly
    """
    args = com_reg.group("args")
    if "," not in args:
        # only one arg => return it
        return args
    args_region = com_reg.regs[COMMAND_REG.groupindex["args"]]
    cursor = com_reg.start() + pos - args_region[0]

    if cursor < 0 or len(args) < cursor:
        # need to explicit select the argument
        message = "Selection to vague. Directly click on the name" " inside the command."
        logger.error(message)
        sublime.status_message(message)
        return
    before = args[:cursor]
    after = args[cursor:]

    start_before = before.rfind(",") + 1
    end_after = after.find(",")
    if end_after == -1:
        end_after = len(after)

    arg = before[start_before:] + after[:end_after]
    arg = arg.strip()

    return arg


def _show_usage_label(view, args):
    tex_root = get_tex_root(view)
    if not tex_root:
        return

    ana = analysis.analyze_document(tex_root)
    if not ana:
        return

    def is_correct_ref(c):
        command = (f"\\{c.command}{{")[::-1]
        return NEW_STYLE_REF_REGEX.match(command) and c.args == args

    refs = list(ana.filter_commands(is_correct_ref))

    if len(refs) == 0:
        sublime.error_message(f"No references for '{args}' found.")
        return
    elif len(refs) == 1:
        ref = refs[0]
        utils.open_and_select_region(view, ref.file_name, ref.region)
        return

    captions = [ana_utils.create_rel_file_str(ana, r) for r in refs]

    quickpanel.show_quickpanel(captions, refs)


def _jumpto_ref(view, com_reg, pos):
    label_id = _get_selected_arg(view, com_reg, pos)
    if not label_id:
        return
    sublime.status_message(f"Scanning document for label '{label_id}'...")
    tex_root = get_tex_root(view)
    ana = analysis.analyze_document(tex_root)
    if ana is None:
        return

    def is_correct_label(c):
        return c.command == "label" and c.args == label_id

    labels = ana.filter_commands(is_correct_label)
    try:
        label = next(labels)
    except Exception:
        message = f"No matching label found for '{label_id}'."
        logger.error(message)
        sublime.status_message(message)
        return
    label_region = label.region
    message = f"Jumping to label '{label_id}'"
    logger.info(message)
    sublime.status_message(message)
    utils.open_and_select_region(view, label.file_name, label_region)


def _jumpto_cite(view, com_reg, pos):
    tex_root = get_tex_root(view)
    bib_key = _get_selected_arg(view, com_reg, pos)
    if tex_root is None or not bib_key:
        return
    message = f"Scanning bibliography files for key '{bib_key}'..."
    logger.info(message)
    sublime.status_message(message)
    base_dir = os.path.dirname(tex_root)
    ana = analysis.get_analysis(tex_root)

    bib_commands = ana.filter_commands(["bibliography", "nobibliography", "addbibresource"])
    for bib_command in bib_commands:
        for bib_file in jumpto_tex_file._split_bib_args(bib_command.args):
            if not os.path.splitext(bib_file)[1]:
                bib_file += ".bib"
            bib_file = os.path.join(base_dir, bib_file)
            try:
                file_content = utils.read_file_unix_endings(bib_file)
                start = file_content.find(bib_key)
                end = start + len(bib_key)
                # check that we found the entry and we are not inside a word
                if (
                    start == -1
                    or file_content[start - 1 : start].isalnum()
                    or file_content[end : end + 1].isalnum()
                ):
                    continue
                region = sublime.Region(start, end)
                message = f"Jumping to bibliography key '{bib_key}'."
                logger.info(message)
                sublime.status_message(message)
                utils.open_and_select_region(view, bib_file, region)
                return
            except Exception as e:
                logger.error(f"Failed to open file {bib_file}:\n  {e}")
                continue
    message = f"Entry '{bib_key}' not found in bibliography."
    logger.error(message)
    sublime.status_message(message)


def _jumpto_glo(view, com_reg, pos, acr=False):
    tex_root = get_tex_root(view)
    if not tex_root:
        return
    ana = analysis.analyze_document(tex_root)
    if not acr:
        commands = ana.filter_commands(["newglossaryentry", "longnewglossaryentry", "newacronym"])
    else:
        commands = ana.filter_commands("newacronym")

    iden = com_reg.group("args")
    try:
        entry = next(c for c in commands if c.args == iden)
    except Exception:
        message = f"Glossary definition not found for '{iden}'"
        logger.error(message)
        sublime.status_message(message)
        return
    message = f"Jumping to Glossary '{iden}'."
    logger.info(message)
    sublime.status_message(message)
    utils.open_and_select_region(view, entry.file_name, entry.args_region)


def _jumpto_pkg_doc(view, com_reg, pos):
    def view_doc(package):
        message = f"Try opening documentation for package '{package}'"
        logger.info(message)
        sublime.status_message(message)
        view.window().run_command("latextools_view_doc", {"file": package})

    package_name = _get_selected_arg(view, com_reg, pos)
    if package_name:
        view_doc(package_name)


def _jumpto_tex_root(view, root):
    if os.path.isabs(root):
        path = root
    else:
        path = os.path.normpath(os.path.join(os.path.dirname(view.file_name()), root))

    sublime.active_window().open_file(path)


def _opt_jumpto_self_def_command(view, com_reg):
    tex_root = get_tex_root(view)
    if not tex_root:
        return False

    # check in the cache whether we should jump (is command self defined)
    newcommand_keywords = ["newcommand", "renewcommand"]
    command = "\\" + com_reg.group("command")
    cana = analysis.get_analysis(tex_root)
    new_commands = cana.filter_commands(newcommand_keywords)
    if command not in [c.args for c in new_commands]:
        logger.error(f"Command not defined (cached) '{command}'")
        return False

    message = f"Scanning document for command definition of '{command}'"
    logger.info(message)
    sublime.status_message(message)
    # analyze the document to retrieve the correct position of the
    # command definition
    ana = analysis.analyze_document(tex_root)
    new_commands = ana.filter_commands(newcommand_keywords)
    try:
        new_com_def = next(filter(lambda c: c.args == command, new_commands))
    except Exception:
        logger.error(f"Command not self defined '{command}'")
        return False
    file_name = new_com_def.file_name
    region = new_com_def.args_region

    message = f"Jumping to definition of '{command}'"
    logger.info(message)
    sublime.status_message(message)
    utils.open_and_select_region(view, file_name, region)
    return True


class LatextoolsJumptoAnywhereCommand(sublime_plugin.TextCommand):
    def run(self, edit, position=None):
        view = self.view
        if not view:
            return

        if position is None:
            if len(view.sel()) != 1:
                logger.error("Jump to anywhere does not work with multiple cursors")
                return
            sel = view.sel()[0]
        else:
            sel = sublime.Region(position, position)

        line_r = view.line(sel)
        line = view.substr(line_r)

        def is_inside(g):
            """check whether the selection is inside the command"""
            if g is None:
                return False
            b = line_r.begin()
            # the region, which should contain the selection
            reg = g.regs[0]
            return reg[0] <= sel.begin() - b and sel.end() - b <= reg[1]

        try:
            com_reg = next(filter(is_inside, COMMAND_REG.finditer(line)))
        except Exception:
            # since the magic comment will not match the command, do this here
            if view.file_name():
                m = TEX_DIRECTIVE.search(line)
                if (
                    m
                    and m.group(1) == "root"
                    and m.start() <= sel.begin() - line_r.begin()
                    and sel.end() - line_r.begin() <= m.end()
                ):
                    _jumpto_tex_root(view, m.group(2))
                    return

            logger.error("Cursor is not inside a command")
            return

        command = com_reg.group("command")
        args = com_reg.group("args")
        reversed_command = "{" + command[::-1] + "\\"
        # the cursor position inside the command
        pos = sel.b - line_r.begin() - com_reg.start()
        # check if its a ref
        if NEW_STYLE_REF_REGEX.match(reversed_command):
            sublime.status_message(f"Jump to reference '{args}'")
            _jumpto_ref(view, com_reg, pos)
        # check if it is a cite
        elif NEW_STYLE_CITE_REGEX.match(reversed_command):
            sublime.status_message(f"Jump to citation '{args}'")
            _jumpto_cite(view, com_reg, pos)
        elif command == "label":
            _show_usage_label(view, args)
        elif GLO_LINE_RE.match(reversed_command):
            sublime.status_message(f"Jump to glossary '{args}'")
            _jumpto_glo(view, com_reg, pos)
        elif ACR_LINE_RE.match(reversed_command):
            sublime.status_message(f"Jump to acronym '{args}'")
            _jumpto_glo(view, com_reg, pos, acr=True)
        # check if it is any kind of input command
        elif any(reg.match(com_reg.group(0)) for reg in INPUT_REG_EXPS):
            sublime.status_message(f"Jump to file '{args}'")
            self.view.run_command(
                "latextools_jumpto_file",
                {
                    "auto_create_missing_folders": False,
                    "auto_insert_root": False,
                    "position": position
                }
            )
        elif command in ["usepackage", "Requirepackage"]:
            _jumpto_pkg_doc(view, com_reg, pos)
        else:
            # if the cursor is inside the \command part, try jump to
            # self defined commands
            b = line_r.begin()
            command_region = com_reg.regs[COMMAND_REG.groupindex["command"]]
            # if cursor is inside \command
            if command_region[0] + b - 1 <= sel.begin() and sel.end() <= command_region[1] + b:
                _opt_jumpto_self_def_command(view, com_reg)


class LatextoolsJumptoAnywhereByMouseCommand(sublime_plugin.TextCommand):
    def want_event(self):
        return True

    def run(self, edit, event, fallback_command="", set_caret=False):

        def match_selector(selector):
            point = self.view.sel()[0].b if len(self.view.sel()) else 0
            return self.view.match_selector(point, selector)

        if match_selector("text.tex.latex"):
            logger.debug("Jump in tex file.")
            pos = self.view.window_to_text((event["x"], event["y"]))
            self.view.run_command("latextools_jumpto_anywhere", {"position": pos})
        elif fallback_command:
            if set_caret:
                self._set_caret(event)
            logger.debug(f"Run command '{fallback_command}'")
            self.view.run_command(fallback_command)

    def _set_caret(self, event):
        pos = self.view.window_to_text((event["x"], event["y"]))
        if pos >= 0:
            self.view.sel().clear()
            self.view.sel().add(pos)
