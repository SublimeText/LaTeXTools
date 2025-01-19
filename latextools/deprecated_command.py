import sublime
import sublime_plugin

from .utils.logging import logger
from .utils.settings import global_settings

__all__ = ["deprecate", "LatextoolsFindDeprecatedCommandsCommand"]

_setting_name = "compatibility_enable_version3_commands"


class LatextoolsDeprecatedCommand:
    # every subclass should overwrite this attribute
    new_classname = ""

    def run(self, *args, **kwargs):
        settings = global_settings()
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
        logger.warning('LaTeXTools WARN: "%s" has been renamed to "%s"', name, new_name)
        activate_commands = sublime.ok_cancel_dialog(
            'Dear LaTeXTools user,\n\n you have called the command "{}", '
            "which has been deprecated during a major refactoring "
            'and is now called "{}" and will be removed in the future.\n'
            "Please update your keybindings accordingly. "
            "Until then you can active the old commands during this session.\n"
            "To disable this dialog you can set the setting "
            '"{}" in LaTeXTools user settings to true (not recommended).'.format(
                name, new_name, _setting_name
            ),
            "Activate deprecated commands (I will update the bindings later)",
        )
        return activate_commands

    def _run_new_command(self, kwargs):
        new_name = self.new_name()
        logger.warning("Running %s instead of %s", new_name, self.name())
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
        return _convert_name(clsname)


def _convert_name(clsname):
    name = clsname[0].lower()
    last_upper = False
    for c in clsname[1:]:
        if c.isupper() and not last_upper:
            name += "_"
            name += c.lower()
        else:
            name += c
        last_upper = c.isupper()
    if name.endswith("_command"):
        name = name[0:-8]
    return name


if "deprecated_commands" not in globals():
    deprecated_commands = {}


def deprecate(module, old_classname, NewClass):
    if issubclass(NewClass, sublime_plugin.TextCommand):
        ParentClass = sublime_plugin.TextCommand
    else:
        ParentClass = sublime_plugin.WindowCommand

    new_classname = NewClass.__name__
    deprecated_commands[_convert_name(old_classname)] = _convert_name(new_classname)
    module[old_classname] = type(
        old_classname,
        (LatextoolsDeprecatedCommand, ParentClass),
        {"new_classname": new_classname},
    )


class LatextoolsFindDeprecatedCommandsCommand(sublime_plugin.TextCommand):
    def is_visible(self):
        return self.view.match_selector(0, "source.json.sublime")

    def run(self, edit):
        view = self.view

        regex = '"(:?{})"'.format("|".join(deprecated_commands.keys()))
        all_deprecated_commands = view.find_all(regex)
        if not all_deprecated_commands:
            sublime.message_dialog("No deprecated commands found in this view.")
        for region in reversed(all_deprecated_commands):
            view.show_at_center(region)

            old_command = view.substr(region)[1:-1]
            new_command = deprecated_commands[old_command]
            r = sublime.yes_no_cancel_dialog(
                "Replace {} with {}?".format(old_command, new_command),
                "Replace!",
                "Next",
            )
            if r == sublime.DIALOG_CANCEL:
                return
            elif r == sublime.DIALOG_NO:
                continue
            view.replace(edit, region, '"{}"'.format(new_command))
