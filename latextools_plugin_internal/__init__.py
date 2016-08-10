'''
This is internal definitions used by the latextools_plugin module

This separate module is required because ST's reload semantics make it
impossible to implement something like this within that module itself.
'''

import re

_REGISTRY = None
# list of tuples consisting of a path and a glob to load in the plugin_loaded()
# method to handle the case where `add_plugin_path` is called before this
# module has been fully loaded.
_REGISTERED_PATHS_TO_LOAD = []

# list of tuples consisting of names and class objects to load in the
# plugin_loaded() method to handle the case where a plugin is defined before
# the registry has been created
_REGISTERED_CLASSES_TO_LOAD = []

# a list of tuples consisting of a module name and a module object used in the
# _latextools_modules_hack context manager to provide an API for adding modules
_WHITELIST_ADDED = []


# LaTeXToolsPlugin - base class for all plugins
class LaTeXToolsPluginMeta(type):
    '''
    Metaclass for plugins which will automatically register them with the
    plugin registry
    '''
    def __init__(cls, name, bases, attrs):
        try:
            super(LaTeXToolsPluginMeta, cls).__init__(name, bases, attrs)
        except TypeError:
            # occurs on reload
            return

        if cls == LaTeXToolsPluginMeta or cls is None:
            return

        try:
            if not any(
                (True for base in bases if issubclass(base, LaTeXToolsPlugin))
            ):
                return
        except NameError:
            return

        registered_name = _classname_to_internal_name(name)

        _REGISTERED_CLASSES_TO_LOAD.append((registered_name, cls))

        if _REGISTRY is not None:
            _REGISTRY[registered_name] = cls


LaTeXToolsPlugin = LaTeXToolsPluginMeta('LaTeXToolsPlugin', (object,), {})
LaTeXToolsPlugin.__doc__ = '''
Base class for LaTeXTools plugins. Implementation details will depend on where
this plugin is supposed to be loaded. See the documentation for details.
'''


def _classname_to_internal_name(s):
    '''
    Converts a Python class name in to an internal name

    The intention here is to mirror how ST treats *Command objects, i.e., by
    converting them from CamelCase to under_scored. Similarly, we will chop
    "Plugin" off the end of the plugin, though it isn't necessary for the class
    to be treated as a plugin.

    E.g.,
        SomeClass will become some_class
        ReferencesPlugin will become references
        BibLaTeXPlugin will become biblatex
    '''
    if not s:
        return s

    # little hack to support LaTeX or TeX in the plugin name
    while True:
        match = re.search(r'(?:Bib)?(?:La)?TeX', s)
        if match:
            s = s.replace(
                match.group(0),
                match.group(0)[0] + match.group(0)[1:].lower()
            )
        else:
            break

    # pilfered from http://code.activestate.com/recipes/66009/
    s = re.sub(r'(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', r"_\g<0>", s).lower()

    if s.endswith('_plugin'):
        s = s[:-7]

    return s
