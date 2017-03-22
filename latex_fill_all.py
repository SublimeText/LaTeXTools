from __future__ import print_function

import sublime
import sublime_plugin
import re
import sys
import traceback

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    from getRegion import getRegion
    from latextools_plugin import (
        get_plugins_by_type, _classname_to_internal_name
    )
    from latextools_utils import get_setting
    from latextools_utils.internal_types import FillAllHelper

    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")

    strbase = basestring
else:
    _ST3 = True
    # hack to ensure relative package imports work
    __package__ = 'LaTeXTools'

    from .getRegion import getRegion
    from .latextools_plugin import (
        get_plugins_by_type, _classname_to_internal_name
    )
    from .latextools_utils import get_setting
    from .latextools_utils.internal_types import FillAllHelper

    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    strbase = str
    long = int


class LatexFillHelper(object):
    '''
    Base class for some LaTeXTools TextCommands. Implements several methods
    helpful for inserting text into the view and updating the cursor posiiton.
    '''

    # This is necessarily incomplete, but is intended to cover a number of
    # cases and could be extended as needed. I'm unsure that this is the best
    # design; it's done this way to emulate STs default definition of
    # word_separators
    #
    # defines non-word characters; see get_current_word
    NON_WORD_CHARACTERS = u'/\\()"\':,.;<>~!@#$%^&*|+=\\[\\]{}`~?\\s'

    WORD_SEPARATOR_RX = re.compile(
        r'([^' + NON_WORD_CHARACTERS + r']*)',
        re.UNICODE
    )

    # define fancy match prefix to support, e.g., \cite_prefix
    FANCY_PREFIX_RX = re.compile(
        r'([^_' + NON_WORD_CHARACTERS + r']*)_',
        re.UNICODE
    )

    # defines which characters need a matching bracket and their match
    MATCH_CHARS = {
        '{': '}',
        '[': ']',
        '(': ')'
    }

    def complete_auto_match(self, view, edit, insert_char):
        '''
        Completes brackets if auto_match is enabled; also implements the
        "smart_bracket_auto_trigger" logic, which tries to complete the nearest
        open bracket intelligently.

        :param view:
            the current view

        :param edit:
            the current edit

        :param insert_char:
            the character to try to automatch
        '''
        if sublime.load_settings('Preferences.sublime-settings').get(
            'auto_match_enabled', True
        ):
            # simple case: we have an insert char, insert closing char,
            # if its defined
            if insert_char:
                self.insert_at_end(
                    view, edit, self.get_match_char(insert_char)
                )

                # if the insert_char is a bracket, move cursor to middle of
                # bracket and return
                if insert_char in self.MATCH_CHARS:
                    new_regions = []
                    for sel in view.sel():
                        if not sel.empty():
                            new_regions.append(sel)
                        else:
                            new_point = sel.end() - 1
                            new_regions.append(getRegion(new_point, new_point))

                    self.update_selections(view, new_regions)
                    return
            elif get_setting('smart_bracket_auto_trigger', True):
                # more complex: if we do not have an insert_char, try to close
                # the nearest bracket that occurs before each selection
                new_regions = []

                for sel in view.sel():
                    word_region = self.get_current_word(view, sel)
                    close_bracket = self.get_closing_bracket(view, word_region)
                    # we should close the bracket
                    if close_bracket:
                        # insert the closing bracket
                        view.insert(edit, word_region.end(), close_bracket)

                        if sel.empty():
                            if word_region.empty():
                                new_regions.append(
                                    getRegion(
                                        word_region.end(), word_region.end()))
                            else:
                                new_point = word_region.end() + len(
                                    close_bracket)
                                new_regions.append(getRegion(
                                    new_point, new_point))
                        else:
                            new_regions.append(
                                getRegion(
                                    sel.begin(),
                                    word_region.end() + len(close_bracket)))
                    else:
                        new_regions.append(sel)

                self.update_selections(view, new_regions)

    def complete_brackets(self, view, edit, insert_char='', remove_regions=[]):
        '''
        Intended to be called from a TextCommand to insert a specified
        insert_char, close the nearest bracket, and remove any regions
        specified

        :param view:
            the current view

        :param edit:
            the current edit

        :param insert_char:
            the character to insert and possibly automatch

        :param remove_regions:
            any regions to be removed from the current view
        '''
        self.insert_at_end(view, edit, insert_char)
        self.complete_auto_match(view, edit, insert_char)
        self.remove_regions(view, edit, remove_regions)
        self.clear_bracket_cache()

    def get_closing_bracket(self, view, sel):
        '''
        Determines if the nearest bracket that occurs before the given
        selection is closed. If the bracket should be closed, returns the
        closing bracket to use.

        Note that this will not work if the arguments to the command span
        multiple lines, but we generally don't support that anyway.

        :param view:
            the current view

        :param sel:
            a sublime.Region indicating the selected area
        '''
        # candidates stores matched bracket-pairs so that we only have
        # to find all matches once per bracket type
        # if the view has changed, we reset the candidates
        candidates = None

        if not hasattr(self, 'last_view') or self.last_view != view.id():
            self.last_view = view.id()
            self.use_full_scan = get_setting(
                'smart_bracket_scan_full_document', False)
            candidates = self.candidates = {}

        if not self.use_full_scan:
            # always clear the candidates when not using a full scan
            candidates = {}
            # when not using a full scan, get the number of lines to
            # look-behind
            try:
                look_around = int(get_setting('smart_bracket_look_around', 5))
            except ValueError:
                look_around = 5

        if candidates is None:
            try:
                candidates = self.candidates
            except:
                candidates = self.candidates = {}

        # first, find the nearest bracket
        if type(sel) is sublime.Region:
            start, end = sel.begin(), sel.end()
        else:
            start = end = sel

        if self.use_full_scan:
            prefix = view.substr(getRegion(0, start))
            prefix_start = 0
            suffix_end = view.size()
        else:
            prefix_lines = view.lines(getRegion(0, start))
            if len(prefix_lines) >= look_around:
                prefix_start = prefix_lines[-look_around].begin()
            else:
                prefix_start = prefix_lines[0].begin()

            suffix_lines = view.lines(getRegion(end, view.size()))
            if len(suffix_lines) >= look_around:
                suffix_end = suffix_lines[look_around].end()
            else:
                suffix_end = suffix_lines[-1].end()

            prefix = view.substr(getRegion(prefix_start, start))

        open_bracket, last_index = None, -1
        for char in self.MATCH_CHARS:
            index = prefix.rfind(char)
            if index > last_index:
                open_bracket, last_index = char, index

        if last_index == -1:
            # can't determine bracket to match
            return None

        close_bracket = self.MATCH_CHARS[open_bracket]
        open_brackets = []
        # this is used to throw-away as many matches as possible
        # so subsequent requests don't need to consider every match
        closed_brackets = []

        if open_bracket not in candidates:
            # find all open / close brackets in the current buffer,
            # removing all comments
            candidates[open_bracket] = results = []

            start = prefix_start
            re_str = re.escape(open_bracket) + '|' + re.escape(close_bracket)
            while True:
                if start >= suffix_end:
                    break

                c = view.find(re_str, start)
                if c is None or c.begin() == -1:
                    break

                if c.end() > suffix_end:
                    break

                if view.score_selector(c.begin(), 'comment') != 0:
                    start = c.end()
                    continue

                results.append(c)

                start = c.end()

        for candidate in candidates[open_bracket]:
            if view.substr(candidate) == open_bracket:
                if len(open_brackets) == 0 and candidate.begin() > end:
                    break

                open_brackets.append(candidate)
            else:
                try:
                    removed = open_brackets.pop()
                    if candidate.end() < start:
                        closed_brackets.append(removed)
                        closed_brackets.append(candidate)
                except IndexError:
                    # unbalanced close before open
                    if candidate.end() > end:
                        break

        if len(closed_brackets) > 0:
            candidates[open_bracket] = [
                c for c in candidates[open_bracket]
                if c not in closed_brackets
            ]

        # if we have an open bracket left, then the current bracket needs to
        # be closed
        return close_bracket if len(open_brackets) > 0 else None

    def clear_bracket_cache(self):
        '''
        Clears the cache of brackets stored by get_closing_bracket

        If get_closing_bracket is used, this method must be called at the end
        or else subsequent calls to get_closing_brackets will not be updated
        with a fresh view of the current buffer
        '''
        try:
            del self.candidates
        except:
            pass

        try:
            del self.last_view
        except:
            pass

        try:
            del self.use_full_scan
        except:
            pass

    def get_common_prefix(self, view, locations):
        '''
        gets the common prefix (if any) from a list of locations

        :param view:
            the current view

        :param locations:
            either a list of points or a list of sublime.Regions
        '''
        if type(locations[0]) is int or type(locations[0]) is long:
            locations = [getRegion(l, l) for l in locations]

        old_prefix = None
        for location in locations:
            if location.empty():
                word_region = getRegion(
                    self.get_current_word(view, location).begin(),
                    location.b
                )
                prefix = view.substr(word_region)
            else:
                prefix = view.substr(location)

            if old_prefix is None:
                old_prefix = prefix
            elif old_prefix != prefix:
                prefix = ''
                break

        return prefix

    def get_common_fancy_prefix(self, view, locations):
        '''
        get the common fancy prefix (if any) from a list of locations

        see get_fancy_prefix for the definition of a fancy prefix

        :param view:
            the current view

        :param locations:
            either a list of points or a list of sublime.Regions
        '''
        remove_regions = []
        old_prefix = None
        new_prefix = ''

        for location in locations:
            prefix_region = self.get_fancy_prefix(view, location)
            if prefix_region.empty():
                continue

            new_prefix = view.substr(
                getRegion(
                    prefix_region.begin() + 1, prefix_region.end()
                )
            )

            remove_regions.append(prefix_region)

            if old_prefix is None:
                old_prefix = new_prefix
            elif old_prefix != new_prefix:
                # dummy value that is not None and will never match the
                # prefix
                old_prefix = True
                new_prefix = ''

        return new_prefix, remove_regions

    def get_current_word(self, view, location):
        '''
        Gets the region containing the current word which contains the caret
        or the given selection.

        The current word is defined between the nearest non-word characters to
        the left and to the right of the current selected location.

        Non-word characters are defined by the WORD_SEPARATOR_RX.

        :param view:
            the current view

        :param location:
            either a point or a sublime.Region that defines the caret position
            or current selection
        '''
        if isinstance(location, sublime.Region):
            start, end = location.begin(), location.end()
        else:
            start = end = location

        start_line = view.line(start)
        end_line = view.line(end)
        # inverse prefix so we search from the right-hand side
        line_prefix = view.substr(getRegion(start_line.begin(), start))[::-1]
        line_suffix = view.substr(getRegion(end, end_line.end()))

        # prefix is the characters before caret
        m = self.WORD_SEPARATOR_RX.search(line_prefix)
        prefix = m.group(1) if m else ''

        m = self.WORD_SEPARATOR_RX.search(line_suffix)
        suffix = m.group(1) if m else ''

        return getRegion(
            start - len(prefix), end + len(suffix)
        )

    def get_match_char(self, insert_char):
        return self.MATCH_CHARS.get(insert_char, '')

    def get_fancy_prefix(self, view, location):
        '''
        Gets the prefix for the command assuming it takes a form like:
            \cite_prefix
            \ref_prefix

        These are also supported:
            \cite_prefix{
            \ref_prefix{

        The prefix is defined by everything *after* the underscore

        :param view:
            the current view

        :param location:
            either a point or a sublime.Region that defines the caret position
            or current selection
        '''
        if isinstance(location, sublime.Region):
            start = location.begin()
        else:
            start = location

        start_line = view.line(start)
        # inverse prefix so we search from the right-hand side
        line_prefix = view.substr(getRegion(start_line.begin(), start))[::-1]

        m = self.FANCY_PREFIX_RX.match(line_prefix)
        if not m:
            return getRegion(start, start)

        return getRegion(
            start - len(m.group(0)),
            start - m.start()
        )

    def insert_at_end(self, view, edit, value):
        '''
        Inserts a string at the end of every current selection

        :param view:
            the current view

        :param edit:
            the current edit

        :param value:
            the string to insert
        '''
        if value:
            new_regions = []
            for sel in view.sel():
                view.insert(edit, sel.end(), value)
                if sel.empty():
                    new_start = new_end = sel.end() + len(value)
                else:
                    new_start = sel.begin()
                    new_end = sel.end() + len(value)

                new_regions.append(getRegion(new_start, new_end))
            self.update_selections(view, new_regions)

    def replace_word(self, view, edit, value):
        '''
        Replaces the current word with the provided string in each selection

        For the definition of word, see get_current_word()

        :param view:
            the current view

        :param edit:
            the current edit

        :param value:
            the string to replace the current word with
        '''
        new_regions = []
        for sel in view.sel():
            if sel.empty():
                word_region = self.get_current_word(view, sel.end())
                start_point = word_region.begin()
                end_point = word_region.end()
            else:
                word_region = self.get_current_word(view, sel)
                start_point = word_region.begin()
                end_point = word_region.end()

            view.replace(
                edit, getRegion(start_point, end_point),
                value
            )

            if sel.empty():
                start_point = end_point = start_point + len(value)
            else:
                end_point = start_point + len(value)
            new_regions.append(getRegion(start_point, end_point))

        self.update_selections(view, new_regions)

    def remove_regions(self, view, edit, regions):
        view = self.view
        for region in regions:
            view.erase(edit, region)

    def update_selections(self, view, new_regions):
        '''
        Removes all current selections and adds the specified selections

        NB When calling this method, it is important that all current
        selections be either replaced or simply included as-is. Otherwise,
        these selections will be lost

        :param view:
            the current view

        :param new_regions:
            a list of sublime.Regions that should be selected
        '''
        sel = view.sel()
        sel.clear()
        # we could use ST3's add_all, but this way has less branching...
        for region in new_regions:
            sel.add(region)

    def regions_to_tuples(self, regions):
        '''
        Converts a list of regions to a list of two-element tuples containing
        the corresponding points

        This is necessary to properly serialize a set of regions as an argument
        to a Sublime command, since arguments MUST be serializable as JSON
        objects

        :param regions:
            an iterable of sublime.Regions to convert to tuples
        '''
        # a and b are used instead of begin() / end() so that the caret
        # position (b) is preserved
        if type(regions) == sublime.Region:
            return [(regions.a, regions.b)]

        return [
            [r.a, r.b]
            for r in regions
        ]

    def tuples_to_regions(self, tuples):
        '''
        Converts a list of 2-tuples to a list of corresponding regions

        This is the opposite of regions_to_tuples and is intended to
        deserialize regions serialized using that method

        :param tuples:
            an iterable of two-element tuples to convert to sublime.Regions
        '''
        if type(tuples) == tuple:
            return [getRegion(tuples[0], tuples[1])]

        return [
            getRegion(start, end)
            for start, end in tuples
        ]

    def score_selector(self, view, selector):
        '''
        Scores a selector on a view, returns True if the selectors is
        scored for each selection.

        :param view:
            the current view

        :param selector:
            the selector, which should be scored
        '''
        return all(view.score_selector(sel.b, selector) for sel in view.sel())


