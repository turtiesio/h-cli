"""Structured logging setup for h-cli."""

import logging
import sys
from typing import Any, Optional, cast

import structlog
from structlog.stdlib import BoundLogger


def setup_logger(name: str = "h-cli", level: Optional[int] = None) -> BoundLogger:
    """Set up structured logging for the application.

    Args:
        name: The name of the logger.
        level: Optional logging level. Defaults to INFO if not specified.

    Returns:
        A configured structlog logger instance.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level or logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return cast(BoundLogger, structlog.get_logger(name))
