#
# This module will reload any existing submodules, such as latextools_utils,
# that may be cached in memory. Note that it must be run before any module
# that uses any imports from any of those modules, hence the name.
#

import sublime
import sys

if sys.version_info >= (3,):
    from imp import reload


MOD_PREFIX = ''

if sublime.version() > '3000':
    MOD_PREFIX = 'LaTeXTools.' + MOD_PREFIX

# these modules must be specified in the order they depend on one another
LOAD_ORDER = [
    'latextools_utils',

    # no internal dependencies
    'latextools_utils.settings',
    'latextools_utils.utils',
    'latextools_utils.tex_directives',
    'latextools_utils.system',

    # depend on previous only
    'latextools_utils.distro_utils',
    'latextools_utils.is_tex_file',
    'latextools_utils.sublime_utils',
    'latextools_utils.cache',

    # depend on any previous
    'latextools_utils.analysis',
    'latextools_utils.output_directory',

    'latextools_plugin_internal',

    'latex_chars'
]


for suffix in LOAD_ORDER:
    mod = MOD_PREFIX + suffix
    if mod in sys.modules and sys.modules[mod] is not None:
        reload(sys.modules[mod])
