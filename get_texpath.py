import sublime
import os
import sys

if sublime.version() < '3000':
    _ST3 = False
else:
    _ST3 = True

__all__ = ['get_texpath']

def get_texpath():
    settings = sublime.load_settings('LaTeXTools.sublime-settings')
    platform_settings = settings.get(sublime.platform())
    texpath = platform_settings['texpath']

    if not _ST3:
        return os.path.expandvars(texpath).encode(sys.getfilesystemencoding())
    else:
        return os.path.expandvars(texpath)
