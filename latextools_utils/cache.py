import os
import re
import shutil
import hashlib
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle

import sublime

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import get_setting
else:
    _ST3 = True
    from . import get_setting
    long = int

# the folder, if the local cache is not hidden, i.e. folder in the same
# folder as the tex root
LOCAL_CACHE_FOLDER = ".st_lt_cache"
# folder to store all hidden local caches in the cache path
HIDDEN_LOCAL_CACHE_FOLDER = "local_cache"
# global cache folder for ST2, this folder will be created inside the User
# folder to store the global and the local cache
ST2_GLOBAL_CACHE_FOLDER = ".lt_cache"


TIME_RE = re.compile(
    r"\s*(?:(?P<day>\d+)\s*d(?:ays?)?)?"
    r"\s*(?:(?P<hour>\d+)\s*h(?:ours?)?)?"
    r"\s*(?:(?P<minute>\d+)\s*m(?:in(?:utes?)?)?)?"
    r"\s*(?:(?P<second>\d+)\s*s(?:ec(?:onds?)?)?)?\s*"
)


class CacheMiss(Exception):
    """exception to indicate that the cache file is missing"""
    pass


def hash_digest(text):
    """
    Create the hash digest for a text. These digest can be used to
    create a unique filename from the path to the root file.
    The used has function is md5.

    Arguments:
    text -- the text for which the digest should be created
    """
    text_encoded = text.encode("utf8")
    hash_result = hashlib.md5(text_encoded)
    return hash_result.hexdigest()


def delete_local_cache(tex_root):
    """
    Removes the local cache folder and the local cache files
    """
    print(u"Deleting local cache for '{0}'.".format(repr(tex_root)))
    local_cache_paths = [_hidden_local_cache_path(),
                         _local_cache_path(tex_root)]
    for cache_path in local_cache_paths:
        if os.path.exists(cache_path):
            print(u"Delete local cache folder '{0}'".format(repr(cache_path)))
            shutil.rmtree(cache_path)


def invalidate_local_cache(cache_path):
    """
    Invalidates the local cache by removing the cache folders
    """
    if os.path.exists(cache_path):
        print(u"Invalidate local cache '{0}'.".format(repr(cache_path)))
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
    The object at the location with the name
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
    _create_cache_timestamp(cache_path)


def read_local(tex_root, name):
    """
    Reads the object from the local cache using pickle.
    The local cache is per tex document and the path will extracted
    from the tex root

    Arguments:
    tex_root -- the root of the tex file (for the folder of the cache)
    name -- the relative file name to read the object

    Returns:
    The object at the location with the name
    """
    cache_path = _local_cache_path(tex_root)
    _validate_life_span(cache_path)
    return _read(cache_path, name)


def cache_global(name, generate):
    """
    Uses the global sublime cache retrieve the entry for the name.
    If the entry is not available, it will be calculated via the
    generate-function and cached using pickle.

    Arguments:
    name -- the relative file name to write the object
    generate -- a function pointer/closure to create the cached object
        for case it is not available in the cache,
        must be compatible with pickle
    """
    try:
        result = read_global(name)
    except CacheMiss:
        result = generate()
        write_global(name, result)
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
    The object at the location with the name
    """
    cache_path = _global_cache_path()
    return _read(cache_path, name)


def _local_cache_path(tex_root):
    hide_cache = get_setting("hide_local_cache", True)

    if not hide_cache:
        root_folder = os.path.dirname(tex_root)
        return os.path.join(root_folder, LOCAL_CACHE_FOLDER)
    else:
        cache_path = _hidden_local_cache_path()
        # convert the root to plain string and hash it
        root_hash = hash_digest(tex_root)
        return os.path.join(cache_path, root_hash)


def _hidden_local_cache_path():
    global_path = _global_cache_path()
    return os.path.join(global_path, HIDDEN_LOCAL_CACHE_FOLDER)


def _global_cache_path():
    # For ST3, put the cache files in cache dir
    # and for ST2, put it in the user packages dir
    if _ST3:
        cache_path = os.path.join(sublime.cache_path(), "LaTeXTools")
    else:
        cache_path = os.path.join(sublime.packages_path(),
                                  "User",
                                  ST2_GLOBAL_CACHE_FOLDER)
    return os.path.normpath(cache_path)


def _write(cache_path, name, obj):
    if _ST3:
        try:
            os.makedirs(cache_path, exist_ok=True)
        except FileExistsError:
            pass
    else:
        if not os.path.isdir(cache_path):
            os.makedirs(cache_path)

    file_path = os.path.join(cache_path, name)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f, protocol=-1)


def _read(cache_path, name):
    file_path = os.path.join(cache_path, name)
    if not os.path.exists(file_path):
        raise CacheMiss()

    with open(file_path, "rb") as f:
        return pickle.load(f)


_CACHE_TIMESTAMP_FILE = "created_time_stamp"


def _create_cache_timestamp(cache_path):
    """
    Creates a life span with the current time (cache folder exist).
    Does only create a timestamp if it does not already exists.
    """
    access_path = os.path.join(cache_path, _CACHE_TIMESTAMP_FILE)
    if not os.path.exists(access_path):
        print(u"Writing cache creation timestamp")
        created = long(time.time())
        try:
            with open(access_path, "w") as f:
                f.write(str(created))
        except Exception as e:
            print(u"Error occured writing cache creation timestamp")
            print(e)


def _validate_life_span(cache_path):
    life_span = _read_life_span()
    # if life span is none: only manual deletion
    if life_span is None:
        return

    created = _read_cache_timestamp(cache_path)

    current_time = long(time.time())
    if created + life_span < current_time:
        print(u"Life span of local cache is over. Invalidate local cache.")
        invalidate_local_cache(cache_path)
        raise CacheMiss(u"Cache life span expired")


def _read_cache_timestamp(cache_path):
    access_path = os.path.join(cache_path, _CACHE_TIMESTAMP_FILE)
    try:
        with open(access_path, "r") as f:
            created = long(f.read())
    except:
        print(u"No creation timestamp for local cache")
        invalidate_local_cache(cache_path)
        raise CacheMiss(u"Life span timestamp missing")
    return created


def _read_life_span():
    try:
        life_span_string = get_setting("local_cache_life_span")
        if not life_span_string:
            raise Exception(u"No lifespan defined")
        if life_span_string == "infinite":
            return None
        life_span = _parse_life_span_string(life_span_string)
    except:
        life_span = 30 * 60  # default: 30 mins
    return life_span


def _parse_life_span_string(life_span_string):
    """Parses a life span string, raises an exception if it cannot parse"""
    try:
        life_span = int(life_span_string)
    except:
        life_span = _convert_life_span_string(life_span_string)
    if life_span <= 0:
        raise Exception("Life span must be greater than 0")
    return life_span


def _convert_life_span_string(life_span_string):
    """Converts a TIME_RE compatible life span string,
    raises an exception if it is not compatible"""
    (d, h, m, s) = TIME_RE.match(life_span_string).groups()
    # time conversions in seconds
    times = [(s, 1), (m, 60), (h, 3600), (d, 86400)]
    # sum the converted times
    # if not specified (None) use 0
    return sum(int(t[0] or 0) * t[1] for t in times)
