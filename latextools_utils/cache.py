import collections
import copy
import hashlib
import os
import re
import shutil
import time
import threading
import traceback

try:
    import cPickle as pickle
except ImportError:
    import pickle

import sublime

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils import get_setting
    from external.frozendict import frozendict
    from latextools_utils.six import unicode, long, strbase
    from latextools_utils.system import make_dirs
    from latextools_utils.utils import ThreadPool
else:
    _ST3 = True
    from . import get_setting
    from ..external.frozendict import frozendict
    from .six import unicode, long, strbase
    from .system import make_dirs
    from .utils import ThreadPool


# the folder, if the local cache is not hidden, i.e. folder in the same
# folder as the tex root
LOCAL_CACHE_FOLDER = ".st_lt_cache"
# folder to store all hidden local caches in the cache path
HIDDEN_LOCAL_CACHE_FOLDER = "local_cache"
# global cache folder for ST2, this folder will be created inside the User
# folder to store the global and the local cache
ST2_GLOBAL_CACHE_FOLDER = ".lt_cache"

# re for parsing the local_cache_life_span setting when written
# in "natural" language:
# 100 d(ays) 100 h(ours) 100 m((in)utes) 100 s((ec)onds)
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


def cache_local(tex_root, key, func):
    '''
    alias for cache() on the LocalCache instance corresponding to the tex_root:

    convenience method to attempt to get the value from the cache and
    generate the value if it hasn't been cached yet or the entry has
    otherwise been invalidated

    :param tex_root:
        the tex_root the data should be associated with

    :param key:
        the key to retrieve or set

    :param func:
        a callable that takes no arguments and when invoked will return
        the proper value
    '''
    return LocalCache(tex_root).cache(key, func)


def write_local(tex_root, key, obj):
    '''
    alias for set() on the LocalCache instance corresponding to the tex_root:

    set the cache value for the given key

    :param tex_root:
        the tex_root the data should be associated with

    :param key:
        the key to set

    :param obj:
        the value to store; note that obj *must* be picklable
    '''
    return LocalCache(tex_root).set(key, obj)


def read_local(tex_root, key):
    '''
    alias for get() on the LocalCache instance corresponding to the tex_root:

    retrieve the cached value for the corresponding key

    raises CacheMiss if value has not been cached

    :param tex_root:
        the tex_root the data should be associated with

    :param key:
        the key to set
    '''
    return LocalCache(tex_root).get(key)


def cache_global(key, func):
    '''
    alias for cache() on the GlobalCache:

    convenience method to attempt to get the value from the cache and
    generate the value if it hasn't been cached yet or the entry has
    otherwise been invalidated

    :param key:
        the key to retrieve or set

    :param func:
        a callable that takes no arguments and when invoked will return
        the proper value
    '''
    return GlobalCache().cache(key, func)


def write_global(key, obj):
    '''
    alias for set() on the GlobalCache:

    set the cache value for the given key

    :param key:
        the key to set

    :param obj:
        the value to store; note that obj *must* be picklable
    '''
    return GlobalCache().set(key, obj)


def read_global(key):
    '''
    alias for get() on the GlobablCache:

    retrieve the cached value for the corresponding key

    raises CacheMiss if value has not been cached

    :param tex_root:
        the tex_root the data should be associated with

    :param key:
        the key to set
    '''
    return GlobalCache().get(key)


# aliases
cache = cache_local
write = write_local
read = read_local

if _ST3:
    def _global_cache_path():
        return os.path.normpath(os.path.join(
            sublime.cache_path(), "LaTeXTools"))
else:
    def _global_cache_path():
        return os.path.normpath(os.path.join(
            sublime.packages_path(), "User", ST2_GLOBAL_CACHE_FOLDER))


# marker object for invalidated result
try:
    _invalid_object
except NameError:
    _invalid_object = object()


