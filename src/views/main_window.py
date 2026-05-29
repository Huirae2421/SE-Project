"""
main_window.py: 메인 윈도우 및 화면 전환 관리
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QStackedWidget, QStatusBar
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCloseEvent

from ..controllers.app_controller import AppController
from ..models.data_models import AnalysisSession
from .dashboard_view import DashboardView
from .chart_view import ChartView
from .settings_view import SettingsView
from .report_view import ReportView
from .error_helper_view import ErrorHelperView
from .nav_bar import NavBar
from . import i18n


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

WINDOW_TITLE = "CLAP - Code Learning Analysis Program"
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

PAGE_DASHBOARD = 0
PAGE_CHART = 1
PAGE_SETTINGS = 2
PAGE_REPORT = 3
PAGE_HELPER = 4


# ──────────────────────────────────────────────
# MainWindow
# ──────────────────────────────────────────────

class MainWindow(QMainWindow):

    analysis_completed = pyqtSignal(AnalysisSession)
    analysis_started   = pyqtSignal(str)
    notification       = pyqtSignal(str, str)   # (message, level)
    folder_removed     = pyqtSignal(str)

    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        # 저장된 언어 설정을 먼저 적용한 뒤 화면을 구성한다
        i18n.set_language(self.controller.get_language(i18n.LANG_KO))
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

        self.nav_bar = NavBar()
        layout.addWidget(self.nav_bar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.dashboard_view = DashboardView(self.controller)
        self.chart_view = ChartView(self.controller)
        self.settings_view = SettingsView(self.controller)
        self.report_view = ReportView(self.controller)
        self.helper_view = ErrorHelperView(self.controller)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.chart_view)
        self.stack.addWidget(self.settings_view)
        self.stack.addWidget(self.report_view)
        self.stack.addWidget(self.helper_view)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("CLAP 준비 완료")

    # ──────────────────────────────────────────────
    # 시그널 연결
    # ──────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.nav_bar.navigate.connect(self._on_nav)
        self.settings_view.language_changed.connect(self._on_language_changed)
        self.analysis_completed.connect(self._on_analysis_completed)
        self.analysis_started.connect(self._on_analysis_started)
        self.notification.connect(self.show_notification)
        self.folder_removed.connect(self._on_folder_removed)

    # ──────────────────────────────────────────────
    # 언어 변경 처리
    # ──────────────────────────────────────────────

    def _on_language_changed(self, lang: str) -> None:
        i18n.set_language(lang)
        self.nav_bar.retranslate_ui()
        self.dashboard_view.retranslate_ui()
        self.chart_view.retranslate_ui()
        self.report_view.retranslate_ui()
        self.helper_view.retranslate_ui()
        self.settings_view.retranslate_ui()
        # 현재 보고 있는 화면의 데이터를 새 언어로 다시 로드
        self._load_dashboard()

    # ──────────────────────────────────────────────
    # 화면 전환
    # ──────────────────────────────────────────────

    def _on_nav(self, page_index: int) -> None:
        if page_index == PAGE_CHART:
            self._show_chart()
        elif page_index == PAGE_SETTINGS:
            self._show_settings()
        elif page_index == PAGE_REPORT:
            self._show_report()
        elif page_index == PAGE_HELPER:
            self._show_helper()
        else:
            self._show_dashboard()

    def _show_dashboard(self) -> None:
        self.stack.setCurrentIndex(PAGE_DASHBOARD)
        self.nav_bar.set_active(PAGE_DASHBOARD)
        self._load_dashboard()

    def _show_chart(self) -> None:
        self.stack.setCurrentIndex(PAGE_CHART)
        self.nav_bar.set_active(PAGE_CHART)
        self.chart_view.load_charts()

    def _show_settings(self) -> None:
        self.stack.setCurrentIndex(PAGE_SETTINGS)
        self.nav_bar.set_active(PAGE_SETTINGS)
        self.settings_view.load_settings()

    def _show_report(self) -> None:
        self.stack.setCurrentIndex(PAGE_REPORT)
        self.nav_bar.set_active(PAGE_REPORT)
        self.report_view.load_report()

    def _show_helper(self) -> None:
        self.stack.setCurrentIndex(PAGE_HELPER)
        self.nav_bar.set_active(PAGE_HELPER)
        self.helper_view.load_helper()

    # ──────────────────────────────────────────────
    # 분석 시작/완료 콜백 (백그라운드 스레드 → 시그널로 안전하게 전달)
    # ──────────────────────────────────────────────

    def on_analysis_started(self, file_path: str) -> None:
        self.analysis_started.emit(file_path)

    def _on_analysis_started(self, file_path: str) -> None:
        import os
        self.status_bar.setStyleSheet("")
        self.status_bar.showMessage(f"분석 중: {os.path.basename(file_path)} ...")

    def on_analysis_completed(self, session: AnalysisSession) -> None:
        self.analysis_completed.emit(session)

    def _on_analysis_completed(self, session: AnalysisSession) -> None:
        self.status_bar.setStyleSheet("")
        self.status_bar.showMessage(
            f"분석 완료: {session.file_path} | "
            f"McCabe: {session.ast_result.mccabe_score} | "
            f"난이도: {session.difficulty_score.label}"
        )
        # 현재 보고 있는 화면을 새 분석 결과로 즉시 갱신
        self._refresh_current_page()

    # ──────────────────────────────────────────────
    # 현재 화면 새로고침
    # ──────────────────────────────────────────────

    def _refresh_current_page(self) -> None:
        index = self.stack.currentIndex()
        if index == PAGE_DASHBOARD:
            self._load_dashboard()
        elif index == PAGE_CHART:
            self.chart_view.load_charts()
        elif index == PAGE_REPORT:
            self.report_view.load_report()
        elif index == PAGE_HELPER:
            self.helper_view.load_helper()

    # ──────────────────────────────────────────────
    # 저장 실패 콜백
    # ──────────────────────────────────────────────

    def on_save_failed(self, file_path: str) -> None:
        import os
        self.notification.emit(
            f"데이터 저장 실패: {os.path.basename(file_path)}", "error"
        )

    # ──────────────────────────────────────────────
    # 폴더 삭제 콜백
    # ──────────────────────────────────────────────

    def on_folder_removed(self, folder_path: str) -> None:
        self.folder_removed.emit(folder_path)

    def _on_folder_removed(self, folder_path: str) -> None:
        self.controller.unregister_folder(folder_path)
        self.notification.emit(f"폴더를 찾을 수 없습니다: {folder_path}", "warning")
        self._refresh_current_page()

    # ──────────────────────────────────────────────
    # 상태표시줄 알림
    # ──────────────────────────────────────────────

    def show_notification(self, message: str, level: str = "info") -> None:
        colors = {
            "error":   "color: #dc3545; font-weight: bold;",
            "warning": "color: #fd7e14; font-weight: bold;",
            "info":    "",
        }
        self.status_bar.setStyleSheet(colors.get(level, ""))
        self.status_bar.showMessage(message)

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