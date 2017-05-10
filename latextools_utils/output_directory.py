import hashlib
import json
import os
import sublime
import tempfile

try:
    from latextools_utils import get_setting
    from latextools_utils.distro_utils import using_miktex
    from latextools_utils.tex_directives import (
        get_tex_root, parse_tex_directives
    )
    from latextools_utils.sublime_utils import get_project_file_name
    from latextools_utils.system import make_dirs
except ImportError:
    from . import get_setting
    from .distro_utils import using_miktex
    from .tex_directives import get_tex_root, parse_tex_directives
    from .sublime_utils import get_project_file_name
    from .system import make_dirs


__all__ = [
    'get_aux_directory', 'get_output_directory', 'get_jobname',
    'UnsavedFileException'
]


# raised whenever the root cannot be determined, which indicates an unsaved
# file
class UnsavedFileException(Exception):
    pass


# finds the aux-directory
# general algorithm:
#   1. check for an explicit aux_directory directive
#   2. check for an --aux-directory flag
#   3. check for a project setting
#   4. check for a global setting
#   5. assume aux_directory is the same as output_directory
# return_setting indicates that the raw setting should be returned
# as well as the auxiliary directory
def get_aux_directory(view_or_root, return_setting=False):
    # not supported using texify or the simple builder
    if not using_miktex() or using_texify_or_simple():
        if return_setting:
            return (None, None)
        else:
            return None

    root = get_root(view_or_root)

    aux_directory = get_directive(view_or_root, 'aux_directory')

    if (aux_directory is None or aux_directory == '') and (
            root is not None and view_or_root != root):
        aux_directory = get_directive(root, 'aux_directory')

    if aux_directory is not None and aux_directory != '':
        aux_dir = resolve_to_absolute_path(
            root, aux_directory, _get_root_directory(root)
        )

        if return_setting:
            return (aux_dir, aux_directory)
        else:
            return aux_dir

    view = sublime.active_window().active_view()
    aux_directory = view.settings().get('aux_directory')

    if aux_directory is not None and aux_directory != '':
        aux_dir = resolve_to_absolute_path(
            root,
            aux_directory,
            _get_root_directory(get_project_file_name(view))
        )

        if return_setting:
            return (aux_dir, aux_directory)
        else:
            return aux_dir

    settings = sublime.load_settings('LaTeXTools.sublime-settings')
    aux_directory = settings.get('aux_directory')

    if aux_directory is not None and aux_directory != '':
        aux_dir = resolve_to_absolute_path(
            root, aux_directory, _get_root_directory(root)
        )

        if return_setting:
            return (aux_dir, aux_directory)
        else:
            return aux_dir

    return get_output_directory(root, return_setting)


# finds the output-directory
# general algorithm:
#   1. check for an explicit output_directory directive
#   2. check for an --output-directory flag
#   3. check for a project setting
#   4. check for a global setting
#   5. assume output_directory is None
# return_setting indicates that the raw setting should be returned
# as well as the output directory
def get_output_directory(view_or_root, return_setting=False):
    # not supported using texify or the simple builder
    if using_texify_or_simple():
        if return_setting:
            return (None, None)
        else:
            return None

    root = get_root(view_or_root)

    output_directory = get_directive(view_or_root, 'output_directory')

    if (output_directory is None or output_directory == '') and (
            root is not None and view_or_root != root):
        output_directory = get_directive(root, 'output_directory')

    if output_directory is not None and output_directory != '':
        out_dir = resolve_to_absolute_path(
            root, output_directory, _get_root_directory(root)
        )

        if return_setting:
            return (out_dir, output_directory)
        else:
            return out_dir

    view = sublime.active_window().active_view()
    output_directory = view.settings().get('output_directory')

    if output_directory is not None and output_directory != '':
        out_dir = resolve_to_absolute_path(
            root,
            output_directory,
            _get_root_directory(get_project_file_name(view))
        )

        if return_setting:
            return (out_dir, output_directory)
        else:
            return out_dir

    settings = sublime.load_settings('LaTeXTools.sublime-settings')
    output_directory = settings.get('output_directory')

    if output_directory is not None and output_directory != '':
        out_dir = resolve_to_absolute_path(
            root, output_directory, _get_root_directory(root)
        )

        if return_setting:
            return (out_dir, output_directory)
        else:
            return out_dir

    if return_setting:
        return (None, None)
    else:
        return None


