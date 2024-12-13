"""로깅 유틸리티."""
import structlog
from typing import Optional


def get_logger(name: Optional[str] = None):
    """로거 인스턴스 생성.
    
    Args:
        name: 로거 이름
        
    Returns:
        structlog.BoundLogger: 로거 인스턴스
    """
    return structlog.get_logger(name)
