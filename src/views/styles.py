"""
styles.py: UI 공통 폰트, 색상, 스타일 정의

각 화면에 흩어져 있던 폰트와 색상 값을 한 곳에서 관리하여
앱 전체의 디자인을 일관되게 유지한다.
"""

from PyQt5.QtGui import QFont


# ──────────────────────────────────────────────
# 폰트
# ──────────────────────────────────────────────

FONT_TITLE  = QFont("맑은 고딕", 18, QFont.Bold)
FONT_LABEL  = QFont("맑은 고딕", 11)
FONT_VALUE  = QFont("맑은 고딕", 13, QFont.Bold)
FONT_BUTTON = QFont("맑은 고딕", 10)
FONT_NAV    = QFont("맑은 고딕", 11, QFont.Bold)


# ──────────────────────────────────────────────
# 색상 팔레트
# ──────────────────────────────────────────────

COLOR_PRIMARY      = "#4A90D9"
COLOR_PRIMARY_DARK = "#357ABD"
COLOR_BG           = "#ffffff"
COLOR_PANEL        = "#f8f9fa"
COLOR_BORDER       = "#dee2e6"
COLOR_TEXT         = "#212529"
COLOR_MUTED        = "#6c757d"

COLOR_NAV_BG         = "#2c3e50"
COLOR_NAV_TEXT       = "#ecf0f1"
COLOR_NAV_PILL       = "#3b4f63"   # 비활성 버튼: 바 배경과 비슷한 톤
COLOR_NAV_PILL_HOVER = "#46607a"   # 비활성 버튼 마우스 오버

# 난이도 레이블별 강조 색상
COLOR_DANGER  = "#dc3545"
COLOR_WARNING = "#fd7e14"
COLOR_SUCCESS = "#28a745"


# ──────────────────────────────────────────────
# 난이도 → 색상 매핑
# ──────────────────────────────────────────────

DIFFICULTY_COLORS = {
    "very hard":         COLOR_DANGER,
    "harder than usual": COLOR_WARNING,
    "average":           COLOR_PRIMARY,
    "easy":              COLOR_SUCCESS,
    "collecting data":   COLOR_MUTED,
}


def difficulty_color(label: str) -> str:
    """난이도 레이블에 해당하는 강조 색상을 반환한다."""
    return DIFFICULTY_COLORS.get(label, COLOR_MUTED)


# ──────────────────────────────────────────────
# 공통 스타일시트 조각
# ──────────────────────────────────────────────

def panel_style(bg: str = COLOR_PANEL, border: str = COLOR_BORDER) -> str:
    return f"""
        QFrame {{
            background-color: {bg};
            border: 1px solid {border};
            border-radius: 8px;
            padding: 8px;
        }}
    """


def primary_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLOR_PRIMARY};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_PRIMARY_DARK};
        }}
    """
