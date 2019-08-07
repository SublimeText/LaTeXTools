import sublime
import sublime_plugin

_setting_name = 'compatibility_enable_version3_commands'


class LatexToolsDeprecatedCommand(object):
    # every subclass should overwrite this attribute
    new_classname = ''

    def run(self, *args, **kwargs):
        settings = sublime.load_settings('LaTeXTools.sublime-settings')
        backward_compatible = settings.get(_setting_name, False)
        if not backward_compatible:
            # check whether the new command shall be executed
            activate_commands = self._ask_for_activation()
            if not activate_commands:
                return
            # update the settings to enable backward commands,
            # but don't save them
            settings.set(_setting_name, True)
        # run the new command
        self._run_new_command(kwargs)

    def _ask_for_activation(self):
        name = self.name()
        new_name = self.new_name()
        print(
            'LaTeXTools WARN: "{}" has been renamed to "{}"'
            .format(name, new_name)
        )
        activate_commands = sublime.ok_cancel_dialog(
            'Dear LaTeXTools user,\n\n you have called the command "{}", '
            'which has been deprecated during a major refactoring '
            'and is now called "{}" and will be removed in the future.\n'
            'Please refactor your keybindings accordingly. '
            'Until then you can active the old commands during this session.\n'
            'To disable this dialog you can set the setting '
            '"{}" in LaTeXTools user settings to true (not recommended).'
            .format(name, new_name, _setting_name),
            'Activate deprecated commands, I will refactor later'
        )
        return activate_commands

    def _run_new_command(self, kwargs):
        new_name = self.new_name()
        print('running {}'.format(new_name))
        if isinstance(self, sublime_plugin.TextCommand) and self.view:
            self.view.run_command(new_name, kwargs)
        elif isinstance(self, sublime_plugin.WindowCommand) and self.window:
            self.window.run_command(new_name, kwargs)
        else:
            window = sublime.active_window()
            if window:
                window.run_command(new_name, kwargs)

    def new_name(self):
        clsname = self.new_classname
        name = clsname[0].lower()
        last_upper = False
        for c in clsname[1:]:
            if c.isupper() and not last_upper:
                name += '_'
                name += c.lower()
            else:
                name += c
            last_upper = c.isupper()
        if name.endswith("_command"):
            name = name[0:-8]
        return name


def deprecate(module, oldClassName, NewClass):
    if issubclass(NewClass, sublime_plugin.TextCommand):
        ParentClass = sublime_plugin.TextCommand
    else:
        ParentClass = sublime_plugin.WindowCommand

    module[oldClassName] = type(
        oldClassName,
        (LatexToolsDeprecatedCommand, ParentClass),
        {"new_classname": NewClass.__name__}
    )
