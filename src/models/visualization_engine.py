"""
visualization_engine.py: 시각화 데이터 생성
"""

from collections import defaultdict
from typing import List
from .data_models import AnalysisSession, ChartData


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

MIN_SESSIONS = 5


# ──────────────────────────────────────────────
# VisualizationEngine
# ──────────────────────────────────────────────

class VisualizationEngine:

    def build_chart_data(self, sessions: List[AnalysisSession]) -> ChartData:
        if len(sessions) < MIN_SESSIONS:
            return ChartData(has_enough_data=False)

        sorted_sessions = sorted(sessions, key=lambda s: s.timestamp)

        clap_scores = [s.ast_result.clap_components.score for s in sorted_sessions]
        clap_average = round(sum(clap_scores) / len(clap_scores), 2) if clap_scores else 0.0

        return ChartData(
            has_enough_data=True,
            error_bar=self._error_bar_data(sorted_sessions),
            activity_line=self._activity_line_data(sorted_sessions),
            mccabe_line=self._mccabe_line_data(sorted_sessions),
            clap_line=self._clap_line_data(sorted_sessions),
            clap_average=clap_average,
            difficulty_area=self._difficulty_area_data(sorted_sessions),
            error_pie=self._error_pie_data(sorted_sessions)
        )

    # ──────────────────────────────────────────────
    # 막대 그래프: 오류 유형별 발생 횟수
    # ──────────────────────────────────────────────

    def _error_bar_data(self, sessions: List[AnalysisSession]) -> dict:
        counts: dict = defaultdict(int)

        for session in sessions:
            if session.error_record:
                counts[session.error_record.error_type] += 1

        return dict(counts)

    # ──────────────────────────────────────────────
    # 꺾은선 그래프: 날짜별 학습 활동 횟수
    # ──────────────────────────────────────────────

    def _activity_line_data(self, sessions: List[AnalysisSession]) -> list:
        counts: dict = defaultdict(int)

        for session in sessions:
            date = session.timestamp[:10]
            counts[date] += 1

        return [
            {"date": date, "count": count}
            for date, count in sorted(counts.items())
        ]

    # ──────────────────────────────────────────────
    # 꺾은선 그래프: McCabe 복잡도 변화
    # ──────────────────────────────────────────────

    def _mccabe_line_data(self, sessions: List[AnalysisSession]) -> list:
        return [
            {
                "timestamp": s.timestamp,
                "score": s.ast_result.mccabe_score,
                "label": s.ast_result.mccabe_label
            }
            for s in sessions
        ]

    # ──────────────────────────────────────────────
    # 꺾은선 + 평균선: CLAP 복잡도 변화
    # ──────────────────────────────────────────────

    def _clap_line_data(self, sessions: List[AnalysisSession]) -> list:
        return [
            {
                "timestamp": s.timestamp,
                "score": s.ast_result.clap_components.score
            }
            for s in sessions
        ]

    # ──────────────────────────────────────────────
    # 영역 그래프: 난이도 변화
    # ──────────────────────────────────────────────

    def _difficulty_area_data(self, sessions: List[AnalysisSession]) -> list:
        return [
            {
                "timestamp": s.timestamp,
                "score": s.difficulty_score.score,
                "label": s.difficulty_score.label
            }
            for s in sessions
        ]

    # ──────────────────────────────────────────────
    # 파이 차트: 오류 유형 분포 비율
    # ──────────────────────────────────────────────

    def _error_pie_data(self, sessions: List[AnalysisSession]) -> dict:
        counts: dict = defaultdict(int)

        for session in sessions:
            if session.error_record:
                counts[session.error_record.error_type] += 1

        total = sum(counts.values())
        if total == 0:
            return {}

        return {
            error_type: round(count / total, 4)
            for error_type, count in counts.items()
        }