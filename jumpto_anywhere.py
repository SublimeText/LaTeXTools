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

# we need an filter as iterator
if not _ST3:
    from itertools import ifilter
else:
    ifilter = filter

INPUT_REG_EXPS = [INPUT_REG, BIB_REG, IMAGE_REG]

COMMAND_REG = re.compile(
    r"\\(?P<command>[\w]+)"
    r"(?:\[[^\]]*\])?"
    r"\{(?P<args>[^}]+)\}",
    re.UNICODE
)


def _jumpto_ref(view, com_reg):
    ana = analysis.analyze_document(view)
    if ana is None:
        return
    label_id = com_reg.group("args")

    def is_correct_label(c):
        return c.command == "label" and c.args == label_id
    labels = ana.filter_commands(is_correct_label)
    try:
        label = labels[0]
    except:
        print("No matching label for '{0}'".format(label_id))
        return
    label_region = label.args_region
    utils.open_and_select_region(view, label.file_name, label_region)


def _jumpto_cite(view, com_reg):
    tex_root = get_tex_root(view)
    if tex_root is None:
        return
    base_dir = os.path.dirname(tex_root)
    ana = analysis.get_analysis(tex_root)

    bib_commands = ana.filter_commands(
       ["bibliography", "nobibliography", "addbibresource"])
    bib_key = com_reg.group("args")
    for bib_command in bib_commands:
        for bib_file in jumpto_tex_file._split_bib_args(bib_command.args):
            if not os.path.splitext(bib_file)[1]:
                bib_file += ".bib"
            bib_file = os.path.join(base_dir, bib_file)
            try:
                file_content = utils.read_file_unix_endings(bib_file)
                start = file_content.find(bib_key)
                if start == -1:
                    continue
                region = sublime.Region(start, start + len(bib_key))
                utils.open_and_select_region(view, bib_file, region)
                return
            except Exception as e:
                print("Error occured opening file {0}".format(bib_file))
                print(e)
                continue


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
