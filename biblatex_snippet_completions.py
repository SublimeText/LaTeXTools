# coding=utf-8

# This is here precisely so snippet completion doesn't interfere
# with other autocompletions.
import os
import traceback
from xml.etree import ElementTree

import sublime
import sublime_plugin

from .latextools_utils.logging import logger

__all__ = ["SnippetCompletions"]

__dir = os.path.dirname(__file__)
if __dir == '.':
    __dir = os.path.join(sublime.packages_path(), 'LaTeXTools')


def _get_completions(ext):
    completions = []

    for root, dirs, files in os.walk(
            os.path.join(__dir, 'snippets')):
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
            except Exception:
                logger.error(
                    'Error occurred when trying to load snippet from {0}',
                    os.path.join(root, f)
                )
                traceback.print_exc()

    return completions


def get_biblatex_completions():
    return _get_completions('.biblatex-snippet')


def get_bibtex_completions():
    return _get_completions('.bibtex-snippet')


class SnippetCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        pt = locations[0]
        # do not return completions if the cursor is inside an entry
        if not view.match_selector(
            pt,
            '(text.bibtex, text.biblatex)'
            # ST3
            ' - meta.entry.braces.bibtex - meta.entry.parenthesis.bibtex'
            # ST4
            ' - meta.entry.arguments.bibtex'
        ):
            return []

        if view.match_selector(pt, 'text.biblatex'):
            return (get_biblatex_completions(), sublime.INHIBIT_WORD_COMPLETIONS)
        else:
            return (get_bibtex_completions(), sublime.INHIBIT_WORD_COMPLETIONS)
