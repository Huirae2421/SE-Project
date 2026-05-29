"""
code_executor.py: Python 코드 실행 및 오류 수집
"""

import subprocess
import re
import sys
import shutil
import time
from .data_models import ExecutionResult


# ──────────────────────────────────────────────
# 파이썬 실행기 결정
# ──────────────────────────────────────────────

def resolve_python() -> str:
    """사용자 코드를 실행할 파이썬 인터프리터를 찾는다.

    개발 환경에서는 현재 실행 중인 파이썬을 쓰고, exe(PyInstaller)로
    패키징된 경우에는 sys.executable 이 앱 자신을 가리키므로 시스템에
    설치된 파이썬을 PATH 에서 찾아 사용한다.
    """
    if not getattr(sys, "frozen", False):
        return sys.executable
    return shutil.which("python") or shutil.which("python3") or "python"


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

DEFAULT_TIMEOUT = 10.0

SUPPORTED_ERRORS = frozenset({
    "SyntaxError",
    "NameError",
    "TypeError",
    "IndentationError",
    "IndexError",
    "ValueError",
    "AttributeError",
    "KeyError",
    "ZeroDivisionError",
    "ModuleNotFoundError",
    "UnboundLocalError",
    "RecursionError",
})


# ──────────────────────────────────────────────
# CodeExecutor
# ──────────────────────────────────────────────

class CodeExecutor:

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.python_cmd = resolve_python()

    def execute(self, file_path: str) -> ExecutionResult:
        start = time.perf_counter()

        try:
            proc = subprocess.run(
                [self.python_cmd, file_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout
            )
            elapsed = time.perf_counter() - start

            error_type = self._parse_error_type(proc.stderr)
            error_message = self._parse_error_message(proc.stderr)

            return ExecutionResult(
                file_path=file_path,
                stdout=proc.stdout,
                stderr=proc.stderr,
                error_type=error_type,
                error_message=error_message,
                elapsed_seconds=round(elapsed, 4),
                timed_out=False,
                success=(proc.returncode == 0)
            )

        except subprocess.TimeoutExpired:
            elapsed = time.perf_counter() - start
            return ExecutionResult(
                file_path=file_path,
                stderr="TimeoutExpired: execution time limit exceeded",
                error_type="TimeoutExpired",
                error_message="execution time limit exceeded",
                elapsed_seconds=round(elapsed, 4),
                timed_out=True,
                success=False
            )

        except Exception as e:
            elapsed = time.perf_counter() - start
            return ExecutionResult(
                file_path=file_path,
                stderr=str(e),
                error_type="UnknownError",
                error_message=str(e),
                elapsed_seconds=round(elapsed, 4),
                timed_out=False,
                success=False
            )

    # ──────────────────────────────────────────────
    # 오류 파싱
    # ──────────────────────────────────────────────

    def _parse_error_type(self, stderr: str) -> str | None:
        if not stderr:
            return None

        pattern = r"(" + "|".join(SUPPORTED_ERRORS) + r")"
        match = re.search(pattern, stderr)

        if match:
            return match.group(1)

        generic = re.search(r"(\w+Error|\w+Exception)", stderr)
        if generic:
            return "UnknownError"

        return None

    def _parse_error_message(self, stderr: str) -> str:
        if not stderr:
            return ""

        lines = stderr.strip().splitlines()
        for line in reversed(lines):
            if line.strip():
                return line.strip()

        return ""