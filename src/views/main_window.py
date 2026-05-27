"""
main_window.py: 메인 윈도우 및 화면 전환 관리
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QStackedWidget, QStatusBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent

from ..controllers.app_controller import AppController
from ..models.data_models import AnalysisSession
from .dashboard_view import DashboardView
from .chart_view import ChartView
from .settings_view import SettingsView


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

WINDOW_TITLE = "CLAP - Code Learning Analysis Program"
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

PAGE_DASHBOARD = 0
PAGE_CHART = 1
PAGE_SETTINGS = 2


# ──────────────────────────────────────────────
# MainWindow
# ──────────────────────────────────────────────

class MainWindow(QMainWindow):

    analysis_completed = pyqtSignal(AnalysisSession)

    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        self._init_ui()
        self._connect_signals()
        self._load_dashboard()

    # ──────────────────────────────────────────────
    # UI 초기화
    # ──────────────────────────────────────────────

    def _init_ui(self) -> None:
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.dashboard_view = DashboardView(self.controller)
        self.chart_view = ChartView(self.controller)
        self.settings_view = SettingsView(self.controller)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.chart_view)
        self.stack.addWidget(self.settings_view)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("CLAP 준비 완료")

    # ──────────────────────────────────────────────
    # 시그널 연결
    # ──────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.dashboard_view.navigate_to_chart.connect(self._show_chart)
        self.dashboard_view.navigate_to_settings.connect(self._show_settings)
        self.chart_view.navigate_to_dashboard.connect(self._show_dashboard)
        self.settings_view.navigate_to_dashboard.connect(self._show_dashboard)
        self.analysis_completed.connect(self._on_analysis_completed)

    # ──────────────────────────────────────────────
    # 화면 전환
    # ──────────────────────────────────────────────

    def _show_dashboard(self) -> None:
        self.stack.setCurrentIndex(PAGE_DASHBOARD)
        self._load_dashboard()

    def _show_chart(self) -> None:
        self.stack.setCurrentIndex(PAGE_CHART)
        self.chart_view.load_charts()

    def _show_settings(self) -> None:
        self.stack.setCurrentIndex(PAGE_SETTINGS)
        self.settings_view.load_settings()

    # ──────────────────────────────────────────────
    # 분석 완료 콜백
    # ──────────────────────────────────────────────

    def on_analysis_completed(self, session: AnalysisSession) -> None:
        self.analysis_completed.emit(session)

    def _on_analysis_completed(self, session: AnalysisSession) -> None:
        self.status_bar.showMessage(
            f"분석 완료: {session.file_path} | "
            f"McCabe: {session.ast_result.mccabe_score} | "
            f"난이도: {session.difficulty_score.label}"
        )
        if self.stack.currentIndex() == PAGE_DASHBOARD:
            self._load_dashboard()

    # ──────────────────────────────────────────────
    # 데이터 로드
    # ──────────────────────────────────────────────

    def _load_dashboard(self) -> None:
        dashboard_data = self.controller.get_dashboard_data()
        self.dashboard_view.update_data(dashboard_data)

    # ──────────────────────────────────────────────
    # 종료 처리
    # ──────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent) -> None:
        self.controller.file_watcher.stop_all()
        self.controller.db_manager.close()
        event.accept()