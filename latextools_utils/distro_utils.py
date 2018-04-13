import sublime

try:
    from latextools_utils import get_setting
except ImportError:
    from . import get_setting


def using_miktex():
    platform_settings = get_setting(sublime.platform(), {})
    distro = platform_settings.get('distro', '')

    if sublime.platform() == 'windows':
        return distro in ['miktex', '']
    else:
        return distro == 'miktex'
