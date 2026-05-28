"""
difficulty_estimator.py: 학습 난이도 자동 추정
"""

import math
from typing import List
from .data_models import DifficultyScore, HistoricalSession


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

MIN_HISTORY = 5

WEIGHTS = {
    "error":      0.4,
    "complexity": 0.3,
    "time":       0.3,
}

LABELS = {
    "very_hard": "very hard",
    "hard":      "harder than usual",
    "normal":    "average",
    "easy":      "easy",
    "pending":   "collecting data",
}


# ──────────────────────────────────────────────
# DifficultyEstimator
# ──────────────────────────────────────────────

class DifficultyEstimator:

    def estimate(
        self,
        history: List[HistoricalSession],
        current_error_count: int,
        current_clap_score: float,
        current_elapsed: float
    ) -> DifficultyScore:

        if len(history) < MIN_HISTORY:
            return DifficultyScore(
                score=0.0,
                label=LABELS["pending"],
                is_relative=False
            )

        error_values      = [h.error_count      for h in history]
        complexity_values = [h.clap_score        for h in history]
        time_values       = [h.elapsed_seconds   for h in history]

        norm_error      = self._normalize(current_error_count,  error_values)
        norm_complexity = self._normalize(current_clap_score,   complexity_values)
        norm_time       = self._normalize(current_elapsed,      time_values)

        score = (
            norm_error      * WEIGHTS["error"]      +
            norm_complexity * WEIGHTS["complexity"] +
            norm_time       * WEIGHTS["time"]
        )

        label = self._label(score, norm_error, norm_complexity)

        return DifficultyScore(
            score=round(score, 4),
            label=label,
            is_relative=True,
            normalized_error=round(norm_error, 4),
            normalized_complexity=round(norm_complexity, 4),
            normalized_time=round(norm_time, 4)
        )

    # ──────────────────────────────────────────────
    # 정규화 (z-score + sigmoid)
    # ──────────────────────────────────────────────

    def _normalize(self, value: float, history: List[float]) -> float:
        if not history:
            return 0.5

        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        stdev = math.sqrt(variance)

        if stdev == 0:
            return 0.5

        z_score = (value - mean) / stdev
        return self._sigmoid(z_score)

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-x))

    # ──────────────────────────────────────────────
    # 난이도 레이블 결정
    # ──────────────────────────────────────────────

    def _label(
        self,
        score: float,
        norm_error: float,
        norm_complexity: float
    ) -> str:
        if score >= 0.75:
            return LABELS["very_hard"]
        if score >= 0.55 and (norm_error > 0.6 or norm_complexity > 0.6):
            return LABELS["hard"]
        if score >= 0.4:
            return LABELS["normal"]
        return LABELS["easy"]