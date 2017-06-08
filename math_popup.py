import html

import sublime
import sublime_plugin

import mdpopups

from .latextools_utils import latexhtml
# TODO for development reload
import imp
imp.reload(latexhtml)

_prefix_len = 10
_symbol_len = 10
_command_len = 10


def _get_command_entries():
    if hasattr(_get_command_entries, "result"):
        return _get_command_entries.result
    try:
        resource = sublime.load_resource(
            "Packages/LaTeXTools/resource/insert_math_popup_entries.json")
        command_mapping = sublime.decode_value(resource)
        _get_command_entries.result = command_mapping
    except (OSError, ValueError):
        return []
    return _get_command_entries.result


def _get_css():
    if hasattr(_get_css, "result"):
        return _get_css.result
    try:
        _get_css.result = sublime.load_resource(
            "Packages/LaTeXTools/resource/insert_math_popup.css")
    except OSError:
        return ".selected { background-color: #FFFF00; }"
    return _get_css.result


_html_options = """
<div>
<a href="option_back">(back)</a>
</div>
"""


def show_html_popup(view, html_content):

    def cleanup():
        _cleanup(view)

    def _update_popup(content):
        mdpopups.update_popup(
            view, content, md=False, css=_get_css(),
            wrapper_class="latextools-insert-math")

    def _show_popup(content, on_navigate, on_hide):
        mdpopups.show_popup(
            view, content, md=False, css=_get_css(),
            wrapper_class="latextools-insert-math", on_navigate=on_navigate,
            on_hide=on_hide)

    def navigate(href):
        print("navigate!!!")
        print("href:", href)

        if href == "toggle_search":
            do_search = view.settings().get("lt_mp_search")
            view.settings().set("lt_mp_search", not do_search)
            view.settings().set("lt_mp_prefix", "")
            _execute_command(view, "")
        elif href == "options":
            _update_popup(_html_options)
        elif href == "option_back":
            _update_popup(html_content)
        else:
            try:
                mapping = _prefix_entries(view)
                entry = mapping[int(href)]
            except (ValueError, KeyError):
                print("Unkown href: ", href)
                return
            cleanup()
            mdpopups.hide_popup(view)
            view.run_command("insert", {"characters": entry[1]})
    if mdpopups.is_popup_visible(view):
        _update_popup(html_content)
    else:
        _show_popup(html_content, on_navigate=navigate, on_hide=cleanup)


def _escape_html(s):
    return html.escape(s, quote=False)


def _get_html_size(s):
    try:
        special_size = _get_html_size.special_size
    except AttributeError:
        special_size = latexhtml.get_symbol_map().get(":special_size:", {})
        _get_html_size.special_size = special_size

    # TODO better size estimation
    if s in special_size:
        return special_size[s]
    else:
        return len(s)
    return len(s)


def _imake_html(entries, do_search, prefix, invalid_char, index):
    # create the header
    yield '<div class="prefix_line">'
    if do_search:
        yield "Search: \\"
    else:
        yield "Match: "
    yield '<span class="prefix">'
    yield _escape_html(prefix)
    yield "</span>"
    yield "&nbsp;"
    if invalid_char:
        yield "&nbsp;" * 4
        yield '<span class="invalid_char">'
        yield "({0})".format(_escape_html(invalid_char))
        yield "</span>"
    yield "</div>"
    yield '<div class="button-line">'
    yield '<a class="button" href="toggle_search">'
    yield "(Toggle Mode)"
    yield "</a>"
    yield "&nbsp;"
    yield '<a class="button" href="options">(Options)</a>'
    yield '</div>'

    def high_common_prefix(s):
        pre = "\\" + prefix if do_search else prefix
        # check there is really a match!
        if not s.startswith(pre):
            return _escape_html(s)
        post = _escape_html(s[len(pre):])
        pre = _escape_html(pre)
        return (
            '<span class="common_prefix">{0}</span>'
            '<span class="common_postfix">{1}</span>'
            .format(pre, post)
        )
    for i, m in enumerate(entries):
        trigger, value, *rest = m
        hlatex = latexhtml.highlight_latex(
            value, is_math=True, as_snippet=True)

        if i == index:
            yield "<div class=\"selected\">"
        else:
            yield "<div>"
        yield '<a class="entry" href={0}>'.format(i)

        if not do_search and prefix:
            yield high_common_prefix(trigger)
        else:
            yield _escape_html(trigger)

        yield ("&nbsp;" * (_prefix_len - len(trigger)))
        yield "<span>"
        yield hlatex
        yield "</span>"
        vsize = _get_html_size(hlatex)
        yield ("&nbsp;" * (_symbol_len - vsize))
        yield "<span>"
        if do_search and prefix:
            yield high_common_prefix(value)
        else:
            yield _escape_html(value)
        yield "</span>"
        yield "</a>"
        yield "</div>"


def _make_html(entries, do_search, prefix, invalid_char, index):
    return "".join(_imake_html(**locals()))


def _prefix_entries(view, prefix=None):
    search_mode = view.settings().get("lt_mp_search")
    if prefix is None:
        prefix = view.settings().get("lt_mp_prefix", "")
    cache = (_prefix_entries.cache if not search_mode
             else _prefix_entries.search_cache)
    try:
        return cache[prefix]
    except KeyError:
        print("not cached" + prefix, search_mode)
        sprefix = "\\" + prefix
        if search_mode:
            def is_prefixed(m):
                return m[1].startswith(sprefix)
        else:
            def is_prefixed(m):
                return m[0].startswith(prefix)

        cache[prefix] = [m for m in _get_command_entries() if is_prefixed(m)]
        return cache[prefix]


