import logging

__all__ = [
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_LEVEL_NAME",
    "EVENT_LEVEL",
    "handler",
    "logger"
]

DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_LOG_LEVEL_NAME = logging.getLevelName(DEFAULT_LOG_LEVEL)
EVENT_LEVEL = logging.INFO

logger = logging.getLogger("LaTeXTools")
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt="{name} [{levelname}]: {message}", style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(DEFAULT_LOG_LEVEL)
logger.propagate = False  # prevent root logger from catching this
