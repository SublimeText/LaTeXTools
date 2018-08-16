#
# On reload, this module will attempt to remove any phantoms associated
# with ViewEventListeners from all active views.
#
import sublime
import sublime_plugin

if sublime.version() > '3118' and sublime_plugin.api_ready:
    for w in sublime.windows():
        for v in w.views():
            if v.score_selector(0, 'text.tex.latex') == 0:
                continue
            v.erase_phantoms('preview_math')
            v.erase_phantoms('preview_image')
            v.settings().clear_on_change('preview_math')
            v.settings().clear_on_change('preview_image')
    s = sublime.load_settings('LaTeXTools.sublime-settings')
    s.clear_on_change('preview_math')
    s.clear_on_change('preview_image')
