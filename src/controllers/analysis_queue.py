"""
analysis_queue.py: 분석 파이프라인 및 백그라운드 처리
"""

import threading
import logging
from typing import Callable, Optional
from ..models.data_models import AnalysisSession
from ..models.code_executor import CodeExecutor
from ..models.ast_analyzer import ASTAnalyzer
from ..models.error_analyzer import ErrorAnalyzer
from ..models.difficulty_estimator import DifficultyEstimator
from ..models.database_manager import DatabaseManager
from ..app_paths import log_path

# ──────────────────────────────────────────────
# 로그 설정 (사용자 홈 ~/.clap 아래에 기록)
# ──────────────────────────────────────────────

logging.basicConfig(
    filename=log_path(),
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# ──────────────────────────────────────────────
# AnalysisQueue
# ──────────────────────────────────────────────

class AnalysisQueue:

    def __init__(
        self,
        code_executor: CodeExecutor,
        ast_analyzer: ASTAnalyzer,
        error_analyzer: ErrorAnalyzer,
        difficulty_estimator: DifficultyEstimator,
        db_manager: DatabaseManager,
        on_complete: Optional[Callable[[AnalysisSession], None]] = None,
        on_start: Optional[Callable[[str], None]] = None,
        on_save_failed: Optional[Callable[[str], None]] = None,
    ):
        self.code_executor = code_executor
        self.ast_analyzer = ast_analyzer
        self.error_analyzer = error_analyzer
        self.difficulty_estimator = difficulty_estimator
        self.db_manager = db_manager
        self.on_complete = on_complete
        self.on_start = on_start
        self.on_save_failed = on_save_failed

    # ──────────────────────────────────────────────
    # 백그라운드 분석 시작
    # ──────────────────────────────────────────────

    def enqueue(self, file_path: str) -> None:
        thread = threading.Thread(
            target=self._process,
            args=(file_path,),
            daemon=True
        )
        thread.start()

    # ──────────────────────────────────────────────
    # 분석 파이프라인
    # ──────────────────────────────────────────────

    def _process(self, file_path: str) -> None:
        try:
            # 분석 시작 알림 (상태표시줄 "분석 중" 표시용)
            if self.on_start:
                self.on_start(file_path)

            execution_result = self.code_executor.execute(file_path)
            ast_result = self.ast_analyzer.analyze(file_path)
            error_record = self.error_analyzer.classify(execution_result)

            history = self.db_manager.get_historical_sessions()
            difficulty_score = self.difficulty_estimator.estimate(
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

            session_id = self.db_manager.save_session(session)

            # DB 저장 실패 시: 롤백은 save_session 내부에서 처리됨, 사용자에게 알림
            if session_id is None:
                logging.error(f"세션 저장 실패 [{file_path}]")
                if self.on_save_failed:
                    self.on_save_failed(file_path)
                return

            session.session_id = session_id

            if self.on_complete:
                self.on_complete(session)

        except Exception as e:
            logging.error(f"파이프라인 오류 [{file_path}]: {e}", exc_info=True)