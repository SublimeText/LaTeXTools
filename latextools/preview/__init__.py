from inspect import currentframe

import sublime_plugin

from ..utils.decorators import debounce

from .preview_image import ImagePreviewHoverListener
from .preview_image import ImagePreviewPhantomProvider
from .preview_math import MathPreviewPhantomProvider

__all__ = ["ImagePreviewHoverListener", "PreviewPhantomListener"]


class PreviewPhantomListener(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        """
        Constructs a new math preview listener instance.

        Called if `is_applicable()` returned true but no listener instance exists.

        :param view:
            The view to listen events for
        """
        super().__init__(view)
        self.image_provider = ImagePreviewPhantomProvider(view)
        self.math_provider = MathPreviewPhantomProvider(view)

    def __del__(self):
        # unsubscribe to enable garbage collection of provider instances
        self.image_provider.unsubscribe()
        self.math_provider.unsubscribe()

    @classmethod
    def is_applicable(cls, settings):
        try:
            view = currentframe().f_back.f_locals["view"]
            return len(view.find_by_selector("text.tex.latex")) > 0
        except KeyError:
            syntax = settings.get("syntax")
            return syntax == "Packages/LaTeX/LaTeX.sublime-syntax"

    @classmethod
    def applies_to_primary_view_only(cls):
        # TODO: handle scopes individually for split views in "selected" mode
        return True

    @debounce(600)
    def on_modified(self):
        # Preview all images, update modified
        if self.image_provider.mode == "all":
            self.image_provider.update_phantoms()
        # Preview all environments, update modified
        if self.math_provider.mode == "all":
            self.math_provider.update_phantoms()

    @debounce(600)
    def on_selection_modified(self):
        # Preview selected images
        if self.image_provider.mode == "selected" or not self.image_provider.phantoms:
            self.image_provider.update_phantoms()
        # Preview selected math equations
        if self.math_provider.mode == "selected" or not self.math_provider.phantoms:
            self.math_provider.update_phantoms()
