"""
test_app_controller.py: AppController 단위 테스트

폴더 등록/해제, 대시보드/차트/리포트 조회, 최근 오류, 언어 설정 등
컨트롤러가 Model을 올바르게 조합하는지 검증한다. (FileWatcher/Queue는 페이크)
"""

import pytest

from src.controllers.app_controller import AppController
from src.models.database_manager import DatabaseManager
from src.models.visualization_engine import VisualizationEngine
from src.models.data_models import (
    AnalysisSession, ExecutionResult, ASTResult, ClapComponents, ErrorRecord,
)


# ──────────────────────────────────────────────
# 페이크 의존성
# ──────────────────────────────────────────────

class FakeWatcher:
    def __init__(self):
        self.folders = set()

    def is_watching(self, p):
        return p in self.folders

    def start_watching(self, p):
        self.folders.add(p)
        return True

    def stop_watching(self, p):
        self.folders.discard(p)

    def get_watching_folders(self):
        return list(self.folders)

    def stop_all(self):
        self.folders.clear()


class FakeQueue:
    def __init__(self):
        self.enqueued = []

    def enqueue(self, file_path):
        self.enqueued.append(file_path)


def make_error_session(error_type="NameError", timestamp="2026-05-20T10:00:00"):
    return AnalysisSession(
        file_path="f.py", timestamp=timestamp,
        execution_result=ExecutionResult(
            file_path="f.py", success=False,
            error_type=error_type, error_message="msg",
        ),
        ast_result=ASTResult(file_path="f.py", clap_components=ClapComponents(score=5.0)),
        error_record=ErrorRecord(error_type=error_type, error_message="msg", file_path="f.py"),
    )


@pytest.fixture
def controller(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / "c.db"))
    ctrl = AppController(db, FakeQueue(), FakeWatcher(), VisualizationEngine())
    yield ctrl
    db.close()


# ──────────────────────────────────────────────
# 폴더 등록 / 해제
# ──────────────────────────────────────────────

class TestFolderRegistration:

    def test_register_valid_folder(self, controller, tmp_path):
        result = controller.register_folder(str(tmp_path))
        assert result["success"] is True
        assert controller.file_watcher.is_watching(str(tmp_path))

    def test_register_invalid_folder(self, controller):
        result = controller.register_folder("/no/such/dir/xyz")
        assert result["success"] is False
        assert "존재하지" in result["error"]

    def test_register_duplicate(self, controller, tmp_path):
        controller.register_folder(str(tmp_path))
        result = controller.register_folder(str(tmp_path))
        assert result["success"] is False
        assert "이미" in result["error"]

    def test_unregister_folder(self, controller, tmp_path):
        controller.register_folder(str(tmp_path))
        controller.unregister_folder(str(tmp_path))
        assert controller.file_watcher.is_watching(str(tmp_path)) is False
        assert str(tmp_path) not in controller.db_manager.get_folder_configs()

    def test_on_file_changed_enqueues(self, controller):
        controller.on_file_changed("a.py")
        assert controller.analysis_queue.enqueued == ["a.py"]


# ──────────────────────────────────────────────
# 대시보드 / 차트 / 리포트
# ──────────────────────────────────────────────

class TestDataQueries:

    def test_dashboard_empty(self, controller):
        data = controller.get_dashboard_data()
        assert data.summary_stats.total_sessions == 0

    def test_dashboard_reflects_sessions(self, controller):
        controller.db_manager.save_session(make_error_session())
        data = controller.get_dashboard_data()
        assert data.summary_stats.total_sessions == 1
        assert data.summary_stats.total_errors == 1

    def test_dashboard_registered_folders(self, controller, tmp_path):
        controller.register_folder(str(tmp_path))
        data = controller.get_dashboard_data()
        assert str(tmp_path) in data.registered_folders

    def test_report_html_no_data(self, controller):
        html = controller.get_report_html()
        assert "데이터가 없습니다" in html

    def test_report_html_with_error(self, controller):
        controller.db_manager.save_session(make_error_session("NameError"))
        html = controller.get_report_html()
        assert "NameError" in html

    def test_chart_data_returned(self, controller):
        data = controller.get_chart_data()
        assert data.has_enough_data is False

    def test_reset_all(self, controller):
        controller.db_manager.save_session(make_error_session())
        assert controller.reset_all_data() is True
        assert controller.get_dashboard_data().summary_stats.total_sessions == 0


# ──────────────────────────────────────────────
# 오류 도우미 / 언어 설정
# ──────────────────────────────────────────────

class TestHelperAndLanguage:

    def test_latest_error_none_when_empty(self, controller):
        assert controller.get_latest_error() is None

    def test_latest_error_returns_recent(self, controller):
        controller.db_manager.save_session(make_error_session("TypeError"))
        latest = controller.get_latest_error()
        assert latest is not None
        assert latest["error_type"] == "TypeError"

    def test_supported_errors_count(self, controller):
        assert len(controller.get_supported_errors()) == 12

    def test_language_default_ko(self, controller):
        assert controller.get_language() == "ko"

    def test_language_persists(self, controller):
        controller.set_language("en")
        assert controller.get_language() == "en"
