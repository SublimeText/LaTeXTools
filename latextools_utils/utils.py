import sublime

if sublime.version() < '3000':
    _ST3 = False
    import codecs
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


def read_file_unix_endings(file_name, encoding="utf8"):
    """
    Reads a file with unix (LF) line endings and converts windows (CRLF)
    line endings into (LF) line endings. This is necessary if you want to have
    the same string positions as in ST, because the length of ST line endings
    is 1 and the length if CRLF line endings is 2.
    """
    if _ST3:
        with open(file_name, "rt", encoding=encoding) as f:
            file_content = f.read()
    else:
        with codecs.open(file_name, "r", encoding) as f:
            file_content = f.read()
            file_content = file_content.replace("\r\n", "\n")
    return file_content
