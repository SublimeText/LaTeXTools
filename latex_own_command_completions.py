import sublime

_ST3 = sublime.version() >= '3000'

if _ST3:
    from .latextools_utils import analysis, cache
    from .latextools_utils.parser_utils import command_to_snippet
    from .getTeXRoot import get_tex_root
else:
    from latextools_utils import analysis, cache
    from latextools_utils.parser_utils import command_to_snippet
    from getTeXRoot import get_tex_root

__all__ = ["get_own_env_completion", "get_own_command_completion"]


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

    # use special handling (additional completions) for math mode
    math_selector = (
        "string.other.math.tex, "
        "string.other.math.latex, "
        "string.other.math.block.environment.latex"
    )
    is_math = bool(view.score_selector(view.sel()[0].b, math_selector))

    def make_completions():
        ana = analysis.get_analysis(tex_root)
        return _make_own_command_completion(ana, is_math)

    cache_name = "own_command_completion"
    if is_math:
        cache_name += "_math"

    return list(
        cache.LocalCache(tex_root).cache(cache_name, make_completions) or [])


def _make_own_env_completion(ana):
    commands = ana.filter_commands(["newenvironment", "renewenvironment"])
    return [(c.args.ljust(50) + "\tlocal", c.args) for c in commands]


def _make_own_command_completion(ana, is_math):
    com = ana.filter_commands(["newcommand", "renewcommand"])
    res = [_parse_command(c) for c in com]

    env = ana.filter_commands(["newenvironment", "renewenvironment"])
    for e in env:
        res.extend([
            ("\\begin{{{0}}}".format(e.args).ljust(50) + "\tlocal",
                "\\begin{{{0}}}\n$1\n\\end{{{0}}}$0".format(e.args)),
            ("\\end{{{0}}}".format(e.args).ljust(50) + "\tlocal",
                "\\end{{{0}}}".format(e.args))
        ])

    if is_math:
        dop = ana.filter_commands(["DeclareMathOperator"])
        res.extend(
            (s.args.ljust(50) + "\tlocal", s.args)
            for s in dop
        )

    return res


def _parse_command(c):
    class NoArgs(Exception):
        pass

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

    s = s.ljust(50)
    return (s + "\tlocal", comp)
