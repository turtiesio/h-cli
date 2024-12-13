"""로깅 유틸리티."""

from typing import Optional

import structlog

DLogger = structlog.stdlib.BoundLogger

logger: DLogger = structlog.get_logger()


def get_logger(name: Optional[str] = None) -> DLogger:
    """로거 인스턴스 생성.

    Args:
        name: 로거 이름

    Returns:
        structlog.BoundLogger: 로거 인스턴스
    """
    return logger.bind(name=name)
