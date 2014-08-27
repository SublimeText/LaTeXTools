# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
# Copyright (c) 2014  Matthias C. M. Troffaes
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os.path  # splitext
import pkg_resources

from pybtex.exceptions import PybtexError


class Plugin(object):
    pass


#: default pybtex plugins
_DEFAULT_PLUGINS = {
    "pybtex.database.input": "bibtex",
    "pybtex.database.output": "bibtex",
    "pybtex.backends": "latex",
    "pybtex.style.labels": "number",
    "pybtex.style.names": "plain",
    "pybtex.style.sorting": "none",
    "pybtex.style.formatting": "unsrt",
}


class PluginGroupNotFound(PybtexError):

    def __init__(self, group_name):
        message = 'plugin group {group_name} not found'.format(
            group_name=group_name,
        )
        super(PluginGroupNotFound, self).__init__(message)


class PluginNotFound(PybtexError):

    def __init__(self, plugin_group, name):
        if not name.startswith('.'):
            message = 'plugin {plugin_group}.{name} not found'.format(
                plugin_group=plugin_group,
                name=name,
            )
        else:
            assert plugin_group.endswith('.suffixes')
            message = (
                'plugin {plugin_group} for suffix {suffix} not found'.format(
                    plugin_group=plugin_group,
                    suffix=name,
                )
            )

        super(PluginNotFound, self).__init__(message)


def _load_entry_point(group, name, use_aliases=False):
    groups = [group, group + '.aliases'] if use_aliases else [group]
    for search_group in groups:
        for entry_point in pkg_resources.iter_entry_points(search_group, name):
            return entry_point.load()
    raise PluginNotFound(group, name)


def find_plugin(plugin_group, name=None, filename=None):
    """Find a :class:`Plugin` class within *plugin_group* which
    matches *name*, or *filename* if *name* is not specified, or
    the default plugin if neither *name* nor *filename* is
    specified.

    If *name* is specified, return the :class:`Plugin` class
    registered under *name*. If *filename* is specified, look at
    its suffix (i.e. extension) and return the :class:`Plugin`
    class registered for this suffix.

    If *name* is not a string, but a plugin class, just return it back.
    (Used to make functions like :function:`make_bibliography` accept already
    loaded plugins as well as plugin names.

    """
    if isinstance(name, type) and issubclass(name, Plugin):
        return name

    if plugin_group not in _DEFAULT_PLUGINS:
        raise PluginGroupNotFound(plugin_group)
    if name:
        return _load_entry_point(plugin_group, name, use_aliases=True)
    elif filename:
        suffix = os.path.splitext(filename)[1]
        return _load_entry_point(plugin_group + '.suffixes', suffix)
    else:
        return _load_entry_point(plugin_group, _DEFAULT_PLUGINS[plugin_group])


def enumerate_plugin_names(plugin_group):
    """Enumerate all plugin names for the given *plugin_group*."""
    return (entry_point.name
            for entry_point in pkg_resources.iter_entry_points(plugin_group))


class _FakeEntryPoint(pkg_resources.EntryPoint):

    def __init__(self, name, klass):
        self.name = name
        self.klass = klass

    def __str__(self):
        return "%s = :%s" % (self.name, self.klass.__name__)

    def __repr__(self):
        return (
            "_FakeEntryPoint(name=%r, klass=%s)"
            % (self.name, self.klass.__name__))

    def load(self, require=True, env=None, installer=None):
        return self.klass

    def require(self, env=None, installer=None):
        pass


def register_plugin(plugin_group, name, klass, force=False):
    """Register a plugin on the fly.

    This works by adding *klass* as a pybtex entry point, under entry
    point group *plugin_group* and entry point name *name*.

    To register a suffix, append ".suffixes" to the plugin group, and
    *name* is then simply the suffix, which should start with a
    period.

    To register an alias plugin name, append ".aliases" to the plugin group.
    Aliases work just as real names, but are not returned by
    :function:`enumerate_plugin_names` and not advertised in the command line
    help.

    If *force* is ``False``, then existing entry points are not
    overwritten. If an entry point with the given group and name
    already exists, then returns ``False``, otherwise returns
    ``True``.

    If *force* is ``True``, then existing entry points are
    overwritten, and the function always returns ``True``.

    """
    if plugin_group.endswith(".suffixes"):
        base_group, _ = plugin_group.rsplit(".", 1)
        if not name.startswith('.'):
            raise ValueError("a suffix must start with a period")
    elif plugin_group.endswith(".aliases"):
        base_group, _ = plugin_group.rsplit(".", 1)
    else:
        base_group = plugin_group
    if base_group not in _DEFAULT_PLUGINS:
        raise PluginGroupNotFound(base_group)

    dist = pkg_resources.get_distribution('pybtex')
    ep_map = pkg_resources.get_entry_map(dist)
    if plugin_group not in ep_map:
        ep_map[plugin_group] = {}
    if name in ep_map[plugin_group] and not force:
        return False
    else:
        ep_map[plugin_group][name] = _FakeEntryPoint(name, klass)
        return True
