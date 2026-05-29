"""
test_difficulty_estimator.py: DifficultyEstimator 단위 테스트
"""

import pytest
from src.models.difficulty_estimator import DifficultyEstimator, MIN_HISTORY
from src.models.data_models import HistoricalSession


@pytest.fixture
def estimator():
    return DifficultyEstimator()


def make_history(n: int, error=0, clap=5.0, elapsed=1.0):
    return [
        HistoricalSession(
            session_id=i,
            timestamp=f"2025-05-{i+1:02d}T00:00:00",
            error_count=error,
            clap_score=clap,
            mccabe_score=3.0,
            elapsed_seconds=elapsed,
            difficulty_score=0.5,
            difficulty_label="average"
        )
        for i in range(n)
    ]


# ──────────────────────────────────────────────
# 데이터 부족 테스트
# ──────────────────────────────────────────────

class TestInsufficientData:

    def test_pending_label_when_no_history(self, estimator):
        result = estimator.estimate([], 0, 0.0, 0.0)
        assert result.label == "collecting data"

    def test_not_relative_when_no_history(self, estimator):
        result = estimator.estimate([], 0, 0.0, 0.0)
        assert result.is_relative is False

    def test_score_zero_when_no_history(self, estimator):
        result = estimator.estimate([], 0, 0.0, 0.0)
        assert result.score == 0.0

    def test_pending_when_less_than_min(self, estimator):
        history = make_history(MIN_HISTORY - 1)
        result = estimator.estimate(history, 0, 5.0, 1.0)
        assert result.label == "collecting data"


# ──────────────────────────────────────────────
# 상대 기준 활성화 테스트
# ──────────────────────────────────────────────

class TestRelativeMode:

    def test_relative_flag_when_enough_data(self, estimator):
        history = make_history(MIN_HISTORY)
        result = estimator.estimate(history, 0, 5.0, 1.0)
        assert result.is_relative is True

    def test_score_between_0_and_1(self, estimator):
        history = make_history(MIN_HISTORY)
        result = estimator.estimate(history, 0, 5.0, 1.0)
        assert 0.0 <= result.score <= 1.0

    def test_normalized_values_between_0_and_1(self, estimator):
        history = make_history(MIN_HISTORY)
        result = estimator.estimate(history, 0, 5.0, 1.0)
        assert 0.0 <= result.normalized_error <= 1.0
        assert 0.0 <= result.normalized_complexity <= 1.0
        assert 0.0 <= result.normalized_time <= 1.0


# ──────────────────────────────────────────────
# 난이도 레이블 테스트
# ──────────────────────────────────────────────

class TestDifficultyLabel:

    def test_easy_label_for_simple_code(self, estimator):
        history = make_history(MIN_HISTORY, error=5, clap=20.0, elapsed=10.0)
        result = estimator.estimate(history, 0, 0.0, 0.0)
        assert result.label in ("easy", "average")

    def test_hard_label_for_complex_code(self, estimator):
        history = make_history(MIN_HISTORY, error=0, clap=1.0, elapsed=0.5)
        result = estimator.estimate(history, 10, 50.0, 30.0)
        assert result.label != "easy"

    def test_consistent_label_same_input(self, estimator):
        history = make_history(MIN_HISTORY)
        result1 = estimator.estimate(history, 1, 5.0, 1.0)
        result2 = estimator.estimate(history, 1, 5.0, 1.0)
        assert result1.label == result2.label

    def test_consistent_score_same_input(self, estimator):
        history = make_history(MIN_HISTORY)
        result1 = estimator.estimate(history, 1, 5.0, 1.0)
        result2 = estimator.estimate(history, 1, 5.0, 1.0)
        assert result1.score == result2.score


# ──────────────────────────────────────────────
# 정규화 테스트
# ──────────────────────────────────────────────

class TestNormalization:

    def test_average_input_gives_mid_score(self, estimator):
        history = make_history(MIN_HISTORY, error=2, clap=5.0, elapsed=2.0)
        result = estimator.estimate(history, 2, 5.0, 2.0)
        assert 0.3 <= result.score <= 0.7

    def test_zero_stdev_gives_half(self, estimator):
        history = make_history(MIN_HISTORY, error=3, clap=5.0, elapsed=1.0)
        result = estimator.estimate(history, 3, 5.0, 1.0)
        assert result.normalized_error == 0.5
        assert result.normalized_complexity == 0.5
        assert result.normalized_time == 0.5