"""
test_error_analyzer.py: ErrorAnalyzer 단위 테스트
"""

import pytest
from src.models.error_analyzer import ErrorAnalyzer
from src.models.data_models import ExecutionResult, ErrorRecord


@pytest.fixture
def analyzer():
    return ErrorAnalyzer()


def make_result(error_type=None, success=False, file_path="test.py"):
    return ExecutionResult(
        file_path=file_path,
        error_type=error_type,
        error_message=f"{error_type}: test error" if error_type else "",
        success=success
    )


# ──────────────────────────────────────────────
# classify 테스트
# ──────────────────────────────────────────────

class TestClassify:

    def test_success_returns_none(self, analyzer):
        result = make_result(success=True)
        assert analyzer.classify(result) is None

    def test_no_error_type_returns_none(self, analyzer):
        result = make_result(error_type=None, success=False)
        assert analyzer.classify(result) is None

    def test_name_error_returns_record(self, analyzer):
        result = make_result(error_type="NameError")
        record = analyzer.classify(result)
        assert isinstance(record, ErrorRecord)

    def test_error_type_preserved(self, analyzer):
        result = make_result(error_type="TypeError")
        record = analyzer.classify(result)
        assert record.error_type == "TypeError"

    def test_file_path_preserved(self, analyzer):
        result = make_result(error_type="NameError", file_path="myfile.py")
        record = analyzer.classify(result)
        assert record.file_path == "myfile.py"

    def test_timestamp_set(self, analyzer):
        result = make_result(error_type="NameError")
        record = analyzer.classify(result)
        assert record.timestamp != ""


# ──────────────────────────────────────────────
# 오류 그룹화 테스트
# ──────────────────────────────────────────────

class TestErrorGroup:

    def test_name_error_group(self, analyzer):
        result = make_result(error_type="NameError")
        record = analyzer.classify(result)
        assert record.error_group == "undefined variable group"

    def test_indentation_error_group(self, analyzer):
        result = make_result(error_type="IndentationError")
        record = analyzer.classify(result)
        assert record.error_group == "indentation error group"

    def test_type_error_group(self, analyzer):
        result = make_result(error_type="TypeError")
        record = analyzer.classify(result)
        assert record.error_group == "type mismatch group"

    def test_syntax_error_group(self, analyzer):
        result = make_result(error_type="SyntaxError")
        record = analyzer.classify(result)
        assert record.error_group == "syntax error group"

    def test_index_error_group(self, analyzer):
        result = make_result(error_type="IndexError")
        record = analyzer.classify(result)
        assert record.error_group == "index error group"

    def test_value_error_group(self, analyzer):
        result = make_result(error_type="ValueError")
        record = analyzer.classify(result)
        assert record.error_group == "value error group"


# ──────────────────────────────────────────────
# 오류 요약 통계 테스트
# ──────────────────────────────────────────────

class TestErrorSummary:

    def make_records(self, types):
        return [
            ErrorRecord(
                error_type=t,
                error_message=f"{t}: msg",
                file_path="test.py",
                error_group=""
            )
            for t in types
        ]

    def test_empty_records(self, analyzer):
        summary = analyzer.get_error_summary([])
        assert summary == {}

    def test_single_error_count(self, analyzer):
        records = self.make_records(["NameError"])
        summary = analyzer.get_error_summary(records)
        assert summary["NameError"] == 1

    def test_multiple_same_error(self, analyzer):
        records = self.make_records(["NameError", "NameError", "NameError"])
        summary = analyzer.get_error_summary(records)
        assert summary["NameError"] == 3

    def test_mixed_errors(self, analyzer):
        records = self.make_records(["NameError", "TypeError", "NameError"])
        summary = analyzer.get_error_summary(records)
        assert summary["NameError"] == 2
        assert summary["TypeError"] == 1

    def test_sorted_by_count(self, analyzer):
        records = self.make_records(["TypeError", "NameError", "NameError"])
        summary = analyzer.get_error_summary(records)
        keys = list(summary.keys())
        assert keys[0] == "NameError"


# ──────────────────────────────────────────────
# 가장 많은 오류 테스트
# ──────────────────────────────────────────────

class TestMostFrequent:

    def make_records(self, types):
        return [
            ErrorRecord(
                error_type=t,
                error_message="",
                file_path="test.py",
                error_group=""
            )
            for t in types
        ]

    def test_empty_returns_none(self, analyzer):
        result = analyzer.get_most_frequent([])
        assert result == "none"

    def test_single_error(self, analyzer):
        records = self.make_records(["NameError"])
        assert analyzer.get_most_frequent(records) == "NameError"

    def test_most_frequent(self, analyzer):
        records = self.make_records(["NameError", "TypeError", "NameError", "NameError"])
        assert analyzer.get_most_frequent(records) == "NameError"