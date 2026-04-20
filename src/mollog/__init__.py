"""mollog — structured logging for molcrafts."""

from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

from mollog._context import Context
from mollog._file_handler import FileHandler, RotatingFileHandler, TimedRotatingFileHandler
from mollog._filter import Filter, LevelFilter
from mollog._formatter import Formatter, JSONFormatter, TextFormatter
from mollog._handler import Handler, NullHandler, StreamHandler
from mollog._level import Level
from mollog._logger import Logger
from mollog._manager import LoggerManager, configure, get_logger, shutdown
from mollog._queue import QueueHandler, QueueListener
from mollog._record import LogRecord
from mollog._rich import RichHandler

if TYPE_CHECKING:  # pragma: no cover
    from mollog._logfire import configure_logfire

try:
    __version__ = version("mollog")
except PackageNotFoundError:
    __version__ = "0+unknown"


def __getattr__(name: str) -> Any:
    if name == "configure_logfire":
        from mollog._logfire import configure_logfire

        return configure_logfire
    raise AttributeError(f"module 'mollog' has no attribute {name!r}")


__all__ = [
    "__version__",
    "Context",
    "Level",
    "LogRecord",
    "Formatter",
    "TextFormatter",
    "JSONFormatter",
    "Filter",
    "LevelFilter",
    "Handler",
    "StreamHandler",
    "NullHandler",
    "FileHandler",
    "RotatingFileHandler",
    "TimedRotatingFileHandler",
    "QueueHandler",
    "QueueListener",
    "Logger",
    "LoggerManager",
    "RichHandler",
    "configure",
    "configure_logfire",
    "get_logger",
    "shutdown",
]
