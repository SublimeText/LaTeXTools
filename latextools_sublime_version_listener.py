from __future__ import print_function

import sublime
import sublime_plugin

import re

VERSION = sublime.version()


class LatextoolsSublimeVersionEventListener(sublime_plugin.EventListener):

    def __init__(self, *args, **kwargs):
        super(LatextoolsSublimeVersionEventListener, self).__init__(
            *args, **kwargs
        )

        self.ops = {
            sublime.OP_EQUAL: self._equal,
            sublime.OP_NOT_EQUAL: self._not_equal,
            sublime.OP_REGEX_MATCH: self._regex_match,
            sublime.OP_NOT_REGEX_MATCH: self._not_regex_match,
            sublime.OP_REGEX_CONTAINS: self._regex_contains,
            sublime.OP_NOT_REGEX_CONTAINS: self._not_regex_contains
        }

    def on_query_context(self, view, key, operator, operand, match_all):
        if not key == 'ltt_st_build':
            return None

        try:
            return self.ops[operator](operand)
        # caution
        except KeyError:
            return None

    def _equal(self, operand):
        return VERSION == operand

    def _not_equal(self, operand):
        return VERSION != operand

    def _regex_match(self, operand):
        return re.match(operand, VERSION, re.UNICODE) is not None

    def _not_regex_match(self, operand):
        return re.match(operand, VERSION, re.UNICODE) is None

    def _regex_contains(self, operand):
        return re.search(operand, VERSION, re.UNICODE) is not None

    def _not_regex_contains(self, operand):
        return re.search(operand, VERSION, re.UNICODE) is None
