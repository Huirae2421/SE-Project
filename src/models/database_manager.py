"""
database_manager.py: SQLite 데이터베이스 연동 및 데이터 관리
"""

import sqlite3
import threading
import functools
from typing import List, Optional
from .data_models import (
    AnalysisSession, HistoricalSession, ExecutionResult,
    ASTResult, ClapComponents, ErrorRecord, DifficultyScore
)
from ..app_paths import db_path


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

# 사용자 홈(~/.clap) 아래에 DB를 둔다 (exe 실행 위치와 무관하게 동작)
DB_PATH = db_path()


# ──────────────────────────────────────────────
# 스레드 동기화 데코레이터
# ──────────────────────────────────────────────

def _synchronized(method):
    """DB 접근 메서드를 락으로 직렬화한다.

    분석은 백그라운드 스레드에서, UI 조회는 메인 스레드에서 일어나므로
    하나의 SQLite 연결을 여러 스레드가 안전하게 공유하도록 보호한다.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


# ──────────────────────────────────────────────
# DatabaseManager
# ──────────────────────────────────────────────

class DatabaseManager:

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()
        self.initialize_schema()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            # check_same_thread=False: 백그라운드 분석 스레드에서도 사용 가능
            # (실제 동시 접근은 _synchronized 락으로 직렬화)
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    # ──────────────────────────────────────────────
    # 스키마 초기화
    # ──────────────────────────────────────────────

    @_synchronized
    def initialize_schema(self) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path        TEXT    NOT NULL,
                timestamp        TEXT    NOT NULL,
                stdout           TEXT    DEFAULT '',
                stderr           TEXT    DEFAULT '',
                error_type       TEXT,
                error_message    TEXT    DEFAULT '',
                elapsed_seconds  REAL    DEFAULT 0.0,
                timed_out        INTEGER DEFAULT 0,
                success          INTEGER DEFAULT 0,
                line_count       INTEGER DEFAULT 0,
                function_count   INTEGER DEFAULT 0,
                branch_count     INTEGER DEFAULT 0,
                loop_count       INTEGER DEFAULT 0,
                nesting_depth    INTEGER DEFAULT 0,
                function_length  REAL    DEFAULT 0.0,
                clap_score       REAL    DEFAULT 0.0,
                mccabe_score     REAL    DEFAULT 0.0,
                mccabe_label     TEXT    DEFAULT 'simple',
                feedback_message TEXT    DEFAULT '',
                error_group      TEXT    DEFAULT '',
                difficulty_score REAL    DEFAULT 0.0,
                difficulty_label TEXT    DEFAULT 'collecting data',
                is_relative      INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS folder_configs (
                config_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT NOT NULL UNIQUE,
                created_at  TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_timestamp
            ON sessions (timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_file_path
            ON sessions (file_path)
        """)

        conn.commit()

    # ──────────────────────────────────────────────
    # 세션 저장
    # ──────────────────────────────────────────────

    @_synchronized
    def save_session(self, session: AnalysisSession) -> Optional[int]:
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            er = session.execution_result
            ar = session.ast_result
            cc = ar.clap_components
            ds = session.difficulty_score
            error_group = session.error_record.error_group if session.error_record else ""

            cursor.execute("""
                INSERT INTO sessions (
                    file_path, timestamp,
                    stdout, stderr, error_type, error_message,
                    elapsed_seconds, timed_out, success,
                    line_count, function_count,
                    branch_count, loop_count, nesting_depth,
                    function_length, clap_score,
                    mccabe_score, mccabe_label, feedback_message,
                    error_group,
                    difficulty_score, difficulty_label, is_relative
                ) VALUES (
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?,
                    ?, ?, ?
                )
            """, (
                session.file_path, session.timestamp,
                er.stdout, er.stderr, er.error_type, er.error_message,
                er.elapsed_seconds, int(er.timed_out), int(er.success),
                ar.line_count, ar.function_count,
                cc.branch_count, cc.loop_count, cc.nesting_depth,
                cc.function_length, cc.score,
                ar.mccabe_score, ar.mccabe_label, ar.feedback_message,
                error_group,
                ds.score, ds.label, int(ds.is_relative)
            ))

            conn.commit()
            return cursor.lastrowid

        except Exception:
            conn.rollback()
            return None

    # ──────────────────────────────────────────────
    # 세션 조회
    # ──────────────────────────────────────────────

    @_synchronized
    def get_sessions(self, limit: int = 100) -> List[AnalysisSession]:
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM sessions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        sessions = []

        for row in rows:
            execution_result = ExecutionResult(
                file_path=row["file_path"],
                stdout=row["stdout"],
                stderr=row["stderr"],
                error_type=row["error_type"],
                error_message=row["error_message"],
                elapsed_seconds=row["elapsed_seconds"],
                timed_out=bool(row["timed_out"]),
                success=bool(row["success"])
            )

            clap_components = ClapComponents(
                branch_count=row["branch_count"],
                loop_count=row["loop_count"],
                nesting_depth=row["nesting_depth"],
                function_length=row["function_length"],
                score=row["clap_score"]
            )

            ast_result = ASTResult(
                file_path=row["file_path"],
                line_count=row["line_count"],
                function_count=row["function_count"],
                clap_components=clap_components,
                mccabe_score=row["mccabe_score"],
                mccabe_label=row["mccabe_label"],
                feedback_message=row["feedback_message"]
            )

            error_record = None
            if row["error_type"]:
                error_record = ErrorRecord(
                    error_type=row["error_type"],
                    error_message=row["error_message"],
                    file_path=row["file_path"],
                    timestamp=row["timestamp"],
                    error_group=row["error_group"]
                )

            difficulty_score = DifficultyScore(
                score=row["difficulty_score"],
                label=row["difficulty_label"],
                is_relative=bool(row["is_relative"])
            )

            session = AnalysisSession(
                file_path=row["file_path"],
                timestamp=row["timestamp"],
                execution_result=execution_result,
                ast_result=ast_result,
                error_record=error_record,
                difficulty_score=difficulty_score,
                session_id=row["session_id"]
            )
            sessions.append(session)

        return sessions

    @_synchronized
    def get_historical_sessions(self, limit: int = 100) -> List[HistoricalSession]:
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, timestamp,
                   CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END as error_count,
                   clap_score, mccabe_score, elapsed_seconds,
                   difficulty_score, difficulty_label
            FROM sessions
            ORDER BY timestamp ASC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        return [
            HistoricalSession(
                session_id=row["session_id"],
                timestamp=row["timestamp"],
                error_count=row["error_count"],
                clap_score=row["clap_score"],
                mccabe_score=row["mccabe_score"],
                elapsed_seconds=row["elapsed_seconds"],
                difficulty_score=row["difficulty_score"],
                difficulty_label=row["difficulty_label"]
            )
            for row in rows
        ]

    # ──────────────────────────────────────────────
    # 오류 통계
    # ──────────────────────────────────────────────

    @_synchronized
    def get_error_counts(self) -> dict:
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT error_type, COUNT(*) as count
            FROM sessions
            WHERE error_type IS NOT NULL
            GROUP BY error_type
            ORDER BY count DESC
        """)

        return {row["error_type"]: row["count"] for row in cursor.fetchall()}

    # ──────────────────────────────────────────────
    # 폴더 설정 관리
    # ──────────────────────────────────────────────

    @_synchronized
    def get_folder_configs(self) -> List[str]:
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT folder_path FROM folder_configs ORDER BY created_at ASC")
        return [row["folder_path"] for row in cursor.fetchall()]

    @_synchronized
    def save_folder_config(self, folder_path: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            from datetime import datetime
            cursor.execute("""
                INSERT OR IGNORE INTO folder_configs (folder_path, created_at)
                VALUES (?, ?)
            """, (folder_path, datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    @_synchronized
    def delete_folder_config(self, folder_path: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM folder_configs WHERE folder_path = ?",
                (folder_path,)
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    # ──────────────────────────────────────────────
    # 앱 설정 (key-value)
    # ──────────────────────────────────────────────

    @_synchronized
    def get_setting(self, key: str, default: str = "") -> str:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    @_synchronized
    def set_setting(self, key: str, value: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO app_settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    # ──────────────────────────────────────────────
    # 데이터 초기화 및 종료
    # ──────────────────────────────────────────────

    @_synchronized
    def reset_all(self) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM sessions")
            cursor.execute("DELETE FROM folder_configs")
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    @_synchronized
    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None