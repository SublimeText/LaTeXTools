# based on Keith Hall's forum entry:
# https://forum.sublimetext.com/t/feature-request-plugins-access-quickpanel-text/26804/4?u=r-stein
import sublime
import sublime_plugin

exports = [
    "_InputQuickpanelListener", "LatextoolsConfirmQuickpanelCommand"
]

_DO_NOTHING = 0
_SEARCH_QUICKPANEL = 1
_CAPTURE_QUICKPANEL = 2


class _InputQuickpanelListener(sublime_plugin.EventListener):
    _capturing = _DO_NOTHING
    _confirmed = False
    _view_id = -1
    _last_known_text = ""

    @staticmethod
    def get_view_content(view_id):
        view = sublime.View(view_id)
        return view.substr(sublime.Region(0, view.size()))

    @classmethod
    def start_capture_quickpanel(cls):
        cls._capturing = _SEARCH_QUICKPANEL
        cls._confirmed = False
        cls._view_id = -1
        cls._last_known_text = ""

    @classmethod
    def is_quickpanel_captured(cls):
        return cls._capturing > 0

    @classmethod
    def confirm_quickpanel(cls, window):
        cls._confirmed = True
        window.run_command("hide_overlay")

    @classmethod
    def is_quickpanel_confirmed(cls):
        return cls._confirmed

    @classmethod
    def get_quickpanel_text(cls):
        return cls._last_known_text

    @classmethod
    def capture_and_show_input_quick_panel(cls, window, items, on_done, flags,
                                           selected_index, on_highlight):
        def wrap_on_done(index):
            if cls.is_quickpanel_confirmed():
                assert index == -1
                index = None
            on_done(index, cls.get_quickpanel_text())

        cls.start_capture_quickpanel()
        window.show_quick_panel(
            items, wrap_on_done, flags=flags, selected_index=selected_index,
            on_highlight=on_highlight
        )

    def on_activated(self, view):
        cls = self.__class__
        if cls._capturing == _SEARCH_QUICKPANEL:
            cls._view_id = view.id()
            cls._capturing = _CAPTURE_QUICKPANEL

    def on_deactivated(self, view):
        cls = self.__class__
        if view.id() == cls._view_id:
            cls._last_known_text = self.get_view_content(cls._view_id)
            cls._capturing = _DO_NOTHING

    def on_query_context(self, view, key, operator, operand, match_all):
        if key != "latextools.input_overlay_visible":
            return
        return self.is_quickpanel_captured()


class LatextoolsConfirmQuickpanelCommand(sublime_plugin.WindowCommand):
    def run(self):
        _InputQuickpanelListener.confirm_quickpanel(self.window)


# on_done: (int/None, str) => ?
def show_input_quick_panel(window, items, on_done, flags=0,
                           selected_index=-1, on_highlight=None):
    _InputQuickpanelListener.capture_and_show_input_quick_panel(
        window, items, on_done, flags, selected_index, on_highlight)