class Cache(object):
    '''
    default cache object and definition

    implements the shared functionality between the various caches
    '''

    def __new__(cls, *args, **kwargs):
        # don't allow this class to be instantiated directly
        if cls is Cache:
            raise NotImplemented

        return super(Cache, cls).__new__(cls)

    def __init__(self):
        # initialize state but ONLY if it hasn't already been initialized
        if not hasattr(self, '_disk_lock'):
            self._disk_lock = threading.Lock()
        if not hasattr(self, '_write_lock'):
            self._write_lock = threading.Lock()
        if not hasattr(self, '_save_lock'):
            self._save_lock = threading.Lock()
        if not hasattr(self, '_objects'):
            self._objects = {}
        if not hasattr(self, '_dirty'):
            self._dirty = False
        if not hasattr(self, '_save_queue'):
            self._save_queue = []
        if not hasattr(self, '_pool'):
            self._pool = ThreadPool(2)

        self.cache_path = self._get_cache_path()

    def get(self, key):
        '''
        retrieve the cached value for the corresponding key

        raises CacheMiss if value has not been cached

        :param key:
            the key that the value has been stored under
        '''
        if key is None:
            raise ValueError('key cannot be None')

        try:
            result = self._objects[key]
        except KeyError:
            # note: will raise CacheMiss if can't be found
            result = self.load(key)

        if result is _invalid_object:
            raise CacheMiss('{0} is invalid'.format(key))

        # return a copy of any objects
        try:
            if hasattr(result, '__dict__') or hasattr(result, '__slots__'):
                result = copy.copy(result)
        except:
            pass

        return result

    def has(self, key):
        '''
        check if cache has a value for the corresponding key

        :param key:
            the key that the value has been stored under
        '''
        if key is None:
            raise ValueError('key cannot be None')

        return (
            key in self._objects and
            self._objects[key] is not _invalid_object
        )

    def set(self, key, obj):
        '''
        set the cache value for the given key

        :param key:
            the key to store the value under

        :param obj:
            the value to store; note that obj *must* be picklable
        '''
        if key is None:
            raise ValueError('key cannot be None')

        try:
            pickle.dumps(obj, protocol=-1)
        except pickle.PicklingError:
            raise ValueError('obj must be picklable')

        if isinstance(obj, list):
            obj = tuple(obj)
        elif isinstance(obj, dict):
            obj = frozendict(obj)
        elif isinstance(obj, set):
            obj = frozenset(obj)

        with self._write_lock:
            self._objects[key] = obj
            self._dirty = True
        self._schedule_save()

    def cache(self, key, func):
        '''
        convenience method to attempt to get the value from the cache and
        generate the value if it hasn't been cached yet or the entry has
        otherwise been invalidated

        :param key:
            the key to retrieve or set

        :param func:
            a callable that takes no arguments and when invoked will return
            the proper value
        '''
        if key is None:
            raise ValueError('key cannot be None')

        try:
            return self.get(key)
        except:
            result = func()
            self.set(key, result)
            return result

    def invalidate(self, key=None):
        '''
        invalidates either this whole cache, a single entry or a list of
        entries in this cache

        :param key:
            the key of the entry to invalidate; if None, the entire cache
            will be invalidated
        '''
        def _invalidate(key):
            try:
                self._objects[key] = _invalid_object
            except:
                print('error occurred while invalidating {0}'.format(key))
                traceback.print_exc()

        with self._write_lock:
            if key is None:
                for k in self._objects.keys():
                    _invalidate(k)
            else:
                if isinstance(key, strbase):
                    _invalidate(key)
                else:
                    for k in key:
                        _invalidate(k)

        self._schedule_save()

    def _get_cache_path(self):
        return _global_cache_path()

    def load(self, key=None):
        '''
        loads the value specified from the disk and stores it in the in-memory
        cache

        :param key:
            the key to load from disk; if None, all entries in the cache
            will be read from disk
        '''
        with self._write_lock:
            if key is None:
                for entry in os.listdir(self.cache_path):
                    if os.path.isfile(entry):
                        entry_name = os.path.basename[entry]
                        try:
                            self._objects[entry_name] = self._read(entry_name)
                        except:
                            print(
                                u'error while loading {0}'.format(entry_name))
            else:
                self._objects[key] = self._read(key)

    def load_async(self, key=None):
        '''
        an async version of load; does the loading in a new thread
        '''
        self._pool.apply_async(self.load, key)

    def _read(self, key):
        file_path = os.path.join(self.cache_path, key)
        with self._disk_lock:
            try:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            except:
                raise CacheMiss(u'cannot read cache file {0}'.format(key))

    def save(self, key=None):
        '''
        saves the cache entry specified to disk

        :param key:
            the entry to flush to disk; if None, all entries in the cache will
            be written to disk
        '''
        if not self._dirty:
            return

        # lock is aquired here so that all keys being flushed reflect the
        # same state; note that this blocks disk reads, but not cache reads
        with self._disk_lock:
            # operate on a stable copy of the object
            with self._write_lock:
                _objs = copy.deepcopy(self._objects)
                self._dirty = False

            if key is None:
                # remove all InvalidObjects
                delete_keys = [
                    k for k in _objs if _objs[k] is _invalid_object
                ]

                for k in delete_keys:
                    del _objs[k]

                if _objs:
                    make_dirs(self.cache_path)
                    for k in _objs.keys():
                        try:
                            self._write(k, _objs)
                        except:
                            traceback.print_exc()
                else:
                    # cache has been emptied, so remove it
                    try:
                        shutil.rmtree(self.cache_path)
                    except:
                        print(
                            'error while deleting {0}'.format(self.cache_path))
                        traceback.print_exc()
            elif key in _objs:
                if _objs[key] is _invalid_object:
                    file_path = os.path.join(self.cache_path, key)
                    try:
                        os.path.remove(file_path)
                    except:
                        print('error while deleting {0}'.format(file_path))
                        traceback.print_exc()
                else:
                    make_dirs(self.cache_path)
                    self._write(key, _objs)

    def save_async(self, key=None):
        '''
        an async version of save; does the save in a new thread
        '''
        self._pool.apply_async(self.save, key)

    def _write(self, key, obj):
        try:
            _obj = obj[key]
        except KeyError:
            raise CacheMiss()

        try:
            with open(os.path.join(self.cache_path, key), 'wb') as f:
                pickle.dump(_obj, f, protocol=-1)
        except OSError:
            print('error while writing to {0}'.format(key))
            traceback.print_exc()
            raise CacheMiss()

    def _schedule_save(self):
        with self._save_lock:
            self._save_queue.append(0)
            threading.Timer(0.5, self._debounce_save).start()

    def _debounce_save(self):
        with self._save_lock:
            if len(self._save_queue) > 1:
                self._save_queue.pop()
            else:
                self._save_queue = []
                sublime.set_timeout(self.save_async, 0)

    # ensure cache is saved to disk when removed from memory
    def __del__(self):
        self.save_async()
        self._pool.terminate()


