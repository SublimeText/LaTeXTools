from functools import partial, wraps
import time

import sublime
import sublime_plugin


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
            diff = threshold - time.time() * 1000
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
            to_call_times[vid] = time.time() * 1000 + delay_in_ms
            if busy:
                return
            callback = partial(func, self, *args, **kwargs)
            set_timeout(partial(_debounced_callback, view, callback), delay_in_ms)

        return wrapper

    return decorator
