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
    """
    Central context provider for latextools.-contexts
    each context method is prefixed with _ctx_contextname where
    contextname comes from latextools.contextname[.keys]

    The method can have the fields:
    foreach (false):
        whether the method should be called for each sel
    consume_operand (false):
        whether the method should be compared the operand or True
        Nonetheless it will be compared to the string of the operator is
        "equal" or "not equal"
    """

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
            foreach = False

        consume_operand = False
        if operator in (sublime.OP_EQUAL, sublime.OP_NOT_EQUAL):
            try:
                consume_operand = context_method.consume_operand
            except AttributeError:
                pass

        keys = key_array[2:]
        op = operator_map[operator]
        kwargs = {
            "view": view,
            "operator": operator,
            "operand": operand,
            "keys": keys,
            "consume_operand": consume_operand,
        }
        compare_operand = operand if not consume_operand else True
        if not foreach:
            result = op(compare_operand, context_method(**kwargs))
        else:
            quantor = all if match_all else any
            result = quantor(
                op(compare_operand, context_method(sel=sel, **kwargs))
                for sel in view.sel()
            )

        return bool(result)

    def _ctx_setting(self, view, keys, **kwargs):
        return get_setting(keys[0], view=view)

    def _ctx_st_version(self, operand, consume_operand, **kwargs):
        st_version = sublime.version()
        if not consume_operand:
            return st_version

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
        result = compare(st_version, operand.strip())
        return result
    _ctx_st_version.consume_operand = True

    def _ctx_documentclass(self, view, **kwargs):
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

    def _ctx_usepackage(self, **kwargs):
        print("LaTeXTools context 'usedpackage' not implemented")
        pass

    def _ctx_env_selector(self, view, sel, keys, **kwargs):
        print("LaTeXTools context 'env_selector' not implemented")
        pass