class LatexFillAllPluginConsumer(object):
    '''
    Base class for classes which use FillAllHelper plugins
    '''
    COMPLETION_TYPE_NAMES = []
    COMPLETION_TYPES = None

    def _load_plugins(self):
        '''
        Loads the FillAllHelper plugins
        '''
        self.COMPLETION_TYPES = {}
        for plugin in get_plugins_by_type(FillAllHelper):
            name = _classname_to_internal_name(plugin.__name__)
            if name.endswith('_fill_all_helper'):
                name = name[:-16]
                self.COMPLETION_TYPES[name] = plugin()

        self.COMPLETION_TYPE_NAMES = list(self.COMPLETION_TYPES.keys())

    def get_completion_types(self):
        '''
        Gets the list of plugin names
        '''
        if self.COMPLETION_TYPES is None:
            self._load_plugins()
        return self.COMPLETION_TYPE_NAMES

    def get_completion_type(self, name):
        if self.COMPLETION_TYPES is None:
            self._load_plugins()
        return self.COMPLETION_TYPES.get(name)


class LatexFillAllEventListener(
    sublime_plugin.EventListener, LatexFillHelper, LatexFillAllPluginConsumer
):
    '''
    Implements the query completions and query context functionality for some
    completions and the logic to insert brackets as necessary
    '''

    # keys supported by on_query_context
    SUPPORTED_KEYS = None

    SUPPORTED_INSERT_CHARS = {
        'open_curly': '{',
        'open_square': '[',
        'comma': ',',
        'equal_sign': '='
    }

    def on_query_context(self, view, key, operator, operand, match_all):
        '''
        supports query_context for all completion types
        key is "lt_fill_all_{name}" where name is the short name of the
        completion type, e.g. "lt_fill_all_cite", etc.
        '''
        # quick exit conditions
        if not key.startswith("lt_fill_all_"):
            return None
        for sel in view.sel():
            point = sel.b
            if not view.score_selector(point, "text.tex.latex"):
                return None

        # load the plugins
        if self.SUPPORTED_KEYS is None:
            self.SUPPORTED_KEYS = dict(
                ("lt_fill_all_{0}".format(name), name)
                for name in self.get_completion_types()
            )

        try:
            key, insert_char = key.split('.')
        except:
            insert_char = ''

        # not handled here
        if key not in self.SUPPORTED_KEYS:
            return None
        # unsupported bracket
        elif insert_char and insert_char not in self.SUPPORTED_INSERT_CHARS:
            return False
        # unsupported operators
        elif operator not in [sublime.OP_EQUAL, sublime.OP_NOT_EQUAL]:
            return False

        insert_char = self.SUPPORTED_INSERT_CHARS.get(insert_char, '')

        completion_type = self.get_completion_type(
            self.SUPPORTED_KEYS.get(key)
        )

        if not(completion_type and completion_type.is_enabled()):
            return False

        selector = completion_type.get_supported_scope_selector()
        if not self.score_selector(view, selector):
            return False

        lines = [
            insert_char + view.substr(
                getRegion(view.line(sel).begin(), sel.b)
            )[::-1]
            for sel in view.sel()
        ]

        func = all if match_all else any
        result = func((
            completion_type.matches_line(line)
            for line in lines
        ))

        return result if operator == sublime.OP_EQUAL else not result

    def on_query_completions(self, view, prefix, locations):
        for location in locations:
            if not view.score_selector(location, "text.tex.latex"):
                return

        completion_types = self.get_completion_types()

        orig_prefix = prefix

        # tracks any regions to be removed
        fancy_prefix, remove_regions = self.get_common_fancy_prefix(
            view, locations
        )
        # although a prefix is passed in, our redefinition of "word" boundaries
        # mean we should recalculate this
        prefix = self.get_common_prefix(view, locations)

        fancy_prefixed_line = None
        if remove_regions:
            if remove_regions:
                fancy_prefixed_line = view.substr(
                    getRegion(view.line(locations[0]).begin(), locations[0])
                )[::-1]

        line = view.substr(
            getRegion(view.line(locations[0]).begin(), locations[0])
        )[::-1]

        completion_type = None
        for name in completion_types:
            ct = self.get_completion_type(name)
            if (
                fancy_prefixed_line is not None and
                hasattr(ct, 'matches_fancy_prefix')
            ):
                if ct.matches_fancy_prefix(fancy_prefixed_line):
                    line = fancy_prefixed_line
                    prefix = fancy_prefix
                    completion_type = ct
                    break
                elif ct.matches_line(line):
                    completion_type = ct
                    remove_regions = []
                    break
            elif ct.matches_line(line):
                completion_type = ct
                # reset fancy prefix
                remove_regions = []
                break

        if completion_type is None:
            self.clear_bracket_cache()
            return []
        elif not self.score_selector(
                view, completion_type.get_supported_scope_selector()):
            self.clear_bracket_cache()
            return []
        # completions could be unpredictable if we've changed the prefix
        elif orig_prefix and not prefix:
            self.clear_bracket_cache()
            return []

        try:
            completions = completion_type.get_auto_completions(
                view, prefix, line[::-1]
            )
        except:
            traceback.print_exc()
            self.clear_bracket_cache()
            return []

        if len(completions) == 0:
            self.clear_bracket_cache()
            return []
        elif type(completions) is tuple and len(completions) == 2:
            completions, insert_char = completions
            if len(completions) == 0:
                self.clear_bracket_cache()
                return []
        else:
            # this assumes that all regions have a similar current word
            # not ideal, but reasonably safe see:
            # http://docs.sublimetext.info/en/latest/extensibility/completions.html#completions-with-multiple-cursors
            insert_char = view.substr(
                self.get_current_word(view, locations[0])
            )

        # we found a _<prefix> entry, so clear it and remove the prefix
        # and close the brackets
        if remove_regions:
            view.run_command(
                'latex_tools_fill_all_complete_bracket',
                {
                    'insert_char': insert_char,
                    'remove_regions': self.regions_to_tuples(remove_regions)
                }
            )

        if type(completions[0]) is tuple:
            show, completions = zip(*completions)
        else:
            show = completions[:]

        # we did not find a fancy prefix, so append the closing bracket,
        # if needed, to the completions
        if not remove_regions:
            closing_bracket = None
            for sel in view.sel():
                new_bracket = self.get_closing_bracket(view, sel)
                if closing_bracket is None:
                    closing_bracket = new_bracket
                elif new_bracket != closing_bracket:
                    closing_bracket = None
                    break

            if closing_bracket:
                completions = [
                    c + closing_bracket
                    for c in completions
                ]

        self.clear_bracket_cache()

        return (
            zip(show, completions),
            sublime.INHIBIT_WORD_COMPLETIONS |
            sublime.INHIBIT_EXPLICIT_COMPLETIONS
        )


