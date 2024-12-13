"""로깅 유틸리티."""

from typing import Optional

import structlog


def get_logger(name: Optional[str] = None):
    """로거 인스턴스 생성.

    Args:
        name: 로거 이름

    Returns:
        structlog.BoundLogger: 로거 인스턴스
    """
    return structlog.get_logger(name)
