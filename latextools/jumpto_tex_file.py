import re
import os
import codecs
import shlex
import traceback

import sublime
import sublime_plugin

from .deprecated_command import deprecate
from .utils import analysis
from .utils import utils
from .utils.external_command import external_command
from .utils.logging import logger
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

__all__ = ["LatextoolsJumptoFileCommand"]

INPUT_REG = re.compile(
    r"\\(?:input|include|subfile|loadglsentries)\{(?P<file>[^}]+)\}", re.UNICODE
)

IMPORT_REG = re.compile(
    r"\\(?:(?:sub)?import|(?:sub)?inputfrom|(?:sub)?includefrom)"
    r"\*?"
    r"\{(?P<path>[^}]+)\}"
    r"(?:\{(?P<file>[^}]+)\})?",  # optional for compat with jumpto-anywhere
    re.UNICODE,
)

BIB_REG = re.compile(
    r"\\(?:bibliography|nobibliography|addbibresource|add(?:global|section)bib)"
    r"(?:\[[^\]]*\])?"
    r"\{(?P<file>[^}]+)\}",
    re.UNICODE,
)

IMAGE_REG = re.compile(
    r"\\includegraphics(?:<[^>]*>)?(?:\[[^\]]*\])?\{(?P<file>[^\}]+)\}"
    , re.UNICODE
)


def _jumpto_tex_file(
    view, window, tex_root, file_name, auto_create_missing_folders, auto_insert_root
):
    file_name = file_name.strip('"')

    root_base_path, root_base_name = os.path.split(tex_root)

    ana = analysis.get_analysis(tex_root)
    base_path = ana.tex_base_path(view.file_name())

    _, ext = os.path.splitext(file_name)
    if not ext:
        file_name += ".tex"

    # clean-up any directory manipulating components
    file_name = os.path.normpath(file_name)

    containing_folder, file_name = os.path.split(file_name)

    # allow absolute paths on \include or \input
    isabs = os.path.isabs(containing_folder)
    if not isabs:
        containing_folder = os.path.normpath(os.path.join(base_path, containing_folder))

    # create the missing folder
    if auto_create_missing_folders and not os.path.exists(containing_folder):
        try:
            os.makedirs(containing_folder)
        except OSError:
            # most likely a permissions error
            logger.error('Error occurred while creating path "%s"', containing_folder)
            traceback.print_last()
        else:
            logger.info('Created folder: "%s"', containing_folder)

    if not os.path.exists(containing_folder):
        sublime.status_message("Cannot open tex file as folders are missing")
        return
    is_root_inserted = False
    full_new_path = os.path.join(containing_folder, file_name)
    if auto_insert_root and not os.path.exists(full_new_path):
        if isabs:
            root_path = tex_root
        else:
            root_path = os.path.join(
                os.path.relpath(root_base_path, containing_folder), root_base_name
            )

        # Use slashes consistent with TeX's usage
        if sublime.platform() == "windows" and not isabs:
            root_path = root_path.replace("\\", "/")

        root_string = "%!TEX root = {0}\n".format(root_path)
        try:
            with open(full_new_path, "w", encoding="utf-8") as new_file:
                new_file.write(root_string)
            is_root_inserted = True
        except OSError:
            logger.error('An error occurred while creating file "%s"', file_name)
            traceback.print_last()

    # open the file
    logger.info("Open the file '%s'", full_new_path)

    # await opening and move cursor to end of the new view
    if auto_insert_root and is_root_inserted:
        cursor_pos = len(root_string)
        new_region = sublime.Region(cursor_pos, cursor_pos)
        utils.open_and_select_region(view, full_new_path, new_region)
    else:
        window.open_file(full_new_path)


def _jumpto_bib_file(view, window, tex_root, file_name, auto_create_missing_folders):
    # just abuse the insights of _jumpto_tex_file and call it
    # disable all tex features and open the file
    _, ext = os.path.splitext(file_name)
    if not ext:
        file_name += ".bib"
    _jumpto_tex_file(view, window, tex_root, file_name, auto_create_missing_folders, False)


