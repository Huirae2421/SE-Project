"""
test_ast_analyzer.py: ASTAnalyzer 단위 테스트
"""

import os
import pytest
from src.models.ast_analyzer import ASTAnalyzer

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def fixture_path(filename: str) -> str:
    return os.path.abspath(os.path.join(FIXTURES, filename))


@pytest.fixture
def analyzer():
    return ASTAnalyzer()


# ──────────────────────────────────────────────
# 정상 파싱 테스트
# ──────────────────────────────────────────────

class TestValidParsing:

    def test_valid_flag(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.valid is True

    def test_line_count_positive(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.line_count > 0

    def test_function_count(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.function_count >= 1

    def test_mccabe_score_non_negative(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.mccabe_score >= 0

    def test_clap_score_non_negative(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.clap_components.score >= 0

    def test_feedback_message_not_empty(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.feedback_message != ""


# ──────────────────────────────────────────────
# 문법 오류 파일 테스트
# ──────────────────────────────────────────────

class TestInvalidParsing:

    def test_syntax_error_invalid_flag(self, analyzer):
        result = analyzer.analyze(fixture_path("syntax_error.py"))
        assert result.valid is False

    def test_syntax_error_feedback(self, analyzer):
        result = analyzer.analyze(fixture_path("syntax_error.py"))
        assert result.feedback_message != ""

    def test_indentation_error_invalid_flag(self, analyzer):
        result = analyzer.analyze(fixture_path("indentation_error.py"))
        assert result.valid is False


# ──────────────────────────────────────────────
# 복잡도 분석 테스트
# ──────────────────────────────────────────────

class TestComplexityAnalysis:

    def test_deep_nesting_depth(self, analyzer):
        result = analyzer.analyze(fixture_path("deep_nesting.py"))
        assert result.clap_components.nesting_depth >= 3

    def test_deep_nesting_clap_score_high(self, analyzer):
        deep = analyzer.analyze(fixture_path("deep_nesting.py"))
        clean = analyzer.analyze(fixture_path("clean_code.py"))
        assert deep.clap_components.score > clean.clap_components.score

    def test_deep_nesting_mccabe_high(self, analyzer):
        deep = analyzer.analyze(fixture_path("deep_nesting.py"))
        clean = analyzer.analyze(fixture_path("clean_code.py"))
        assert deep.mccabe_score > clean.mccabe_score

    def test_long_function_length(self, analyzer):
        result = analyzer.analyze(fixture_path("long_function.py"))
        assert result.clap_components.function_length > 20

    def test_clean_code_low_complexity(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.clap_components.nesting_depth <= 3


# ──────────────────────────────────────────────
# McCabe 레이블 테스트
# ──────────────────────────────────────────────

class TestMcCabeLabel:

    def test_clean_code_simple_label(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.mccabe_label == "simple"

    def test_deep_nesting_label_not_simple(self, analyzer):
        result = analyzer.analyze(fixture_path("deep_nesting.py"))
        assert result.mccabe_label in ("moderate", "complex")


# ──────────────────────────────────────────────
# 피드백 메시지 테스트
# ──────────────────────────────────────────────

class TestFeedbackMessage:

    def test_deep_nesting_feedback_contains_keyword(self, analyzer):
        result = analyzer.analyze(fixture_path("deep_nesting.py"))
        assert "nesting" in result.feedback_message or "complex" in result.feedback_message

    def test_long_function_feedback_contains_keyword(self, analyzer):
        result = analyzer.analyze(fixture_path("long_function.py"))
        assert "function" in result.feedback_message or "splitting" in result.feedback_message

    def test_clean_code_positive_feedback(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert "good" in result.feedback_message


# ──────────────────────────────────────────────
# CLAP 컴포넌트 테스트
# ──────────────────────────────────────────────

class TestClapComponents:

    def test_branch_count_non_negative(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.clap_components.branch_count >= 0

    def test_loop_count_non_negative(self, analyzer):
        result = analyzer.analyze(fixture_path("clean_code.py"))
        assert result.clap_components.loop_count >= 0

    def test_deep_nesting_has_loops(self, analyzer):
        result = analyzer.analyze(fixture_path("deep_nesting.py"))
        assert result.clap_components.loop_count > 0

    def test_deep_nesting_has_branches(self, analyzer):
        result = analyzer.analyze(fixture_path("deep_nesting.py"))
        assert result.clap_components.branch_count > 0