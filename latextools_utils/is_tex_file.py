from .settings import get_setting


def get_tex_extensions():
    tex_file_exts = get_setting('tex_file_exts', ['.tex'])

    return [s.lower() for s in set(tex_file_exts)]


def is_tex_file(file_name):
    if not isinstance(file_name, str):
        raise TypeError('file_name must be a string')

    tex_file_exts = get_tex_extensions()
    for ext in tex_file_exts:
        if file_name.lower().endswith(ext):
            return True
    return False
