import os
import tempfile

from h.utils.logger import get_logger

logger = get_logger(__name__)


def create_temp_file(
    filename: str,
    content: str,
) -> str:
    """임시 파일 생성.
    Args:
        filename: 파일 이름
        content: 파일 내용

    Returns:
        생성된 임시 파일 경로
    """
    tempfile_path = os.path.join(tempfile.gettempdir(), filename)

    with open(tempfile_path, "w", encoding="utf-8") as temp:
        temp.write(content)

    return tempfile_path
