"""
study_coach.py: 자기주도 학습 코치

학습자의 최근 오류 기록을 분석해 '이번 주 약점'을 진단하고, 그 약점을
바탕으로 AI 도구에 물어보면 좋은 맞춤 질문을 생성한다. 정답을 대신
주는 대신, 무엇을 더 공부하고 무엇을 질문해야 하는지를 스스로 알도록
돕는 것이 목적이다 (AI 에이전트 앞단의 자기 진단 도구).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from collections import defaultdict

from .data_models import AnalysisSession
from .error_guide import ErrorGuideProvider


# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────

WEAKNESS_WINDOW_DAYS = 7   # '이번 주' 기준 기간
MAX_WEAKNESSES = 3


# ──────────────────────────────────────────────
# 데이터 클래스
# ──────────────────────────────────────────────

@dataclass
class WeaknessItem:
    error_type: str
    count: int
    concept: str


# ──────────────────────────────────────────────
# StudyCoach
# ──────────────────────────────────────────────

class StudyCoach:

    def __init__(self, guide_provider: ErrorGuideProvider = None):
        self.guide_provider = guide_provider or ErrorGuideProvider()

    # ──────────────────────────────────────────────
    # 이번 주 약점 분석
    # ──────────────────────────────────────────────

    def analyze_weaknesses(
        self,
        sessions: List[AnalysisSession],
        days: int = WEAKNESS_WINDOW_DAYS,
        limit: int = MAX_WEAKNESSES,
    ) -> List[WeaknessItem]:
        errored = [s for s in sessions if s.error_record is not None]
        if not errored:
            return []

        recent = self._within_window(errored, days)
        if not recent:
            recent = errored

        counts = defaultdict(int)
        for session in recent:
            counts[session.error_record.error_type] += 1

        ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)

        items: List[WeaknessItem] = []
        for error_type, count in ordered[:limit]:
            items.append(
                WeaknessItem(
                    error_type=error_type,
                    count=count,
                    concept=self.guide_provider.get_concept(error_type),
                )
            )
        return items

    def _within_window(
        self, sessions: List[AnalysisSession], days: int
    ) -> List[AnalysisSession]:
        # 가장 최근 세션 시각을 기준으로 days 일 이내만 추린다
        try:
            latest = max(datetime.fromisoformat(s.timestamp) for s in sessions)
        except (ValueError, TypeError):
            return sessions

        cutoff = latest - timedelta(days=days)
        result = []
        for session in sessions:
            try:
                if datetime.fromisoformat(session.timestamp) >= cutoff:
                    result.append(session)
            except (ValueError, TypeError):
                result.append(session)
        return result

    # ──────────────────────────────────────────────
    # AI에게 물어볼 질문 생성 (약점을 빠짐없이 포괄)
    # ──────────────────────────────────────────────

    def generate_questions(self, weaknesses: List[WeaknessItem]) -> List[str]:
        if not weaknesses:
            return []

        questions: List[str] = []

        # 1) 약점별 개별 질문
        for item in weaknesses:
            questions.append(
                f"'{item.concept}'이(가) 자주 헷갈립니다. "
                f"{item.error_type}가 왜 발생하는지 원리를 설명하고, "
                f"올바르게 작성하는 방법을 간단한 예시 코드와 함께 알려주세요."
            )

        # 2) 약점 전체를 묶는 종합 질문 (2개 이상일 때)
        if len(weaknesses) >= 2:
            concepts = ", ".join(f"'{w.concept}'" for w in weaknesses)
            questions.append(
                f"제가 이번 주에 자주 틀린 개념은 {concepts}입니다. "
                "이 개념들을 초보자가 이해하기 쉽게 묶어서 정리해 주고, "
                "각 개념마다 연습 문제를 하나씩 내주세요."
            )

        return questions
