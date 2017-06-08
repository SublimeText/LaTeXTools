import sublime

from . import get_setting


def using_miktex():
    if sublime.platform() != 'windows':
        return False

    platform_settings = get_setting(sublime.platform(), {})

    try:
        distro = platform_settings.get('distro', 'miktex')
        return distro in ['miktex', '']
    except KeyError:
        return True
