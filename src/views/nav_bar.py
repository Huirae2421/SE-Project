"""
nav_bar.py: 상단 고정 네비게이션 바

모든 화면 위쪽에 항상 표시되어, 어느 화면에서든 한 번의 클릭으로
대시보드 / 차트 / 리포트 / 설정 사이를 이동할 수 있게 한다.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt

from . import styles
from .i18n import tr


# ──────────────────────────────────────────────
# 네비게이션 항목 정의 (번역 키, 페이지 인덱스)
# ──────────────────────────────────────────────

NAV_ITEMS = [
    ("nav.dashboard", 0),
    ("nav.chart", 1),
    ("nav.report", 3),
    ("nav.helper", 4),
    ("nav.settings", 2),
]


# ──────────────────────────────────────────────
# NavBar
# ──────────────────────────────────────────────

class NavBar(QWidget):

    navigate = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._buttons = {}
        self._init_ui()

    # ──────────────────────────────────────────────
    # UI 초기화
    # ──────────────────────────────────────────────

    def _init_ui(self) -> None:
        # QWidget 은 기본적으로 스타일시트 배경을 칠하지 않으므로 속성을 켠다
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {styles.COLOR_NAV_BG};")
        self.setFixedHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        brand = QLabel("CLAP")
        brand.setFont(styles.FONT_NAV)
        brand.setStyleSheet(
            f"color: {styles.COLOR_NAV_TEXT}; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(brand)
        layout.addSpacing(20)

        self._keys = {}
        for key, page_index in NAV_ITEMS:
            button = QPushButton(tr(key))
            button.setFont(styles.FONT_NAV)
            button.setFixedHeight(38)
            # 너비는 글자 길이에 맞춰 자연스럽게 달라지도록 둔다
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(
                lambda _checked, idx=page_index: self.navigate.emit(idx)
            )
            self._buttons[page_index] = button
            self._keys[page_index] = key
            layout.addWidget(button)

        layout.addStretch()
        self.set_active(0)

    # ──────────────────────────────────────────────
    # 언어 변경 시 텍스트 갱신
    # ──────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        for page_index, button in self._buttons.items():
            button.setText(tr(self._keys[page_index]))

    # ──────────────────────────────────────────────
    # 활성 탭 표시
    # ──────────────────────────────────────────────

    def set_active(self, page_index: int) -> None:
        for idx, button in self._buttons.items():
            if idx == page_index:
                button.setStyleSheet(self._active_style())
            else:
                button.setStyleSheet(self._inactive_style())

    def _active_style(self) -> str:
        # 선택된 탭: 파란색 알약 + 흰 글자
        return f"""
            QPushButton {{
                background-color: {styles.COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 4px 16px;
            }}
        """

    def _inactive_style(self) -> str:
        # 비활성 탭: 바 배경과 비슷한 톤의 둥근 알약 + 또렷한 글자
        return f"""
            QPushButton {{
                background-color: {styles.COLOR_NAV_PILL};
                color: {styles.COLOR_NAV_TEXT};
                border: none;
                border-radius: 8px;
                padding: 4px 16px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLOR_NAV_PILL_HOVER};
            }}
        """
