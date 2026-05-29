"""
report_generator.py: 학습 분석 리포트 생성

세션 기록을 집계하여 학습자용 종합 리포트를 생성한다.
요약 통계, 파일별 분석, 오류 분석, 개선 제안을 포함하며
Markdown / HTML / 텍스트 형식으로 렌더링할 수 있다.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from .data_models import AnalysisSession, HistoricalSession, SummaryStats
from .error_guide import ErrorGuideProvider
from .study_coach import StudyCoach, WeaknessItem


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

MIN_SESSIONS_FOR_TREND = 3

# 개선 제안 판단 임계값
HIGH_MCCABE_THRESHOLD = 10.0
HIGH_CLAP_THRESHOLD = 7.0
SLOW_EXECUTION_THRESHOLD = 5.0
FREQUENT_ERROR_RATIO = 0.3


# ──────────────────────────────────────────────
# 점수 해설 (초보자 친화 설명)
# ──────────────────────────────────────────────

def describe_mccabe(score: float) -> str:
    """McCabe 점수를 사람이 이해하기 쉬운 말로 바꾼다."""
    if score <= 10:
        return "단순한 코드"
    if score <= 20:
        return "중간 복잡도 (주의)"
    return "복잡한 코드 (리팩토링 권장)"


# 점수 용어 설명 (리포트 용어집에 사용)
SCORE_GLOSSARY = [
    (
        "McCabe 복잡도",
        "코드 안의 갈림길(if/for/while 등) 개수예요. "
        "숫자가 낮을수록 단순합니다. 10 이하는 단순, 11~20은 주의, "
        "21 이상은 복잡해서 함수 분리를 권장해요.",
    ),
    (
        "CLAP 복잡도",
        "함수 길이와 중첩 깊이까지 반영한 '나만의' 복잡도 점수예요. "
        "내가 평소 작성하던 코드의 평균과 비교해서 높고 낮음을 봅니다.",
    ),
    (
        "학습 난이도",
        "오류 수, 복잡도, 풀이 시간을 종합한 값이에요. "
        "남과 비교하는 게 아니라, 내 평소 기록 대비로 해석합니다.",
    ),
]


# ──────────────────────────────────────────────
# 리포트 데이터 클래스
# ──────────────────────────────────────────────

@dataclass
class FileReportEntry:
    """파일 단위 분석 요약"""
    file_path: str
    session_count: int = 0
    error_count: int = 0
    success_count: int = 0
    avg_clap_score: float = 0.0
    avg_mccabe_score: float = 0.0
    avg_elapsed_seconds: float = 0.0
    last_timestamp: str = ""
    dominant_error: str = "none"
    complexity_label: str = "단순한 코드"

    @property
    def success_rate(self) -> float:
        if self.session_count == 0:
            return 0.0
        return round(self.success_count / self.session_count, 4)


@dataclass
class ErrorAnalysisEntry:
    """오류 유형별 분석 항목 (가이드 포함)"""
    error_type: str
    count: int = 0
    ratio: float = 0.0
    concept: str = "알 수 없음"
    solution: str = ""


@dataclass
class TrendSummary:
    """시간에 따른 추세 요약"""
    has_trend: bool = False
    clap_direction: str = "stable"
    mccabe_direction: str = "stable"
    error_direction: str = "stable"
    first_clap: float = 0.0
    last_clap: float = 0.0
    first_mccabe: float = 0.0
    last_mccabe: float = 0.0


@dataclass
class StudentReport:
    """학습자 종합 리포트"""
    title: str = "학습 분석 리포트"
    generated_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    summary_stats: SummaryStats = field(default_factory=SummaryStats)
    file_entries: List[FileReportEntry] = field(default_factory=list)
    error_entries: List[ErrorAnalysisEntry] = field(default_factory=list)
    trend: TrendSummary = field(default_factory=TrendSummary)
    suggestions: List[str] = field(default_factory=list)
    weaknesses: List["WeaknessItem"] = field(default_factory=list)
    ai_questions: List[str] = field(default_factory=list)
    has_data: bool = False


# ──────────────────────────────────────────────
# ReportGenerator
# ──────────────────────────────────────────────

class ReportGenerator:

    def __init__(self, guide_provider: Optional[ErrorGuideProvider] = None):
        self.guide_provider = guide_provider or ErrorGuideProvider()
        self.study_coach = StudyCoach(self.guide_provider)

    # ──────────────────────────────────────────────
    # 리포트 생성 (진입점)
    # ──────────────────────────────────────────────

    def generate(
        self,
        sessions: List[AnalysisSession],
        historical: Optional[List[HistoricalSession]] = None,
    ) -> StudentReport:
        if not sessions:
            return StudentReport(has_data=False)

        report = StudentReport(has_data=True)
        report.summary_stats = self._build_summary_stats(sessions)
        report.file_entries = self._build_file_entries(sessions)
        report.error_entries = self._build_error_entries(sessions)
        report.trend = self._build_trend(historical or [])
        report.suggestions = self._build_suggestions(
            report.summary_stats, report.error_entries,
            report.trend, report.file_entries
        )
        report.weaknesses = self.study_coach.analyze_weaknesses(sessions)
        report.ai_questions = self.study_coach.generate_questions(report.weaknesses)
        return report

    # ──────────────────────────────────────────────
    # 요약 통계 집계
    # ──────────────────────────────────────────────

    def _build_summary_stats(
        self, sessions: List[AnalysisSession]
    ) -> SummaryStats:
        total = len(sessions)
        error_count = sum(1 for s in sessions if s.error_record is not None)

        clap_scores = [s.ast_result.clap_components.score for s in sessions]
        mccabe_scores = [s.ast_result.mccabe_score for s in sessions]
        elapsed = [s.execution_result.elapsed_seconds for s in sessions]

        error_freq: Dict[str, int] = defaultdict(int)
        for s in sessions:
            if s.error_record:
                error_freq[s.error_record.error_type] += 1

        most_frequent = "none"
        if error_freq:
            most_frequent = max(error_freq.items(), key=lambda kv: kv[1])[0]

        return SummaryStats(
            total_sessions=total,
            total_errors=error_count,
            avg_mccabe_score=self._safe_avg(mccabe_scores),
            avg_clap_score=self._safe_avg(clap_scores),
            avg_elapsed_seconds=self._safe_avg(elapsed),
            most_frequent_error=most_frequent,
        )

    # ──────────────────────────────────────────────
    # 파일별 분석 집계
    # ──────────────────────────────────────────────

    def _build_file_entries(
        self, sessions: List[AnalysisSession]
    ) -> List[FileReportEntry]:
        grouped: Dict[str, List[AnalysisSession]] = defaultdict(list)
        for s in sessions:
            grouped[s.file_path].append(s)

        entries: List[FileReportEntry] = []
        for file_path, file_sessions in grouped.items():
            entries.append(self._build_single_file_entry(file_path, file_sessions))

        # 세션이 많은 파일을 먼저 보여준다
        entries.sort(key=lambda e: e.session_count, reverse=True)
        return entries

    def _build_single_file_entry(
        self, file_path: str, file_sessions: List[AnalysisSession]
    ) -> FileReportEntry:
        count = len(file_sessions)
        errors = sum(1 for s in file_sessions if s.error_record is not None)
        successes = sum(1 for s in file_sessions if s.execution_result.success)

        clap = [s.ast_result.clap_components.score for s in file_sessions]
        mccabe = [s.ast_result.mccabe_score for s in file_sessions]
        elapsed = [s.execution_result.elapsed_seconds for s in file_sessions]

        error_freq: Dict[str, int] = defaultdict(int)
        for s in file_sessions:
            if s.error_record:
                error_freq[s.error_record.error_type] += 1

        dominant = "none"
        if error_freq:
            dominant = max(error_freq.items(), key=lambda kv: kv[1])[0]

        last_timestamp = max(s.timestamp for s in file_sessions)

        avg_mccabe = self._safe_avg(mccabe)

        return FileReportEntry(
            file_path=file_path,
            session_count=count,
            error_count=errors,
            success_count=successes,
            avg_clap_score=self._safe_avg(clap),
            avg_mccabe_score=avg_mccabe,
            avg_elapsed_seconds=self._safe_avg(elapsed),
            last_timestamp=last_timestamp,
            dominant_error=dominant,
            complexity_label=describe_mccabe(avg_mccabe),
        )

    # ──────────────────────────────────────────────
    # 오류 분석 집계 (가이드 연동)
    # ──────────────────────────────────────────────

    def _build_error_entries(
        self, sessions: List[AnalysisSession]
    ) -> List[ErrorAnalysisEntry]:
        error_freq: Dict[str, int] = defaultdict(int)
        for s in sessions:
            if s.error_record:
                error_freq[s.error_record.error_type] += 1

        total = sum(error_freq.values())
        if total == 0:
            return []

        entries: List[ErrorAnalysisEntry] = []
        for error_type, count in error_freq.items():
            entries.append(
                ErrorAnalysisEntry(
                    error_type=error_type,
                    count=count,
                    ratio=round(count / total, 4),
                    concept=self.guide_provider.get_concept(error_type),
                    solution=self.guide_provider.get_solution_text(error_type),
                )
            )

        entries.sort(key=lambda e: e.count, reverse=True)
        return entries

    # ──────────────────────────────────────────────
    # 추세 분석 (이력 기반)
    # ──────────────────────────────────────────────

    def _build_trend(
        self, historical: List[HistoricalSession]
    ) -> TrendSummary:
        if len(historical) < MIN_SESSIONS_FOR_TREND:
            return TrendSummary(has_trend=False)

        ordered = sorted(historical, key=lambda h: h.timestamp)
        half = max(1, len(ordered) // 2)
        first_half = ordered[:half]
        last_half = ordered[half:]

        first_clap = self._safe_avg([h.clap_score for h in first_half])
        last_clap = self._safe_avg([h.clap_score for h in last_half])
        first_mccabe = self._safe_avg([h.mccabe_score for h in first_half])
        last_mccabe = self._safe_avg([h.mccabe_score for h in last_half])
        first_err = self._safe_avg([h.error_count for h in first_half])
        last_err = self._safe_avg([h.error_count for h in last_half])

        return TrendSummary(
            has_trend=True,
            clap_direction=self._direction(first_clap, last_clap),
            mccabe_direction=self._direction(first_mccabe, last_mccabe),
            error_direction=self._direction(first_err, last_err),
            first_clap=first_clap,
            last_clap=last_clap,
            first_mccabe=first_mccabe,
            last_mccabe=last_mccabe,
        )

    def _direction(self, first: float, last: float) -> str:
        delta = last - first
        if abs(delta) < 1e-6:
            return "stable"
        return "up" if delta > 0 else "down"

    # ──────────────────────────────────────────────
    # 개선 제안 생성
    # ──────────────────────────────────────────────

    def _build_suggestions(
        self,
        stats: SummaryStats,
        error_entries: List[ErrorAnalysisEntry],
        trend: TrendSummary,
        file_entries: Optional[List[FileReportEntry]] = None,
    ) -> List[str]:
        suggestions: List[str] = []

        # 가장 복잡한 파일을 콕 집어 안내한다
        if file_entries:
            most_complex = max(file_entries, key=lambda e: e.avg_clap_score)
            if most_complex.avg_clap_score >= HIGH_CLAP_THRESHOLD:
                name = os.path.basename(most_complex.file_path)
                suggestions.append(
                    f"'{name}' 파일의 복잡도(CLAP {most_complex.avg_clap_score})가 "
                    "가장 높습니다. 이 파일부터 함수 분리를 시도해 보세요."
                )

        if stats.avg_mccabe_score >= HIGH_MCCABE_THRESHOLD:
            suggestions.append(
                f"평균 McCabe 복잡도가 {stats.avg_mccabe_score}로 높습니다. "
                "함수를 더 작은 단위로 분리해 보세요."
            )

        if stats.avg_clap_score >= HIGH_CLAP_THRESHOLD:
            suggestions.append(
                f"평균 CLAP 점수가 {stats.avg_clap_score}로 높습니다. "
                "중첩 깊이와 분기 수를 줄이면 가독성이 좋아집니다."
            )

        if stats.avg_elapsed_seconds >= SLOW_EXECUTION_THRESHOLD:
            suggestions.append(
                f"평균 실행 시간이 {stats.avg_elapsed_seconds}초로 깁니다. "
                "반복문이나 비효율적인 연산이 없는지 확인하세요."
            )

        # 가장 빈번한 오류에 대한 학습 개념 안내
        if error_entries:
            top = error_entries[0]
            if top.ratio >= FREQUENT_ERROR_RATIO:
                suggestions.append(
                    f"'{top.error_type}' 오류가 전체의 {int(top.ratio * 100)}%를 "
                    f"차지합니다. '{top.concept}' 개념을 복습하면 도움이 됩니다."
                )

        # 추세 기반 격려/주의 메시지
        if trend.has_trend:
            if trend.error_direction == "down":
                suggestions.append("오류 발생이 줄어드는 추세입니다. 잘하고 있어요!")
            elif trend.error_direction == "up":
                suggestions.append(
                    "최근 오류가 늘어나는 추세입니다. 새로 시도한 코드를 "
                    "차근차근 점검해 보세요."
                )

        if not suggestions:
            suggestions.append(
                "전반적으로 안정적인 학습 상태입니다. 현재 방식을 유지하세요."
            )

        return suggestions

    # ──────────────────────────────────────────────
    # 보조 유틸
    # ──────────────────────────────────────────────

    def _safe_avg(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)


# ──────────────────────────────────────────────
# ReportRenderer: 리포트를 문자열 형식으로 변환
# ──────────────────────────────────────────────

class ReportRenderer:

    # ──────────────────────────────────────────────
    # 텍스트 렌더링
    # ──────────────────────────────────────────────

    def render_text(self, report: StudentReport) -> str:
        if not report.has_data:
            return (
                "아직 분석할 데이터가 없습니다.\n"
                "설정에서 폴더를 등록하고 .py 파일을 저장하면 리포트가 만들어집니다."
            )

        lines: List[str] = []
        lines.append("=" * 50)
        lines.append(report.title)
        lines.append(f"생성 시각: {self._format_time(report.generated_at)}")
        lines.append("=" * 50)
        lines.append("")
        lines.append("내 코드 학습 기록을 한눈에 정리한 리포트입니다.")
        lines.append("")

        stats = report.summary_stats
        lines.append("[ 요약 통계 ]")
        lines.append(f"  총 세션 수      : {stats.total_sessions}")
        lines.append(f"  총 오류 수      : {stats.total_errors}")
        lines.append(f"  평균 CLAP 점수  : {stats.avg_clap_score}")
        lines.append(f"  평균 McCabe 점수: {stats.avg_mccabe_score}")
        lines.append(f"  평균 실행 시간  : {stats.avg_elapsed_seconds}초")
        lines.append(f"  최빈 오류       : {stats.most_frequent_error}")
        lines.append("")

        lines.append("[ 파일별 분석 ]")
        for entry in report.file_entries:
            lines.append(f"  - {self._display_name(entry.file_path)}")
            lines.append(
                f"      분석 {entry.session_count}회 / 상태: {self._status_text(entry)}"
            )
            lines.append(
                f"      복잡도: McCabe {entry.avg_mccabe_score} "
                f"({entry.complexity_label}) / CLAP {entry.avg_clap_score}"
            )
        lines.append("")

        lines.append("[ 점수가 무슨 뜻인가요? ]")
        for term, desc in SCORE_GLOSSARY:
            lines.append(f"  · {term}: {desc}")
        lines.append("")

        if report.error_entries:
            lines.append("[ 오류 분석 ]")
            for e in report.error_entries:
                lines.append(
                    f"  - {e.error_type}: {e.count}회 "
                    f"({int(e.ratio * 100)}%) — 개념: {e.concept}"
                )
                lines.append(f"      해결: {e.solution}")
            lines.append("")

        lines.append("[ 개선 제안 ]")
        for i, suggestion in enumerate(report.suggestions, start=1):
            lines.append(f"  {i}. {suggestion}")
        lines.append("")

        if report.weaknesses:
            lines.append("[ 이번 주 약점 ]")
            for w in report.weaknesses:
                lines.append(f"  · {w.concept} ({w.error_type}) — {w.count}회")
            lines.append("")

        if report.ai_questions:
            lines.append("[ AI에게 물어볼 질문 ]")
            for i, q in enumerate(report.ai_questions, start=1):
                lines.append(f"  {i}. {q}")

        return "\n".join(lines)

    # ──────────────────────────────────────────────
    # Markdown 렌더링
    # ──────────────────────────────────────────────

    def render_markdown(self, report: StudentReport) -> str:
        if not report.has_data:
            return (
                "# 학습 분석 리포트\n\n"
                "아직 분석할 데이터가 없습니다. "
                "설정에서 폴더를 등록하고 .py 파일을 저장하면 리포트가 만들어집니다."
            )

        lines: List[str] = []
        lines.append(f"# {report.title}")
        lines.append("")
        lines.append(f"_생성 시각: {self._format_time(report.generated_at)}_")
        lines.append("")
        lines.append("> 내 코드 학습 기록을 한눈에 정리한 리포트입니다.")
        lines.append("")

        stats = report.summary_stats
        lines.append("## 요약 통계")
        lines.append("")
        lines.append("| 항목 | 값 |")
        lines.append("| --- | --- |")
        lines.append(f"| 총 세션 수 | {stats.total_sessions} |")
        lines.append(f"| 총 오류 수 | {stats.total_errors} |")
        lines.append(f"| 평균 CLAP 점수 | {stats.avg_clap_score} |")
        lines.append(f"| 평균 McCabe 점수 | {stats.avg_mccabe_score} |")
        lines.append(f"| 평균 실행 시간(초) | {stats.avg_elapsed_seconds} |")
        lines.append(f"| 최빈 오류 | {stats.most_frequent_error} |")
        lines.append("")

        lines.append("## 파일별 분석")
        lines.append("")
        lines.append("| 파일 | 분석 횟수 | 오류 | 복잡도 | 상태 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for entry in report.file_entries:
            lines.append(
                f"| {self._display_name(entry.file_path)} | {entry.session_count} | "
                f"{entry.error_count} | "
                f"McCabe {entry.avg_mccabe_score} ({entry.complexity_label}) | "
                f"{self._status_text(entry)} |"
            )
        lines.append("")

        lines.append("## 점수가 무슨 뜻인가요?")
        lines.append("")
        for term, desc in SCORE_GLOSSARY:
            lines.append(f"- **{term}**: {desc}")
        lines.append("")

        if report.error_entries:
            lines.append("## 오류 분석")
            lines.append("")
            for e in report.error_entries:
                lines.append(f"### {e.error_type} ({e.count}회, {int(e.ratio * 100)}%)")
                lines.append("")
                lines.append(f"- **학습 개념**: {e.concept}")
                lines.append(f"- **해결 방법**: {e.solution}")
                lines.append("")

        lines.append("## 개선 제안")
        lines.append("")
        for suggestion in report.suggestions:
            lines.append(f"- {suggestion}")
        lines.append("")

        if report.weaknesses:
            lines.append("## 이번 주 약점")
            lines.append("")
            for w in report.weaknesses:
                lines.append(f"- **{w.concept}** ({w.error_type}) — {w.count}회")
            lines.append("")

        if report.ai_questions:
            lines.append("## AI에게 물어볼 질문")
            lines.append("")
            for q in report.ai_questions:
                lines.append(f"- {q}")
            lines.append("")

        return "\n".join(lines)

    # ──────────────────────────────────────────────
    # HTML 렌더링
    # ──────────────────────────────────────────────

    def render_html(self, report: StudentReport) -> str:
        if not report.has_data:
            return (
                "<html><body style='font-family: sans-serif; margin: 24px;'>"
                "<h1>학습 분석 리포트</h1>"
                "<p>아직 분석할 데이터가 없습니다.</p>"
                "<p>설정에서 폴더를 등록하고 편집기에서 <b>.py 파일을 저장</b>하면 "
                "리포트가 자동으로 만들어집니다.</p>"
                "</body></html>"
            )

        parts: List[str] = []
        parts.append("<html><head><meta charset='utf-8'>")
        parts.append("<style>")
        parts.append("body { font-family: sans-serif; margin: 24px; }")
        parts.append("table { border-collapse: collapse; margin: 12px 0; }")
        parts.append("th, td { border: 1px solid #ccc; padding: 6px 12px; }")
        parts.append("th { background: #f0f0f0; }")
        parts.append("h1 { color: #2c3e50; }")
        parts.append("</style></head><body>")

        parts.append(f"<h1>{self._escape(report.title)}</h1>")
        parts.append(
            f"<p><em>생성 시각: {self._format_time(report.generated_at)}</em></p>"
        )
        parts.append(
            "<p>내 코드 학습 기록을 한눈에 정리한 리포트입니다.</p>"
        )

        stats = report.summary_stats
        parts.append("<h2>요약 통계</h2>")
        parts.append("<table>")
        parts.append("<tr><th>항목</th><th>값</th></tr>")
        parts.append(f"<tr><td>총 세션 수</td><td>{stats.total_sessions}</td></tr>")
        parts.append(f"<tr><td>총 오류 수</td><td>{stats.total_errors}</td></tr>")
        parts.append(f"<tr><td>평균 CLAP 점수</td><td>{stats.avg_clap_score}</td></tr>")
        parts.append(
            f"<tr><td>평균 McCabe 점수</td><td>{stats.avg_mccabe_score}</td></tr>"
        )
        parts.append(
            f"<tr><td>평균 실행 시간(초)</td><td>{stats.avg_elapsed_seconds}</td></tr>"
        )
        parts.append(
            f"<tr><td>최빈 오류</td>"
            f"<td>{self._escape(stats.most_frequent_error)}</td></tr>"
        )
        parts.append("</table>")

        parts.append("<h2>파일별 분석</h2>")
        parts.append("<table>")
        parts.append(
            "<tr><th>파일</th><th>분석 횟수</th><th>오류</th>"
            "<th>복잡도</th><th>상태</th></tr>"
        )
        for entry in report.file_entries:
            parts.append(
                f"<tr><td>{self._escape(self._display_name(entry.file_path))}</td>"
                f"<td>{entry.session_count}</td>"
                f"<td>{entry.error_count}</td>"
                f"<td>McCabe {entry.avg_mccabe_score} "
                f"({self._escape(entry.complexity_label)})</td>"
                f"<td>{self._escape(self._status_text(entry))}</td></tr>"
            )
        parts.append("</table>")

        if report.error_entries:
            parts.append("<h2>오류 분석</h2>")
            for e in report.error_entries:
                parts.append(
                    f"<h3>{self._escape(e.error_type)} "
                    f"({e.count}회, {int(e.ratio * 100)}%)</h3>"
                )
                parts.append("<ul>")
                parts.append(f"<li><b>학습 개념</b>: {self._escape(e.concept)}</li>")
                parts.append(f"<li><b>해결 방법</b>: {self._escape(e.solution)}</li>")
                parts.append("</ul>")

        parts.append("<h2>개선 제안</h2>")
        parts.append("<ul>")
        for suggestion in report.suggestions:
            parts.append(f"<li>{self._escape(suggestion)}</li>")
        parts.append("</ul>")

        if report.weaknesses:
            parts.append("<h2>이번 주 약점</h2>")
            parts.append("<ul>")
            for w in report.weaknesses:
                parts.append(
                    f"<li><b>{self._escape(w.concept)}</b> "
                    f"({self._escape(w.error_type)}) — {w.count}회</li>"
                )
            parts.append("</ul>")

        if report.ai_questions:
            parts.append("<h2>AI에게 물어볼 질문</h2>")
            parts.append(
                "<p>아래 질문을 ChatGPT 같은 AI에 그대로 물어보면 도움이 돼요.</p>"
            )
            parts.append("<ul>")
            for q in report.ai_questions:
                parts.append(f"<li>{self._escape(q)}</li>")
            parts.append("</ul>")

        parts.append("<h2>점수가 무슨 뜻인가요?</h2>")
        parts.append("<ul>")
        for term, desc in SCORE_GLOSSARY:
            parts.append(
                f"<li><b>{self._escape(term)}</b>: {self._escape(desc)}</li>"
            )
        parts.append("</ul>")

        parts.append("</body></html>")
        return "".join(parts)

    # ──────────────────────────────────────────────
    # 보조 유틸
    # ──────────────────────────────────────────────

    def _escape(self, text: str) -> str:
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _format_time(self, iso_text: str) -> str:
        """ISO 시간 문자열을 'YYYY-MM-DD HH:MM' 형태로 다듬는다."""
        try:
            dt = datetime.fromisoformat(iso_text)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return iso_text

    def _display_name(self, file_path: str) -> str:
        """전체 경로 대신 파일 이름만 보여준다 (초보자 친화)."""
        return os.path.basename(file_path) or file_path

    def _status_text(self, entry: FileReportEntry) -> str:
        """파일의 실행 상태를 한 줄로 표현한다."""
        if entry.error_count == 0:
            return "정상 실행"
        return f"오류 발생 ({entry.dominant_error})"
