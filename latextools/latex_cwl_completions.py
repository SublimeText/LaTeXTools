from __future__ import annotations
import os
import re
from sys import exc_info

import sublime
import sublime_plugin

from .utils import analysis
from .utils import utils
from .utils.cache import cache_local
from .utils.logging import logger
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

ALPHAS_REGEX = re.compile(r"^[a-zA-Z]+$")

BEGIN_ENV_REGEX = re.compile(
    r"\\begin{(?P<name>[^\}]*)\}(?:(?P<remainder1>.*)(?P<item>\\item)|(?P<remainder2>.*))"
)
"""
regex to parse a environment line from the cwl file
"""

END_ENV_REGEX = re.compile(r"\\end\{(?P<name>[^\}]+)\}")
"""
regex to parse a environment line from the cwl file
only search for \\end to create a list without duplicates
"""

BRACKETS_REGEX = re.compile(r"\{([^\}]*)\}|\[([^\]]*)\]|%<(.+?)%>")
"""
used to convert arguments and optional arguments into fields
"""

FIELD_REGEX = re.compile(r"%<(.+?)%>")
"""
used to convert %<...%> tags into fields
"""

KIND_REGEX = re.compile(r"%[a-z]+")
"""
used to filter %plain, %l, etc.
"""

PACKAGE_CWL_FILES = {
    "class-scrartcl": "class-scrartcl,scrreprt,scrbook.cwl",
    "class-scrreprt": "class-scrartcl,scrreprt,scrbook.cwl",
    "class-book": "class-scrartcl,scrreprt,scrbook.cwl",
    "polyglossia": "babel.cwl",
}
"""
Translation from package names to cwl files.
Package name and cwl file name are equal with some exceptions.
"""

CMD_COMPLETIONS = {}
ENV_COMPLETIONS = {}
CWL_DEPENDENCIES = {}


def get_cwl_command_completions(tex_root: str) -> list[sublime.CompletionItem]:
    completions = []

    for cwl_file in get_cwl_files(tex_root):
        cwl_exists = cwl_file in CMD_COMPLETIONS
        if not cwl_exists:  # todo: reload if cwl file was modified
            cwl_exists = load_cwl_file(cwl_file)
        if cwl_exists:
            completions.extend(CMD_COMPLETIONS[cwl_file])

    return completions


def get_cwl_env_completions(tex_root: str) -> list[sublime.CompletionItem]:
    completions = []

    for cwl_file in get_cwl_files(tex_root):
        cwl_exists = cwl_file in ENV_COMPLETIONS
        if not cwl_exists:  # todo: reload if cwl file was modified
            cwl_exists = load_cwl_file(cwl_file)
        if cwl_exists:
            completions.extend(ENV_COMPLETIONS[cwl_file])

    return completions


def get_cwl_files(tex_root: str) -> tuple[str]:
    """
    Determine all cwl files associated with a TeX document.

    :param tex_root:
        The main TeX document

    :returns:
        A tuple of cwl files.
    """

    def make():
        # static user defined list of cwl files always to load completions from
        cwl_files = set(
            get_setting(
                "cwl_list",
                [
                    "latex-document.cwl",
                    "tex.cwl",
                    "latex-dev.cwl",
                    "latex-209.cwl",
                    "latex-l2tabu.cwl",
                    "latex-mathsymbols.cwl",
                ],
            ),
        )

        # autoload cwl_files by scanning the document
        if get_setting("cwl_autoload", True):
            ana = analysis.get_analysis(tex_root)
            if ana:
                flags = analysis.ONLY_PREAMBLE | analysis.ONLY_COMMANDS_WITH_ARGS

                for documentclass in ana.filter_commands("documentclass", flags):
                    for package in documentclass.args.split(","):
                        cwl_files.add(package_to_cwl(f"class-{package.strip()}"))

                for usepackage in ana.filter_commands("usepackage", flags):
                    for package in usepackage.args.split(","):
                        cwl_files.add(package_to_cwl(package.strip()))

                # recursively resolve dependencies
                flag = True
                while flag:
                    resolved = set(cwl_files)
                    for package in cwl_files:
                        resolved |= set(CWL_DEPENDENCIES.get(package, []))
                    flag = len(resolved) > len(cwl_files)
                    cwl_files = resolved

        return tuple(cwl_files)

    return cache_local(tex_root, "cwl_files", make)


def package_to_cwl(package: str) -> str:
    if package.endswith(".cwl"):
        return package
    return PACKAGE_CWL_FILES.get(package, package + ".cwl")


def load_cwl_file(base_name: str) -> bool:
    for cwl_file in (f"Packages/LaTeXTools/cwl/{base_name}", f"Packages/User/cwl/{base_name}"):
        try:
            text = sublime.load_resource(cwl_file)
        except FileNotFoundError:
            logger.info(f"{cwl_file} does not exist!")
        except UnicodeDecodeError:
            logger.error(f"{cwl_file}: {exc_info()[1]}")
        else:
            (
                CMD_COMPLETIONS[base_name],
                ENV_COMPLETIONS[base_name],
                CWL_DEPENDENCIES[base_name],
            ) = parse_cwl_file(base_name, text)
            return True

    return False