# finds the jobname
# general algorithm:
#   1. check for an explict jobname setting
#   2. check for a --jobname flag
#   3. check for a project setting
#   4. check for a global setting
#   5. assume jobname is basename of tex_root
# Note: returns None if root is unsaved
def get_jobname(view_or_root):
    root = get_root(view_or_root)
    if root is None:
        return None

    # exit condition: texify and simple do not support jobname
    # so always return the root path
    if using_texify_or_simple():
        return os.path.splitext(
            os.path.basename(root)
        )[0]

    jobname = get_directive(view_or_root, 'jobname')
    if (jobname is None or jobname == '') and view_or_root != root:
        jobname = get_directive(root, 'jobname')

    if jobname is None or jobname == '':
        jobname = get_setting('jobname')

    if jobname is None or jobname == '':
        return os.path.splitext(
            os.path.basename(root)
        )[0]

    return jobname


def using_texify_or_simple():
    if using_miktex():
        builder = get_setting('builder', 'traditional')
        if builder in ['', 'default', 'traditional', 'simple']:
            return True
    return False


def get_root(view_or_root):
    if isinstance(view_or_root, sublime.View):
        # here we can still handle root being None if the output_directory
        # setting is an aboslute path
        return get_tex_root(view_or_root)
    else:
        return view_or_root


def get_directive(root, key):
    directives = parse_tex_directives(
        root, multi_values=['options'], only_for=['options', key]
    )

    try:
        return directives[key]
    except KeyError:
        option = key.replace('_', '-')
        for opt in directives.get('options', []):
            if opt.lstrip('-').startswith(option):
                try:
                    return opt.split('=')[1].strip()
                except:
                    # invalid option parameter
                    return None
        return None


def resolve_to_absolute_path(root, value, root_path):
    # special values
    if (
        len(value) > 4 and
        value[0] == '<' and
        value[1] == '<' and
        value[-2] == '>' and
        value[-1] == '>'
    ):
        root_hash = _get_root_hash(root)
        if root_hash is None:
            raise UnsavedFileException()

        if value == '<<temp>>':
            result = os.path.join(
                _get_tmp_dir(), root_hash
            )
        elif value == '<<project>>':
            result = os.path.join(
                root_path, root_hash
            )
        elif value == '<<cache>>':
            result = os.path.join(
                get_cache_directory(),
                root_hash
            )
        else:
            print(u'unrecognized special value: {0}'.format(value))

            # NOTE this assumes that the value provided is a typo, etc.
            # and tries not to do anything harmful. This may not be the
            # best assumption
            return None

        # create the directory
        make_dirs(result)

        return result

    result = os.path.expandvars(
        os.path.expanduser(
            value
        )
    )

    if not os.path.isabs(result):
        result = os.path.join(root_path, result)
    result = os.path.normpath(result)
    if os.path.exists(result):
        result = os.path.realpath(result)

    return result


if sublime.version() < '3000':
    def get_cache_directory():
        return os.path.join(
            sublime.packages_path(),
            'User',
            '.lt_cache'
        )
else:
    def get_cache_directory():
        return os.path.join(
            sublime.cache_path(),
            'LaTeXTools'
        )


# uses a process-wide temp directory which should be cleaned-up on exit
def _get_tmp_dir():
    if hasattr(_get_tmp_dir, 'directory'):
        return _get_tmp_dir.directory
    else:
        _get_tmp_dir.directory = tempfile.mkdtemp()

        # register directory to be deleted on next start-up
        # unfortunately, there is no reliable way to do clean-up on exit
        # see https://github.com/SublimeTextIssues/Core/issues/10
        cache_dir = get_cache_directory()
        make_dirs(cache_dir)

        temporary_output_dirs = os.path.join(
            cache_dir,
            'temporary_output_dirs'
        )

        if os.path.exists(temporary_output_dirs):
            with open(temporary_output_dirs, 'r') as f:
                data = json.load(f)
        else:
            data = {'directories': []}

        data['directories'].append(_get_tmp_dir.directory)

        with open(temporary_output_dirs, 'w') as f:
            json.dump(data, f)

        return _get_tmp_dir.directory


def _get_root_directory(root):
    if root is None:
        # best guess
        return os.getcwd()
    else:
        if not os.path.isabs(root):
            # again, best guess
            return os.path.join(os.getcwd(), os.path.dirname(root))
        return os.path.dirname(root)


def _get_root_hash(root):
    if root is None:
        return None

    if os.path.exists(root):
        root = os.path.realpath(root)

    return hashlib.md5(root.encode('utf-8')).hexdigest()
