"""
test_integration.py: 전체 파이프라인 통합 테스트
"""

import os
import time
import pytest
from src.models.code_executor import CodeExecutor
from src.models.ast_analyzer import ASTAnalyzer
from src.models.error_analyzer import ErrorAnalyzer
from src.models.difficulty_estimator import DifficultyEstimator, MIN_HISTORY
from src.models.database_manager import DatabaseManager
from src.models.visualization_engine import VisualizationEngine
from src.models.data_models import AnalysisSession, HistoricalSession

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def fixture_path(filename: str) -> str:
    return os.path.abspath(os.path.join(FIXTURES, filename))


@pytest.fixture
def pipeline(tmp_path):
    db_path = str(tmp_path / "test_clap.db")
    return {
        "executor":    CodeExecutor(),
        "analyzer":    ASTAnalyzer(),
        "error":       ErrorAnalyzer(),
        "difficulty":  DifficultyEstimator(),
        "db":          DatabaseManager(db_path=db_path),
        "viz":         VisualizationEngine(),
    }


def run_pipeline(pipeline, file_path, history=None):
    execution_result = pipeline["executor"].execute(file_path)
    ast_result = pipeline["analyzer"].analyze(file_path)
    error_record = pipeline["error"].classify(execution_result)

    if history is None:
        history = []

    difficulty_score = pipeline["difficulty"].estimate(
        history=history,
        current_error_count=1 if error_record else 0,
        current_clap_score=ast_result.clap_components.score,
        current_elapsed=execution_result.elapsed_seconds
    )

    session = AnalysisSession(
        file_path=file_path,
        execution_result=execution_result,
        ast_result=ast_result,
        error_record=error_record,
        difficulty_score=difficulty_score
    )

    session_id = pipeline["db"].save_session(session)
    session.session_id = session_id
    return session


# ──────────────────────────────────────────────
# 정상 코드 파이프라인
# ──────────────────────────────────────────────

class TestCleanCodePipeline:

    def test_session_created(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert session is not None

    def test_session_id_assigned(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert session.session_id is not None

    def test_no_error_record(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert session.error_record is None

    def test_success_flag(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert session.execution_result.success is True

    def test_ast_valid(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert session.ast_result.valid is True

    def test_session_saved_to_db(self, pipeline):
        run_pipeline(pipeline, fixture_path("clean_code.py"))
        sessions = pipeline["db"].get_sessions()
        assert len(sessions) == 1


# ──────────────────────────────────────────────
# 오류 코드 파이프라인
# ──────────────────────────────────────────────

class TestErrorCodePipeline:

    def test_name_error_pipeline(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("name_error.py"))
        assert session.error_record is not None
        assert session.error_record.error_type == "NameError"

    def test_type_error_pipeline(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("type_error.py"))
        assert session.error_record is not None
        assert session.error_record.error_type == "TypeError"

    def test_error_group_set(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("name_error.py"))
        assert session.error_record.error_group == "undefined variable group"

    def test_error_saved_to_db(self, pipeline):
        run_pipeline(pipeline, fixture_path("name_error.py"))
        counts = pipeline["db"].get_error_counts()
        assert "NameError" in counts


# ──────────────────────────────────────────────
# 복잡도 분석 파이프라인
# ──────────────────────────────────────────────

class TestComplexityPipeline:

    def test_deep_nesting_high_score(self, pipeline):
        deep = run_pipeline(pipeline, fixture_path("deep_nesting.py"))
        clean = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert deep.ast_result.clap_components.score > clean.ast_result.clap_components.score

    def test_deep_nesting_feedback(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("deep_nesting.py"))
        assert session.ast_result.feedback_message != ""


# ──────────────────────────────────────────────
# 난이도 추정 파이프라인
# ──────────────────────────────────────────────

class TestDifficultyPipeline:

    def test_pending_label_initially(self, pipeline):
        session = run_pipeline(pipeline, fixture_path("clean_code.py"))
        assert session.difficulty_score.label == "collecting data"

    def test_relative_mode_after_enough_data(self, pipeline):
        history = [
            HistoricalSession(
                session_id=i,
                timestamp=f"2025-05-{i+1:02d}T00:00:00",
                error_count=0,
                clap_score=5.0,
                mccabe_score=3.0,
                elapsed_seconds=1.0,
                difficulty_score=0.5,
                difficulty_label="normal"
            )
            for i in range(MIN_HISTORY)
        ]
        session = run_pipeline(pipeline, fixture_path("clean_code.py"), history=history)
        assert session.difficulty_score.is_relative is True


# ──────────────────────────────────────────────
# 시각화 파이프라인
# ──────────────────────────────────────────────

class TestVisualizationPipeline:

    def test_insufficient_data_flag(self, pipeline):
        for _ in range(3):
            run_pipeline(pipeline, fixture_path("clean_code.py"))
        sessions = pipeline["db"].get_sessions()
        chart_data = pipeline["viz"].build_chart_data(sessions)
        assert chart_data.has_enough_data is False

    def test_sufficient_data_flag(self, pipeline):
        for _ in range(6):
            run_pipeline(pipeline, fixture_path("clean_code.py"))
        sessions = pipeline["db"].get_sessions()
        chart_data = pipeline["viz"].build_chart_data(sessions)
        assert chart_data.has_enough_data is True

    def test_error_bar_populated(self, pipeline):
        for _ in range(6):
            run_pipeline(pipeline, fixture_path("name_error.py"))
        sessions = pipeline["db"].get_sessions()
        chart_data = pipeline["viz"].build_chart_data(sessions)
        assert "NameError" in chart_data.error_bar