class GlobalCache(Cache):
    '''
    the global cache

    stores data in the appropriate global cache folder; SHOULD NOT be used
    for data related to a particular tex document

    note that all instance of the global cache share state, meaning that it
    behaves as though there were a single object
    '''

    __STATE = {}

    def __new__(cls, *args, **kwargs):
        # almost-singleton implementation; all instances share the same state
        inst = super(GlobalCache, cls).__new__(cls, *args, **kwargs)
        inst.__dict__ = cls.__STATE
        return inst

    def invalidate(self, key):
        if key is None:
            raise ValueError('key must not be None')
        super(GlobalCache, self).invalidate(key)


class ValidatingCache(Cache):
    '''
    an abstract class for a cache which implements validation either when an
    entry is retrieved or changed

    implementing subclasses SHOULD override validate_on_get or validate_on_set
    as appropriate
    '''

    def __new__(cls, *args, **kwargs):
        # don't allow this class to be instantiated directly
        if cls is ValidatingCache:
            raise NotImplemented

        return super(ValidatingCache, cls).__new__(cls, *args, **kwargs)

    def validate_on_get(self, key):
        '''
        subclasses should override this to run validation when an object is
        retrieved from the cache

        subclasses should raise a ValueError if the validation shouldn't
        succeed
        '''

    def validate_on_set(self, key, obj):
        '''
        subclasses should override this to run validation when an object is
        added or modified in the cache

        subclasses should raise a ValueError if the validation shouldn't
        succeed
        '''

    def get(self, key):
        try:
            self.validate_on_get(key)
        except ValueError as e:
            self.invalidate()
            raise CacheMiss(unicode(e))

        return super(ValidatingCache, self).get(key)

    get.__doc__ = Cache.get.__doc__

    def set(self, key, obj):
        if key is None:
            raise ValueError('key cannot be None')

        self.validate_on_set(key, obj)

        return super(ValidatingCache, self).set(key, obj)

    set.__doc__ = Cache.set.__doc__


