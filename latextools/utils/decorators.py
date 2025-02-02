import cProfile
import pstats
import sys
from functools import partial, wraps
from timeit import default_timer

import sublime
import sublime_plugin

PROFILE = False


def async_completions(func):
    """Asynchronously query completions

    Creates and immediately returns a `sublime.CompletionList`, applying results
    once `on_query_completions` has finished executing in ST's worker thread.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        completion_list = sublime.CompletionList()

        def query():
            try:
                completions = func(*args, **kwargs)
                if completions:
                    flags = sublime.INHIBIT_WORD_COMPLETIONS
                else:
                    flags = 0
                    completions = []
            except Exception:
                completion_list.set_completions([])
                raise
            else:
                completion_list.set_completions(completions, flags)

        sublime.set_timeout_async(query)

        return completion_list

    return wrapper


def debounce(delay_in_ms, sync=False):
    """Delay calls to event hooks until they weren't triggered for n ms.

    Performs view-specific tracking and is best suited for the
    `on_modified` and `on_selection_modified` methods
    and their `_async` variants.
    The `view` is taken from the first argument for `EventListener`s
    and from the instance for `ViewEventListener`s.

    Calls are only made when the `view` is still "valid" according to ST's API,
    so it's not necessary to check it in the wrapped function.
    """

    # We assume that locking is not necessary because each function will be called
    # from either the ui or the async thread only.
    set_timeout = sublime.set_timeout if sync else sublime.set_timeout_async

    def decorator(func):
        to_call_times = {}

        def _debounced_callback(view, callback):
            vid = view.id()
            threshold = to_call_times.get(vid)
            if not threshold:
                return
            if not view.is_valid():
                del to_call_times[vid]
                return
            diff = threshold - default_timer() * 1000
            if diff > 0:
                set_timeout(partial(_debounced_callback, view, callback), diff)
            else:
                del to_call_times[vid]
                callback()

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            view = self.view if hasattr(self, 'view') else args[0]
            if not view.is_valid():
                return
            vid = view.id()
            busy = vid in to_call_times
            to_call_times[vid] = default_timer() * 1000 + delay_in_ms
            if busy:
                return
            callback = partial(func, self, *args, **kwargs)
            set_timeout(partial(_debounced_callback, view, callback), delay_in_ms)

        return wrapper

    return decorator


def profile(func):
    """Run the profiler in the given function

    Debugging helper decorateor
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not PROFILE:
            return func(*args, **kwargs)
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        ps = pstats.Stats(pr, stream=sys.stdout)
        ps.sort_stats('time')
        ps.print_stats(15)
        return result

    return wrapper


def timing(func):
    """Print decorated function's execution time

    Debugging helper decorateor
    """

    @wraps(func)
    def decorator(*args, **kw):
        ts = default_timer()
        result = func(*args, **kw)
        te = default_timer()
        print(f"{func.__name__}({args}, {kw}) took: {1000.0 * (te - ts):2.3f} ms")
        return result

    return decorator
