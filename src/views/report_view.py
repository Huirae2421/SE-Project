"""
report_view.py: 학습 리포트 화면 구성

대시보드의 분석 데이터를 종합한 학습 리포트를 한 화면에서 보여준다.
초보 학습자가 자신의 오류 패턴과 개선 방향을 쉽게 확인할 수 있도록
HTML 형식으로 렌더링하여 표시하며, 파일로 저장하는 기능도 제공한다.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextBrowser, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter

from ..controllers.app_controller import AppController
from .i18n import tr


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

FONT_TITLE  = QFont("맑은 고딕", 18, QFont.Bold)
FONT_LABEL  = QFont("맑은 고딕", 11)
FONT_BUTTON = QFont("맑은 고딕", 10)


# ──────────────────────────────────────────────
# ReportView
# ──────────────────────────────────────────────

class ReportView(QWidget):

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
        layout.addWidget(self._build_report_area())
        layout.addLayout(self._build_nav_buttons())

    # ──────────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.title_label = QLabel(tr("report.title"))
        self.title_label.setFont(FONT_TITLE)

        layout.addWidget(self.title_label)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 리포트 표시 영역
    # ──────────────────────────────────────────────

    def _build_report_area(self) -> QTextBrowser:
        self.report_browser = QTextBrowser()
        self.report_browser.setOpenExternalLinks(False)
        self.report_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        return self.report_browser

    # ──────────────────────────────────────────────
    # 하단 내비게이션 버튼
    # ──────────────────────────────────────────────

    def _build_nav_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.btn_save = QPushButton(tr("report.save_html"))
        self.btn_save.setFont(FONT_BUTTON)
        self.btn_save.setFixedHeight(36)
        self.btn_save.clicked.connect(self._on_save_clicked)

        self.btn_pdf = QPushButton(tr("report.save_pdf"))
        self.btn_pdf.setFont(FONT_BUTTON)
        self.btn_pdf.setFixedHeight(36)
        self.btn_pdf.clicked.connect(self._on_save_pdf_clicked)

        layout.addStretch()
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_pdf)
        return layout

    # ──────────────────────────────────────────────
    # 언어 변경 시 텍스트 갱신
    # ──────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self.title_label.setText(tr("report.title"))
        self.btn_save.setText(tr("report.save_html"))
        self.btn_pdf.setText(tr("report.save_pdf"))

    # ──────────────────────────────────────────────
    # 리포트 로드
    # ──────────────────────────────────────────────

    def load_report(self) -> None:
        html = self.controller.get_report_html()
        self.report_browser.setHtml(html)

    # ──────────────────────────────────────────────
    # 리포트 저장
    # ──────────────────────────────────────────────

    def _on_save_clicked(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "리포트 저장",
            "학습_리포트.html",
            "HTML 파일 (*.html)"
        )

        if not file_path:
            return

        saved = self.controller.save_report_html(file_path)
        if saved:
            QMessageBox.information(
                self, "저장 완료",
                f"리포트를 저장했습니다.\n{file_path}"
            )
        else:
            QMessageBox.warning(
                self, "저장 실패",
                "리포트 저장 중 문제가 발생했습니다."
            )

    # ──────────────────────────────────────────────
    # 리포트 PDF 저장
    # ──────────────────────────────────────────────

    def _on_save_pdf_clicked(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF로 저장",
            "학습_리포트.pdf",
            "PDF 파일 (*.pdf)"
        )

        if not file_path:
            return

        if self._export_pdf(file_path):
            QMessageBox.information(
                self, "저장 완료",
                f"PDF로 저장했습니다.\n{file_path}"
            )
        else:
            QMessageBox.warning(
                self, "저장 실패",
                "PDF 저장 중 문제가 발생했습니다."
            )

    def _export_pdf(self, file_path: str) -> bool:
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            # 화면에 표시 중인 리포트 내용을 그대로 PDF로 출력한다
            self.report_browser.document().print_(printer)
            return True
        except Exception:
            return False
