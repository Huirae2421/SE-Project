"""
chart_view.py: 학습 데이터 시각화 화면
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFrame
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from ..controllers.app_controller import AppController
from ..models.data_models import ChartData


# ──────────────────────────────────────────────
# 한글 폰트 설정
# ──────────────────────────────────────────────

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

FONT_TITLE  = QFont("맑은 고딕", 18, QFont.Bold)
FONT_LABEL  = QFont("맑은 고딕", 11)
FONT_BUTTON = QFont("맑은 고딕", 10)

COLOR_PRIMARY = "#4A90D9"
COLOR_AVERAGE = "#E74C3C"
COLOR_AREA    = "#85C1E9"


# ──────────────────────────────────────────────
# ChartCanvas
# ──────────────────────────────────────────────

class ChartCanvas(FigureCanvas):

    def __init__(self, width: int = 6, height: int = 4):
        self.fig = Figure(figsize=(width, height), tight_layout=True)
        super().__init__(self.fig)

    def clear(self) -> None:
        self.fig.clear()
        self.draw()


# ──────────────────────────────────────────────
# ChartView
# ──────────────────────────────────────────────

class ChartView(QWidget):

    navigate_to_dashboard = pyqtSignal()

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

        self.tabs = QTabWidget()
        self.tabs.setFont(FONT_LABEL)
        layout.addWidget(self.tabs)

        self._build_tabs()
        layout.addLayout(self._build_nav_buttons())

    # ──────────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        title = QLabel("학습 데이터 시각화")
        title.setFont(FONT_TITLE)

        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 탭 구성
    # ──────────────────────────────────────────────

    def _build_tabs(self) -> None:
        self.canvas_error_bar       = ChartCanvas()
        self.canvas_activity_line   = ChartCanvas()
        self.canvas_mccabe_line     = ChartCanvas()
        self.canvas_clap_line       = ChartCanvas()
        self.canvas_difficulty_area = ChartCanvas()
        self.canvas_error_pie       = ChartCanvas()

        self.tabs.addTab(self.canvas_error_bar,       "오류 발생 횟수")
        self.tabs.addTab(self.canvas_activity_line,   "날짜별 학습 활동")
        self.tabs.addTab(self.canvas_mccabe_line,     "McCabe 복잡도")
        self.tabs.addTab(self.canvas_clap_line,       "CLAP 복잡도")
        self.tabs.addTab(self.canvas_difficulty_area, "난이도 변화")
        self.tabs.addTab(self.canvas_error_pie,       "오류 유형 분포")

    # ──────────────────────────────────────────────
    # 하단 내비게이션 버튼
    # ──────────────────────────────────────────────

    def _build_nav_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        btn_back = QPushButton("← 대시보드로")
        btn_back.setFont(FONT_BUTTON)
        btn_back.setFixedHeight(36)
        btn_back.clicked.connect(self.navigate_to_dashboard.emit)

        layout.addWidget(btn_back)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 차트 로드
    # ──────────────────────────────────────────────

    def load_charts(self) -> None:
        chart_data = self.controller.get_chart_data()

        if not chart_data.has_enough_data:
            self._draw_no_data_all()
            return

        self._draw_error_bar(chart_data)
        self._draw_activity_line(chart_data)
        self._draw_mccabe_line(chart_data)
        self._draw_clap_line(chart_data)
        self._draw_difficulty_area(chart_data)
        self._draw_error_pie(chart_data)

    def _draw_no_data_all(self) -> None:
        for canvas in [
            self.canvas_error_bar, self.canvas_activity_line,
            self.canvas_mccabe_line, self.canvas_clap_line,
            self.canvas_difficulty_area, self.canvas_error_pie
        ]:
            canvas.fig.clear()
            ax = canvas.fig.add_subplot(111)
            ax.text(
                0.5, 0.5,
                "데이터가 부족합니다.\n5회 이상 분석 후 활성화됩니다.",
                ha="center", va="center",
                fontsize=12, color="#6c757d",
                transform=ax.transAxes
            )
            ax.axis("off")
            canvas.draw()

    # ──────────────────────────────────────────────
    # 막대 그래프: 오류 유형별 발생 횟수
    # ──────────────────────────────────────────────

    def _draw_error_bar(self, data: ChartData) -> None:
        canvas = self.canvas_error_bar
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)

        if not data.error_bar:
            ax.text(0.5, 0.5, "오류 기록 없음", ha="center", va="center",
                    transform=ax.transAxes, color="#6c757d")
            ax.axis("off")
        else:
            keys = list(data.error_bar.keys())
            values = list(data.error_bar.values())
            bars = ax.bar(keys, values, color=COLOR_PRIMARY, edgecolor="white")
            ax.set_title("오류 유형별 발생 횟수", fontsize=12)
            ax.set_xlabel("오류 유형")
            ax.set_ylabel("발생 횟수")
            ax.bar_label(bars, padding=3)

        canvas.draw()

    # ──────────────────────────────────────────────
    # 꺾은선 그래프: 날짜별 학습 활동 횟수
    # ──────────────────────────────────────────────

    def _draw_activity_line(self, data: ChartData) -> None:
        canvas = self.canvas_activity_line
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)

        if not data.activity_line:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center",
                    transform=ax.transAxes, color="#6c757d")
            ax.axis("off")
        else:
            dates  = [d["date"]  for d in data.activity_line]
            counts = [d["count"] for d in data.activity_line]
            ax.plot(dates, counts, marker="o", color=COLOR_PRIMARY, linewidth=2)
            ax.set_title("날짜별 학습 활동 횟수", fontsize=12)
            ax.set_xlabel("날짜")
            ax.set_ylabel("분석 횟수")
            ax.tick_params(axis="x", rotation=30)
            ax.grid(axis="y", linestyle="--", alpha=0.5)

        canvas.draw()

    # ──────────────────────────────────────────────
    # 꺾은선 그래프: McCabe 복잡도 변화
    # ──────────────────────────────────────────────

    def _draw_mccabe_line(self, data: ChartData) -> None:
        canvas = self.canvas_mccabe_line
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)

        if not data.mccabe_line:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center",
                    transform=ax.transAxes, color="#6c757d")
            ax.axis("off")
        else:
            indices = list(range(1, len(data.mccabe_line) + 1))
            scores  = [d["score"] for d in data.mccabe_line]
            ax.plot(indices, scores, marker="o", color=COLOR_PRIMARY, linewidth=2)
            ax.axhline(y=10, color="orange", linestyle="--", linewidth=1, label="단순 기준 (10)")
            ax.axhline(y=20, color=COLOR_AVERAGE, linestyle="--", linewidth=1, label="복잡 기준 (20)")
            ax.set_title("McCabe 순환 복잡도 변화", fontsize=12)
            ax.set_xlabel("분석 횟수")
            ax.set_ylabel("McCabe 점수")
            ax.legend(fontsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.5)

        canvas.draw()

    # ──────────────────────────────────────────────
    # 꺾은선 + 평균선: CLAP 복잡도 변화
    # ──────────────────────────────────────────────

    def _draw_clap_line(self, data: ChartData) -> None:
        canvas = self.canvas_clap_line
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)

        if not data.clap_line:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center",
                    transform=ax.transAxes, color="#6c757d")
            ax.axis("off")
        else:
            indices = list(range(1, len(data.clap_line) + 1))
            scores  = [d["score"] for d in data.clap_line]
            ax.plot(indices, scores, marker="o", color=COLOR_PRIMARY,
                    linewidth=2, label="CLAP 점수")
            ax.axhline(y=data.clap_average, color=COLOR_AVERAGE,
                       linestyle="--", linewidth=1.5,
                       label=f"누적 평균 ({data.clap_average:.1f})")
            ax.set_title("CLAP 복잡도 변화 (누적 평균 대비)", fontsize=12)
            ax.set_xlabel("분석 횟수")
            ax.set_ylabel("CLAP 점수")
            ax.legend(fontsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.5)

        canvas.draw()

    # ──────────────────────────────────────────────
    # 영역 그래프: 난이도 변화
    # ──────────────────────────────────────────────

    def _draw_difficulty_area(self, data: ChartData) -> None:
        canvas = self.canvas_difficulty_area
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)

        if not data.difficulty_area:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center",
                    transform=ax.transAxes, color="#6c757d")
            ax.axis("off")
        else:
            indices = list(range(1, len(data.difficulty_area) + 1))
            scores  = [d["score"] for d in data.difficulty_area]
            ax.fill_between(indices, scores, alpha=0.4, color=COLOR_AREA)
            ax.plot(indices, scores, color=COLOR_PRIMARY, linewidth=2)
            ax.set_title("학습 난이도 변화", fontsize=12)
            ax.set_xlabel("분석 횟수")
            ax.set_ylabel("난이도 점수 (0~1)")
            ax.set_ylim(0, 1)
            ax.grid(axis="y", linestyle="--", alpha=0.5)

        canvas.draw()

    # ──────────────────────────────────────────────
    # 파이 차트: 오류 유형 분포
    # ──────────────────────────────────────────────

    def _draw_error_pie(self, data: ChartData) -> None:
        canvas = self.canvas_error_pie
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)

        if not data.error_pie:
            ax.text(0.5, 0.5, "오류 기록 없음", ha="center", va="center",
                    transform=ax.transAxes, color="#6c757d")
            ax.axis("off")
        else:
            labels = list(data.error_pie.keys())
            sizes  = list(data.error_pie.values())
            ax.pie(
                sizes, labels=labels,
                autopct="%1.1f%%",
                startangle=140,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5}
            )
            ax.set_title("오류 유형 분포", fontsize=12)

        canvas.draw()