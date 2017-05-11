import html
import re
import shlex
import string
import yaml

import sublime


def _create_char_map(upper_start, lower_start=None):
    # if lower start is None we assume the lower case chars
    # to start after the uppercase char
    if lower_start is None:
        lower_start = upper_start + len(string.ascii_lowercase)
    char_map = {
        c: chr(lower_start + i)
        for i, c in enumerate(string.ascii_lowercase)
    }
    char_map.update({
        c: chr(upper_start + i)
        for i, c in enumerate(string.ascii_uppercase)
    })
    return char_map


def get_math_font_maps():
    if hasattr(get_math_font_maps, "result"):
        return get_math_font_maps.result
    mbb_map = _create_char_map(120120)
    # fix missing chars
    mbb_map.update({
        "C": chr(8450),
        "H": chr(8461),
        "N": chr(8469),
        "P": chr(8473),
        "Q": chr(8474),
        "R": chr(8477),
        "Z": chr(8484),
    })
    mcal_map = _create_char_map(119964)
    mfrak_map = _create_char_map(120068)

    math_font_maps = {
        "\\mathfrak": mfrak_map,
        "\\mathbb": mbb_map,
        "\\mathcal": mcal_map
    }
    get_math_font_maps.result = math_font_maps
    return get_math_font_maps.result


def get_tag_map():
    tag_map = {
        "\\textbf": "b",
        "\\textit": "i",
        "\\textsl": "i",
        "\\emph": "em",
        "\\underline": "u",
        "\\texttt": "code",
        "\\mathbf": "b",
        "\\mathit": "i",
    }
    return tag_map


_RE_IS_COMMAND = re.compile(r"\\[{0}]+$".format(string.ascii_letters + "@"))


def is_command(token):
    return bool(_RE_IS_COMMAND.match(token))


def _escape_html(content):
    return html.escape(content, quote=False)


def _highlight_missing(content):
    return '<u style="color: red;">{0}</u>'.format(_escape_html(content))


def parse_snippet(it):
    c = next(it)

    if c.isnumeric():
        return '<span style="color: yellow;">{0}</span>'.format("$" + c)
        if c == "0":
            return "|"
        return chr(8943)
    return "----"


def tokenize(latex_string):
    # lex the string and set some options
    shl = shlex.shlex(latex_string)
    shl.wordchars = string.ascii_letters + "\\"
    # we want to preserve white spaces
    shl.whitespace = ""
    shl.commenters = "%"

    # split command, which are directly behind each other
    # e.g. \alpha\beta -> \alpha,\beta
    for token in shl:
        if "\\" not in token[1:]:
            yield token
            continue
        print("token:", token)
        while True:
            try:
                index = token[1:].index("\\") + 1
            except ValueError:
                break
            yield token[0:index]

            token = token[index:]


def get_symbol_map():
    if hasattr(get_symbol_map, "result"):
        return get_symbol_map.result

    try:
        resource = sublime.load_resource(
            "Packages/LaTeXtools/resource/latex_symbols.yaml")
        get_symbol_map.result = yaml.load(resource)
    except (OSError, ValueError):
        return {}

    return get_symbol_map.result


def highlight_latex(latex_string, is_math=True, as_snippet=False,
                    skip_unknown=True):
    symbol_map = get_symbol_map()
    math_font_maps = get_math_font_maps()
    tag_map = get_tag_map()

    def _missing(content):
        return _highlight_missing(content)

    it = tokenize(latex_string)
    html_lst = []
    tags = []
    do_tag = ""
    escape_symbol = False  # escape symbols, e.g. \&
    for t in it:
        # if we have an escaped char, we insert it (next char), e.g. \&
        if escape_symbol:
            html_lst.append(_escape_html(t))
            escape_symbol = False
        elif t == "\\":
            escape_symbol = True
        # if it is a symbol we insert it, e.g. \alpha
        elif t in symbol_map:
            html_lst.append(symbol_map[t])
        # insert special symbols from the map, e.g. \mathbb{N}
        elif t in math_font_maps:
            char_map = math_font_maps.get(t, {})
            orig_t = t
            # TODO handle wrong input
            assert next(it) == "{"
            t = next(it)
            if t == "$":
                c = "{0}{{{1}}}".format(orig_t, parse_snippet(it))
                # c += parse_snippet(it)
            else:
                c = char_map.get(t, _missing(t))
            html_lst.append(c)
            assert next(it) == "}"
        # if we have a markup command (text/textit) we prepare the
        # corresponding tag
        elif t in tag_map:
            do_tag = tag_map[t]
        # handle super and subscript
        elif t == "^" or t == "_":
            # subscript/superscript are not supported by minihtml,
            # hence we just use small instead
            do_tag = "small"
        elif t == "{":
            if do_tag:
                html_lst.append("<{0}>".format(do_tag))
                tags.append("</{0}>".format(do_tag))
            else:
                html_lst.append(_missing("{"))
                tags.append(_missing("}"))

            do_tag = ""
        elif t == "}":
            try:
                html_lst.append(tags.pop())
            except IndexError:
                html_lst.append(_missing("}"))
        # test single char tags for ^ and _
        elif t.isalnum() and do_tag:
            html_lst.append("<{0}>{1}</{0}>{2}".format(do_tag, t[:1], t[1:]))
            do_tag = ""
        elif is_command(t):
            if skip_unknown:
                html_lst.append(" ")
            else:
                html_lst.append(_missing(t))
        elif t.isalnum() or t.isspace() or t in "+-*/'\"":
            html_lst.append(t)
        elif t == "$" and as_snippet:
            html_lst.append(parse_snippet(it))
        else:
            html_lst.append(_missing(t))

    html_str = "".join(html_lst)
    return html_str
