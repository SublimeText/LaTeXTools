import sublime
import codecs
import itertools
import sys
import threading
import time

try:
    from os import cpu_count
except ImportError:
    try:
        from multiprocessing import cpu_count
    # quickfix for ST2 compat
    except ImportError:
        def cpu_count():
            return 1

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils.six import reraise
else:
    _ST3 = True
    from .six import reraise


def run_after_loading(view, func):
    """Run a function after the view has finished loading"""
    def run():
        if view.is_loading():
            sublime.set_timeout(run, 10)
        else:
            # add an additional delay, because it might not be ready
            # even if the loading function returns false
            sublime.set_timeout(func, 10)
    run()


def open_and_select_region(view, file_name, region):
    new_view = view

    def select_label():
        new_view.sel().clear()
        new_view.sel().add(region)
        new_view.show(region)

    # TODO better compare?
    if view.file_name() != file_name:
        new_view = view.window().open_file(file_name)
        run_after_loading(new_view, select_label)
    else:
        select_label()


def _read_file_content(file_name, encoding="utf8", ignore=True):
    errors = "ignore" if ignore else "strict"
    with codecs.open(file_name, "r", encoding, errors) as f:
        return f.read()


def read_file_unix_endings(file_name, encoding="utf8", ignore=True):
    """
    Reads a file with unix (LF) line endings and converts windows (CRLF)
    line endings into (LF) line endings. This is necessary if you want to have
    the same string positions as in ST, because the length of ST line endings
    is 1 and the length if CRLF line endings is 2.
    """
    if _ST3:
        errors = "ignore" if ignore else "strict"
        with open(file_name, "rt", encoding=encoding, errors=errors) as f:
            file_content = f.read()
    else:
        file_content = _read_file_content(file_name, encoding, ignore)
        file_content = file_content.replace("\r\n", "\n")
    return file_content


def get_view_content(file_name):
    """
    If the file is open in a view, then this will return its content.
    Otherwise this will return None
    """
    view = get_open_view(file_name)
    if view is not None:
        return view.substr(sublime.Region(0, view.size()))


def get_open_view(file_name):
    '''
    Returns the view for the specified file_name if it exists
    '''
    active_window = sublime.active_window()
    active_view = active_window.active_view()
    # search for the file name in 3 hierarchical steps
    # 1. check the active view
    if active_view.file_name() == file_name:
        return active_view
    # 2. check all views in the active windows
    view = active_window.find_open_file(file_name)
    if view:
        return view
    # 3. check all other views
    for window in sublime.windows():
        if window == active_window:
            continue
        view = window.find_open_file(file_name)
        if view:
            return view


def get_file_content(file_name, encoding="utf8", ignore=True,
                     force_lf_endings=False):
    """
    Returns the content of this file.
    If the file is opened in a view, then the content of the view will
    be returned. Otherwise the file will be opened and the content
    will be returned.
    """
    if force_lf_endings:
        read_file_content = read_file_unix_endings
    else:
        read_file_content = _read_file_content

    content = (get_view_content(file_name) or
               read_file_content(file_name, encoding, ignore))
    return content


class TimeoutError(Exception):
    pass


__sentinel__ = object()


def run_on_main_thread(func, timeout=10, default_value=__sentinel__):
    """
    Ensures the function, func is run on the main thread and returns the rsult
    of that function call.

    Note that this function blocks the thread it is executed on and should only
    be used when the result of the function call is necessary to continue.

    Arguments:
    func (callable): a no-args callable; functions that need args should
        be wrapped in a `functools.partial`
    timeout (int): the maximum amount of time to wait in seconds. A
        TimeoutError is raised if this limit is reached a no `default_value`
        is specified
    default_value (any): the value to be returned if a timeout occurs

    Note that both timeout and default value are ignored when run in ST3 or
    from the main thread.
    """
    # quick exit condition: we are on ST3 or the main thread
    if _ST3 or threading.current_thread().getName() == 'MainThread':
        return func()

    condition = threading.Condition()
    condition.acquire()

    def _get_result():
        with condition:
            _get_result.result = func()
            condition.notify()

    sublime.set_timeout(_get_result, 0)

    condition.wait(timeout)

    if not hasattr(_get_result, 'result'):
        if default_value is __sentinel__:
            raise TimeoutError('Timeout while waiting for {0}'.format(func))
        else:
            return default_value

    return _get_result.result


