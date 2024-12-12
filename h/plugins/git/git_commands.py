"""Git 명령어 실행을 위한 모듈."""

import subprocess
from typing import List

from h.plugins.git.exceptions import GitError


class GitCommands:
    """Git 명령어 실행을 위한 클래스."""

    def __init__(self, logger):
        """초기화.

        Args:
            logger: 로거 인스턴스
        """
        self.logger = logger

    def run_command(self, args: List[str], check: bool = True) -> str:
        """Git 명령어 실행.

        Args:
            args: 실행할 git 명령어와 인자들
            check: 명령어 실행 결과 체크 여부

        Returns:
            명령어 실행 결과

        Raises:
            GitError: git 명령어 실행 실패시
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                check=check,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"git.{args[0]}.failed", error=str(e))
            raise GitError(f"git {args[0]} 명령어 실행 중 오류가 발생했습니다.")

    def check_changes(self) -> None:
        """변경사항과 스테이지된 파일 확인.

        Raises:
            GitError: 변경사항이 없거나 스테이지된 파일이 없을 때
        """
        # 변경사항 확인 (git diff)
        changes = self.run_command(["diff"])

        # 스테이지된 변경사항 확인 (git diff --staged)
        staged = self.run_command(["diff", "--staged"])

        # 변경사항이 없으면 에러
        if not changes and not staged:
            raise GitError("변경사항이 없습니다.")

        # 스테이지된 파일이 없으면 에러
        if not staged:
            raise GitError(
                "스테이지된 변경사항이 없습니다. 'git add' 명령어로 변경사항을 먼저 스테이지해주세요."
            )

    def get_status(self) -> str:
        """Git status 가져오기."""
        return self.run_command(["status"])

    def get_staged_diff(self) -> str:
        """스테이지된 변경사항 가져오기."""
        return self.run_command(["diff", "--staged"])

    def get_recent_logs(self, count: int = 5) -> List[str]:
        """최근 커밋 로그 가져오기.

        Args:
            count: 가져올 로그 개수

        Returns:
            최근 커밋 로그 목록
        """
        logs = self.run_command(
            ["log", f"-{count}", "--oneline", "--no-merges"]
        ).splitlines()
        return logs if logs else ["No commit history"]

    def get_directory_tree(self, depth: int = 3) -> str:
        """디렉토리 트리 가져오기.

        Args:
            depth: 트리 깊이

        Returns:
            디렉토리 트리 문자열
        """
        try:
            return self.run_command(["ls-tree", "--full-tree", "-r", "HEAD", "--name-only"])
        except GitError:
            return "Could not generate directory tree"
