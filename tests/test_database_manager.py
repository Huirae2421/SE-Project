"""
test_database_manager.py: DatabaseManager 단위 테스트
"""

import os
import pytest
from src.models.database_manager import DatabaseManager
from src.models.data_models import (
    AnalysisSession, ExecutionResult, ASTResult,
    ClapComponents, ErrorRecord, DifficultyScore
)


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test_clap.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def make_session(file_path="test.py", with_error=False):
    execution_result = ExecutionResult(
        file_path=file_path,
        stdout="Hello",
        stderr="",
        error_type="NameError" if with_error else None,
        error_message="name 'x' is not defined" if with_error else "",
        elapsed_seconds=0.5,
        timed_out=False,
        success=not with_error
    )

    clap_components = ClapComponents(
        branch_count=2,
        loop_count=1,
        nesting_depth=2,
        function_length=10.0,
        score=8.5
    )

    ast_result = ASTResult(
        file_path=file_path,
        valid=True,
        line_count=30,
        function_count=2,
        clap_components=clap_components,
        mccabe_score=5.0,
        mccabe_label="simple",
        feedback_message="Code structure looks good."
    )

    error_record = ErrorRecord(
        error_type="NameError",
        error_message="name 'x' is not defined",
        file_path=file_path,
        error_group="undefined variable group"
    ) if with_error else None

    difficulty_score = DifficultyScore(
        score=0.4,
        label="average",
        is_relative=True
    )

    return AnalysisSession(
        file_path=file_path,
        execution_result=execution_result,
        ast_result=ast_result,
        error_record=error_record,
        difficulty_score=difficulty_score
    )


# ──────────────────────────────────────────────
# 스키마 초기화 테스트
# ──────────────────────────────────────────────

class TestSchema:

    def test_tables_created(self, db):
        conn = db._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "sessions" in tables
        assert "folder_configs" in tables

    def test_indexes_created(self, db):
        conn = db._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        assert "idx_sessions_timestamp" in indexes


# ──────────────────────────────────────────────
# 세션 저장 테스트
# ──────────────────────────────────────────────

class TestSaveSession:

    def test_save_returns_id(self, db):
        session = make_session()
        session_id = db.save_session(session)
        assert session_id is not None
        assert session_id > 0

    def test_save_increments_id(self, db):
        id1 = db.save_session(make_session("file1.py"))
        id2 = db.save_session(make_session("file2.py"))
        assert id2 > id1

    def test_save_with_error(self, db):
        session = make_session(with_error=True)
        session_id = db.save_session(session)
        assert session_id is not None

    def test_save_without_error(self, db):
        session = make_session(with_error=False)
        session_id = db.save_session(session)
        assert session_id is not None


# ──────────────────────────────────────────────
# 세션 조회 테스트
# ──────────────────────────────────────────────

class TestGetSessions:

    def test_empty_db_returns_empty_list(self, db):
        sessions = db.get_sessions()
        assert sessions == []

    def test_saved_session_retrievable(self, db):
        db.save_session(make_session())
        sessions = db.get_sessions()
        assert len(sessions) == 1

    def test_multiple_sessions(self, db):
        for i in range(5):
            db.save_session(make_session(f"file{i}.py"))
        sessions = db.get_sessions()
        assert len(sessions) == 5

    def test_limit_parameter(self, db):
        for i in range(10):
            db.save_session(make_session(f"file{i}.py"))
        sessions = db.get_sessions(limit=3)
        assert len(sessions) == 3

    def test_error_type_preserved(self, db):
        db.save_session(make_session(with_error=True))
        sessions = db.get_sessions()
        assert sessions[0].execution_result.error_type == "NameError"

    def test_clap_score_preserved(self, db):
        db.save_session(make_session())
        sessions = db.get_sessions()
        assert sessions[0].ast_result.clap_components.score == 8.5


# ──────────────────────────────────────────────
# 오류 통계 테스트
# ──────────────────────────────────────────────

class TestErrorCounts:

    def test_empty_returns_empty_dict(self, db):
        counts = db.get_error_counts()
        assert counts == {}

    def test_single_error_counted(self, db):
        db.save_session(make_session(with_error=True))
        counts = db.get_error_counts()
        assert counts.get("NameError") == 1

    def test_multiple_same_errors(self, db):
        for _ in range(3):
            db.save_session(make_session(with_error=True))
        counts = db.get_error_counts()
        assert counts.get("NameError") == 3


# ──────────────────────────────────────────────
# 폴더 설정 테스트
# ──────────────────────────────────────────────

class TestFolderConfig:

    def test_save_folder(self, db):
        result = db.save_folder_config("/test/folder")
        assert result is True

    def test_get_folders(self, db):
        db.save_folder_config("/test/folder1")
        db.save_folder_config("/test/folder2")
        folders = db.get_folder_configs()
        assert "/test/folder1" in folders
        assert "/test/folder2" in folders

    def test_delete_folder(self, db):
        db.save_folder_config("/test/folder")
        db.delete_folder_config("/test/folder")
        folders = db.get_folder_configs()
        assert "/test/folder" not in folders

    def test_duplicate_folder_ignored(self, db):
        db.save_folder_config("/test/folder")
        db.save_folder_config("/test/folder")
        folders = db.get_folder_configs()
        assert folders.count("/test/folder") == 1


# ──────────────────────────────────────────────
# 데이터 초기화 테스트
# ──────────────────────────────────────────────

class TestReset:

    def test_reset_clears_sessions(self, db):
        for i in range(3):
            db.save_session(make_session(f"file{i}.py"))
        db.reset_all()
        assert db.get_sessions() == []

    def test_reset_clears_folders(self, db):
        db.save_folder_config("/test/folder")
        db.reset_all()
        assert db.get_folder_configs() == []

    def test_reset_returns_true(self, db):
        result = db.reset_all()
        assert result is True