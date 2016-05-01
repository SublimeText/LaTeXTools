import os
import sublime
import sublime_plugin
import subprocess


class OpenLatextoolsReadmeFile(sublime_plugin.WindowCommand):

    def run(self):
        readme = os.path.normpath(
            os.path.join(
                sublime.packages_path(),
                'LaTeXTools',
                'README.pdf'
            )
        )

        platform = sublime.platform()
        if platform == 'windows':
            os.startfile(readme)
        elif platform == 'osx':
            subprocess.call(['open', readme])
        else:
            subprocess.call(['xdg-open', readme])
