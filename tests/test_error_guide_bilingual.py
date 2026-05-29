"""
test_error_guide_bilingual.py: ErrorGuideProvider 한/영 가이드 테스트
"""

import pytest

from src.models.error_guide import ErrorGuideProvider, ERROR_GUIDES


@pytest.fixture
def provider():
    return ErrorGuideProvider()


# ──────────────────────────────────────────────
# 언어별 텍스트
# ──────────────────────────────────────────────

class TestBilingualText:

    def test_korean_cause(self, provider):
        text = provider.get_cause("NameError", "ko")
        assert "정의" in text

    def test_english_cause(self, provider):
        text = provider.get_cause("NameError", "en")
        assert "defined" in text.lower()

    def test_korean_and_english_differ(self, provider):
        assert provider.get_cause("TypeError", "ko") != provider.get_cause("TypeError", "en")

    def test_default_language_is_korean(self, provider):
        assert provider.get_solution_text("NameError") == provider.get_solution_text("NameError", "ko")

    def test_english_solution_present(self, provider):
        for error_type in ERROR_GUIDES:
            assert len(provider.get_solution_text(error_type, "en")) > 0

    def test_english_concept_present(self, provider):
        for error_type in ERROR_GUIDES:
            assert len(provider.get_concept(error_type, "en")) > 0


# ──────────────────────────────────────────────
# 모든 가이드가 영어 필드를 갖는지
# ──────────────────────────────────────────────

class TestCoverage:

    def test_all_guides_have_english_fields(self):
        for error_type, guide in ERROR_GUIDES.items():
            assert guide.cause_en, f"{error_type} missing cause_en"
            assert guide.solution_en, f"{error_type} missing solution_en"
            assert guide.concept_en, f"{error_type} missing concept_en"

    def test_full_guide_text_english_labels(self, provider):
        text = provider.get_full_guide_text("NameError", "en")
        assert "Cause" in text
        assert "Solution" in text

    def test_full_guide_text_korean_labels(self, provider):
        text = provider.get_full_guide_text("NameError", "ko")
        assert "원인" in text
        assert "해결 방법" in text

    def test_unknown_error_message_by_language(self, provider):
        assert provider.get_cause("MysteryError", "en") != provider.get_cause("MysteryError", "ko")
