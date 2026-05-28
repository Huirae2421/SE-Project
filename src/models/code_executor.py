"""
code_executor.py: Python 코드 실행 및 오류 수집
"""

import subprocess
import re
import time
from .data_models import ExecutionResult


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
})

ERROR_GROUPS = {
    "NameError":       "undefined variable group",
    "IndentationError": "indentation error group",
    "TypeError":       "type mismatch group",
    "SyntaxError":     "syntax error group",
    "IndexError":      "index error group",
    "ValueError":      "value error group",
}


# ──────────────────────────────────────────────
# CodeExecutor
# ──────────────────────────────────────────────

class CodeExecutor:

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def execute(self, file_path: str) -> ExecutionResult:
        start = time.perf_counter()

        try:
            proc = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
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

    # ──────────────────────────────────────────────
    # 오류 그룹 반환
    # ──────────────────────────────────────────────

    def get_error_group(self, error_type: str) -> str:
        return ERROR_GROUPS.get(error_type, "other error group")