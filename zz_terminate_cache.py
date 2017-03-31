import sublime

try:
    try:
        from .latextools_utils.cache import _terminate_cache_threadpool
    except (ValueError, ImportError):
        from latextools_utils.cache import _terminate_cache_threadpool
except (ValueError, ImportError):
    pass
else:
    plugin_unloaded = _terminate_cache_threadpool

    if sublime.version() < '3000':
        import inspect

        def unload_handler():
            frame = inspect.currentframe()
            try:
                if frame.f_back.f_back.f_code.co_name == 'reload_plugin':
                    return
            finally:
                del frame

            _terminate_cache_threadpool()
