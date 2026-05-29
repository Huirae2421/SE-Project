"""
dashboard_view.py: 대시보드 화면 구성
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGridLayout
)
from PyQt5.QtGui import QFont

from ..controllers.app_controller import AppController
from ..models.data_models import DashboardData
from ..models.report_generator import describe_mccabe
from . import styles
from .i18n import tr


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

FONT_TITLE  = QFont("맑은 고딕", 18, QFont.Bold)
FONT_LABEL  = QFont("맑은 고딕", 11)
FONT_VALUE  = QFont("맑은 고딕", 13, QFont.Bold)


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

    def set_value_color(self, color: str) -> None:
        self.value_label.setStyleSheet(f"color: {color};")


# ──────────────────────────────────────────────
# DashboardView
# ──────────────────────────────────────────────

class DashboardView(QWidget):

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

    # ──────────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.title_label = QLabel(tr("dash.title"))
        self.title_label.setFont(FONT_TITLE)

        layout.addWidget(self.title_label)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 통계 카드
    # ──────────────────────────────────────────────

    def _build_stat_cards(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(12)

        self.card_sessions     = StatCard(tr("dash.card.sessions"))
        self.card_errors       = StatCard(tr("dash.card.errors"))
        self.card_mccabe       = StatCard(tr("dash.card.mccabe"))
        self.card_clap         = StatCard(tr("dash.card.clap"))
        self.card_difficulty   = StatCard(tr("dash.card.difficulty"))
        self.card_top_error    = StatCard(tr("dash.card.toperror"))

        # 초보자용 설명 (마우스를 올리면 표시)
        self.card_sessions.setToolTip("지금까지 코드를 분석한 총 횟수예요.")
        self.card_errors.setToolTip("분석 중 발생한 오류의 총 개수예요.")
        self.card_mccabe.setToolTip(
            "코드 안의 갈림길(if/for 등) 개수예요. 낮을수록 단순합니다.\n"
            "10 이하: 단순 / 11~20: 주의 / 21 이상: 복잡(함수 분리 권장)"
        )
        self.card_clap.setToolTip(
            "함수 길이·중첩 깊이까지 반영한 나만의 복잡도 점수예요.\n"
            "내 평소 평균과 비교해 높고 낮음을 봅니다."
        )
        self.card_difficulty.setToolTip(
            "오류 수·복잡도·풀이 시간을 종합한 값이에요.\n"
            "남과 비교하는 게 아니라 내 평소 기록 대비로 해석합니다."
        )
        self.card_top_error.setToolTip("가장 자주 발생한 오류 유형이에요.")

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

        self.feedback_header = QLabel(tr("dash.feedback.header"))
        self.feedback_header.setFont(FONT_LABEL)
        self.feedback_header.setStyleSheet("color: #0c5460; font-weight: bold;")
        header = self.feedback_header

        self.feedback_label = QLabel(tr("dash.feedback.empty"))
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

        self.folder_header = QLabel(tr("dash.folder.header"))
        self.folder_header.setFont(FONT_LABEL)
        self.folder_header.setStyleSheet("font-weight: bold; color: #495057;")
        header = self.folder_header

        self.folder_label = QLabel(tr("dash.folder.empty"))
        self.folder_label.setFont(FONT_LABEL)
        self.folder_label.setStyleSheet("color: #6c757d;")
        self.folder_label.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(self.folder_label)

        return layout

    # ──────────────────────────────────────────────
    # 데이터 업데이트
    # ──────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        stats = data.summary_stats

        self.card_sessions.set_value(str(stats.total_sessions))
        self.card_errors.set_value(str(stats.total_errors))
        self.card_mccabe.set_value(
            f"{stats.avg_mccabe_score:.1f} ({describe_mccabe(stats.avg_mccabe_score)})"
        )
        self.card_clap.set_value(f"{stats.avg_clap_score:.1f}")
        self.card_difficulty.set_value(data.difficulty_score.label)
        self.card_difficulty.set_value_color(
            styles.difficulty_color(data.difficulty_score.label)
        )
        self.card_top_error.set_value(stats.most_frequent_error)

        if data.latest_session:
            feedback = data.latest_session.ast_result.feedback_message
            self.feedback_label.setText(feedback if feedback else "-")
        else:
            self.feedback_label.setText(tr("dash.feedback.empty"))

        if data.registered_folders:
            self.folder_label.setText("\n".join(data.registered_folders))
        else:
            self.folder_label.setText(tr("dash.folder.empty"))

    # ──────────────────────────────────────────────
    # 언어 변경 시 텍스트 갱신
    # ──────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self.title_label.setText(tr("dash.title"))
        self.card_sessions.title_label.setText(tr("dash.card.sessions"))
        self.card_errors.title_label.setText(tr("dash.card.errors"))
        self.card_mccabe.title_label.setText(tr("dash.card.mccabe"))
        self.card_clap.title_label.setText(tr("dash.card.clap"))
        self.card_difficulty.title_label.setText(tr("dash.card.difficulty"))
        self.card_top_error.title_label.setText(tr("dash.card.toperror"))
        self.feedback_header.setText(tr("dash.feedback.header"))
        self.folder_header.setText(tr("dash.folder.header"))