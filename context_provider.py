from functools import partial
import operator as opi
import re

import sublime
import sublime_plugin

from .latextools_utils import analysis
from .latextools_utils.settings import get_setting
from .latextools_utils.selectors import build_ast, match_selector


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
            "state": {},
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
        ana = analysis.get_analysis(view)
        if not ana:
            return ""
        com = ana.filter_commands("documentclass")
        if not com:
            return ""
        doc_class = com[0].args
        return doc_class

    def _ctx_usepackage(self, view, consume_operand, operand, **kwargs):
        falsity = False if consume_operand else ""
        ana = analysis.get_analysis(view)
        if not ana:
            return falsity
        com = ana.filter_commands("usepackage")
        if not com:
            return falsity
        packages = [
            p.strip()
            for c in com
            for p in c.args.split(",")
        ]
        if consume_operand:
            return operand in packages
        else:
            return ",".join(packages)
    _ctx_usepackage.consume_operand = True

    def _ctx_env_selector(self, view, sel, operand, **kwargs):
        # we use the state to store the ast
        try:
            ast = self._env_ast_cache[operand]
        except KeyError:
            ast = self._env_ast_cache[operand] = build_ast(operand)
        res = match_selector(ast, partial(self._inside_envs, view, sel.b))
        return res
    _env_ast_cache = {}
    _ctx_env_selector.consume_operand = True
    _ctx_env_selector.foreach = True

    def _inside_envs(self, view, pos, envs):
        # for each environment search for the closest begin command
        search_end = pos
        for env in reversed(envs):
            # create the search regex
            only_nearest = False
            if env.endswith("^"):
                env = env[:-1]
                only_nearest = True
            star = {
                env.endswith("!"): "",
                env.endswith("*"): r"\*",
            }.get(True, r"\*?")
            env = env.rstrip("*!")
            benv = r"\\begin(?:\[[^\]]\])?{{{}{}}}".format(env, star)
            eenv = r"\\end{{{}{}}}".format(env, star)

            if only_nearest:
                real_benv = benv
                benv = r"\\begin(?:\[[^\]]\])?{[^\}]+}"
                eenv = r"\\end{[^\}]+}"

            # search for the regions in the document
            regions = [r for r in view.find_all(benv) if r.b < search_end]
            # if there is no \begin we are not inside the environment
            if not regions:
                return False
            closed_regions = len(list(
                r for r in view.find_all(eenv) if r.b < search_end))
            # if we have closed as many (or more?) environments as we opened
            # we are not inside the environment
            if len(regions) <= closed_regions:
                return False

            # if we only have the nearest environment check that the
            # nearest environment is the correct one
            if (only_nearest and
                    not re.match(real_benv, view.substr(regions[-1]))):
                return False

            # update the end if the search to the start of the closest
            # environment
            search_end = regions[-1].a
        # if this position is reaching each environment has been found
        # -> return True to indicate that it matches
        return True

    def _ctx_command_selector(self, view, sel, operand, **kwargs):
        # we use the state to store the ast
        try:
            ast = self._command_ast_cache[operand]
        except KeyError:
            ast = self._command_ast_cache[operand] = build_ast(operand)
        res = match_selector(ast, partial(self._inside_coms, view, sel.b))
        return res
    _command_ast_cache = {}
    _ctx_command_selector.consume_operand = True
    _ctx_command_selector.foreach = True

    def _inside_coms(self, view, pos, coms):
        # TODO threshold?
        command_re = analysis._RE_COMMAND
        args_index = command_re.groupindex["args"]
        text = view.substr(sublime.Region(0, view.size()))
        inside_commands = []

        # get all surrounding commands (search for commands in the args)
        text_pos = pos
        while text:
            try:
                command_match = next(
                    c for c in command_re.finditer(text)
                    if c.start() < text_pos and text_pos < c.end()
                )
            except StopIteration:
                break
            command = command_match.group("command")
            text = command_match.group(args_index)
            text_pos = pos - command_match.regs[args_index][0]
            has_star = bool(command_match.group("star"))
            # append the command name to the surrounding commands
            inside_commands.append((command, has_star))

        # goto over all search commands
        for com in reversed(coms):
            only_nearest = False
            if com.endswith("^"):
                com = com[:-1]
                only_nearest = True
            star = {
                com.endswith("!"): False,
                com.endswith("*"): True,
            }.get(True, None)
            com = com.rstrip("*!^")
            # go over all surrounding commands and search for the command
            while inside_commands:
                head, has_star = inside_commands.pop()
                # stop the search if the head matches
                if head == com and (star is None or has_star is star):
                    break
                # if we only search for the nearest command the head
                # must match
                elif only_nearest:
                    return False
            # if we iterated over all commands, but found none return False
            else:
                return False
        # return True if all commands are processed successfully
        return True
