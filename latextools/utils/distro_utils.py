import sublime

from .settings import get_setting

def using_miktex():
    platform_settings = get_setting(sublime.platform(), {})
    distro = platform_settings.get("distro", "")

    if sublime.platform() == "windows":
        return distro != "texlive"
    else:
        return distro == "miktex"
