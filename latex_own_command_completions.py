from .latextools_utils import analysis
from .latextools_utils import cache
from .latextools_utils.parser_utils import command_to_snippet
from .latextools_utils.tex_directives import get_tex_root


class NoArgs(Exception):
    pass


def get_own_env_completion(view):
    tex_root = get_tex_root(view)
    if not tex_root:
        return []

    def make_completions():
        ana = analysis.get_analysis(tex_root)
        return _make_own_env_completion(ana)

    return list(cache.LocalCache(tex_root).cache(
        "own_env_completion", make_completions) or [])


def get_own_command_completion(view):
    tex_root = get_tex_root(view)
    if not tex_root:
        return []

    sel = view.sel()
    if not sel:
        return []

    # use special handling (additional completions) for math mode
    is_math = view.match_selector(sel[0].b, "text.tex meta.environment.math")

    def make_completions():
        ana = analysis.get_analysis(tex_root)
        return _make_own_command_completion(ana, is_math)

    cache_name = "own_command_completion"
    if is_math:
        cache_name += "_math"

    return list(cache.LocalCache(tex_root).cache(cache_name, make_completions) or [])


def _make_own_env_completion(ana):
    return [
        [c.args + "\tlocal", c.args]
        for c in ana.filter_commands(["newenvironment", "renewenvironment"])
    ]


def _make_own_command_completion(ana, is_math):
    res = []

    for c in ana.filter_commands(["newcommand", "renewcommand"]):
        try:
            if not c.optargs2:
                raise NoArgs()
            arg_count = int(c.optargs2)
            has_opt = bool(c.optargs2a)
            s = c.args
            if has_opt:
                s += "[{0}]".format(c.optargs2a)
                arg_count -= 1
            elif arg_count == 0:
                raise NoArgs()
            s += "{arg}" * arg_count
            comp = command_to_snippet(s)
            if comp is None:
                raise NoArgs()
            comp = comp[1]
        except:  # no args
            s = c.args + "{}"
            comp = s

        res.append([s + "\tlocal", comp])

    for c in ana.filter_commands(["newenvironment", "renewenvironment"]):
        res.append([
            "\\begin{{{0}}}\tlocal".format(c.args),
            "\\begin{{{0}}}\n$0\n\\end{{{0}}}".format(c.args),
        ])
        res.append([
            "\\end{{{0}}}\tlocal".format(c.args),
            "\\end{{{0}}}".format(c.args),
        ])

    if is_math:
        for c in ana.filter_commands(["DeclareMathOperator"]):
            res.append([c.args + "\tlocal", c.args])

    return res
