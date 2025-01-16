import logging
import sublime

from .settings import global_settings

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_LEVEL_NAME = logging.getLevelName(DEFAULT_LOG_LEVEL)
EVENT_LEVEL = logging.INFO

logger = logging.getLogger("LaTeXTools")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt="{name} [{levelname}]: {message}", style="{"))
    logger.addHandler(handler)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    logger.propagate = False  # prevent root logger from catching this
    handler = None


def _on_settings_changed():
    cur_log_level = logger.getEffectiveLevel()
    new_log_level_name = global_settings().get("log_level", DEFAULT_LOG_LEVEL_NAME).upper()
    new_log_level = getattr(logging, new_log_level_name, DEFAULT_LOG_LEVEL)
    if new_log_level != cur_log_level:
        logger.setLevel(new_log_level)


def init_logger():
    global_settings().add_on_change(__name__, _on_settings_changed)
    _on_settings_changed()  # trigger on inital settings load, too


def shutdown_logger():
    global_settings().clear_on_change(__name__)
