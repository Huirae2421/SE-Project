"""
i18n.py: 인터페이스 다국어(한국어/영어) 지원

화면에 보이는 라벨·버튼 등 인터페이스 텍스트를 한국어와 영어로
전환할 수 있게 한다. tr(key) 로 현재 언어의 문자열을 얻고,
set_language() 로 언어를 바꾼다.
"""

# 지원 언어
LANG_KO = "ko"
LANG_EN = "en"

# 현재 언어 (기본 한국어)
_current = LANG_KO


# ──────────────────────────────────────────────
# 번역 문자열 (key -> {ko, en})
# ──────────────────────────────────────────────

STRINGS = {
    # 네비게이션
    "nav.dashboard": {"ko": "🏠 대시보드", "en": "🏠 Dashboard"},
    "nav.chart":     {"ko": "📊 차트", "en": "📊 Charts"},
    "nav.report":    {"ko": "📄 리포트", "en": "📄 Report"},
    "nav.helper":    {"ko": "🩹 오류 도우미", "en": "🩹 Error Helper"},
    "nav.settings":  {"ko": "⚙️ 설정", "en": "⚙️ Settings"},

    # 대시보드
    "dash.title":          {"ko": "CLAP 대시보드", "en": "CLAP Dashboard"},
    "dash.card.sessions":  {"ko": "총 분석 횟수", "en": "Total Analyses"},
    "dash.card.errors":    {"ko": "총 오류 발생", "en": "Total Errors"},
    "dash.card.mccabe":    {"ko": "평균 McCabe 점수", "en": "Avg McCabe Score"},
    "dash.card.clap":      {"ko": "평균 CLAP 점수", "en": "Avg CLAP Score"},
    "dash.card.difficulty": {"ko": "현재 난이도", "en": "Current Difficulty"},
    "dash.card.toperror":  {"ko": "가장 많은 오류", "en": "Most Frequent Error"},
    "dash.feedback.header": {"ko": "최근 분석 피드백", "en": "Latest Feedback"},
    "dash.feedback.empty": {
        "ko": "아직 분석된 코드가 없습니다.\n설정에서 폴더를 등록한 뒤, 편집기에서 .py 파일을 저장하면\n자동으로 분석이 시작됩니다.",
        "en": "No code analyzed yet.\nRegister a folder in Settings, then save a .py file in your editor\nto start analysis automatically.",
    },
    "dash.folder.header":  {"ko": "감시 중인 폴더", "en": "Watched Folders"},
    "dash.folder.empty":   {"ko": "등록된 폴더가 없습니다.", "en": "No folders registered."},

    # 차트
    "chart.title":       {"ko": "학습 데이터 시각화", "en": "Learning Data Charts"},
    "chart.tab.errorbar": {"ko": "오류 발생 횟수", "en": "Error Counts"},
    "chart.tab.activity": {"ko": "날짜별 학습 활동", "en": "Daily Activity"},
    "chart.tab.mccabe":  {"ko": "McCabe 복잡도", "en": "McCabe Complexity"},
    "chart.tab.clap":    {"ko": "CLAP 복잡도", "en": "CLAP Complexity"},
    "chart.tab.difficulty": {"ko": "난이도 변화", "en": "Difficulty Trend"},
    "chart.tab.errorpie": {"ko": "오류 유형 분포", "en": "Error Distribution"},

    # 리포트 화면
    "report.title":      {"ko": "학습 리포트", "en": "Learning Report"},
    "report.save_html":  {"ko": "💾 HTML 저장", "en": "💾 Save HTML"},
    "report.save_pdf":   {"ko": "📄 PDF 저장", "en": "📄 Save PDF"},

    # 오류 도우미
    "helper.title":   {"ko": "오류 도우미", "en": "Error Helper"},
    "helper.intro": {
        "ko": "내가 만든 오류가 무슨 뜻인지 쉽게 풀어주고, 어떻게 고치는지 알려줘요. 아래에서 오류 종류를 골라 자세히 볼 수도 있어요.",
        "en": "We explain what your error means in plain language and how to fix it. You can also pick an error type below to learn more.",
    },
    "helper.pick":    {"ko": "오류 종류 선택", "en": "Choose an error type"},
    "helper.latest":  {"ko": "가장 최근 오류", "en": "Latest error"},
    "helper.no_error": {
        "ko": "최근 발생한 오류가 없어요. 아래에서 오류 종류를 골라 미리 배워둘 수 있어요.",
        "en": "No recent error. You can choose an error type below to learn in advance.",
    },
    "helper.section.meaning":  {"ko": "🔎 쉬운 해석", "en": "🔎 What it means"},
    "helper.section.solution": {"ko": "💡 해결 방법", "en": "💡 How to fix"},
    "helper.section.wrong":    {"ko": "❌ 이렇게 하면 안 돼요", "en": "❌ Don't do this"},
    "helper.section.fixed":    {"ko": "✅ 이렇게 고치세요", "en": "✅ Do this instead"},
    "helper.section.concept":  {"ko": "📘 학습 개념", "en": "📘 Concept to learn"},

    # 설정
    "settings.title":        {"ko": "설정", "en": "Settings"},
    "settings.folder.header": {"ko": "감시 폴더 관리", "en": "Watched Folder Management"},
    "settings.folder.placeholder": {"ko": "폴더 경로를 입력하거나 선택하세요", "en": "Enter or choose a folder path"},
    "settings.folder.browse": {"ko": "폴더 선택", "en": "Browse"},
    "settings.folder.add":   {"ko": "등록", "en": "Add"},
    "settings.folder.remove": {"ko": "선택한 폴더 제거", "en": "Remove Selected"},
    "settings.reset.header": {"ko": "데이터 초기화", "en": "Reset Data"},
    "settings.reset.desc": {
        "ko": "모든 학습 데이터와 오류 로그를 삭제합니다. 이 작업은 되돌릴 수 없습니다.",
        "en": "Deletes all learning data and error logs. This cannot be undone.",
    },
    "settings.reset.button": {"ko": "전체 데이터 초기화", "en": "Reset All Data"},
    "settings.lang.header":  {"ko": "언어 설정", "en": "Language"},
}


# ──────────────────────────────────────────────
# API
# ──────────────────────────────────────────────

def set_language(lang: str) -> None:
    global _current
    if lang in (LANG_KO, LANG_EN):
        _current = lang


def get_language() -> str:
    return _current


def tr(key: str) -> str:
    """현재 언어의 문자열을 반환한다. 없으면 key 를 그대로 반환."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(_current, entry.get(LANG_KO, key))
