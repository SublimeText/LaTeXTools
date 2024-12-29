import collections
from functools import partial
import threading
import traceback

import sublime
import sublime_plugin

from .latex_cite_completions import find_bib_files
from .latex_cite_completions import run_plugin_command
from .latextools_utils import analysis
from .latextools_utils.activity_indicator import ActivityIndicator
from .latextools_utils.cache import LocalCache
from .latextools_utils.logging import logger
from .latextools_utils.settings import get_setting
from .latextools_utils.tex_directives import get_tex_root

__all__ = [
    "LatextoolsCacheUpdateListener",
    "LatextoolsAnalysisUpdateCommand",
    "LatextoolsBibcacheUpdateCommand",
]

# stores a cache instance per open LaTeX view
# note that cache instances share state
_TEX_CACHES = {}


def get_cache(view):
    vid = view.id()
    cache = _TEX_CACHES.get(vid)
    if cache is None:
        tex_root = get_tex_root(view)
        if not tex_root:
            return

        cache = _TEX_CACHES[vid] = LocalCache(tex_root)

    return cache


def remove_cache(view):
    _TEX_CACHES.pop(view.id(), None)


def update_cache(cache, doc, bib):
    def worker():
        with ActivityIndicator("Updating LaTeXTools cache") as activity:
            try:
                cache.invalidate("bib_files")
                if doc:
                    logger.debug("Updating analysis cache for %s", cache.tex_root)
                    cache.set("analysis", analysis.analyze_document(cache.tex_root))
                if bib:
                    logger.debug("Updating bibliography cache for %s", cache.tex_root)
                    run_plugin_command(
                        "get_entries", *(find_bib_files(cache.tex_root) or [])
                    )
            except Exception:
                traceback.print_exc()
            else:
                activity.finish("LaTeXTools cache updated")

    if cache and (doc or bib):
        threading.Thread(target=worker).start()


class LatextoolsCacheUpdateListener(sublime_plugin.EventListener):
    def on_load(self, view):
        if not view.match_selector(0, "text.tex.latex"):
            return

        update_doc = get_setting("cache.analysis.update_on_load", True, view)
        update_bib = get_setting("cache.bibliography.update_on_load", True, view)
        if not update_doc and not update_bib:
            return

        cache = get_cache(view)
        if not cache:
            return

        # because cache state is shared amongst all documents sharing a tex
        # root, this ensure we only load the analysis ONCE in the on_load
        # event
        update_cache(
            cache,
            update_doc and not cache.has("analysis"),
            update_bib and not cache.has("bib_files"),
        )

    def on_close(self, view):
        remove_cache(view)

    def on_post_save(self, view):
        if not view.match_selector(0, "text.tex.latex"):
            return

        if not view.is_primary():
            return

        update_doc = get_setting("cache.analysis.update_on_save", True, view)
        update_bib = get_setting("cache.bibliography.update_on_save", True, view)
        if not update_doc and not update_bib:
            return

        update_cache(get_cache(view), update_doc, update_bib)


class LatextoolsAnalysisUpdateCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self):
        view = self.window.active_view()
        if not view:
            return

        if not view.match_selector(0, "text.tex.latex"):
            return

        update_cache(get_cache(view), True, False)


class LatextoolsBibcacheUpdateCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self):
        view = self.window.active_view()
        if not view:
            return

        if not view.match_selector(0, "text.tex.latex"):
            return

        update_cache(get_cache(view), False, True)
