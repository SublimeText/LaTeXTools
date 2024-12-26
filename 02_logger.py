import logging

import sublime

__all__ = ["plugin_loaded", "plugin_unloaded"]

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_LEVEL_NAME = logging.getLevelName(DEFAULT_LOG_LEVEL)
EVENT_LEVEL = logging.INFO

logger = logging.getLogger("LaTeXTools")
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt="{name} [{levelname}]: {message}", style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(DEFAULT_LOG_LEVEL)
logger.propagate = False  # prevent root logger from catching this


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
