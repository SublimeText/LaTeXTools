import os
import pickle
import shutil

import sublime

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
else:
    _ST3 = True

CACHE_FOLDER = ".st_ltt_cache"


class CacheMiss(Exception):
    """exception to indicate that the cache file is missing"""
    pass


def delete_local_cache(tex_root):
    """
    Removes the local cache folder and the local cache files
    """
    cache_path = _local_cache_path(tex_root)
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)


def cache(tex_root, name, generate):
    """
    Alias for cache_local:
    Uses the local cache to retrieve the entry for the name.
    If the entry is not available, it will be calculated via the
    generate-function and cached using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root.

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to write the object
    generate -- a function pointer/closure to create the cached object
        for case it is not available in the cache,
        must be compatible with pickle
    """
    return cache_local(tex_root, name, generate)


def write(tex_root, name, obj):
    """
    Alias for write_local:
    Writes the object to the local cache using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to write the object
    obj -- the object to write, must be compatible with pickle
    """
    write_local(tex_root, name, obj)


def read(tex_root, name):
    """
    Alias for read_local:
    Reads the object from the local cache using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to read the object

    Returns:
    The object at the location with the name,
    None - if the file does not exists
    """
    return read_local(tex_root, name)


def cache_local(tex_root, name, generate):
    """
    Uses the local cache to retrieve the entry for the name.
    If the entry is not available, it will be calculated via the
    generate-function and cached using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root.

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to write the object
    generate -- a function pointer/closure to create the cached object
        for case it is not available in the cache,
        must be compatible with pickle
    """
    try:
        result = read_local(tex_root, name)
    except CacheMiss:
        result = generate()
        write_local(tex_root, name, result)
    return result


def write_local(tex_root, name, obj):
    """
    Writes the object to the local cache using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to write the object
    obj -- the object to write, must be compatible with pickle
    """
    cache_path = _local_cache_path(tex_root)
    _write(cache_path, name, obj)


def read_local(tex_root, name):
    """
    Reads the object from the local cache using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to read the object

    Returns:
    The object at the location with the name,
    None - if the file does not exists
    """
    cache_path = _local_cache_path(tex_root)
    return _read(cache_path, name)


def cache_global(tex_root, name, generate):
    """
    Uses the global sublime cache retrieve the entry for the name.
    If the entry is not available, it will be calculated via the
    generate-function and cached using pickle.

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to write the object
    generate -- a function pointer/closure to create the cached object
        for case it is not available in the cache,
        must be compatible with pickle
    """
    try:
        result = read_global(tex_root, name)
    except CacheMiss:
        result = generate()
        write_global(tex_root, name, result)
    return result


def write_global(name, obj):
    """
    Writes the object to the global sublime cache path using pickle

    Arguments:
    name -- the relative file name to write the object
    obj -- the object to write, must be compatible with pickle
    """
    cache_path = _global_cache_path()
    _write(cache_path, name, obj)


def read_global(name):
    """
    Reads the object from the global sublime cache path using pickle

    Arguments:
    name -- the relative file name to read the object

    Returns:
    The object at the location with the name,
    None - if the file does not exists
    """
    cache_path = _global_cache_path()
    return _read(cache_path, name)


def _local_cache_path(tex_root):
    root_folder = os.path.dirname(tex_root)
    return os.path.join(root_folder, CACHE_FOLDER)


def _global_cache_path():
    # For ST3, put the cache files in cache dir
    # and for ST2, put it in the user packages dir
    if _ST3:
        cache_path = os.path.join(sublime.cache_path(), "LaTeXTools")
    else:
        cache_path = os.path.join(sublime.packages_path(),
                                  "User",
                                  CACHE_FOLDER)
    return os.path.normpath(cache_path)


def _write(cache_path, name, obj):
    if _ST3:
        os.makedirs(cache_path, exist_ok=True)
    else:
        if not os.path.isdir(cache_path):
            os.makedirs(cache_path)

    file_path = os.path.join(cache_path, name)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def _read(cache_path, name):
    file_path = os.path.join(cache_path, name)
    if not os.path.exists(file_path):
        raise CacheMiss()

    with open(file_path, "rb") as f:
        return pickle.load(f)