class LatexFillAllCommand(
    sublime_plugin.TextCommand, LatexFillHelper, LatexFillAllPluginConsumer
):
    '''
    Implements the quick panel for auto-triggered completions and the
    logic to insert brackets as necessary

    :param edit:
        the current edit

    :param completion_type:
        the completion plugin to use (optional)
        may be:
            * a string indicating the specific completion type, e.g. "cite"
            * a list of such strings
            * None, in which case all available completion types are searched

    :param insert_char:
        the character to insert before the completion; also determines the
        matching brace if any

    :param overwrite:
        boolean indicating whether or not to overwrite the current field;
        if false, text within the current selection or to the left of the
        cursor is treated as the prefix, which usually restricts the
        displayed results;
        if true, the current word will be replaced by the selected entry

    :param force:
        boolean indicating whether or not to match the context or simply
        insert an entry; if force is true, completion_type must be a string;
        if force is true, the bracket matching and word overwriting behaviour
        is disabled
    '''

    def run(
        self, edit, completion_type=None, insert_char="", overwrite=False,
        force=False
    ):
        view = self.view

        for sel in view.sel():
            point = sel.b
            if not view.score_selector(point, "text.tex.latex"):
                self.complete_brackets(view, edit, insert_char)
                return

        # if completion_type is a simple string, try to load it
        if isinstance(completion_type, strbase):
            completion_type = self.get_completion_type(completion_type)
            if completion_type is None:
                if not force:
                    self.complete_brackets(view, edit, insert_char)
                return
        elif force:
            print('Cannot set `force` if completion type is not specified')
            return

        if force:
            insert_char = ''
            overwrite = False

        # tracks any regions to be removed
        remove_regions = []
        prefix = ''

        # handle the _ prefix, if necessary
        if (
            not isinstance(completion_type, FillAllHelper) or
            hasattr(completion_type, 'matches_fancy_prefix')
        ):
            fancy_prefix, remove_regions = self.get_common_fancy_prefix(
                view, view.sel()
            )

        # if we found a _ prefix, we use the raw line, so \ref_eq
        fancy_prefixed_line = None
        if remove_regions:
            fancy_prefixed_line = view.substr(
                getRegion(view.line(point).begin(), point)
            )[::-1]

        # normal line calculation
        line = (view.substr(
            getRegion(view.line(point).begin(), point)
        ) + insert_char)[::-1]

        # handle a list of completion types
        if type(completion_type) is list:
            for name in completion_type:
                try:
                    ct = self.get_completion_type(name)
                    if (
                        fancy_prefixed_line is not None and
                        hasattr(ct, 'matches_fancy_prefix')
                    ):
                        if ct.matches_fancy_prefix(fancy_prefixed_line):
                            completion_type = ct
                            prefix = fancy_prefix
                            break
                        elif ct.matches_line(line):
                            completion_type = ct
                            remove_regions = []
                            break
                    elif ct.matches_line(line):
                        completion_type = ct
                        remove_regions = []
                        break
                except:
                    pass

            if type(completion_type) is list:
                message = "No valid completions found"
                print(message)
                sublime.status_message(message)
                self.complete_brackets(view, edit, insert_char)
                return
        # unknown completion type
        elif (
            completion_type is None or
            not isinstance(completion_type, FillAllHelper)
        ):
            for name in self.get_completion_types():
                ct = self.get_completion_type(name)
                if ct is None:
                    continue

                if (
                    fancy_prefixed_line is not None and
                    hasattr(ct, 'matches_fancy_prefix')
                ):
                    if ct.matches_fancy_prefix(fancy_prefixed_line):
                        completion_type = ct
                        prefix = fancy_prefix
                        break
                    elif ct.matches_line(line):
                        completion_type = ct
                        remove_regions = []
                        break
                elif ct.matches_line(line):
                    completion_type = ct
                    remove_regions = []
                    break

            if (
                completion_type is None or
                isinstance(completion_type, strbase)
            ):
                message = \
                    'Cannot determine completion type for current selection'
                print(message)
                sublime.status_message(message)

                self.complete_brackets(view, edit, insert_char)
                return
        # assume only a single completion type to use
        else:
            # if force is set, we do no matching
            if not force:
                if (
                    fancy_prefixed_line is not None and
                    hasattr(completion_type, 'matches_fancy_prefix')
                ):
                    if completion_type.matches_fancy_prefix(
                        fancy_prefixed_line
                    ):
                        prefix = fancy_prefix
                    elif completion_type.matches_line(line):
                        remove_regions = []
                elif completion_type.matches_line(line):
                    remove_regions = []

        # we only check if the completion type is enabled if we're also
        # inserting a comma or bracket; otherwise, it must've been a keypress
        if insert_char and not completion_type.is_enabled():
            self.complete_brackets(view, edit, insert_char)
            return

        # we are not adding a bracket or comma, we do not have a fancy prefix
        # and the overwrite and force options were not set, so calculate the
        # prefix as the previous word
        if insert_char == '' and not prefix and not overwrite and not force:
            prefix = self.get_common_prefix(view, view.sel())

        # reset the _ completions if we are not using them
        if (
            insert_char and
            "fancy_prefix" in locals() and
            prefix != fancy_prefix
        ):
            remove_regions = []
            prefix = ''

        try:
            completions = completion_type.get_completions(
                view, prefix, line[::-1]
            )
        except:
            self.complete_brackets(
                view, edit, insert_char, remove_regions=remove_regions
            )
            reraise(*sys.exc_info())

        if completions is None:
            self.complete_brackets(
                view, edit, insert_char, remove_regions=remove_regions
            )
            return
        elif type(completions) is tuple:
            formatted_completions, completions = completions
        else:
            formatted_completions = completions

        if len(completions) == 0:
            self.complete_brackets(
                view, edit, insert_char, remove_regions=remove_regions
            )
        elif len(completions) == 1:
            # if there is only one completion and it already matches the
            # current text
            if force:
                view.insert(edit, completions[0])
                return
            else:
                if completions[0] == prefix:
                    return

                if insert_char:
                    insert_text = (
                        insert_char + completions[0]
                        if completions[0] else insert_char
                    )
                    self.insert_at_end(view, edit, insert_text)
                elif completions[0]:
                    self.replace_word(view, edit, completions[0])

                self.complete_auto_match(view, edit, insert_char)
                self.remove_regions(view, edit, remove_regions)
            self.clear_bracket_cache()
        else:
            def on_done(i):
                if i < 0:
                    view.run_command(
                        'latex_tools_fill_all_complete_bracket',
                        {
                            'insert_char': insert_char,
                            'remove_regions':
                                self.regions_to_tuples(remove_regions)
                        }
                    )
                    return

                if force:
                    view.run_command(
                        'insert',
                        {
                            'characters': completions[i]
                        }
                    )
                else:
                    view.run_command(
                        'latex_tools_replace_word',
                        {
                            'insert_char': insert_char,
                            'replacement': completions[i],
                            'remove_regions':
                                self.regions_to_tuples(remove_regions)
                        }
                    )

            view.window().show_quick_panel(formatted_completions, on_done)
            self.clear_bracket_cache()


