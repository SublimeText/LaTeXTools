import sublime
import re

_ST3 = sublime.version() >= '3000'

if _ST3:
    from .latextools_utils import analysis, cache
    from .getTeXRoot import get_tex_root
else:
    from latextools_utils import analysis, cache
    from getTeXRoot import get_tex_root

__all__ = ["get_own_env_completion", "get_own_command_completion"]


def get_own_env_completion(view):
    tex_root = get_tex_root(view)
    if not tex_root:
        return []

    def make_completions():
        ana = analysis.get_analysis(tex_root)
        return _make_own_env_completion(ana)

    return cache.cache(tex_root, "own_env_completion", make_completions)


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
    return cache.cache(tex_root, cache_name, make_completions)


def _make_own_env_completion(ana):
    commands = ana.filter_commands(["newenvironment", "renewenvironment"])
    return [(c.args + "\tself-defined", c.args) for c in commands]


def _make_own_command_completion(ana, is_math):
    com = ana.filter_commands(["newcommand", "renewcommand"])
    res = [_parse_command(c) for c in com]

    if is_math:
        dop = ana.filter_commands(["DeclareMathOperator"])
        res.extend((s.args + "\tself-declared operator", s.args) for s in dop)

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
        comp = parse_keyword(s)
    except:  # no args
        s = c.args + "{}"
        comp = s
    return (s + "\tself-defined", comp)


# TODO duplicate to avoid cyclic imports
def parse_keyword(keyword):
    # Replace strings in [] and {} with snippet syntax
    def replace_braces(matchobj):
        replace_braces.index += 1
        if matchobj.group(1) is not None:
            word = matchobj.group(1)
            return u'{${%d:%s}}' % (replace_braces.index, word)
        else:
            word = matchobj.group(2)
            return u'[${%d:%s}]' % (replace_braces.index, word)
    replace_braces.index = 0

    replace, n = re.subn(r'\{([^\{\}\[\]]*)\}|\[([^\{\}\[\]]*)\]', replace_braces, keyword)

    # I do not understand why some of the input will eat the '\' charactor before it!
    # This code is to avoid these things.
    if n == 0 and re.search(r'^[a-zA-Z]+$', keyword[1:].strip()) != None:
        return keyword
    else:
        return replace
