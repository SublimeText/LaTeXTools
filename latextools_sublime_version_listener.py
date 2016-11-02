from __future__ import print_function

import sublime
import sublime_plugin

import operator as opi
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
        if not key == 'latextools.st_version':
            return None

        try:
            return self.ops[operator](operand)
        # caution
        except KeyError:
            return None

    def _equal(self, operand):
        # if the operand starts with <, >, <=, >=, (=, or ==)
        # change the compare operator correspondingly and strip the operand
        if operand[0:1] in "<>=":
            i = 1 if operand[1:2] != "=" else 2
            comp_str, operand = operand[:i], operand[i:]
            compare = {
                "<": opi.lt,
                ">": opi.gt,
                "<=": opi.le,
                ">=": opi.ge
            }.get(comp_str, opi.eq)
        else:
            compare = opi.eq
        return compare(VERSION, operand.strip())

    def _not_equal(self, operand):
        return not self._equal(operand)

    def _regex_match(self, operand):
        return re.match(operand, VERSION, re.UNICODE) is not None

    def _not_regex_match(self, operand):
        return re.match(operand, VERSION, re.UNICODE) is None

    def _regex_contains(self, operand):
        return re.search(operand, VERSION, re.UNICODE) is not None

    def _not_regex_contains(self, operand):
        return re.search(operand, VERSION, re.UNICODE) is None
