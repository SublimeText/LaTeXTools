"""
Plugin auto-discovery system intended for use in LaTeXTools package.

Overview
========

A plugin is a Python class that extends LaTeXToolsPlugin and provides some
functionality, usually via a function, that LaTeXTools code interacts with.
This module provide mechanisms for loading such plugins from arbitrary files
and configuring the environment in which they are used. It tries to make as
few assumptions as possible about how the consuming code and the plugin
interact. At it's heart it is just a plugin registry.

A quick example plugin:

    from latextools_plugin import LaTeXToolsPlugin

    class PluginSample(LaTeXToolsPlugin):
        def do_something():
            pass

And example consuming code:

    from latextools_plugin import get_plugin

    plugin = get_plugin('plugin_sample')
    # instantiate and use the plugin
    plugin().do_something()

Note that we make no assumption about how plugins are used, just how they are
loaded. It is up to the consuming code to provide a protocol for interaction,
i.e., methods that will be called, etc.

As shown above, plugin others should import and sub-class the
`LaTeXToolsPlugin` class from this module, as this will ensure the plugin is
properly registered and so available to consuming code. Plugins are registered
by using a version of the class name, so it is important that all plugins used
have a unique class name. The conversion is similar to how Sublime handles
*Command objects, so the name is converted from CamelCase to snake_case. In
addition, the word "Plugin", if it occurs at the end of the class name, is
removed.

Consuming code loads a plugin from the registry by passing the converted plugin
name to the `get_plugin()` function defined in this class. What is returned is
the class itself, i.e., it is the responsibility of the consuming code to
initialize the plugin and then interact with it.

The Plugin Environment
======================
The plugin environment will be setup so that the directory containing the
plugin is the first entry on sys.path, enabling import of any modules located
in the same folder, according to standard Python import rules. In addition, the
standard modules available to SublimeText are available. In addition, a small
number of modules from LaTeXTools itself can be made available.
"""

import re


class LaTeXToolsPluginException(Exception):
    """
    Base class for plugin-related exceptions
    """

    pass


class NoSuchPluginException(LaTeXToolsPluginException):
    """
    Exception raised if an attempt is made to access a plugin that does not
    exist

    Intended to allow the consumer to provide the user with some more useful
    information e.g., how to properly configure a module for an extension point
    """

    pass


class InvalidPluginException(LaTeXToolsPluginException):
    """
    Exception raised if an attempt is made to register a plugin that is not a
    subclass of LaTeXToolsPlugin.
    """

    pass


class LaTeXToolsPluginRegistry(dict):
    """
    Registry used internally to store references to plugins to be retrieved
    by plugin consumers.
    """

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise NoSuchPluginException(
                f"Plugin {key} does not exist. Please ensure that the plugin is "
                "configured as documented"
            )

    def __setitem__(self, key, value):
        if not issubclass(value, LaTeXToolsPlugin):
            raise InvalidPluginException(value)
        super().__setitem__(key, value)


_REGISTRY = LaTeXToolsPluginRegistry()


class LaTeXToolsPlugin:
    """
    Base class for LaTeXTools plugins. Implementation details will depend on where
    this plugin is supposed to be loaded. See the documentation for details.
    """

    def __init_subclass__(cls) -> None:
        _REGISTRY[cls.plugin_name()] = cls
        return super().__init_subclass__()

    @classmethod
    def plugin_name(cls):
        return classname_to_plugin_name(cls.__name__)


def get_plugin(name):
    """
    This is intended to be the main entry-point used by consumers (not
    implementors) of plugins, to find any plugins that have registered
    themselves by name.

    If a plugin cannot be found, a NoSuchPluginException will be thrown. Please
    try to provide the user with any helpful information.

    Use case:
        Provide the user with the ability to load a plugin by a memorable name,
        e.g., in a settings file.

        For example, 'biblatex' will get the plugin named 'BibLaTeX', etc.
    """
    if _REGISTRY is None:
        raise NoSuchPluginException(
            f"Could not load plugin {name} because the registry either hasn't "
            "been loaded or has just been unloaded."
        )
    return _REGISTRY[name]


def get_plugins_by_type(cls):
    if _REGISTRY is None:
        raise NoSuchPluginException(
            "No plugins could be loaded because the registry either hasn't "
            "been loaded or has been unloaded"
        )

    return [plugin for plugin in _REGISTRY.values() if issubclass(plugin, cls)]


def classname_to_plugin_name(s):
    """
    Converts a Python class name in to an internal name

    The intention here is to mirror how ST treats *Command objects, i.e., by
    converting them from CamelCase to under_scored. Similarly, we will chop
    "Plugin" off the end of the plugin, though it isn't necessary for the class
    to be treated as a plugin.

    E.g.,
        SomeClass will become some_class
        ReferencesPlugin will become references
        BibLaTeXPlugin will become biblatex
    """
    if not s:
        return s

    def _repl(match):
        match = match.group(0)
        return match[0] + match[1:].lower()

    s = re.sub(r"(?:Bib)?(?:La)?TeX", _repl, s)

    # pilfered from https://code.activestate.com/recipes/66009/
    s = re.sub(r"(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])", r"_\g<0>", s).lower()

    if s.endswith("_plugin"):
        s = s[:-7]

    return s
