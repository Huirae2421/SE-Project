"""
test_beginner_errors.py: 초보자 빈출 오류 분류/가이드 테스트

CodeExecutor 가 클래스/스코프/재귀/import 등 초보자가 자주 만드는
오류를 올바른 유형으로 분류하고, 각 오류에 학습 가이드가 준비되어
있는지 확인한다.
"""

import pytest

from src.models.code_executor import CodeExecutor
from src.models.error_analyzer import ErrorAnalyzer, ERROR_GROUPS
from src.models.error_guide import ErrorGuideProvider


# ──────────────────────────────────────────────
# 오류를 일으키는 짧은 코드 조각
# ──────────────────────────────────────────────

ERROR_SNIPPETS = {
    "AttributeError": (
        "class Dog:\n"
        "    def bark(self):\n"
        "        print('bark')\n"
        "Dog().run()\n"
    ),
    "KeyError": "d = {'a': 1}\nprint(d['b'])\n",
    "ZeroDivisionError": "print(10 / 0)\n",
    "ModuleNotFoundError": "import nonexistent_module_xyz\n",
    "UnboundLocalError": (
        "count = 0\n"
        "def inc():\n"
        "    count = count + 1\n"
        "    return count\n"
        "inc()\n"
    ),
    "RecursionError": (
        "def f(n):\n"
        "    return f(n - 1)\n"
        "f(5)\n"
    ),
}


@pytest.fixture
def executor():
    return CodeExecutor()


# ──────────────────────────────────────────────
# 오류 유형 분류
# ──────────────────────────────────────────────

class TestBeginnerErrorClassification:

    @pytest.mark.parametrize("expected_type,code", list(ERROR_SNIPPETS.items()))
    def test_classified_as_expected_type(self, executor, tmp_path, expected_type, code):
        script = tmp_path / "snippet.py"
        script.write_text(code, encoding="utf-8")
        result = executor.execute(str(script))
        assert result.error_type == expected_type

    @pytest.mark.parametrize("expected_type,code", list(ERROR_SNIPPETS.items()))
    def test_not_success_on_error(self, executor, tmp_path, expected_type, code):
        script = tmp_path / "snippet.py"
        script.write_text(code, encoding="utf-8")
        result = executor.execute(str(script))
        assert result.success is False


# ──────────────────────────────────────────────
# 오류 그룹 매핑
# ──────────────────────────────────────────────

class TestErrorGroupMapping:

    @pytest.mark.parametrize("error_type", list(ERROR_SNIPPETS.keys()))
    def test_has_dedicated_group(self, error_type):
        # 새 오류 유형은 'other error group' 이 아닌 전용 그룹을 가져야 한다
        assert error_type in ERROR_GROUPS
        assert ERROR_GROUPS[error_type] != "other error group"

    def test_analyzer_assigns_group(self, executor, tmp_path):
        script = tmp_path / "snippet.py"
        script.write_text(ERROR_SNIPPETS["KeyError"], encoding="utf-8")
        result = executor.execute(str(script))
        record = ErrorAnalyzer().classify(result)
        assert record is not None
        assert record.error_group == "key error group"


# ──────────────────────────────────────────────
# 학습 가이드 존재 여부
# ──────────────────────────────────────────────

class TestGuideCoverage:

    @pytest.fixture
    def provider(self):
        return ErrorGuideProvider()

    @pytest.mark.parametrize("error_type", list(ERROR_SNIPPETS.keys()))
    def test_guide_exists(self, provider, error_type):
        assert provider.has_guide(error_type)

    @pytest.mark.parametrize("error_type", list(ERROR_SNIPPETS.keys()))
    def test_guide_has_solution_and_concept(self, provider, error_type):
        guide = provider.get_guide(error_type)
        assert guide is not None
        assert len(guide.solution) > 0
        assert len(guide.concept) > 0
