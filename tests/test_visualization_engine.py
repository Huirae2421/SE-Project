"""
test_visualization_engine.py: VisualizationEngine 단위 테스트

설계 문서 속성 11(차트 데이터 형식 불변 속성)과 각 차트 생성 메서드를 검증한다.
"""

import pytest

from src.models.visualization_engine import VisualizationEngine, MIN_SESSIONS
from src.models.data_models import (
    AnalysisSession, ExecutionResult, ASTResult, ClapComponents,
    ErrorRecord, DifficultyScore,
)


def make_session(error_type=None, clap=5.0, mccabe=3.0, elapsed=1.0,
                 difficulty=0.5, timestamp="2026-05-20T10:00:00"):
    rec = None
    if error_type:
        rec = ErrorRecord(error_type=error_type, error_message="m", file_path="f.py")
    return AnalysisSession(
        file_path="f.py", timestamp=timestamp,
        execution_result=ExecutionResult(
            file_path="f.py", elapsed_seconds=elapsed, success=(error_type is None)
        ),
        ast_result=ASTResult(
            file_path="f.py",
            clap_components=ClapComponents(score=clap),
            mccabe_score=mccabe,
        ),
        error_record=rec,
        difficulty_score=DifficultyScore(score=difficulty, label="average"),
    )


@pytest.fixture
def engine():
    return VisualizationEngine()


def many_sessions(n=6, **kwargs):
    return [
        make_session(timestamp=f"2026-05-{i + 1:02d}T10:00:00", **kwargs)
        for i in range(n)
    ]


# ──────────────────────────────────────────────
# 데이터 부족 처리
# ──────────────────────────────────────────────

class TestInsufficientData:

    def test_empty_not_enough(self, engine):
        assert engine.build_chart_data([]).has_enough_data is False

    def test_below_min_not_enough(self, engine):
        data = engine.build_chart_data(many_sessions(MIN_SESSIONS - 1))
        assert data.has_enough_data is False

    def test_at_min_enough(self, engine):
        data = engine.build_chart_data(many_sessions(MIN_SESSIONS))
        assert data.has_enough_data is True


# ──────────────────────────────────────────────
# 속성 11: 차트 데이터 형식 불변 속성
# ──────────────────────────────────────────────

class TestChartDataInvariants:

    @pytest.fixture
    def data(self, engine):
        sessions = [
            make_session(error_type="NameError", clap=8.0, mccabe=12.0, difficulty=0.3),
            make_session(error_type="TypeError", clap=4.0, mccabe=2.0, difficulty=0.6),
            make_session(clap=6.0, mccabe=5.0, difficulty=0.5),
            make_session(error_type="NameError", clap=10.0, mccabe=21.0, difficulty=0.8),
            make_session(clap=3.0, mccabe=1.0, difficulty=0.2),
            make_session(error_type="IndexError", clap=7.0, mccabe=9.0, difficulty=0.4),
        ]
        return engine.build_chart_data(sessions)

    def test_error_bar_non_negative(self, data):
        assert all(v >= 0 for v in data.error_bar.values())

    def test_activity_counts_non_negative(self, data):
        assert all(d["count"] >= 0 for d in data.activity_line)

    def test_mccabe_scores_non_negative(self, data):
        assert all(d["score"] >= 0.0 for d in data.mccabe_line)

    def test_clap_scores_non_negative(self, data):
        assert all(d["score"] >= 0.0 for d in data.clap_line)

    def test_difficulty_in_range(self, data):
        assert all(0.0 <= d["score"] <= 1.0 for d in data.difficulty_area)

    def test_error_pie_ratios_sum_to_one(self, data):
        if data.error_pie:
            assert sum(data.error_pie.values()) == pytest.approx(1.0, abs=1e-3)


# ──────────────────────────────────────────────
# 개별 차트 데이터
# ──────────────────────────────────────────────

class TestChartContents:

    def test_error_bar_counts(self, engine):
        sessions = (
            [make_session(error_type="NameError") for _ in range(3)]
            + [make_session(error_type="TypeError") for _ in range(2)]
            + [make_session() for _ in range(1)]
        )
        data = engine.build_chart_data(sessions)
        assert data.error_bar.get("NameError") == 3
        assert data.error_bar.get("TypeError") == 2

    def test_clap_average_computed(self, engine):
        sessions = many_sessions(6, clap=5.0)
        data = engine.build_chart_data(sessions)
        assert data.clap_average == pytest.approx(5.0)

    def test_activity_line_groups_by_date(self, engine):
        sessions = [make_session(timestamp="2026-05-20T10:00:00") for _ in range(6)]
        data = engine.build_chart_data(sessions)
        # 모두 같은 날짜 → 활동 라인 1개 지점, count 6
        assert len(data.activity_line) == 1
        assert data.activity_line[0]["count"] == 6

    def test_no_errors_empty_pie(self, engine):
        data = engine.build_chart_data(many_sessions(6))
        assert data.error_pie == {}

    def test_lines_length_matches_sessions(self, engine):
        data = engine.build_chart_data(many_sessions(6))
        assert len(data.mccabe_line) == 6
        assert len(data.clap_line) == 6
        assert len(data.difficulty_area) == 6
