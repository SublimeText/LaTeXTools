'''
Plugin auto-discovery system intended for use in LaTeXTools package.

Configuration options:
    `plugin_paths`: in the standard user configuration.
         A list of paths to search for plugins. Defaults to an empty list, in which
         case nothing will be done.

        Paths can either be specified as absolute paths, paths relative to the
        LaTeXTools package or paths relative to the User package. Paths in the
        User package will mask paths in the LaTeXTools package. This is intended to
        emulate the behaviour of ST.

NB Since this doesn't rely on any plugin naming conventions, this code *will* load any
Python (.py) file found in any of the configured `plugin_paths`. It is advisable that
users keep this setting restricted to a folder that only contains LaTeXTools-related
plugins, e.g., a folder named LaTeXToolsPlugins or similar.

Plugin authors should import the LaTeXToolsPlugin class and use it as a base for any
plugins. Only subclasses of LaTeXToolsPlugin will be registered and properly treated as
plugins.

Any consumers of plugins, i.e., code in the main LaTeXTools tree, should primarily
interact with this system through the `get_plugin()` function, which provides access
to the internal plugin registry.

A quick example plugin:

    from latextools_plugin import LaTeXToolsPlugin

    class PluginSample(LaTeXToolsPlugin):
        def do_something():
            pass

And example consuming code:

    from latextools_plugin import get_plugin

    plugin = get_plugin('plugin_sample')
    plugin.do_something()

Note that we make no assumption about how plugins are used, just how they are loaded.
It is up to the consuming code to provide a protocol for interaction, i.e., methods
that will be called, etc.
'''
from __future__ import print_function

import sublime

import glob as _glob
import os
import sys
import re

import traceback

from contextlib import contextmanager

from collections import MutableMapping

if sys.version_info < (3, 0):
    import imp

    def _load_module(module_name, name, paths):
        f, path, description = imp.find_module(name, list(paths))
        try:
            module = imp.load_module(module_name, f, path, description)
        finally:
            f.close()
        return module
else:
    from importlib.machinery import PathFinder

    # WARNING:
    # imp module is deprecated in 3.x, unfortunately, importlib does not seem
    # to have a stable API, as in 3.4, `find_module` is deprecated in favour of
    # `find_spec` and discussions of how best to provide access to the import
    # internals seem to be on-going
    def _load_module(module_name, name, paths):
        loader = PathFinder.find_module(name, path=paths)
        loader.name = module_name
        return loader.load_module()

__all__ = ['LaTeXToolsPlugin', 'get_plugin', 'add_plugin_path']

_MODULE_PREFIX = '_latextools_'

class LaTeXToolsPluginException(Exception):
    '''
    Base class for plugin-related exceptions
    '''
    pass

class NoSuchPluginException(LaTeXToolsPluginException):
    '''
    Exception raised if an attempt is made to access a plugin that does not exist

    Intended to allow the consumer to provide the user with some more useful information
    e.g., how to properly configure a module for an extension point
    '''
    pass

class InvalidPluginException(LaTeXToolsPluginException):
    '''
    Exception raised if an attempt is made to register a plugin that is not a
    subclass of LaTeXToolsPlugin.
    '''
    pass

class LaTeXToolsPluginRegistry(MutableMapping):
    def __init__(self):
        self._registry = {}

    def __getitem__(self, key):
        try:
            return self._registry[key]
        except KeyError:
            raise NoSuchPluginException(
                'Plugin {} does not exist. Please ensure that the plugin is configured as documented'.format(key))

    def __setitem__(self, key, value):
        if not isinstance(value, LaTeXToolsPlugin):
            raise InvalidPluginException(type(value))

        self._registry[key] = value

    def __delitem__(self, key):
        del self._registry[key]

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)

    def __str__(self):
        return str(self._registry)

_REGISTRY = LaTeXToolsPluginRegistry()

