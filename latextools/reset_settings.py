from pathlib import Path

import sublime
import sublime_plugin

__all__ = ["LatextoolsResetSettingsCommand"]


class LatextoolsResetSettingsCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        user_path = Path(sublime.packages_path(), "User")
        (user_path / "LaTeXTools.sublime-settings").unlink(missing_ok=True)
        (user_path / "LaTeXTools  (Advanced).sublime-settings").unlink(missing_ok=True)
