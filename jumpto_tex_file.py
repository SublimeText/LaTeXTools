import re
import os
import codecs
import shlex
import traceback

import sublime
import sublime_plugin

try:
    _ST3 = True
    from .getTeXRoot import get_tex_root
    from .latextools_utils import get_setting, utils
    from .latextools_utils.external_command import external_command
except:
    _ST3 = False
    from getTeXRoot import get_tex_root
    from latextools_utils import get_setting, utils
    from latextools_utils.external_command import external_command


INPUT_REG = re.compile(
    r"\\(?:input|include|subfile|loadglsentries)"
    r"\{(?P<file>[^}]+)\}",
    re.UNICODE
)

BIB_REG = re.compile(
    r"\\(?:bibliography|nobibliography|addbibresource|add(?:global|section)bib)"
    r"(?:\[[^\]]*\])?"
    r"\{(?P<file>[^}]+)\}",
    re.UNICODE
)

IMAGE_REG = re.compile(
    r"\\includegraphics"
    r"(?:\[[^\]]*\])?"
    r"\{(?P<file>[^\}]+)\}",
    re.UNICODE
)


def _jumpto_tex_file(view, window, tex_root, file_name,
                     auto_create_missing_folders, auto_insert_root):
    base_path, base_name = os.path.split(tex_root)

    _, ext = os.path.splitext(file_name)
    if not ext:
        file_name += '.tex'

    # clean-up any directory manipulating components
    file_name = os.path.normpath(file_name)

    containing_folder, file_name = os.path.split(file_name)

    # allow absolute paths on \include or \input
    isabs = os.path.isabs(containing_folder)
    if not isabs:
        containing_folder = os.path.normpath(
            os.path.join(base_path, containing_folder))

    # create the missing folder
    if auto_create_missing_folders and\
            not os.path.exists(containing_folder):
        try:
            os.makedirs(containing_folder)
        except OSError:
            # most likely a permissions error
            print('Error occurred while creating path "{0}"'
                  .format(containing_folder))
            traceback.print_last()
        else:
            print('Created folder: "{0}"'.format(containing_folder))

    if not os.path.exists(containing_folder):
        sublime.status_message(
            "Cannot open tex file as folders are missing")
        return
    is_root_inserted = False
    full_new_path = os.path.join(containing_folder, file_name)
    if auto_insert_root and not os.path.exists(full_new_path):
        if isabs:
            root_path = tex_root
        else:
            root_path = os.path.join(
                os.path.relpath(base_path, containing_folder),
                base_name)

        # Use slashes consistent with TeX's usage
        if sublime.platform() == 'windows' and not isabs:
            root_path = root_path.replace('\\', '/')

        root_string = '%!TEX root = {0}\n'.format(root_path)
        try:
            with codecs.open(full_new_path, "w", "utf8")\
                    as new_file:
                new_file.write(root_string)
            is_root_inserted = True
        except OSError:
            print('An error occurred while creating file "{0}"'
                  .format(file_name))
            traceback.print_last()

    # open the file
    print("Open the file '{0}'".format(full_new_path))

    # await opening and move cursor to end of the new view
    # (does not work on st2)
    if _ST3 and auto_insert_root and is_root_inserted:
        cursor_pos = len(root_string)
        new_region = sublime.Region(cursor_pos, cursor_pos)
        utils.open_and_select_region(view, full_new_path, new_region)
    else:
        window.open_file(full_new_path)


def _jumpto_bib_file(view, window, tex_root, file_name,
                     auto_create_missing_folders):
    # just abuse the insights of _jumpto_tex_file and call it
    # disable all tex features and open the file
    _, ext = os.path.splitext(file_name)
    if not ext:
        file_name += '.bib'
    _jumpto_tex_file(view, window, tex_root, file_name,
                     auto_create_missing_folders, False)


def find_image(tex_root, file_name):
    base_path = os.path.dirname(tex_root)

    image_types = get_setting(
        "image_types", [
            "png", "pdf", "jpg", "jpeg", "eps"
        ])

    file_path = os.path.normpath(
        os.path.join(base_path, file_name))
    _, extension = os.path.splitext(file_path)
    extension = extension[1:]  # strip the leading point
    if not extension:
        for ext in image_types:
            test_path = file_path + "." + ext
            print("Test file: '{0}'".format(test_path))
            if os.path.exists(test_path):
                extension = ext
                file_path = test_path
                print("Found file: '{0}'".format(test_path))
                break
    if not os.path.exists(file_path):
        return None
    return file_path


def open_image(window, file_path):
    def run_command(command):
            if not _ST3:
                command = str(command)
            command = shlex.split(command)
            # if $file is used, substitute it by the file path
            if "$file" in command:
                command = [file_path if c == "$file" else c
                           for c in command]
            # if $file is not used, append the file path
            else:
                command.append(file_path)

            external_command(command)

    _, extension = os.path.splitext(file_path)
    extension = extension[1:]  # strip the leading point
    psystem = sublime.platform()
    commands = get_setting("open_image_command", {}).get(psystem, None)
    print("Commands: '{0}'".format(commands))
    print("Open File: '{0}'".format(file_path))

    if commands is None:
        window.open_file(file_path)
    elif type(commands) is str:
        run_command(commands)
    else:
        for d in commands:
            print(d)
            # validate the entry
            if "command" not in d:
                message = "Invalid entry {0}, missing: 'command'"\
                    .format(str(d))
                sublime.status_message(message)
                print(message)
                continue
            # check whether the extension matches
            if "extension" in d:
                if extension == d["extension"] or\
                        extension in d["extension"]:
                    run_command(d["command"])
                    break
            # if no extension matches always run the command
            else:
                run_command(d["command"])
                break
        else:
            sublime.status_message(
                "No opening command for {0} defined"
                .format(extension))
            window.open_file(file_path)


def _jumpto_image_file(view, window, tex_root, file_name):
    file_path = find_image(tex_root, file_name)
    if not file_path:
        sublime.status_message("file does not exists: '{0}'".format(file_path))
        return
    open_image(window, file_path)


def _split_bib_args(bib_args):
    if "," in bib_args:
        file_names = bib_args.split(",")
        file_names = [f.strip() for f in file_names]
        print("Bib files: {0}".format(file_names))
    else:
        file_names = [bib_args]
    return file_names


class JumptoTexFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, auto_create_missing_folders=True,
            auto_insert_root=True, position=None):
        view = self.view
        window = view.window()
        tex_root = get_tex_root(view)
        if tex_root is None:
            sublime.status_message("Save your current file first")
            return

        if position is None:
            selections = list(view.sel())
        else:
            selections = [sublime.Region(position, position)]

        for sel in selections:
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

            for g in filter(is_inside, INPUT_REG.finditer(line)):
                file_name = g.group("file")
                print("Jumpto tex file '{0}'".format(file_name))
                _jumpto_tex_file(view, window, tex_root, file_name,
                                 auto_create_missing_folders, auto_insert_root)

            for g in filter(is_inside, BIB_REG.finditer(line)):
                file_group = g.group("file")
                file_names = _split_bib_args(file_group)
                for file_name in file_names:
                    print("Jumpto bib file '{0}'".format(file_name))
                    _jumpto_bib_file(view, window, tex_root, file_name,
                                     auto_create_missing_folders)

            for g in filter(is_inside, IMAGE_REG.finditer(line)):
                file_name = g.group("file")
                print("Jumpto image file '{0}'".format(file_name))
                _jumpto_image_file(view, window, tex_root, file_name)
