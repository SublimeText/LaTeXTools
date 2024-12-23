import webbrowser

import sublime_plugin

__all__ = ["LatextoolsOpenDetexifyCommand"]


class LatextoolsOpenDetexifyCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        webbrowser.open("https://detexify.kirelabs.org/classify.html")