def _classname_to_internal_name(s):
    '''
    Converts a Python class name in to an internal name

    The intention here is to mirror how ST treats *Command objects, i.e., by
    converting them from CamelCase to under_scored. Similarly, we will chop "Plugin"
    off the end of the plugin, though it isn't necessary for the class to be treated
    as a plugin.

    E.g.,
        SomeClass will become some_class
        ReferencesPlugin will become references
        BibLaTeXPlugin will become biblatex
    '''
    if not s:
        return s

    # little hack to support LaTeX or TeX in the plugin name
    while True:
        match = re.search(r'(?:La)?TeX', s)
        if match:
            s = s.replace(match.group(0), match.group(0).lower())
        else:
            break

    # pilfered from http://code.activestate.com/recipes/66009/
    s = re.sub(r'(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', r"_\g<0>", s).lower()

    if s.endswith('_plugin'):
        s = s[:-7]

    return s

class LaTeXToolsPluginMeta(type):
    '''
    Metaclass for plugins which will automatically register them with the
    plugin registry
    '''
    def __init__(cls, name, bases, attrs):
        super(LaTeXToolsPluginMeta, cls).__init__(name, bases, attrs)
        if cls == LaTeXToolsPluginMeta:
            return

        try:
            if not LaTeXToolsPlugin in bases:
                return
        except NameError:
            return

        registered_name = _classname_to_internal_name(name)
        _REGISTRY[registered_name] = cls()

LaTeXToolsPlugin = LaTeXToolsPluginMeta('LaTeXToolsPlugin', (object,), {})
LaTeXToolsPlugin.__doc__ = '''
Base class for LaTeXTools plugins. Implementation details will depend on where this
plugin is supposed to be loaded. See the documentation for details.
'''

def _get_plugin_paths():
    settings = sublime.load_settings('LaTeXTools.sublime-settings')
    plugin_paths = settings.get('plugin_paths', [])
    return plugin_paths

def _load_plugin(name, *paths):
    # hopefully a unique-enough module name!
    module_name = '{}{}'.format(_MODULE_PREFIX, name)
    try:
        return sys.modules[module_name]
    except KeyError:
        pass

    try:
        return _load_module(module_name, name, paths)
    except ImportError:
        print('Could not load module {} using path {}.'.format(name, paths))
        traceback.print_exc()

    return None

def _load_plugins():
    for path in _get_plugin_paths():
        if not os.path.isabs(path):
            path = os.path.normpath(
                os.path.join(sublime.packages_path(), 'User', path))
            if not os.path.exists(path):
                path = os.path.normpath(
                    os.path.join(sublime.packages_path(), 'LaTeXTools', path))
        add_plugin_path(path)

def get_plugin(name):
    '''
    This is intended to be the main entry-point used by consumers (not implementors)
    of plugins, to find any plugins that have registered themselves by name.

    If a plugin cannot be found, a NoSuchPluginException will be thrown. Please try
    to provide the user with any helpful information.

    Use case:
        Provide the user with the ability to load a plugin by a memorable name,
        e.g., in a settings file.

        For example, 'biblatex' will get the plugin named 'BibLaTeX', etc.
    '''
    return _REGISTRY[name]

@contextmanager
def _latextools_module_hack():
    # ugly, ugly hack to ensure plugin authors can import latextools_plugin
    old_latextools_plugin = None
    if 'latextools_plugin' in sys.modules:
        old_latextools_plugin = sys.modules['latextools_plugin']

    sys.modules['latextools_plugin'] = sys.modules[__name__]
    yield
    del sys.modules['latextools_plugin']

    if old_latextools_plugin:
        sys.modules['latextools_plugin'] = old_latextools_plugin

def add_plugin_path(path, glob='*.py'):
    '''
    This function adds plugins from a specified path.

    It is primarily intended to be used by consumers to load plugins from a custom 
    path without needing to access the internals. For example, consuming code could
    use this to load any default plugins

    `glob`, if specified should be a valid Python glob. See the `glob` module.
    '''
    with _latextools_module_hack():
        if not os.path.exists(path):
            return
        for file in _glob.iglob(os.path.join(path, glob)):
            plugin_dir = os.path.dirname(file)
            sys.path.insert(0, plugin_dir)

            _load_plugin(os.path.splitext(
                os.path.basename(file))[0], plugin_dir)

            sys.path.pop(0)

# load plugins when the Sublime API is available, just in case...
def plugin_loaded():
    _load_plugins()

# when this plugin is unloaded, unload all custom plugins from sys.modules
def plugin_unloaded():
    for module in list(sys.modules.keys()):
        if module.startswith(_MODULE_PREFIX):
            del sys.modules[module]
