"""
settings_view.py: 설정 화면 구성
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QFrame,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from ..controllers.app_controller import AppController


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

FONT_TITLE  = QFont("맑은 고딕", 18, QFont.Bold)
FONT_LABEL  = QFont("맑은 고딕", 11)
FONT_BUTTON = QFont("맑은 고딕", 10)


# ──────────────────────────────────────────────
# SettingsView
# ──────────────────────────────────────────────

class SettingsView(QWidget):

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
        layout.addWidget(self._build_folder_section())
        layout.addWidget(self._build_reset_section())
        layout.addStretch()
        layout.addLayout(self._build_nav_buttons())

    # ──────────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        title = QLabel("설정")
        title.setFont(FONT_TITLE)

        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 폴더 관리 섹션
    # ──────────────────────────────────────────────

    def _build_folder_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        header = QLabel("감시 폴더 관리")
        header.setFont(FONT_LABEL)
        header.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(header)

        input_layout = QHBoxLayout()

        self.folder_input = QLineEdit()
        self.folder_input.setFont(FONT_LABEL)
        self.folder_input.setPlaceholderText("폴더 경로를 입력하거나 선택하세요")
        self.folder_input.setFixedHeight(34)

        btn_browse = QPushButton("폴더 선택")
        btn_browse.setFont(FONT_BUTTON)
        btn_browse.setFixedHeight(34)
        btn_browse.clicked.connect(self._browse_folder)

        btn_add = QPushButton("등록")
        btn_add.setFont(FONT_BUTTON)
        btn_add.setFixedHeight(34)
        btn_add.setStyleSheet("background-color: #4A90D9; color: white; border-radius: 4px;")
        btn_add.clicked.connect(self._add_folder)

        input_layout.addWidget(self.folder_input)
        input_layout.addWidget(btn_browse)
        input_layout.addWidget(btn_add)
        layout.addLayout(input_layout)

        self.folder_list = QListWidget()
        self.folder_list.setFont(FONT_LABEL)
        self.folder_list.setFixedHeight(150)
        layout.addWidget(self.folder_list)

        btn_remove = QPushButton("선택한 폴더 제거")
        btn_remove.setFont(FONT_BUTTON)
        btn_remove.setFixedHeight(34)
        btn_remove.clicked.connect(self._remove_folder)
        layout.addWidget(btn_remove)

        return frame

    # ──────────────────────────────────────────────
    # 데이터 초기화 섹션
    # ──────────────────────────────────────────────

    def _build_reset_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #fff3f3;
                border: 1px solid #f5c6cb;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        header = QLabel("데이터 초기화")
        header.setFont(FONT_LABEL)
        header.setStyleSheet("font-weight: bold; color: #721c24;")

        desc = QLabel("모든 학습 데이터와 오류 로그를 삭제합니다. 이 작업은 되돌릴 수 없습니다.")
        desc.setFont(FONT_LABEL)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #721c24;")

        btn_reset = QPushButton("전체 데이터 초기화")
        btn_reset.setFont(FONT_BUTTON)
        btn_reset.setFixedHeight(34)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_reset.clicked.connect(self._confirm_reset)

        layout.addWidget(header)
        layout.addWidget(desc)
        layout.addWidget(btn_reset)

        return frame

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
    # 설정 로드
    # ──────────────────────────────────────────────

    def load_settings(self) -> None:
        self.folder_list.clear()
        folders = self.controller.file_watcher.get_watching_folders()
        for folder in folders:
            self.folder_list.addItem(QListWidgetItem(folder))

    # ──────────────────────────────────────────────
    # 폴더 추가 / 제거
    # ──────────────────────────────────────────────

    def _browse_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder_path:
            self.folder_input.setText(folder_path)

    def _add_folder(self) -> None:
        folder_path = self.folder_input.text().strip()
        if not folder_path:
            QMessageBox.warning(self, "경고", "폴더 경로를 입력해주세요.")
            return

        result = self.controller.register_folder(folder_path)
        if result["success"]:
            self.folder_list.addItem(QListWidgetItem(folder_path))
            self.folder_input.clear()
            QMessageBox.information(self, "완료", f"폴더가 등록되었습니다.\n{folder_path}")
        else:
            QMessageBox.warning(self, "오류", result["error"])

    def _remove_folder(self) -> None:
        selected = self.folder_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "경고", "제거할 폴더를 선택해주세요.")
            return

        folder_path = selected.text()
        self.controller.unregister_folder(folder_path)
        self.folder_list.takeItem(self.folder_list.row(selected))
        QMessageBox.information(self, "완료", f"폴더가 제거되었습니다.\n{folder_path}")

    # ──────────────────────────────────────────────
    # 데이터 초기화
    # ──────────────────────────────────────────────

    def _confirm_reset(self) -> None:
        reply = QMessageBox.question(
            self,
            "데이터 초기화",
            "모든 학습 데이터를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.controller.reset_all_data()
            if success:
                QMessageBox.information(self, "완료", "모든 데이터가 초기화되었습니다.")
            else:
                QMessageBox.critical(self, "오류", "초기화 중 오류가 발생했습니다.")