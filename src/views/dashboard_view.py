"""
dashboard_view.py: 대시보드 화면 구성
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout,
    QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..controllers.app_controller import AppController
from ..models.data_models import DashboardData


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

FONT_TITLE  = QFont("맑은 고딕", 18, QFont.Bold)
FONT_LABEL  = QFont("맑은 고딕", 11)
FONT_VALUE  = QFont("맑은 고딕", 13, QFont.Bold)
FONT_BUTTON = QFont("맑은 고딕", 10)


# ──────────────────────────────────────────────
# StatCard
# ──────────────────────────────────────────────

class StatCard(QFrame):

    def __init__(self, title: str, value: str = "-"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setFont(FONT_LABEL)
        self.title_label.setStyleSheet("color: #6c757d;")

        self.value_label = QLabel(value)
        self.value_label.setFont(FONT_VALUE)
        self.value_label.setStyleSheet("color: #212529;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


# ──────────────────────────────────────────────
# DashboardView
# ──────────────────────────────────────────────

class DashboardView(QWidget):

    navigate_to_chart    = pyqtSignal()
    navigate_to_settings = pyqtSignal()

    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        self._init_ui()

    # ──────────────────────────────────────────────
    # UI 초기화
    # ──────────────────────────────────────────────

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_stat_cards())
        layout.addWidget(self._build_feedback_section())
        layout.addLayout(self._build_folder_section())
        layout.addStretch()
        layout.addLayout(self._build_nav_buttons())

    # ──────────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        title = QLabel("CLAP 대시보드")
        title.setFont(FONT_TITLE)

        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 통계 카드
    # ──────────────────────────────────────────────

    def _build_stat_cards(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(12)

        self.card_sessions     = StatCard("총 분석 횟수")
        self.card_errors       = StatCard("총 오류 발생")
        self.card_mccabe       = StatCard("평균 McCabe 점수")
        self.card_clap         = StatCard("평균 CLAP 점수")
        self.card_difficulty   = StatCard("현재 난이도")
        self.card_top_error    = StatCard("가장 많은 오류")

        grid.addWidget(self.card_sessions,   0, 0)
        grid.addWidget(self.card_errors,     0, 1)
        grid.addWidget(self.card_mccabe,     0, 2)
        grid.addWidget(self.card_clap,       1, 0)
        grid.addWidget(self.card_difficulty, 1, 1)
        grid.addWidget(self.card_top_error,  1, 2)

        return grid

    # ──────────────────────────────────────────────
    # 피드백 섹션
    # ──────────────────────────────────────────────

    def _build_feedback_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(frame)

        header = QLabel("최근 분석 피드백")
        header.setFont(FONT_LABEL)
        header.setStyleSheet("color: #0c5460; font-weight: bold;")

        self.feedback_label = QLabel("아직 분석된 코드가 없습니다.")
        self.feedback_label.setFont(FONT_LABEL)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet("color: #0c5460;")

        layout.addWidget(header)
        layout.addWidget(self.feedback_label)

        return frame

    # ──────────────────────────────────────────────
    # 등록 폴더 섹션
    # ──────────────────────────────────────────────

    def _build_folder_section(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        header = QLabel("감시 중인 폴더")
        header.setFont(FONT_LABEL)
        header.setStyleSheet("font-weight: bold; color: #495057;")

        self.folder_label = QLabel("등록된 폴더가 없습니다.")
        self.folder_label.setFont(FONT_LABEL)
        self.folder_label.setStyleSheet("color: #6c757d;")
        self.folder_label.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(self.folder_label)

        return layout

    # ──────────────────────────────────────────────
    # 하단 내비게이션 버튼
    # ──────────────────────────────────────────────

    def _build_nav_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        btn_chart = QPushButton("📊 차트 보기")
        btn_chart.setFont(FONT_BUTTON)
        btn_chart.setFixedHeight(36)
        btn_chart.clicked.connect(self.navigate_to_chart.emit)

        btn_settings = QPushButton("⚙️ 설정")
        btn_settings.setFont(FONT_BUTTON)
        btn_settings.setFixedHeight(36)
        btn_settings.clicked.connect(self.navigate_to_settings.emit)

        layout.addWidget(btn_chart)
        layout.addWidget(btn_settings)
        layout.addStretch()

        return layout

    # ──────────────────────────────────────────────
    # 데이터 업데이트
    # ──────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        stats = data.summary_stats

        self.card_sessions.set_value(str(stats.total_sessions))
        self.card_errors.set_value(str(stats.total_errors))
        self.card_mccabe.set_value(f"{stats.avg_mccabe_score:.1f}")
        self.card_clap.set_value(f"{stats.avg_clap_score:.1f}")
        self.card_difficulty.set_value(data.difficulty_score.label)
        self.card_top_error.set_value(stats.most_frequent_error)

        if data.latest_session:
            feedback = data.latest_session.ast_result.feedback_message
            self.feedback_label.setText(feedback if feedback else "피드백 없음")
        else:
            self.feedback_label.setText("아직 분석된 코드가 없습니다.")

        if data.registered_folders:
            self.folder_label.setText("\n".join(data.registered_folders))
        else:
            self.folder_label.setText("등록된 폴더가 없습니다.")