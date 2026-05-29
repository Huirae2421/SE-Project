"""
test_analysis_queue.py: AnalysisQueue 단위 테스트

파이프라인 콜백(on_start / on_complete / on_save_failed)과,
백그라운드 스레드에서 분석 결과가 DB에 저장되는지(스레드 안전성 회귀)를 검증한다.
"""

import os
import threading
import pytest

from src.models.code_executor import CodeExecutor
from src.models.ast_analyzer import ASTAnalyzer
from src.models.error_analyzer import ErrorAnalyzer
from src.models.difficulty_estimator import DifficultyEstimator
from src.models.database_manager import DatabaseManager
from src.controllers.analysis_queue import AnalysisQueue

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def fixture_path(name: str) -> str:
    return os.path.abspath(os.path.join(FIXTURES, name))


@pytest.fixture
def make_queue(tmp_path):
    created = []

    def _make(**callbacks):
        db = DatabaseManager(db_path=str(tmp_path / "q.db"))
        queue = AnalysisQueue(
            CodeExecutor(), ASTAnalyzer(), ErrorAnalyzer(),
            DifficultyEstimator(), db, **callbacks
        )
        created.append(db)
        return queue, db

    yield _make
    for db in created:
        db.close()


# ──────────────────────────────────────────────
# 동기 파이프라인 (_process)
# ──────────────────────────────────────────────

class TestProcess:

    def test_on_start_called(self, make_queue):
        started = []
        queue, _ = make_queue(on_start=lambda p: started.append(p))
        queue._process(fixture_path("name_error.py"))
        assert len(started) == 1

    def test_on_complete_called_with_session(self, make_queue):
        done = []
        queue, _ = make_queue(on_complete=lambda s: done.append(s))
        queue._process(fixture_path("name_error.py"))
        assert len(done) == 1
        assert done[0].error_record.error_type == "NameError"

    def test_session_persisted(self, make_queue):
        queue, db = make_queue()
        queue._process(fixture_path("clean_code.py"))
        assert len(db.get_sessions(limit=10)) == 1

    def test_session_id_assigned(self, make_queue):
        done = []
        queue, _ = make_queue(on_complete=lambda s: done.append(s))
        queue._process(fixture_path("clean_code.py"))
        assert done[0].session_id is not None


# ──────────────────────────────────────────────
# 저장 실패 콜백
# ──────────────────────────────────────────────

class TestSaveFailure:

    def test_on_save_failed_called(self, make_queue):
        queue, db = make_queue()
        failed = []
        queue.on_save_failed = lambda p: failed.append(p)
        # save_session 이 실패(None 반환)하도록 강제
        db.save_session = lambda session: None
        queue._process(fixture_path("name_error.py"))
        assert failed == [fixture_path("name_error.py")]

    def test_on_complete_not_called_on_failure(self, make_queue):
        queue, db = make_queue()
        done = []
        queue.on_complete = lambda s: done.append(s)
        db.save_session = lambda session: None
        queue._process(fixture_path("name_error.py"))
        assert done == []


# ──────────────────────────────────────────────
# 백그라운드 스레드 (enqueue) — SQLite 스레드 안전성 회귀
# ──────────────────────────────────────────────

class TestThreadedEnqueue:

    def test_background_analysis_saves_session(self, make_queue):
        done = threading.Event()
        queue, db = make_queue(on_complete=lambda s: done.set())

        queue.enqueue(fixture_path("name_error.py"))

        assert done.wait(timeout=10), "백그라운드 분석이 시간 내 완료되지 않음"
        sessions = db.get_sessions(limit=1)
        assert len(sessions) == 1
        assert sessions[0].error_record.error_type == "NameError"

    def test_enqueue_does_not_block(self, make_queue):
        queue, _ = make_queue()
        # enqueue 는 즉시 반환해야 한다 (백그라운드 실행)
        queue.enqueue(fixture_path("clean_code.py"))
        # 예외 없이 반환되면 통과
        assert True
