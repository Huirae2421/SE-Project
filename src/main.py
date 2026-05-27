"""
main.py: CLAP 애플리케이션 진입점
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.models.database_manager import DatabaseManager
from src.models.code_executor import CodeExecutor
from src.models.ast_analyzer import ASTAnalyzer
from src.models.error_analyzer import ErrorAnalyzer
from src.models.difficulty_estimator import DifficultyEstimator
from src.models.visualization_engine import VisualizationEngine
from src.controllers.analysis_queue import AnalysisQueue
from src.controllers.file_watcher import FileWatcher
from src.controllers.app_controller import AppController
from src.views.main_window import MainWindow


# ──────────────────────────────────────────────
# 의존성 조립
# ──────────────────────────────────────────────

def build_app() -> tuple[QApplication, MainWindow]:
    app = QApplication(sys.argv)
    app.setApplicationName("CLAP")
    app.setApplicationVersion("1.0.0")

    db_manager            = DatabaseManager()
    code_executor         = CodeExecutor()
    ast_analyzer          = ASTAnalyzer()
    error_analyzer        = ErrorAnalyzer()
    difficulty_estimator  = DifficultyEstimator()
    visualization_engine  = VisualizationEngine()
    file_watcher          = FileWatcher(on_file_changed=lambda path: None)

    analysis_queue = AnalysisQueue(
        code_executor=code_executor,
        ast_analyzer=ast_analyzer,
        error_analyzer=error_analyzer,
        difficulty_estimator=difficulty_estimator,
        db_manager=db_manager,
        on_complete=None
    )

    controller = AppController(
        db_manager=db_manager,
        analysis_queue=analysis_queue,
        file_watcher=file_watcher,
        visualization_engine=visualization_engine
    )

    window = MainWindow(controller=controller)

    file_watcher.on_file_changed = controller.on_file_changed
    analysis_queue.on_complete   = window.on_analysis_completed

    return app, window


# ──────────────────────────────────────────────
# 진입점
# ──────────────────────────────────────────────

def main() -> None:
    app, window = build_app()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()