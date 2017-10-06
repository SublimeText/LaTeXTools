# -*- coding: utf-8 -*-
import functools
import html
import re
import webbrowser

import sublime
import sublime_plugin

import mdpopups
from Default.open_context_url import rex as RE_URL

from .latextools_utils import latex2e_html
import imp
# imp.reload(latex2e_html)


class _show_documentation_popup():
    def __init__(self, view, doc, pos):
        self.view = view
        self.doc = doc
        self.pos = pos
        self.history = ([], [])
        self._show_popup(on_hover=True)

    def _command_close(self):
        self.view.hide_popup()

    def _command_go_backward(self):
        doc = self.doc
        try:
            self.doc = self.history[0].pop()
        except IndexError:
            return
        self.history[1].append(doc)
        self._show_popup()

    def _command_go_forward(self):
        doc = self.doc
        try:
            self.doc = self.history[1].pop()
        except IndexError:
            return
        self.history[0].append(doc)
        self._show_popup()

    def _follow_doc_href(self, href):
        # save the previous document in the history
        self.history[0].append(self.doc)
        # clear the go-forward history
        self.history[1].clear()
        self.doc = latex2e_html.read_href_section(href)
        self._show_popup()

    def _open_url_in_browser(self, href):
        pass
        answer = sublime.ok_cancel_dialog(
            "Do you want to open '{href}' in your browser?".format(href=href))
        if answer == sublime.DIALOG_YES:
            webbrowser.open(href)

    def _open_href(self, href):
        print("href:", href)
        if href.startswith("command-"):
            try:
                func = getattr(self, "_command_" + href[len("command-"):])
            except AttributeError:
                print("Error calling {}".format(href))
                return
            func()
        elif RE_URL.match(href):
            self._open_url_in_browser(href)
        else:
            self._follow_doc_href(href)

    def _show_popup(self, on_hover=False):
        symbols = {
            "cancel_char": "×",
            "backward_char": "←",
            "forward_char": "→",
        }
        html_head = "".join([
            '<p>',
            '<a href="command-close">{cancel_char}</a> '.format(**symbols),
            (
                '<a href="command-go_backward">{backward_char}</a> '
                .format(**symbols)
                if self.history[0] else
                '{backward_char} '.format(**symbols)
            ),
            (
                '<a href="command-go_forward">{forward_char}</a> '
                .format(**symbols)
                if self.history[1] else
                '{forward_char} '.format(**symbols)
            ),
            '</p>',
        ])
        html_content = html_head + (self.doc or "No documentation found.")
        mdpopups.show_popup(
            self.view, html_content, md=False, location=self.pos,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY if on_hover else 0,
            on_navigate=self._open_href
        )


class LatexEnvHtmlDocumentationHoverListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return
        if not view.score_selector(
                point,
                "text.tex.latex variable.parameter.function.latex"):
            return

        word_reg = view.word(point)

        line_before = view.substr(
            sublime.Region(view.line(word_reg.a).a, word_reg.a))[::-1]

        # check that it inside a begin/end environment
        if not re.match(r"\w*{(?:nigeb|dne)\\", line_before):
            return

        env_name = view.substr(word_reg)

        doc = latex2e_html.read_env_documentation(env_name)

        pos = word_reg.a
        _show_documentation_popup(view, doc, pos)


class LatexCommandHtmlDocumentationHoverListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return
        if not view.score_selector(
                point,
                "text.tex.latex & ("
                "    support.function"
                "  | keyword.other"
                "  | constant.character.escape"
                ")"):
            return
        word_reg = view.word(point)
        command = view.substr(word_reg)
        char_before = sublime.Region(word_reg.a - 1, word_reg.a)
        if command.startswith("\\"):
            pass
        elif not view.substr(char_before) == "\\":
            return
        else:
            command = "\\" + command
        print("command:", command)
        doc = latex2e_html.read_command_documentation(command)

        pos = word_reg.a
        _show_documentation_popup(view, doc, pos)
