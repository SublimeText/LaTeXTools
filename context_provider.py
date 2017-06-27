import operator as opi
import re

import sublime
import sublime_plugin

from .latextools_utils import analysis
from .latextools_utils.settings import get_setting


operator_map = {
    sublime.OP_EQUAL: opi.eq,
    sublime.OP_NOT_EQUAL: opi.ne,
    sublime.OP_REGEX_CONTAINS: re.search,
    sublime.OP_NOT_REGEX_CONTAINS: lambda p, s: not re.search(p, s),
    sublime.OP_REGEX_MATCH: re.match,
    sublime.OP_NOT_REGEX_MATCH: lambda p, s: not re.match(p, s),
}


class LatextoolsContextListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if not key.startswith("latextools."):
            return
        if not view.score_selector(0, "text.tex.latex"):
            return

        key_array = key.split(".")

        try:
            method_name = "_ctx_{}".format(key_array[1])
            context_method = getattr(self, method_name)
        except IndexError:
            return
        except AttributeError:
            print("Unsupported LaTeXTools context: {0}".format(key))
            return

        try:
            foreach = context_method.foreach
        except AttributeError:
            foreach = True

        op = operator_map[operator]
        keys = key_array[2:]
        if foreach:
            quantor = all if match_all else any
            result = quantor(
                op(operand, context_method(view, sel, keys))
                for sel in view.sel()
            )
        else:
            result = op(operand, context_method(view, keys))

        return result

    def _ctx_setting(self, view, keys, *args, **kwargs):
        return get_setting(keys[0], view=view)
    _ctx_setting.foreach = False

    def _ctx_documentclass(self, view, *args, **kwargs):
        cache_key = "latextools.context.documentclass"
        doc_class = view.settings().get(cache_key)
        if not doc_class:
            ana = analysis.get_analysis(view)
            com = ana.filter_commands("documentclass")
            if not com:
                return ""
            doc_class = com[0].args
            if doc_class:
                view.settings().set(cache_key, doc_class)
        return doc_class
    _ctx_documentclass.foreach = False

    def _ctx_usepackage(self, *args, **kwargs):
        print("LaTeXTools context 'usedpackage' not implemented")
        pass

    def _ctx_env_selector(self, view, sel, keys, *args, **kwargs):
        print("LaTeXTools context 'env_selector' not implemented")
        pass
