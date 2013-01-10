import sublime, sublime_plugin

class SteadySyncCallbackCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        print "Run"
        # Check if steady sync is enabled
        s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
        if s.get("steady_sync", True):
            if self.view.is_scratch() or not self.view.file_name():
                return
            # get the file name and try to open the pdf viewer
            file_name = self.view.file_name()
            scope = self.view.scope_name(self.view.sel()[0].a)
            base_scope_name = scope.split()[0]

            if base_scope_name == "text.tex.latex":
                print "Latex"
                self.view.run_command("jump_to_pdf")

class toggle_steady_syncCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        s = sublime.load_settings("LaTeXTools Preferences.sublime-settings")
        prefs_forward_sync = s.get("steady_sync", True)

        if self.view.settings().get("steady_sync",prefs_forward_sync):
            self.view.settings().set("steady_sync", False)
            sublime.status_message("Do not steady sync PDF (keep current position) on mouse click")
            print "Do not steady sync PDF"
        else:
            self.view.settings().set("steady_sync", True)
            sublime.status_message("Steady sync PDF on mouse click")
            print "Steady sync PDF"