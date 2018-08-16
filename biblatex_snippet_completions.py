# coding=utf-8

# This is here precisely so snippet completion doesn't interfere
# with other autocompletions.

from __future__ import print_function

import sublime
import sublime_plugin

import os
import traceback

from xml.etree import ElementTree

try:
    from latextools_utils import is_bib_buffer, is_biblatex_buffer
except ImportError:
    from .latextools_utils import is_bib_buffer, is_biblatex_buffer

_ST3 = sublime.version() >= '3000'

# ElementTree is broken on Linux ST2
if not _ST3 and sublime.platform() == 'linux':
    from external.elementtree import SimpleXMLTreeBuilder
    ElementTree.XMLTreeBuilder = SimpleXMLTreeBuilder.TreeBuilder

__dir__ = os.path.dirname(__file__)
if __dir__ == '.':
    __dir__ = os.path.join(sublime.packages_path(), 'LaTeXTools')

def _get_completions(ext):
    completions = []

    for root, dirs, files in os.walk(
            os.path.join(__dir__, 'snippets')):
        files = [f for f in files if f.endswith(ext)]

        for f in files:
            doc = ElementTree.parse(os.path.join(root, f))
            try:
                # completions must be tuples on ST2
                completions.append(
                    (
                        "{0}\t{1}".format(
                            doc.find('tabTrigger').text.strip(),
                            doc.find('description').text.strip()
                        ),
                        doc.find('content').text.strip()
                    )
                )
            except:
                print('Error occurred when trying to load snippet from {0}'.format(
                    os.path.join(root, f)
                ))

                traceback.print_exc()

    return completions

def get_biblatex_completions():
    return _get_completions('.biblatex-snippet')

def get_bibtex_completions():
    return _get_completions('.bibtex-snippet')

class SnippetCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not is_bib_buffer(view):
            return []

        # do not return completions if the cursor is inside an entry
        if view.score_selector(view.sel()[0].b, 'meta.entry.braces.bibtex') > 0:
            return []

        if is_biblatex_buffer(view):
            return (get_biblatex_completions(), sublime.INHIBIT_WORD_COMPLETIONS)

        else:
            return (get_bibtex_completions(), sublime.INHIBIT_WORD_COMPLETIONS)