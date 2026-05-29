"""
test_study_coach.py: StudyCoach 약점 분석 / AI 질문 생성 테스트
"""

import pytest

from src.models.study_coach import StudyCoach, WeaknessItem
from src.models.data_models import (
    AnalysisSession, ExecutionResult, ASTResult, ClapComponents, ErrorRecord,
)


def make_session(error_type=None, timestamp="2026-05-29T10:00:00"):
    rec = None
    if error_type:
        rec = ErrorRecord(error_type=error_type, error_message="m", file_path="f.py")
    return AnalysisSession(
        file_path="f.py", timestamp=timestamp,
        execution_result=ExecutionResult(file_path="f.py", success=(error_type is None)),
        ast_result=ASTResult(file_path="f.py", clap_components=ClapComponents()),
        error_record=rec,
    )


@pytest.fixture
def coach():
    return StudyCoach()


# ──────────────────────────────────────────────
# 약점 분석
# ──────────────────────────────────────────────

class TestWeaknessAnalysis:

    def test_no_errors_returns_empty(self, coach):
        sessions = [make_session() for _ in range(3)]
        assert coach.analyze_weaknesses(sessions) == []

    def test_most_frequent_weakness_first(self, coach):
        sessions = [
            make_session("NameError"),
            make_session("NameError"),
            make_session("TypeError"),
        ]
        weaknesses = coach.analyze_weaknesses(sessions)
        assert weaknesses[0].error_type == "NameError"
        assert weaknesses[0].count == 2

    def test_concept_is_filled(self, coach):
        sessions = [make_session("NameError")]
        weaknesses = coach.analyze_weaknesses(sessions)
        assert weaknesses[0].concept == "변수 정의와 스코프"

    def test_respects_limit(self, coach):
        sessions = [
            make_session("NameError"), make_session("TypeError"),
            make_session("IndexError"), make_session("KeyError"),
        ]
        assert len(coach.analyze_weaknesses(sessions, limit=2)) == 2

    def test_window_filters_old_sessions(self, coach):
        sessions = [
            make_session("NameError", "2026-05-29T10:00:00"),
            make_session("TypeError", "2026-05-01T10:00:00"),  # 오래됨(7일 밖)
        ]
        weaknesses = coach.analyze_weaknesses(sessions, days=7)
        types = [w.error_type for w in weaknesses]
        assert "NameError" in types
        assert "TypeError" not in types


# ──────────────────────────────────────────────
# AI 질문 생성
# ──────────────────────────────────────────────

class TestQuestionGeneration:

    def test_empty_weaknesses_no_questions(self, coach):
        assert coach.generate_questions([]) == []

    def test_one_question_per_weakness(self, coach):
        weaknesses = [WeaknessItem("NameError", 3, "변수 정의와 스코프")]
        questions = coach.generate_questions(weaknesses)
        # 약점 1개면 개별 질문 1개 (종합 질문은 2개 이상일 때만)
        assert len(questions) == 1
        assert "변수 정의와 스코프" in questions[0]

    def test_comprehensive_question_added_for_multiple(self, coach):
        weaknesses = [
            WeaknessItem("NameError", 3, "변수 정의와 스코프"),
            WeaknessItem("TypeError", 2, "자료형과 형 변환"),
        ]
        questions = coach.generate_questions(weaknesses)
        # 개별 2개 + 종합 1개
        assert len(questions) == 3
        # 종합 질문은 모든 개념을 포괄해야 한다
        assert "변수 정의와 스코프" in questions[-1]
        assert "자료형과 형 변환" in questions[-1]

    def test_questions_are_non_empty_strings(self, coach):
        weaknesses = [WeaknessItem("KeyError", 1, "딕셔너리 키 접근")]
        for q in coach.generate_questions(weaknesses):
            assert isinstance(q, str) and len(q) > 0
