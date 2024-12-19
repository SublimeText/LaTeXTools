#
# This module will reload any existing submodules, such as latextools_utils,
# that may be cached in memory. Note that it must be run before any module
# that uses any imports from any of those modules, hence the name.
#

import sublime

import sys
import traceback

try:
    # python 3.8+
    from importlib import reload
except ImportError:
    # python 3.3
    from imp import reload


def _load_module_exports(module):
    if 'exports' in module.__dict__:
        for name in module.exports:
            try:
                # lift the export to this modules top level
                globals()[name] = module.__dict__[name]
            except KeyError:
                print(
                    "Error: {0} not defined in {1}."
                    .format(name, module.__name__))


MOD_PREFIX = 'LaTeXTools.'

# these modules must be specified in the order they depend on one another
LOAD_ORDER = [
    'external.latex_chars',

    'latextools_plugin_internal',

    # reloaded here so that makePDF imports the current version
    'parseTeXlog',

    'latextools_utils',

    # no internal dependencies
    'latextools_utils.bibformat',
    'latextools_utils.settings',
    'latextools_utils.utils',
    'latextools_utils.tex_directives',
    'latextools_utils.internal_types',

    # depend on previous only
    'latextools_utils.distro_utils',
    'latextools_utils.is_tex_file',
    'latextools_utils.cache',
    'latextools_utils.quickpanel',
    'latextools_utils.external_command',

    # depend on any previous
    'latextools_utils.sublime_utils',

    # depend on any previous
    'latextools_utils.analysis',
    'latextools_utils.ana_utils',
    'latextools_utils.output_directory',
    'latextools_utils.bibcache',

    'latextools_plugin',

    # ensure latex_fill_all is loaded before the modules that depend on it
    'latex_fill_all'
]

# modules which should be scanned for any exports to be hoisted to this
# module's context
EXPORT_MODULES = []
if sublime.version() > '3118':
    LOAD_ORDER += [
        'st_preview.preview_utils',
        'st_preview.preview_threading'
    ]

    EXPORT_MODULES += [
        'latextools_utils.input_quickpanel',
        'st_preview.preview_math',
        'st_preview.preview_image'
    ]

LOAD_ORDER += EXPORT_MODULES

for suffix in LOAD_ORDER:
    mod = MOD_PREFIX + suffix
    try:
        if mod in sys.modules and sys.modules[mod] is not None:
            reload(sys.modules[mod])
        else:
            __import__(mod)
    except:
        traceback.print_exc()

    if suffix in EXPORT_MODULES:
        _load_module_exports(sys.modules[mod])


def plugin_loaded():
    # reload any plugins cached in memory
    mods = [m for m in sys.modules if m.startswith('_latextools_')]
    for mod in mods:
        try:
            del sys.modules[mod]
        except:
            traceback.print_exc()

    for module in EXPORT_MODULES:
        mod = MOD_PREFIX + module
        try:
            sys.modules[mod].plugin_loaded()
        except AttributeError:
            pass


def plugin_unloaded():
    for module in EXPORT_MODULES:
        mod = MOD_PREFIX + module
        try:
            sys.modules[mod].plugin_unloaded()
        except KeyError:
            pass
        except AttributeError:
            pass
