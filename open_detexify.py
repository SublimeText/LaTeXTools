import webbrowser

import sublime_plugin


class LatextoolsOpenDetexifyCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        webbrowser.open("http://detexify.kirelabs.org/classify.html")