class InstanceTrackingCache(Cache):
    '''
    an abstract class for caches that share state between different instances
    that point to the same underlying data; in addition, when all instances
    of a given cache have been removed from memory, the cache is written to
    disk

    this is used, for example, by the local cache to ensure that all documents
    with the same tex_root share a local cache instance; this helps minimize
    memory usage and ensure data consistency across multiple cache instances,
    e.g., caches instantiated in different functions or multiple ST views of
    the "same" document

    subclasses MUST implement the _get_inst_key method
    '''

    _CLASSES = set([])

    def __new__(cls, *args, **kwargs):
        if cls is InstanceTrackingCache:
            raise NotImplemented

        InstanceTrackingCache._CLASSES.add(cls)

        if not hasattr(cls, '_INSTANCES'):
            cls._INSTANCES = collections.defaultdict(lambda: {})
            cls._REF_COUNTS = collections.defaultdict(lambda: 0)
            cls._LOCKS = collections.defaultdict(lambda: threading.Lock())

        inst = super(InstanceTrackingCache, cls).__new__(cls, *args, **kwargs)
        inst_key = inst._get_inst_key(*args, **kwargs)

        with cls._LOCKS[inst_key]:
            inst.__dict__ = cls._INSTANCES[inst_key]
            cls._REF_COUNTS[inst_key] += 1

        return inst

    def _get_inst_key(self, *args, **kwargs):
        '''
        subclasses MUST override this method to return a key which identifies
        this instance; this key MUST be able to be used as a dictionary key

        the key is intended to be shared by multiple instances of the cache,
        but only those which represent the same underlying data; for example,
        the LocalCache uses the tex_root value as its key, so that all
        documents with the same tex_root share the same cache instance

        NB this method is called in TWO DISTINCT ways and subclass
        implementations MUST be able to generate the same response for both or
        else the behavior of the instance-tracking cannot be guaranteed.

            1)  This method is called from __new__ with the args and kwargs
                passed to the constructor; subclasses SHOULD derive the key
                from those args
            2)  This method is called from __del__ without the args and kwargs
                passed to the construtor; subclasses MUST ensure that the same
                key derived in #1 can be derived in this case from information
                stored in the object
        '''
        raise NotImplemented

    # ensure the cache is written to disk when LAST copy of this instance is
    # removed
    def __del__(self):
        inst_key = self._get_inst_key()
        if inst_key is None:
            return

        with self._LOCKS[inst_key]:
            ref_count = self._REF_COUNTS[inst_key]
            ref_count -= 1
            self._REF_COUNTS[inst_key] = ref_count

            if ref_count <= 0:
                self.save_async()
                self._pool.terminate()
                del self._REF_COUNTS[inst_key]
                del self._INSTANCES[inst_key]


class LocalCache(ValidatingCache, InstanceTrackingCache):
    '''
    the local cache

    stores data related to a particular tex document (identified by the
    tex_root) to a uniquely named folder in the cache directory

    all data in this cache SHOULD relate directly to the tex_root
    '''

    _CACHE_TIMESTAMP = "created_time_stamp"
    _LIFE_SPAN_LOCK = threading.Lock()

    def __init__(self, tex_root):
        self.tex_root = tex_root
        # although this could change, currently only the value when the
        # cache is created is relevant
        self.hide_cache = get_setting('hide_local_cache', True)
        super(LocalCache, self).__init__()

    def validate_on_get(self, key):
        try:
            cache_time = Cache.get(self, self._CACHE_TIMESTAMP)
        except:
            raise ValueError('cannot load created timestamp')
        else:
            if not self.is_up_to_date(key, cache_time):
                raise ValueError('value outdated')

    def validate_on_set(self, key, obj):
        if not self.has(self._CACHE_TIMESTAMP):
            Cache.set(self, self._CACHE_TIMESTAMP, long(time.time()))

    def _get_inst_key(self, *args, **kwargs):
        if not hasattr(self, 'tex_root'):
            if len(args) > 0:
                return args[0]
            return None
        else:
            return self.tex_root

    def _get_cache_path(self):
        if self.hide_cache:
            cache_path = super(LocalCache, self)._get_cache_path()
            root_hash = hash_digest(self.tex_root)
            return os.path.join(
                cache_path, HIDDEN_LOCAL_CACHE_FOLDER, root_hash)
        else:
            root_folder = os.path.dirname(self.tex_root)
            return os.path.join(root_folder, LOCAL_CACHE_FOLDER)

    def is_up_to_date(self, key, timestamp):
        if timestamp is None:
            return False

        cache_life_span = LocalCache._get_cache_life_span()

        current_time = long(time.time())
        if timestamp + cache_life_span < current_time:
            return False

        return True

    @classmethod
    def _get_cache_life_span(cls):
        '''
        gets the length of time an item should remain in the local cache
        before being evicted

        note that previous values are calculated and stored since this method
        is used on every cache read
        '''
        def __parse_life_span_string():
            try:
                return long(life_span_string)
            except ValueError:
                try:
                    (d, h, m, s) = TIME_RE.match(life_span_string).groups()
                    # time conversions in seconds
                    times = [(s, 1), (m, 60), (h, 3600), (d, 86400)]
                    # sum the converted times
                    # if not specified (None) use 0
                    return sum(long(t[0] or 0) * t[1] for t in times)
                except:
                    print('error parsing life_span_string {0}'.format(
                        life_span_string))
                    traceback.print_exc()
                    # default 30 minutes in seconds
                    return 1800

        with cls._LIFE_SPAN_LOCK:
            life_span_string = get_setting('local_cache_life_span')
            try:
                if cls._PREV_LIFE_SPAN_STR == life_span_string:
                    return cls._PREV_LIFE_SPAN
            except AttributeError:
                pass

            cls._PREV_LIFE_SPAN_STR = life_span_string
            cls._PREV_LIFE_SPAN = life_span = __parse_life_span_string()
            return life_span
