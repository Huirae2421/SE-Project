"""
app_controller.py: 애플리케이션 전체 흐름 제어
"""

import os
import logging
from typing import Optional
from ..models.database_manager import DatabaseManager
from ..models.visualization_engine import VisualizationEngine
from ..models.data_models import DashboardData, ChartData, SummaryStats
from .analysis_queue import AnalysisQueue
from .file_watcher import FileWatcher


# ──────────────────────────────────────────────
# AppController
# ──────────────────────────────────────────────

class AppController:

    def __init__(
        self,
        db_manager: DatabaseManager,
        analysis_queue: AnalysisQueue,
        file_watcher: FileWatcher,
        visualization_engine: VisualizationEngine
    ):
        self.db_manager = db_manager
        self.analysis_queue = analysis_queue
        self.file_watcher = file_watcher
        self.visualization_engine = visualization_engine
        self._restore_folders()

    # ──────────────────────────────────────────────
    # 폴더 등록 및 해제
    # ──────────────────────────────────────────────

    def register_folder(self, folder_path: str) -> dict:
        if not os.path.isdir(folder_path):
            return {"success": False, "error": "존재하지 않는 폴더 경로입니다."}

        if self.file_watcher.is_watching(folder_path):
            return {"success": False, "error": "이미 등록된 폴더입니다."}

        saved = self.db_manager.save_folder_config(folder_path)
        if not saved:
            return {"success": False, "error": "폴더 설정 저장에 실패했습니다."}

        started = self.file_watcher.start_watching(folder_path)
        if not started:
            self.db_manager.delete_folder_config(folder_path)
            return {"success": False, "error": "폴더 감시 시작에 실패했습니다."}

        return {"success": True, "folder_path": folder_path}

    def unregister_folder(self, folder_path: str) -> dict:
        self.file_watcher.stop_watching(folder_path)
        self.db_manager.delete_folder_config(folder_path)
        return {"success": True, "folder_path": folder_path}

    # ──────────────────────────────────────────────
    # 파일 변경 감지 콜백
    # ──────────────────────────────────────────────

    def on_file_changed(self, file_path: str) -> None:
        self.analysis_queue.enqueue(file_path)

    # ──────────────────────────────────────────────
    # 대시보드 데이터 조회
    # ──────────────────────────────────────────────

    def get_dashboard_data(self) -> DashboardData:
        sessions = self.db_manager.get_sessions(limit=100)
        error_counts = self.db_manager.get_error_counts()
        registered_folders = self.file_watcher.get_watching_folders()

        latest_session = sessions[0] if sessions else None
        difficulty_score = latest_session.difficulty_score if latest_session else None

        from ..models.data_models import DifficultyScore
        if difficulty_score is None:
            difficulty_score = DifficultyScore()

        summary_stats = self._build_summary_stats(sessions, error_counts)

        return DashboardData(
            latest_session=latest_session,
            difficulty_score=difficulty_score,
            error_counts=error_counts,
            summary_stats=summary_stats,
            registered_folders=registered_folders
        )

    def _build_summary_stats(self, sessions, error_counts) -> SummaryStats:
        total_sessions = len(sessions)
        total_errors = sum(error_counts.values())

        if total_sessions == 0:
            return SummaryStats()

        avg_mccabe = sum(s.ast_result.mccabe_score for s in sessions) / total_sessions
        avg_clap = sum(s.ast_result.clap_components.score for s in sessions) / total_sessions
        avg_elapsed = sum(s.execution_result.elapsed_seconds for s in sessions) / total_sessions
        most_frequent = max(error_counts, key=error_counts.get) if error_counts else "없음"

        return SummaryStats(
            total_sessions=total_sessions,
            total_errors=total_errors,
            avg_mccabe_score=round(avg_mccabe, 2),
            avg_clap_score=round(avg_clap, 2),
            avg_elapsed_seconds=round(avg_elapsed, 4),
            most_frequent_error=most_frequent
        )

    # ──────────────────────────────────────────────
    # 차트 데이터 조회
    # ──────────────────────────────────────────────

    def get_chart_data(self) -> ChartData:
        sessions = self.db_manager.get_sessions(limit=100)
        return self.visualization_engine.build_chart_data(sessions)

    # ──────────────────────────────────────────────
    # 데이터 초기화
    # ──────────────────────────────────────────────

    def reset_all_data(self) -> bool:
        return self.db_manager.reset_all()

    # ──────────────────────────────────────────────
    # 저장된 폴더 자동 복원
    # ──────────────────────────────────────────────

    def _restore_folders(self) -> None:
        folders = self.db_manager.get_folder_configs()
        for folder_path in folders:
            if os.path.isdir(folder_path):
                self.file_watcher.start_watching(folder_path)
            else:
                logging.warning(f"저장된 폴더가 존재하지 않아 감시를 건너뜁니다: {folder_path}")