class LatexToolsReplaceWord(sublime_plugin.TextCommand, LatexFillHelper):
    '''
    A TextCommand to replace the current word with a specified replacement

    :param replacement:
        the text to replace the current word with

    :param insert_char:
        if provided, a character to be inserted before the new word
        this is useful to implement bracket-matching around the newly-inserted
        word. Note that if this is provided, the replacement will be inserted
        instead of replacing the current word.

    :param remove_regions:
        any regions to be removed from the view. Regions should be supplied
        as returned by the regions_to_tuples method
    '''

    def run(self, edit, replacement='', insert_char='', remove_regions=[]):
        view = self.view
        if insert_char:
            insert_text = (
                insert_char + replacement
                if replacement else insert_char
            )
            self.insert_at_end(view, edit, insert_text)
        elif replacement:
            self.replace_word(view, edit, replacement)

        self.complete_auto_match(view, edit, insert_char)
        self.remove_regions(view, edit, self.tuples_to_regions(remove_regions))
        self.clear_bracket_cache()


class LatexToolsFillAllCompleteBracket(
    sublime_plugin.TextCommand, LatexFillHelper
):
    '''
    A TextCommand to insert brackets and remove any specified regions

    :param insert_char:
        if provided, a character to be inserted before the new word
        this is useful to implement bracket-matching around the newly-inserted
        word.

    :param remove_regions:
        any regions to be removed from the view. Regions should be supplied
        as returned by the regions_to_tuples method.
    '''

    def run(self, edit, insert_char='', remove_regions=[]):
        self.complete_brackets(
            self.view, edit, insert_char,
            self.tuples_to_regions(remove_regions)
        )
