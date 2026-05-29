"""
error_helper_view.py: 오류 도우미 화면

내가 만든 오류가 무슨 뜻인지 현재 인터페이스 언어(한국어/영어)로 쉽게
풀어주고, 원인·해결 방법·잘못된 예/올바른 예 코드·학습 개념을 보여준다.
가장 최근 오류를 기본으로 보여주며, 콤보 박스로 다른 오류도 학습할 수 있다.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QScrollArea
)
from PyQt5.QtGui import QFont

from ..controllers.app_controller import AppController
from . import styles
from .i18n import tr, get_language


# ──────────────────────────────────────────────
# 코드 예시 박스 (고정폭 글꼴)
# ──────────────────────────────────────────────

class CodeBox(QLabel):

    def __init__(self, border_color: str, bg_color: str):
        super().__init__()
        self.setFont(QFont("Consolas", 10))
        self.setWordWrap(True)
        self.setTextInteractionFlags(self.textInteractionFlags())
        self.setStyleSheet(
            f"background-color: {bg_color}; border: 1px solid {border_color}; "
            f"border-radius: 6px; padding: 8px; color: #212529;"
        )


# ──────────────────────────────────────────────
# ErrorHelperView
# ──────────────────────────────────────────────

class ErrorHelperView(QWidget):

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
        layout.setSpacing(12)

        self.title_label = QLabel(tr("helper.title"))
        self.title_label.setFont(styles.FONT_TITLE)
        layout.addWidget(self.title_label)

        self.intro_label = QLabel(tr("helper.intro"))
        self.intro_label.setFont(styles.FONT_LABEL)
        self.intro_label.setWordWrap(True)
        self.intro_label.setStyleSheet(f"color: {styles.COLOR_MUTED};")
        layout.addWidget(self.intro_label)

        # 오류 종류 선택
        picker = QHBoxLayout()
        self.pick_label = QLabel(tr("helper.pick"))
        self.pick_label.setFont(styles.FONT_LABEL)
        self.error_combo = QComboBox()
        self.error_combo.setFont(styles.FONT_LABEL)
        self.error_combo.setFixedHeight(32)
        self.error_combo.currentTextChanged.connect(self._on_error_selected)
        picker.addWidget(self.pick_label)
        picker.addWidget(self.error_combo)
        picker.addStretch()
        layout.addLayout(picker)

        # 상태(최근 오류 / 오류 없음) 표시
        self.status_label = QLabel("")
        self.status_label.setFont(styles.FONT_LABEL)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {styles.COLOR_PRIMARY}; font-weight: bold;")
        layout.addWidget(self.status_label)

        # 가이드 본문 (스크롤)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.detail = QWidget()
        self.detail_layout = QVBoxLayout(self.detail)
        self.detail_layout.setSpacing(8)
        self.scroll.setWidget(self.detail)
        layout.addWidget(self.scroll)

        self._build_detail_widgets()

    # ──────────────────────────────────────────────
    # 가이드 본문 위젯 구성 (라벨/코드 박스)
    # ──────────────────────────────────────────────

    def _build_detail_widgets(self) -> None:
        self.meaning_header = self._section_header()
        self.meaning_text = self._body_label()

        self.solution_header = self._section_header()
        self.solution_text = self._body_label()

        self.wrong_header = self._section_header()
        self.wrong_code = CodeBox("#f5c6cb", "#fff3f3")

        self.fixed_header = self._section_header()
        self.fixed_code = CodeBox("#c3e6cb", "#f3fff5")

        self.concept_header = self._section_header()
        self.concept_text = self._body_label()

        for w in [
            self.meaning_header, self.meaning_text,
            self.solution_header, self.solution_text,
            self.wrong_header, self.wrong_code,
            self.fixed_header, self.fixed_code,
            self.concept_header, self.concept_text,
        ]:
            self.detail_layout.addWidget(w)
        self.detail_layout.addStretch()

    def _section_header(self) -> QLabel:
        label = QLabel("")
        label.setFont(QFont("맑은 고딕", 11, QFont.Bold))
        label.setStyleSheet("color: #343a40; margin-top: 6px;")
        return label

    def _body_label(self) -> QLabel:
        label = QLabel("")
        label.setFont(styles.FONT_LABEL)
        label.setWordWrap(True)
        return label

    # ──────────────────────────────────────────────
    # 화면 로드
    # ──────────────────────────────────────────────

    def load_helper(self) -> None:
        # 콤보 박스를 지원 오류 목록으로 채운다
        self.error_combo.blockSignals(True)
        self.error_combo.clear()
        self.error_combo.addItems(self.controller.get_supported_errors())
        self.error_combo.blockSignals(False)

        latest = self.controller.get_latest_error()
        if latest and latest["error_type"] in self.controller.get_supported_errors():
            self.status_label.setText(
                f"{tr('helper.latest')}: {latest['error_type']}"
            )
            self.error_combo.setCurrentText(latest["error_type"])
            self._show_guide(latest["error_type"])
        else:
            self.status_label.setText(tr("helper.no_error"))
            if self.error_combo.count() > 0:
                self._show_guide(self.error_combo.currentText())

    def _on_error_selected(self, error_type: str) -> None:
        if error_type:
            self._show_guide(error_type)

    # ──────────────────────────────────────────────
    # 선택된 오류의 가이드 표시 (현재 언어로)
    # ──────────────────────────────────────────────

    def _show_guide(self, error_type: str) -> None:
        lang = get_language()
        provider = self.controller.guide_provider
        guide = provider.get_guide(error_type)
        if guide is None:
            return

        self.meaning_header.setText(
            f"{tr('helper.section.meaning')}  ({error_type})"
        )
        self.meaning_text.setText(provider.get_cause(error_type, lang))

        self.solution_header.setText(tr("helper.section.solution"))
        self.solution_text.setText(provider.get_solution_text(error_type, lang))

        self.wrong_header.setText(tr("helper.section.wrong"))
        self.wrong_code.setText(guide.example_wrong)

        self.fixed_header.setText(tr("helper.section.fixed"))
        self.fixed_code.setText(guide.example_fixed)

        self.concept_header.setText(tr("helper.section.concept"))
        self.concept_text.setText(provider.get_concept(error_type, lang))

    # ──────────────────────────────────────────────
    # 언어 변경 시 텍스트 갱신
    # ──────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self.title_label.setText(tr("helper.title"))
        self.intro_label.setText(tr("helper.intro"))
        self.pick_label.setText(tr("helper.pick"))
        # 현재 선택된 오류를 새 언어로 다시 표시
        self.load_helper()
