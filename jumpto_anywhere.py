import os
import re

import sublime
import sublime_plugin

try:
    _ST3 = True
    from .getTeXRoot import get_tex_root
    from .latextools_utils import analysis, utils
    from .latex_cite_completions import OLD_STYLE_CITE_REGEX
    from .latex_ref_completions import OLD_STYLE_REF_REGEX
    from .jumpto_tex_file import INPUT_REG, BIB_REG, IMAGE_REG
    from . import jumpto_tex_file
except:
    _ST3 = False
    from getTeXRoot import get_tex_root
    from latextools_utils import analysis, utils
    from latex_cite_completions import OLD_STYLE_CITE_REGEX
    from latex_ref_completions import OLD_STYLE_REF_REGEX
    from jumpto_tex_file import INPUT_REG, BIB_REG, IMAGE_REG
    import jumpto_tex_file

# we need a filter as iterator
if not _ST3:
    from itertools import ifilter
else:
    ifilter = filter

INPUT_REG_EXPS = [INPUT_REG, BIB_REG, IMAGE_REG]

COMMAND_REG = re.compile(
    r"\\(?P<command>[\w]+)"
    r"(?:\[[^\]]*\])?"
    r"\{(?P<args>[^}]*)\}",
    re.UNICODE
)


def _jumpto_ref(view, com_reg):
    label_id = com_reg.group("args")
    sublime.status_message(
        "Scanning document for label '{0}'...".format(label_id))
    ana = analysis.analyze_document(view)
    if ana is None:
        return

    def is_correct_label(c):
        return c.command == "label" and c.args == label_id
    labels = ana.filter_commands(is_correct_label)
    try:
        label = labels[0]
    except:
        message = "No matching label found for '{0}'.".format(label_id)
        print(message)
        sublime.status_message(message)
        return
    label_region = label.args_region
    utils.open_and_select_region(view, label.file_name, label_region)


def _jumpto_cite(view, com_reg):
    tex_root = get_tex_root(view)
    bib_key = com_reg.group("args")
    if tex_root is None or not bib_key:
        return
    message = "Scanning bibliography files for key '{0}'...".format(bib_key)
    print(message)
    sublime.status_message(message)
    base_dir = os.path.dirname(tex_root)
    ana = analysis.get_analysis(tex_root)

    bib_commands = ana.filter_commands(
       ["bibliography", "nobibliography", "addbibresource"])
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
                if start == -1 or file_content[start-1:start].isalnum() or\
                        file_content[end:end+1].isalnum():
                    continue
                region = sublime.Region(start, end)
                utils.open_and_select_region(view, bib_file, region)
                return
            except Exception as e:
                print("Error occurred opening file {0}".format(bib_file))
                print(e)
                continue
    message = "Entry '{0}' not found in bibliography.".format(bib_key)
    print(message)
    sublime.status_message(message)


def _jumpto_pkg_doc(view, line_start, com_reg):
    def view_doc(package):
        message = "Try opening documentation for package '{0}'".format(package)
        print(message)
        sublime.status_message(message)
        view.window().run_command("latex_view_doc", {"file": package})
    args = com_reg.group("args")
    if "," not in args:
        # only one arg => open the doc
        view_doc(args)
        return
    args_region = com_reg.regs[COMMAND_REG.groupindex["args"]]
    cursor = view.sel()[0].b - line_start - args_region[0]
    if cursor < 0:
        message = "Package selection to vague. Click on the package name."
        print(message)
        sublime.status_message(message)
        return
    # start from the cursor and select the surrounding word
    a, b = cursor, cursor
    while args[a-1:a].isalpha():
        a -= 1
    while args[b:b+1].isalpha():
        b += 1
    # splice the package from the args and view the doc
    view_doc(args[a:b])


def _opt_jumpto_self_def_command(view, com_reg):
    tex_root = get_tex_root(view)
    if tex_root is None:
        return False

    # check in the cache whether we should jump (is command self defined)
    newcommand_keywords = ["newcommand", "renewcommand"]
    command = "\\" + com_reg.group("command")
    cana = analysis.get_analysis(tex_root)
    new_commands = cana.filter_commands(newcommand_keywords)
    if command not in [c.args for c in new_commands]:
        message = "Command not defined (cached) '{0}'".format(command)
        print(message)
        return False

    message =\
        "Scanning document for command definition of '{0}'".format(command)
    print(message)
    sublime.status_message(message)
    # analyze the document to retrieve the correct position of the
    # command definition
    ana = analysis.analyze_document(view)
    new_commands = ana.filter_commands(newcommand_keywords)
    try:
        new_com_def = next(ifilter(lambda c: c.args == command,
                                   new_commands))
    except:
        message = "Command not self defined '{0}'".format(command)
        print(message)
        return False
    file_name = new_com_def.file_name
    region = new_com_def.args_region

    message =\
        "Jumping to definition of '{0}'".format(command)
    print(message)
    sublime.status_message(message)
    utils.open_and_select_region(view, file_name, region)
    return True


class JumptoTexAnywhereCommand(sublime_plugin.TextCommand):
    def run(self, edit, fallback_command=""):
        view = self.view

        if not view.score_selector(view.sel()[0].b, "text.tex.latex"):
            if fallback_command:
                print("Run command '{0}'".format(fallback_command))
                view.run_command(fallback_command)
            return
        if len(view.sel()) != 1:
            print("Jump to smart command does not work with multiple cursors")
            return
        sel = view.sel()[0]
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
            com_reg = next(ifilter(is_inside, COMMAND_REG.finditer(line)))
        except:
            print("Cursor is not inside a command")
            return
        command = com_reg.group("command")
        args = com_reg.group("args")
        reversed_command = command[::-1]
        # check if its a ref
        if OLD_STYLE_REF_REGEX.match(reversed_command):
            sublime.status_message("Jump to reference '{0}'".format(args))
            _jumpto_ref(view, com_reg)
        # check if it is a cite
        elif OLD_STYLE_CITE_REGEX.match(reversed_command):
            sublime.status_message("Jump to citation '{0}'".format(args))
            _jumpto_cite(view, com_reg)
        # check if it is any kind of input command
        elif any(reg.match(com_reg.group(0)) for reg in INPUT_REG_EXPS):
            args = {
                "auto_create_missing_folders": False,
                "auto_insert_root": False
            }
            view.run_command("jumpto_tex_file", args)
        elif command in ["usepackage", "Requirepackage"]:
            _jumpto_pkg_doc(view, line_r.begin(), com_reg)
        else:
            # if the cursor is inside the \command part, try jump to
            # self defined commands
            b = line_r.begin()
            command_region = com_reg.regs[COMMAND_REG.groupindex["command"]]
            # if cursor is inside \command
            if command_region[0] + b - 1 <= sel.begin() and\
                    sel.end() <= command_region[1] + b:
                _opt_jumpto_self_def_command(view, com_reg)