def parse_cwl_file(
    cwl_file: str, text: str
) -> tuple[list[sublime.CompletionItem], list[sublime.CompletionItem], list[str]]:
    """
    Parse a cwl file
    """
    commands = []
    environments = []
    cwl_dependencies = []

    cwl_name = cwl_file[: -len(".cwl")]

    cmd_kind = (sublime.KIND_ID_FUNCTION, "f", "Command")
    env_kind = (sublime.KIND_ID_NAMESPACE, "e", "Environment")

    # we need some state tracking to ignore keyval data
    # it could be useful at a later date
    KEYVAL = False
    for line in text.splitlines():
        line = line.lstrip()
        if not line:
            continue

        if line[0] == "#":
            if line.startswith("#keyvals") or line.startswith("#ifOption"):
                KEYVAL = True
            if line.startswith("#endkeyvals") or line.startswith("#endif"):
                KEYVAL = False
            if line.startswith("#include:") and not KEYVAL:
                cwl_dependencies.append(package_to_cwl(line[len("#include:") :].strip()))

            continue

        # ignore TeXStudio's keyval structures
        if KEYVAL:
            continue

        # remove everything after the comment hash
        # again TeXStudio uses this for interesting
        # tracking purposes, but we can ignore it
        line = line.split("#", 1)[0]

        # trailing spaces aren't relevant (done here in case they precede)
        # a # char
        line = line.rstrip()

        trigger, snippet = command_to_snippet(line)
        commands.append(
            sublime.CompletionItem(
                trigger=trigger,
                annotation=cwl_name,
                completion=snippet,
                completion_format=sublime.COMPLETION_FORMAT_SNIPPET,
                details=" ",
                kind=cmd_kind,
            )
        )

        match = END_ENV_REGEX.match(line)
        if match is not None:
            environments.append(
                sublime.CompletionItem(
                    trigger=match.group("name"),
                    annotation=cwl_name,
                    details=" ",
                    kind=env_kind,
                )
            )

    return (commands, environments, cwl_dependencies)


def command_to_snippet(cwl_cmd: str) -> tuple[str, str]:
    """
    converts a LaTeX command, like \\dosomething{arg1}{arg2} into a ST snippet
    like \\dosomething{$1:arg1}{$2:arg2}
    """
    index = 0

    def comment_to_field(match: re.Match) -> str:
        """Convert comment to snippet field by replacing %<..%> by ${n:..}."""
        nonlocal index
        return f"${{{(index := index + 1)}:{match.group(1)}}}"

    def bracket_to_field(match: re.Match) -> str:
        """Convert content in [] and {} to snippet fields."""
        nonlocal index

        # convert top-level {...} to ${...} field
        text = match.group(1)
        if text is not None:
            # convert nested %<...%> arguments to ${...} fields
            text, n = FIELD_REGEX.subn(comment_to_field, text)
            return f"{{{text}}}" if n > 0 else f"{{${{{(index := index + 1)}:{text}}}}}"

        # convert top-level [...] to ${...} field
        text = match.group(2)
        if text is not None:
            # convert nested %<...%> arguments to ${...} fields
            text, n = FIELD_REGEX.subn(comment_to_field, text)
            return f"[{text}]" if n > 0 else f"[${{{(index := index + 1)}:{text}}}]"

        # convert top-level %<...%> to ${...} field
        return f"${{{(index := index + 1)}:{match.group(3)}}}"

    # filter out kind information
    cwl_cmd = KIND_REGEX.sub("", cwl_cmd)

    # \begin{}...\end{} pairs should be inserted together
    m = BEGIN_ENV_REGEX.match(cwl_cmd)
    if m:
        item = bool(m.group("item"))
        name = m.group("name")

        # \begin{}, no environment
        if not name:
            replace, n = BRACKETS_REGEX.subn(bracket_to_field, cwl_cmd)
            snippet = f"{replace}\n\t${index + 1}$0\n\\end{{$1}}"
            return cwl_cmd, snippet
        # \begin{} with environment
        # only create fields for any other items
        else:
            remainder = m.group("remainder1") or m.group("remainder2") or ""
            replace, n = BRACKETS_REGEX.subn(bracket_to_field, remainder)

            snippet = f"\\begin{{{name}}}{replace or ''}\n"
            if item:
                snippet += f"\t\\item ${index + 1}$0\n"
            else:
                snippet += f"\t${index + 1}\n"
            snippet += f"\\end{{{name}}}"

            # having \item at the end of the display value messes with
            # completions thus, we cut the \item off the end
            if item:
                return cwl_cmd[:-5], snippet
            else:
                return cwl_cmd, snippet
    else:
        replace, n = BRACKETS_REGEX.subn(bracket_to_field, cwl_cmd)
        cwl_cmd = cwl_cmd.replace("%<", "").replace("%>", "")

        # I do not understand why sometimes the input will eat the '\'
        # character before it! This code is to avoid these things.
        if n == 0 and ALPHAS_REGEX.search(cwl_cmd[1:].strip()) is not None:
            return cwl_cmd, cwl_cmd
        else:
            replace = FIELD_REGEX.sub(comment_to_field, replace or "")
            return cwl_cmd, replace
