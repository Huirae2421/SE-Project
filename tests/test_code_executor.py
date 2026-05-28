"""
test_code_executor.py: CodeExecutor 단위 테스트
"""

import os
import pytest
from src.models.code_executor import CodeExecutor

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def fixture_path(filename: str) -> str:
    return os.path.abspath(os.path.join(FIXTURES, filename))


@pytest.fixture
def executor():
    return CodeExecutor(timeout=10.0)


# ──────────────────────────────────────────────
# 정상 실행 테스트
# ──────────────────────────────────────────────

class TestCleanExecution:

    def test_success_flag(self, executor):
        result = executor.execute(fixture_path("clean_code.py"))
        assert result.success is True

    def test_no_error_type(self, executor):
        result = executor.execute(fixture_path("clean_code.py"))
        assert result.error_type is None

    def test_no_stderr(self, executor):
        result = executor.execute(fixture_path("clean_code.py"))
        assert result.stderr == ""

    def test_elapsed_seconds_positive(self, executor):
        result = executor.execute(fixture_path("clean_code.py"))
        assert result.elapsed_seconds > 0

    def test_not_timed_out(self, executor):
        result = executor.execute(fixture_path("clean_code.py"))
        assert result.timed_out is False

    def test_stdout_not_empty(self, executor):
        result = executor.execute(fixture_path("clean_code.py"))
        assert len(result.stdout) > 0


# ──────────────────────────────────────────────
# 오류 유형 감지 테스트
# ──────────────────────────────────────────────

class TestErrorDetection:

    def test_syntax_error(self, executor):
        result = executor.execute(fixture_path("syntax_error.py"))
        assert result.error_type == "SyntaxError"
        assert result.success is False

    def test_name_error(self, executor):
        result = executor.execute(fixture_path("name_error.py"))
        assert result.error_type == "NameError"
        assert result.success is False

    def test_type_error(self, executor):
        result = executor.execute(fixture_path("type_error.py"))
        assert result.error_type == "TypeError"
        assert result.success is False

    def test_index_error(self, executor):
        result = executor.execute(fixture_path("index_error.py"))
        assert result.error_type == "IndexError"
        assert result.success is False

    def test_value_error(self, executor):
        result = executor.execute(fixture_path("value_error.py"))
        assert result.error_type == "ValueError"
        assert result.success is False

    def test_indentation_error(self, executor):
        result = executor.execute(fixture_path("indentation_error.py"))
        assert result.error_type in ("IndentationError", "SyntaxError")
        assert result.success is False


# ──────────────────────────────────────────────
# 오류 메시지 테스트
# ──────────────────────────────────────────────

class TestErrorMessage:

    def test_error_message_not_empty(self, executor):
        result = executor.execute(fixture_path("name_error.py"))
        assert result.error_message != ""

    def test_stderr_not_empty_on_error(self, executor):
        result = executor.execute(fixture_path("type_error.py"))
        assert result.stderr != ""

    def test_file_path_stored(self, executor):
        path = fixture_path("clean_code.py")
        result = executor.execute(path)
        assert result.file_path == path


# ──────────────────────────────────────────────
# 오류 그룹 테스트
# ──────────────────────────────────────────────

class TestErrorGroup:

    def test_name_error_group(self, executor):
        group = executor.get_error_group("NameError")
        assert group == "undefined variable group"

    def test_indentation_error_group(self, executor):
        group = executor.get_error_group("IndentationError")
        assert group == "indentation error group"

    def test_type_error_group(self, executor):
        group = executor.get_error_group("TypeError")
        assert group == "type mismatch group"

    def test_syntax_error_group(self, executor):
        group = executor.get_error_group("SyntaxError")
        assert group == "syntax error group"

    def test_index_error_group(self, executor):
        group = executor.get_error_group("IndexError")
        assert group == "index error group"

    def test_value_error_group(self, executor):
        group = executor.get_error_group("ValueError")
        assert group == "value error group"

    def test_unknown_error_group(self, executor):
        group = executor.get_error_group("UnknownError")
        assert group == "other error group"


# ──────────────────────────────────────────────
# 타임아웃 테스트
# ──────────────────────────────────────────────

class TestTimeout:

    def test_timeout_flag(self, tmp_path):
        infinite_loop = tmp_path / "infinite.py"
        infinite_loop.write_text("while True: pass")
        executor = CodeExecutor(timeout=1.0)
        result = executor.execute(str(infinite_loop))
        assert result.timed_out is True
        assert result.success is False

    def test_timeout_error_type(self, tmp_path):
        infinite_loop = tmp_path / "infinite.py"
        infinite_loop.write_text("while True: pass")
        executor = CodeExecutor(timeout=1.0)
        result = executor.execute(str(infinite_loop))
        assert result.error_type == "TimeoutExpired"