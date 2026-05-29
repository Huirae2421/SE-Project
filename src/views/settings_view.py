"""
settings_view.py: 설정 화면 구성
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QFrame,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..controllers.app_controller import AppController
from . import styles
from .i18n import tr, LANG_KO, LANG_EN


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

    # 언어가 변경되면 새 언어 코드를 담아 발신한다
    language_changed = pyqtSignal(str)

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
        layout.addWidget(self._build_language_section())
        layout.addWidget(self._build_folder_section())
        layout.addWidget(self._build_reset_section())
        layout.addStretch()

    # ──────────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.title_label = QLabel(tr("settings.title"))
        self.title_label.setFont(FONT_TITLE)

        layout.addWidget(self.title_label)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────
    # 언어 설정 섹션
    # ──────────────────────────────────────────────

    def _build_language_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(styles.panel_style())

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        self.lang_header = QLabel(tr("settings.lang.header"))
        self.lang_header.setFont(FONT_LABEL)
        self.lang_header.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(self.lang_header)

        buttons = QHBoxLayout()
        self.btn_ko = QPushButton("한국어")
        self.btn_en = QPushButton("English")
        for btn, lang in [(self.btn_ko, LANG_KO), (self.btn_en, LANG_EN)]:
            btn.setFont(FONT_BUTTON)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _c, lng=lang: self._on_language_clicked(lng))
            buttons.addWidget(btn)
        buttons.addStretch()
        layout.addLayout(buttons)

        self._refresh_lang_buttons()
        return frame

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

        self.folder_header = QLabel(tr("settings.folder.header"))
        self.folder_header.setFont(FONT_LABEL)
        self.folder_header.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(self.folder_header)

        input_layout = QHBoxLayout()

        self.folder_input = QLineEdit()
        self.folder_input.setFont(FONT_LABEL)
        self.folder_input.setPlaceholderText(tr("settings.folder.placeholder"))
        self.folder_input.setFixedHeight(34)

        self.btn_browse = QPushButton(tr("settings.folder.browse"))
        self.btn_browse.setFont(FONT_BUTTON)
        self.btn_browse.setFixedHeight(34)
        self.btn_browse.clicked.connect(self._browse_folder)

        self.btn_add = QPushButton(tr("settings.folder.add"))
        self.btn_add.setFont(FONT_BUTTON)
        self.btn_add.setFixedHeight(34)
        self.btn_add.setStyleSheet("background-color: #4A90D9; color: white; border-radius: 4px;")
        self.btn_add.clicked.connect(self._add_folder)

        input_layout.addWidget(self.folder_input)
        input_layout.addWidget(self.btn_browse)
        input_layout.addWidget(self.btn_add)
        layout.addLayout(input_layout)

        self.folder_list = QListWidget()
        self.folder_list.setFont(FONT_LABEL)
        self.folder_list.setFixedHeight(150)
        layout.addWidget(self.folder_list)

        self.btn_remove = QPushButton(tr("settings.folder.remove"))
        self.btn_remove.setFont(FONT_BUTTON)
        self.btn_remove.setFixedHeight(34)
        self.btn_remove.clicked.connect(self._remove_folder)
        layout.addWidget(self.btn_remove)

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

        self.reset_header = QLabel(tr("settings.reset.header"))
        self.reset_header.setFont(FONT_LABEL)
        self.reset_header.setStyleSheet("font-weight: bold; color: #721c24;")
        header = self.reset_header

        self.reset_desc = QLabel(tr("settings.reset.desc"))
        self.reset_desc.setFont(FONT_LABEL)
        self.reset_desc.setWordWrap(True)
        self.reset_desc.setStyleSheet("color: #721c24;")
        desc = self.reset_desc

        self.btn_reset = QPushButton(tr("settings.reset.button"))
        btn_reset = self.btn_reset
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
    # 설정 로드
    # ──────────────────────────────────────────────

    def load_settings(self) -> None:
        self.folder_list.clear()
        folders = self.controller.file_watcher.get_watching_folders()
        for folder in folders:
            self.folder_list.addItem(QListWidgetItem(folder))
        self._refresh_lang_buttons()

    # ──────────────────────────────────────────────
    # 언어 선택
    # ──────────────────────────────────────────────

    def _on_language_clicked(self, lang: str) -> None:
        self.controller.set_language(lang)
        self._refresh_lang_buttons()
        self.language_changed.emit(lang)

    def _refresh_lang_buttons(self) -> None:
        current = self.controller.get_language(LANG_KO)
        self.btn_ko.setChecked(current == LANG_KO)
        self.btn_en.setChecked(current == LANG_EN)

    # ──────────────────────────────────────────────
    # 언어 변경 시 텍스트 갱신
    # ──────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self.title_label.setText(tr("settings.title"))
        self.lang_header.setText(tr("settings.lang.header"))
        self.folder_header.setText(tr("settings.folder.header"))
        self.folder_input.setPlaceholderText(tr("settings.folder.placeholder"))
        self.btn_browse.setText(tr("settings.folder.browse"))
        self.btn_add.setText(tr("settings.folder.add"))
        self.btn_remove.setText(tr("settings.folder.remove"))
        self.reset_header.setText(tr("settings.reset.header"))
        self.reset_desc.setText(tr("settings.reset.desc"))
        self.btn_reset.setText(tr("settings.reset.button"))

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