_prefix_entries.cache = {}
_prefix_entries.search_cache = {}


def insert_entry(view, value, postfix=""):
    content = value[1]
    try:
        info = value[2]
    except IndexError:
        info = {}
    vtype = info.get("type", "insert")
    if vtype == "insert":
        view.run_command("insert", {"characters": content + postfix})
    elif vtype == "snippet":
        view.run_command("insert_snippet", {"contents": content})


def _cleanup(view):
    view.settings().erase("lt_mp_sel")
    view.settings().erase("lt_mp_prefix")
    view.settings().erase("lt_mp_search")
    view.settings().erase("lt_mp_index")
    view.hide_popup()


def _execute_command(view, prefix, invalid_char="", index=-1):
        entries = _prefix_entries(view, prefix)
        do_search = view.settings().get("lt_mp_search")
        if len(entries) == 1 and not do_search:
            _cleanup(view)
            insert_entry(view, entries[0], "")
            return
        if index == -1 and prefix:
            index = 0
        view.settings().set("lt_mp_prefix", prefix)
        if index != -1:
            view.settings().set("lt_mp_index", index)
        html_content = _make_html(
            entries, do_search, prefix, invalid_char, index)
        show_html_popup(view, html_content)


class LatextoolsMathPopupShowCommand(sublime_plugin.WindowCommand):
    """Open and show the LaTeXTools "insert math popup"."""

    def run(self, do_search=False):
        view = self.window.active_view()
        # store the current selection to clear the command if the
        # selection changes
        v = str(list(view.sel()))
        view.settings().set("lt_mp_sel", v)
        view.settings().set("lt_mp_search", do_search)

        _execute_command(view, "")


class LatextoolsMathPopupToggleModeCommand(sublime_plugin.WindowCommand):
    """
    Toggle the input mode of the LaTeXTools "insert math popup" between
    matching a trigger sequence and searching the corresponding command.
    """

    def run(self):
        view = self.window.active_view()
        do_search = view.settings().get("lt_mp_search")
        view.settings().set("lt_mp_search", not do_search)
        # remove the prefix and end the command
        _execute_command(view, "")


class LatextoolsMathPopupCommitCommand(sublime_plugin.WindowCommand):
    """
    Commit the selected entry of the LaTeXTools "insert math popup".
    This insert the corresponding text/snippet into the view.
    """

    def run(self, insert_characters="", reopen=False):
        view = self.window.active_view()
        entries = _prefix_entries(view)
        index = view.settings().get("lt_mp_index", 0)
        print("index:", index)
        value = entries[index]
        insert_entry(view, value, insert_characters)
        _cleanup(view)


class LatextoolsMathPopupInsertCharCommand(sublime_plugin.WindowCommand):
    """Insert a character into the LaTeXTools "insert math popup"."""

    def run(self, character):
        view = self.window.active_view()
        prefix = view.settings().get("lt_mp_prefix", "")

        if _prefix_entries(view, prefix + character):
            _execute_command(view, prefix + character, invalid_char="")
        else:
            _execute_command(view, prefix, invalid_char=character)


class LatextoolsMathPopupDeleteCharCommand(sublime_plugin.WindowCommand):
    """Delete a character from the LaTeXTools "insert math popup"."""

    def run(self):
        view = self.window.active_view()
        prefix = view.settings().get("lt_mp_prefix", "")
        _execute_command(view, prefix[:-1])


class LatextoolsMathPopupMoveLineCommand(sublime_plugin.WindowCommand):
    """
    Select the next/previous entry in the LaTeXTools "insert math popup".
    """

    def run(self, forward):
        view = self.window.active_view()
        index = view.settings().get("lt_mp_index", 0)

        index += 1 if forward else -1

        entries_length = len(_prefix_entries(view))
        if index >= entries_length:
            index = 0
        elif index < 0:
            index = entries_length - 1

        print("index:", index)
        # keep the old prefix
        prefix = view.settings().get("lt_mp_prefix", "")
        _execute_command(view, prefix, index=index)


class LatextoolsMathPopupContextListener(sublime_plugin.EventListener):
    """Check whether the LaTeXTools "insert math popup" is open."""

    def on_query_context(self, view, key, operator, operand, match_all):
        # TODO handle operator/operand
        if key != "latextools.math_popup.await_next_key":
            return
        sel = view.settings().get("lt_mp_sel")
        if not sel:
            return False
        if str(list(view.sel())) == sel:
            return True
        _cleanup(view)
        return False


class LatextoolsMathPopupPostfixInsertCommand(sublime_plugin.TextCommand):
    """
    Insert the entry from the math popup based on the text before the
    caret.
    """

    def run(self, edit):
        view = self.view
        command_entries = {k: v for k, v, *_ in _get_command_entries()}
        for sel in view.sel():
            # get the word and the key from the view
            word = sublime.Region(view.word(sel.b).a, sel.b)
            insert_key = view.substr(word)

            # strip the key
            # these characters are stripped and hence can't be used in
            # the sequence
            strip_chars = " \n{}_^"
            insert_key = insert_key.lstrip(strip_chars)
            len_strip_delta = len(word) - len(insert_key)
            if len_strip_delta > 0:
                word = sublime.Region(word.a + len_strip_delta, word.b)

            # retrieve and insert the value for the key
            try:
                insert_value = command_entries[insert_key]
            except KeyError:
                message = "No math insertion key for '{}'".format(insert_key)
                print(message)
                sublime.status_message(message)
                return

            # insert the value and replace the prefix sequence
            view.replace(edit, word, insert_value)
