from __future__ import print_function

import codecs
import os
import re
import sublime
import sys
import traceback

try:
    from latextools_utils.is_tex_file import is_tex_file
    from latextools_utils.sublime_utils import get_project_file_name
except ImportError:
    from .is_tex_file import is_tex_file
    from .sublime_utils import get_project_file_name

if sys.version_info < (3, 0):
    strbase = basestring
else:
    strbase = str

TEX_DIRECTIVE = re.compile(
    r'%+\s*!(?:T|t)(?:E|e)(?:X|x)\s+([\w-]+)\s*=\s*' +
    r'(.*?)\s*$',
    re.UNICODE
)

# this is obviously imperfect, but is intended as a heuristic. we
# can tolerate false negatives, but not false positives that match, e.g.,
# Windows paths or parts of Windows paths.
LATEX_COMMAND = re.compile(r'\\[a-zA-Z]+\*?(?:\[[^\]]+\])*\{[^\}]+\}')


def parse_tex_directives(view_or_path, multi_values=[], key_maps={},
                         only_for=[]):
    '''
    Parses a view or file for any %!TEX directives

    Returns a dictionary of directives keyed from the directive name in
    lower-case

    parameters:
        view_or_path    -   either a ST view or a path to a file to parse
        multi_values    -   a list of directives to allow to have multiple
                            if not included in this list, only the first
                            encountered value is retained
        key_maps        -   a dict mapping from a directive to the directive
                            to be returned. intended to allow directives to
                            be renamed (e.g. ts-program -> program)
        only_for        -   a list of the directives we are interested in
                            if only a single value is present and no
                            multi_values are specified, this will exit once
                            a match is found
    '''
    result = {}

    # used to indicate if we opened a file so it can be closed
    is_file = False
    if isinstance(view_or_path, sublime.View):
        lines = view_or_path.substr(
            sublime.Region(0, view_or_path.size())).split('\n')
    elif isinstance(view_or_path, strbase):
        try:
            lines = codecs.open(view_or_path, "r", "utf-8", "ignore")
        except IOError:
            # fail (relatively) silently if view_or_path is not a valid path
            print('Caught IOError while handling {0} as file'.format(
                view_or_path))
            traceback.print_exc()
            return result
        else:
            is_file = True
    else:
        print('{0} is not supported by parse_tex_directives()'.format(
            type(view_or_path)))
        return result

    try:
        # precompute some conditions that do not vary while looping

        # indicates that there is a list of only_for values
        has_only_for = only_for is not None and len(only_for) > 0

        # whether or not we should break on the first value encountered
        # we do so if only a single directive is being searched for
        # and it is not multi-valued
        break_on_first = has_only_for and len(only_for) == 1 and \
            (multi_values is None or only_for[0] not in multi_values)

        for line in lines:
            # read up until the first LaTeX command
            m = LATEX_COMMAND.search(line)
            if m:
                break
            elif not line.startswith('%'):
                continue

            m = TEX_DIRECTIVE.match(line)
            if m:
                key = m.group(1).lower()
                value = m.group(2)

                if key in key_maps:
                    key = key_maps[key]

                if has_only_for and key not in only_for:
                    continue

                if key in multi_values:
                    if key in result:
                        result[key].append(value)
                    else:
                        result[key] = [value]
                else:
                    if key not in result:
                        result[key] = value

                        if break_on_first:
                            break

        return result
    finally:
        if is_file:
            lines.close()


# Contributed by Sam Finn
def get_tex_root(view):
    view_file = view.file_name()

    root = None
    directives = parse_tex_directives(view, only_for=['root'])
    try:
        root = directives['root']
    except KeyError:
        pass
    else:
        if not is_tex_file(root):
            root = None
        elif not os.path.isabs(root) and view_file is not None:
            file_path, _ = os.path.split(view_file)
            root = os.path.normpath(os.path.join(file_path, root))

    if root is None:
        root = get_tex_root_from_settings(view)

    if root is not None:
        return root
    return view_file


def get_tex_root_from_settings(view):
    root = view.settings().get('TEXroot', None)

    if root is not None:
        if os.path.isabs(root):
            if os.path.isfile(root):
                return root
        else:
            proj_file = get_project_file_name(view)

            if proj_file:
                project_dir = os.path.dirname(proj_file)
                root_path = os.path.normpath(os.path.join(project_dir, root))
                if os.path.isfile(root_path):
                    return root_path

    return root
