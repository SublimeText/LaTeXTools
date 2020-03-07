import os
import sublime
import sublime_plugin

from .deprecated_command import deprecate

class LatextoolsOpenDefaultSettingsCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(LatextoolsOpenDefaultSettingsCommand, self).__init__(*args, **kwargs)
        self.view = None

    def run(self, **args):
        file = args.get('file', 'LaTeXTools.sublime-settings')

        self.view = sublime.active_window().open_file(
            os.path.join(
                sublime.packages_path(),
                "LaTeXTools",
                file
            )
        )

        sublime.set_timeout(self.set_view_readonly, 1)

    def set_view_readonly(self):
        if self.view is None or self.view.is_loading():
            sublime.set_timeout(self.set_view_readonly, 1)
            return

        self.view.set_read_only(True)


class LatextoolsOpenUserSettingsCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(LatextoolsOpenUserSettingsCommand, self).__init__(*args, **kwargs)
        self.view = None

    def run(self):
        user_settings = os.path.join(
            sublime.packages_path(),
            "User",
            "LaTeXTools.sublime-settings"
        )

        load_default = False
        if not os.path.exists(user_settings):
            migrate = sublime.ok_cancel_dialog(
                'You do not currently have a personalized '
                'LaTeXTools.sublime-settings file.\n\n'
                'Create a copy of the default settings file in '
                'your User directory?'
            )

            if migrate:
                sublime.active_window().run_command('latextools_migrate')
            else:
                load_default = True

        self.view = sublime.active_window().open_file(user_settings)

        if load_default:
            sublime.set_timeout(self.set_content, 1)

    def set_content(self):
        if self.view is None or self.view.is_loading():
            sublime.set_timeout(self.set_content, 1)
            return

        self.view.run_command('create_empty_user_file')


class LatextoolsCreateEmptyUserSettingsFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, '{\n\t\n}\n')
        self.view.run_command('save')

        for sel in self.view.sel():
            self.view.sel().subtract(sel)

        self.view.sel().add(sublime.Region(3, 3))

    def is_visible(self):
        return False


deprecate(globals(), 'OpenLatextoolsDefaultSettingsCommand', LatextoolsOpenDefaultSettingsCommand)
deprecate(globals(), 'OpenLatextoolsUserSettingsCommand', LatextoolsOpenUserSettingsCommand)
deprecate(globals(), 'CreateEmptyUserFile', LatextoolsCreateEmptyUserSettingsFileCommand)