def _validate_image(file_path, image_types):
    _, extension = os.path.splitext(file_path)
    extension = extension[1:]  # strip the leading point
    if extension:
        if os.path.exists(file_path):
            return file_path
    else:
        for ext in image_types:
            test_path = file_path + "." + ext
            logger.debug("Test file: '%s'", test_path)
            if os.path.exists(test_path):
                logger.debug("Found file: '%s'", test_path)
                return test_path


def find_image(tex_root, file_name, tex_file_name=None):
    ana = analysis.get_analysis(tex_root)
    base_path = ana.tex_base_path(tex_file_name)

    image_types = get_setting("image_types", ["png", "pdf", "jpg", "jpeg", "eps"])

    for graphics_path in [base_path] + ana.graphics_paths():
        file_path = _validate_image(
            os.path.normpath(os.path.join(graphics_path, file_name)), image_types
        )
        if file_path:
            return file_path


def open_image(window, file_path):
    def run_command(command):
        command = shlex.split(command)
        # if $file is used, substitute it by the file path
        if "$file" in command:
            command = [file_path if c == "$file" else c for c in command]
        # if $file is not used, append the file path
        else:
            command.append(file_path)

        external_command(command, shell=True)

    _, extension = os.path.splitext(file_path)
    extension = extension[1:]  # strip the leading point
    psystem = sublime.platform()
    commands = get_setting("open_image_command", {}).get(psystem, None)
    logger.debug("Commands: '%s'", commands)
    logger.info("Open File: '%s'", file_path)

    if commands is None:
        window.open_file(file_path)
    elif isinstance(commands, str):
        run_command(commands)
    else:
        for d in commands:
            logger.debug(d)
            # validate the entry
            if "command" not in d:
                message = "Invalid entry {0}, missing: 'command'".format(d)
                sublime.status_message(message)
                logger.error(message)
                continue
            # check whether the extension matches
            if "extension" in d:
                if extension == d["extension"] or extension in d["extension"]:
                    run_command(d["command"])
                    break
            # if no extension matches always run the command
            else:
                run_command(d["command"])
                break
        else:
            sublime.status_message("No opening command for {0} defined".format(extension))
            window.open_file(file_path)


def open_image_folder(window, image_path):
    folder_path, image_name = os.path.split(image_path)
    window.run_command("open_dir", {"dir": folder_path, "file": image_name})


def _jumpto_image_file(view, window, tex_root, file_name):
    file_path = find_image(tex_root, file_name, tex_file_name=view.file_name())
    if not file_path:
        sublime.status_message("file does not exists: '{0}'".format(file_path))
        return
    open_image(window, file_path)


def _split_bib_args(bib_args):
    if "," in bib_args:
        file_names = bib_args.split(",")
        file_names = [f.strip() for f in file_names]
        logger.debug("Bib files: %s", file_names)
    else:
        file_names = [bib_args]
    return file_names


class LatextoolsJumptoFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, auto_create_missing_folders=True, auto_insert_root=True, position=None):
        view = self.view
        tex_root = get_tex_root(view)
        if not tex_root:
            sublime.status_message("Save your current file first")
            return

        window = view.window()

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
                logger.info("Jumpto tex file '%s'", file_name)
                _jumpto_tex_file(
                    view,
                    window,
                    tex_root,
                    file_name,
                    auto_create_missing_folders,
                    auto_insert_root,
                )

            for g in filter(is_inside, IMPORT_REG.finditer(line)):
                if not g.group("file"):
                    continue
                file_name = os.path.join(g.group("path"), g.group("file"))
                logger.info("Jumpto tex file '%s'", file_name)
                _jumpto_tex_file(
                    view,
                    window,
                    tex_root,
                    file_name,
                    auto_create_missing_folders,
                    auto_insert_root,
                )

            for g in filter(is_inside, BIB_REG.finditer(line)):
                file_group = g.group("file")
                file_names = _split_bib_args(file_group)
                for file_name in file_names:
                    logger.info("Jumpto bib file '%s'", file_name)
                    _jumpto_bib_file(view, window, tex_root, file_name, auto_create_missing_folders)

            for g in filter(is_inside, IMAGE_REG.finditer(line)):
                file_name = g.group("file")
                logger.info("Jumpto image file '%s'", file_name)
                _jumpto_image_file(view, window, tex_root, file_name)


deprecate(globals(), "JumptoTexFileCommand", LatextoolsJumptoFileCommand)
