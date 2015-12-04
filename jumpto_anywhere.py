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
    r"\{(?P<args>[^}]*)\}",
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
    bib_key = com_reg.group("args")
    if tex_root is None or not bib_key:
        return
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
                # check that we found the entry and we are not inside a word
                if start == -1 or file_content[start-1:start].isalnum() or\
                        file_content[start:start+1].isalnum():
                    continue
                region = sublime.Region(start, start + len(bib_key))
                utils.open_and_select_region(view, bib_file, region)
                return
            except Exception as e:
                print("Error occurred opening file {0}".format(bib_file))
                print(e)
                continue


def _jumpto_pkg_doc(view, line_start, com_reg):
    def view_doc(package):
        view.window().run_command("latex_view_doc", {"file": package})
    args = com_reg.group("args")
    if "," not in args:
        # only one arg => open the doc
        view_doc(args)
        return
    args_region = com_reg.regs[COMMAND_REG.groupindex["args"]]
    cursor = view.sel()[0].b - line_start - args_region[0]
    if cursor < 0:
        print("Package selection to vague")
        return
    # start from the cursor and select the surrounding word
    a, b = cursor, cursor
    while args[a-1:a].isalpha():
        a -= 1
    while args[b:b+1].isalpha():
        b += 1
    # splice the package from the args and view the doc
    view_doc(args[a:b])


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
