from .settings import get_setting


def get_tex_extensions(view=None):
    return [ext.lower() for ext in get_setting("tex_file_exts", [".tex"], view)]


def is_tex_file(file_name, exts=None, view=None):
    if not isinstance(file_name, str):
        raise TypeError("file_name must be a string")

    return any(map(file_name.lower().endswith, exts or get_tex_extensions(view)))
