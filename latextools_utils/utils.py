import sublime

if sublime.version() < '3000':
    _ST3 = False
    import codecs
else:
    _ST3 = True


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
