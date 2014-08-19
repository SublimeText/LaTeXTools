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

import re
import nose.tools

import pybtex.database.input.bibtex
import pybtex.plugin
import pybtex.style.formatting.plain


def test_plugin_loader():
    """Check that all enumerated plugins can be imported."""
    for group in pybtex.plugin._DEFAULT_PLUGINS:
        for name in pybtex.plugin.enumerate_plugin_names(group):
            pybtex.plugin.find_plugin(group, name)


class TestPlugin1(pybtex.plugin.Plugin):
    pass


class TestPlugin2(pybtex.plugin.Plugin):
    pass


class TestPlugin3(pybtex.plugin.Plugin):
    pass


class TestPlugin4(pybtex.plugin.Plugin):
    pass


def test_register_plugin_1():
    nose.tools.assert_true(
        pybtex.plugin.register_plugin(
            'pybtex.style.formatting', 'yippikayee', TestPlugin1))
    nose.tools.assert_is(
        TestPlugin1, pybtex.plugin.find_plugin(
            'pybtex.style.formatting', 'yippikayee'))
    nose.tools.assert_false(
        pybtex.plugin.register_plugin(
            'pybtex.style.formatting', 'yippikayee', TestPlugin2))
    nose.tools.assert_is(
        TestPlugin1, pybtex.plugin.find_plugin(
            'pybtex.style.formatting', 'yippikayee'))
    nose.tools.assert_true(
        pybtex.plugin.register_plugin(
            'pybtex.style.formatting', 'yippikayee', TestPlugin2, force=True))
    nose.tools.assert_is(
        TestPlugin2, pybtex.plugin.find_plugin(
            'pybtex.style.formatting', 'yippikayee'))


def test_register_plugin_2():
    nose.tools.assert_false(
        pybtex.plugin.register_plugin(
            'pybtex.style.formatting', 'plain', TestPlugin2))
    plugin = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')
    nose.tools.assert_is_not(plugin, TestPlugin2)
    nose.tools.assert_is(plugin, pybtex.style.formatting.plain.Style)


def test_register_plugin_3():
    nose.tools.assert_true(
        pybtex.plugin.register_plugin(
            'pybtex.style.formatting.suffixes', '.woo', TestPlugin3))
    plugin = pybtex.plugin.find_plugin(
        'pybtex.style.formatting', filename='test.woo')
    nose.tools.assert_is(plugin, TestPlugin3)


def test_bad_find_plugin():
    nose.tools.assert_raises(
        pybtex.plugin.PluginGroupNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.invalid.group", "__oops"))
    nose.tools.assert_raises_regexp(
        pybtex.plugin.PluginNotFound,
        re.escape('plugin pybtex.style.formatting.__oops not found'),
        lambda: pybtex.plugin.find_plugin("pybtex.style.formatting", "__oops"))
    nose.tools.assert_raises(
        pybtex.plugin.PluginNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.style.formatting",
                                          filename="oh.__oops"))


def test_bad_register_plugin():
    nose.tools.assert_raises(
        pybtex.plugin.PluginGroupNotFound,
        lambda: pybtex.plugin.register_plugin(
            "pybtex.invalid.group", "__oops", TestPlugin1))
    nose.tools.assert_raises(
        pybtex.plugin.PluginGroupNotFound,
        lambda: pybtex.plugin.register_plugin(
            "pybtex.invalid.group.suffixes", ".__oops", TestPlugin1))
    # suffixes must start with a dot
    nose.tools.assert_raises(
        ValueError,
        lambda: pybtex.plugin.register_plugin(
            "pybtex.style.formatting.suffixes", "notasuffix", TestPlugin1))


def test_plugin_suffix():
    plugin = pybtex.plugin.find_plugin(
        "pybtex.database.input", filename="test.bib")
    nose.tools.assert_is(plugin, pybtex.database.input.bibtex.Parser)


def test_plugin_alias():
    pybtex.plugin._DEFAULT_PLUGINS['pybtex.legacy.input'] = 'punchcard'
    nose.tools.assert_true(
        pybtex.plugin.register_plugin(
            'pybtex.legacy.input', 'punchcard', TestPlugin4))
    nose.tools.assert_true(
        pybtex.plugin.register_plugin(
            'pybtex.legacy.input.aliases', 'punchedcard', TestPlugin4))
    nose.tools.assert_equal(
        list(pybtex.plugin.enumerate_plugin_names('pybtex.legacy.input')),
        ['punchcard']
    )
    plugin = pybtex.plugin.find_plugin("pybtex.legacy.input", 'punchedcard')
    nose.tools.assert_equal(plugin, TestPlugin4)
    del pybtex.plugin._DEFAULT_PLUGINS['pybtex.legacy.input']


def test_plugin_class():
    """If a plugin class is passed to find_plugin(), it shoud be returned back."""
    plugin = pybtex.plugin.find_plugin("pybtex.database.input", 'bibtex')
    plugin2 = pybtex.plugin.find_plugin("pybtex.database.input", plugin)
    nose.tools.assert_equal(plugin, plugin2)