class ThreadPool(object):
    '''A relatively simple ThreadPool designed to maintain a number of thread
    workers

    By default, each pool manages a number of processes equal to the number
    of CPU cores. This can be adjusted by setting the processes parameter
    when creating the pool.

    Returned results are similar to multiprocessing.pool.AsyncResult'''

    def __init__(self, processes=None):
        self._task_queue = Queue()
        self._result_queue = Queue()
        # used to indicate if the ThreadPool should be stopped
        self._should_stop = threading.Event()

        # default value is two less than the number of CPU cores to handle
        # the supervisor thread and result thread
        self._processes = max(processes or (cpu_count() or 3) - 2, 1)
        self._workers = []
        self._populate_pool()

        self._job_counter = itertools.count()
        self._result_cache = {}

        self._result_handler = threading.Thread(target=self._handle_results)
        self._result_handler.daemon = True
        self._result_handler.name = u'{0!r} handler'.format(self)
        self._result_handler.start()

        self._supervisor = threading.Thread(target=self._maintain_pool)
        self._supervisor.daemon = True
        self._supervisor.name = u'{0!r} supervisor'.format(self)
        self._supervisor.start()

    # - Public API
    def apply_async(self, func, args=(), kwargs={}):
        job = next(self._job_counter)
        self._task_queue.put((job, (func, args, kwargs)))
        return _ThreadPoolResult(job, self._result_cache)

    def is_running(self):
        return not self._should_stop.is_set()

    def terminate(self):
        '''Stops this thread pool. Note stopping is not immediate. If you
        need to wait for the termination to complete, you should call join()
        after this.'''
        self._should_stop.set()

    def join(self, timeout=None):
        self._supervisor.join(timeout)
        if self._supervisor.is_alive():
            raise TimeoutError

    # - Internal API
    # this is the supervisory task, which will clear workers that have stopped
    # and start fresh workers
    def _maintain_pool(self):
        while self.is_running():
            cleared_processes = False
            for i in reversed(range(len(self._workers))):
                w = self._workers[i]
                if not w.is_alive():
                    w.join()
                    cleared_processes = True
                    del self._workers[i]

            if cleared_processes:
                self._populate_pool()

            time.sleep(0.1)

        # send sentinels to end threads
        for _ in range(len(self._workers)):
            self._task_queue.put(None)

        # ensure worker threads end
        for w in self._workers:
            w.join()

        # stop the result handler
        self._result_queue.put(None)
        self._result_handler.join()

    def _handle_results(self):
        while True:
            result = self._result_queue.get()
            if result is None:
                break

            job, _result = result
            try:
                result_handler = self._result_cache.get(job)
                if result_handler:
                    result_handler._set_result(_result)
            finally:
                self._result_queue.task_done()

    # creates and adds worker threads
    def _populate_pool(self):
        for _ in range(self._processes - len(self._workers)):
            w = _ThreadPoolWorker(self._task_queue, self._result_queue)
            self._workers.append(w)
            w.start()


class _ThreadPoolWorker(threading.Thread):

    def __init__(self, task_queue, result_queue, *args, **kwargs):
        super(_ThreadPoolWorker, self).__init__(*args, **kwargs)
        self.daemon = True
        self._task_queue = task_queue
        self._result_queue = result_queue

    def run(self):
        while True:
            task = self._task_queue.get()
            if task is None:
                break

            job = task[0]
            func, args, kwargs = task[1]

            if args is None:
                args = ()
            if kwargs is None:
                kwargs = {}

            try:
                self._result_queue.put((job, func(*args, **kwargs)))
            except Exception:
                self._result_queue.put((job, sys.exc_info()))
            finally:
                self._task_queue.task_done()


class _ThreadPoolResult(object):

    def __init__(self, job, result_cache):
        self._ready = threading.Event()
        self._value = None
        self._result_cache = result_cache
        self._job = job
        self._result_cache[job] = self

    def ready(self):
        return self._ready.is_set()

    def wait(self, timeout=None):
        self._ready.wait(timeout)

    def get(self, timeout=None):
        self.wait(timeout)
        if not self.ready():
            raise TimeoutError

        # handle an exception, which is passed as a sys.exc_info tuple
        if (
            isinstance(self._value, tuple) and
            len(self._value) == 3 and
            issubclass(self._value[0], Exception)
        ):
            reraise(*self._value)
        else:
            return self._value

    def then(self, callback, timeout=None):
        callback(self.get(timeout))

    def _set_result(self, _value):
        self._value = _value
        self._ready.set()
        del self._result_cache[self._job]
