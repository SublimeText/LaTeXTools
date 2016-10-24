import os

import sublime


def line_nr(ana, entry):
    """
    Return the line number of the start of a command.

    ATTENTION: This is not the row of the command. If you want that
        use rowcol!
    ana -- The analysis, which contains the entry
    entry -- The command entry to get the line number for
    """
    rowcol = ana.rowcol(entry.file_name)
    return rowcol(entry.region.begin())[0] + 1


def create_rel_file_str(ana, entry):
    """
    Create a nice string "rel_path/to/file.tex:line" to show the command
    position to the users.

    tex_root -- The path to the root file
    ana -- The analysis, which contains the entry
    entry -- The command entry to get the line number for
    """
    tex_root = ana.tex_root()
    file_name = entry.file_name
    file_dir, file_base = os.path.split(file_name)
    root_dir, _ = os.path.split(tex_root)
    if file_dir == root_dir:
        show_path = file_base
    else:
        show_path = os.path.relpath(file_dir, root_dir)
        show_path = os.path.join(show_path, file_base)
        # prettify on windows
        if sublime.platform() == "windows":
            show_path = show_path.replace('\\', '/')
    line = line_nr(ana, entry)
    return "{show_path}:{line}".format(**locals())
