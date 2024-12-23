import logging

import sublime

from .latextools_utils.logger import logger
from .latextools_utils.logger import handler
from .latextools_utils.logger import DEFAULT_LOG_LEVEL
from .latextools_utils.logger import DEFAULT_LOG_LEVEL_NAME
from .latextools_utils.logger import EVENT_LEVEL

__all__ = ["plugin_loaded", "plugin_unloaded"]


def _settings():
    return sublime.load_settings("LaTeXTools.sublime-settings")


def plugin_loaded():
    def on_change():
        cur_log_level = logger.getEffectiveLevel()
        new_log_level_name = _settings().get('log_level', DEFAULT_LOG_LEVEL_NAME).upper()
        new_log_level = getattr(logging, new_log_level_name, DEFAULT_LOG_LEVEL)

        if new_log_level != cur_log_level:
            logger.setLevel(new_log_level)

    _settings().add_on_change(__name__, on_change)
    on_change()  # trigger on inital settings load, too


def plugin_unloaded():
    _settings().clear_on_change(__name__)
    logger.removeHandler(handler)
