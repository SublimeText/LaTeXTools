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


def delete_local_cache(tex_root):
    """
    Removes the local cache folder and the local cache files
    """
    cache_path = os.path.dirname(tex_root)
    cache_path = os.path.join(cache_path, CACHE_FOLDER)
    if not os.path.exists(cache_path):
        return
    shutil.rmtree(cache_path)


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
    cache_path = os.path.dirname(tex_root)
    cache_path = os.path.join(cache_path, CACHE_FOLDER)
    if not os.path.isdir(cache_path):
        os.mkdir(cache_path)

    file_path = os.path.join(cache_path, name)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


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
    cache_path = os.path.dirname(tex_root)
    cache_path = os.path.join(cache_path, CACHE_FOLDER)
    file_path = os.path.join(cache_path, name)
    if not os.path.isdir(cache_path) or not os.path.exists(file_path):
        return

    with open(file_path, "rb") as f:
        return pickle.load(f)


def write_global(name, obj):
    """
    Writes the object to the global sublime cache path using pickle

    Arguments:
    name -- the relative file name to write the object
    obj -- the object to write, must be compatible with pickle
    """
    # For ST3, put the cache files in cache dir
    # and for ST2, put it in the user packages dir
    # and change the name
    cache_path = _global_cache_path()
    file_path = os.path.join(cache_path, name)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


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
    if not os.path.isdir(cache_path):
        os.mkdir(cache_path)
    file_path = os.path.join(cache_path, name)
    if not os.path.exists(file_path):
        return
    with open(file_path, "rb") as f:
        return pickle.load(f)


def _global_cache_path():
    if _ST3:
        cache_path = os.path.join(sublime.cache_path(), "LaTeXTools")
    else:
        cache_path = os.path.join(sublime.packages_path(),
                                  "User",
                                  CACHE_FOLDER)
    return os.path.normpath(cache_path)
