import re

import sublime
import sublime_plugin

from .latextools_utils import get_setting


def _RE_FIND_SECTION(command_mapping):
    return re.compile(
        r"\\(?P<command>" + "|".join(command_mapping.keys()) + "|caption)"
        r"(?:\[[^\]]*\])*"
        r"\{(?P<content>[^\}]+)\}"
    )


_RE_IS_LABEL_BEFORE = re.compile(r"(?P<brace>\{)?lebal\\")

_RE_FIND_ENV_END = r"\\end{(\w+)}"


def _create_label_content(command_content):
    label_content = []
    is_underscore = False
    char_replace = get_setting("auto_label_char_replace", {})
    for c in command_content:
        c = c.lower()
        if re.match("[a-z0-9]", c):
            label_content.append(c)
            is_underscore = False
        elif c in char_replace:
            label_content.append(char_replace[c])
            is_underscore = False
        elif not is_underscore:
            label_content.append("_")
            is_underscore = True
    label_content = "".join(label_content)
    return label_content


def _find_label_type_by_env(view, pos):
    env_end_reg = view.find(_RE_FIND_ENV_END, pos)
    if env_end_reg == sublime.Region(-1):
        return
    env_end_str = view.substr(env_end_reg)
    m = re.match(_RE_FIND_ENV_END, env_end_str)
    if not m:
        return
    env_mapping = get_setting("auto_label_env_mapping", {})
    label_type = env_mapping.get(m.group(1))
    return label_type


def _find_label_content(view, pos, find_region):
    label_type = "???"
    find_region_str = view.substr(find_region)
    command_mapping = get_setting("auto_label_command_mapping", {})
    m = _RE_FIND_SECTION(command_mapping).search(find_region_str)
    if m:
        command_content = m.group("content")
        label_content = _create_label_content(command_content)

        command_name = m.group("command")
        if command_name == "caption":
            label_type = _find_label_type_by_env(view, pos) or label_type
        else:
            label_type = command_mapping.get(command_name, label_type)
    else:
        label_content = "label"
    # change the label if we are inside a equation and it is not set already
    if (label_type == "???" and
            view.score_selector(pos, "meta.environment.math")):
        env_mapping = get_setting("auto_label_env_mapping", {})
        label_type = env_mapping.get("<math>", "eq")

    return label_type, label_content


def _create_surrounding_text(view, pos):
    line_before = view.substr(sublime.Region(view.line(pos).a, pos))[::-1]
    m = _RE_IS_LABEL_BEFORE.match(line_before)
    if not m:
        before_text, after_text = "\\label{", "}"
    elif not m.group("brace"):
        before_text, after_text = "{", "}"
    else:
        before_text = after_text = ""
    return before_text, after_text


class LatextoolsAutoInsertLabelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        for sel in view.sel():
            pos = sel.b
            line_above = view.line(view.line(pos).a - 1)
            find_region = sublime.Region(line_above.a, pos)

            label_type, label_content = _find_label_content(
                view, pos, find_region)

            before_text, after_text = _create_surrounding_text(view, pos)

            # if we only have one selection insert it as a snippet
            # else insert the label as it is
            if len(view.sel()) == 1:
                snippet = (
                    "{before_text}"  # leading \label{
                    "${{1:{label_type}}}:${{2:{label_content}}}"
                    "{after_text}"  # trailing }
                    "$0"
                    .format(**locals())
                )
                view.run_command("insert_snippet", {"contents": snippet})
            else:
                content = (
                    "{before_text}"  # leading \label{
                    "{label_type}:{label_content}"
                    "{after_text}"  # trailing }
                    .format(**locals())
                )
                view.insert(edit, pos, content)


class LatextoolsAutoInserLabelListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key != "latextools.setting.auto_label_auto_trigger":
            return
        result = get_setting("auto_label_auto_trigger", False)
        if operator == sublime.OP_EQUAL:
            result = result == operand
        elif operator == sublime.OP_NOT_EQUAL:
            result = result != operand
        else:
            raise Exception(
                "latextools.setting.auto_label_auto_trigger; "
                "Invalid operator must be EQUAL or NOT_EQUAL.")
        return result
