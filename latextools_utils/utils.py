import sublime
import codecs
import threading

if sublime.version() < '3000':
    _ST3 = False
else:
    _ST3 = True


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


def _get_view_content(view):
    if view is not None:
        return view.substr(sublime.Region(0, view.size()))


def get_view_content(file_name):
    """
    If the file is open in a view, then this will return its content.
    Otherwise this will return None
    """
    active_window = sublime.active_window()
    active_view = active_window.active_view()
    # search for the file name in 3 hierarchical steps
    # 1. check the active view
    if active_view.file_name() == file_name:
        return _get_view_content(active_view)
    # 2. check all views in the active windows
    view = active_window.find_open_file(file_name)
    if view:
        return _get_view_content(view)
    # 3. check all other views
    for window in sublime.windows():
        if window == active_window:
            continue
        view = window.find_open_file(file_name)
        return _get_view_content(view)


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
