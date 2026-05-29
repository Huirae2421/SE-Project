"""
test_report_generator.py: ReportGenerator / ReportRenderer 단위 테스트
"""

import pytest

from src.models.report_generator import (
    ReportGenerator, ReportRenderer, StudentReport,
    FileReportEntry, ErrorAnalysisEntry, TrendSummary,
    MIN_SESSIONS_FOR_TREND,
)
from src.models.data_models import (
    AnalysisSession, ExecutionResult, ASTResult, ClapComponents,
    ErrorRecord, HistoricalSession,
)


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def make_session(
    file_path="a.py", error_type=None, clap=5.0, mccabe=3.0,
    elapsed=1.0, success=True, timestamp="2026-05-20T10:00:00",
):
    er = ExecutionResult(
        file_path=file_path, elapsed_seconds=elapsed, success=success
    )
    ar = ASTResult(
        file_path=file_path,
        clap_components=ClapComponents(score=clap),
        mccabe_score=mccabe,
    )
    rec = None
    if error_type:
        rec = ErrorRecord(
            error_type=error_type, error_message="msg", file_path=file_path
        )
    return AnalysisSession(
        file_path=file_path, timestamp=timestamp,
        execution_result=er, ast_result=ar, error_record=rec,
    )


def make_history(n, error=0, clap=5.0, mccabe=3.0, elapsed=1.0):
    return [
        HistoricalSession(
            session_id=i,
            timestamp=f"2026-05-{i + 1:02d}T00:00:00",
            error_count=error,
            clap_score=clap,
            mccabe_score=mccabe,
            elapsed_seconds=elapsed,
        )
        for i in range(n)
    ]


@pytest.fixture
def generator():
    return ReportGenerator()


@pytest.fixture
def renderer():
    return ReportRenderer()


# ──────────────────────────────────────────────
# 빈 데이터 처리
# ──────────────────────────────────────────────

class TestEmptyData:

    def test_no_sessions_returns_no_data(self, generator):
        report = generator.generate([])
        assert report.has_data is False

    def test_no_sessions_has_empty_entries(self, generator):
        report = generator.generate([])
        assert report.file_entries == []
        assert report.error_entries == []

    def test_renderer_text_handles_no_data(self, generator, renderer):
        report = generator.generate([])
        assert "데이터가 없습니다" in renderer.render_text(report)

    def test_renderer_markdown_handles_no_data(self, generator, renderer):
        report = generator.generate([])
        assert "데이터가 없습니다" in renderer.render_markdown(report)

    def test_renderer_html_handles_no_data(self, generator, renderer):
        report = generator.generate([])
        assert "데이터가 없습니다" in renderer.render_html(report)


# ──────────────────────────────────────────────
# 요약 통계 집계
# ──────────────────────────────────────────────

class TestSummaryStats:

    def test_total_session_count(self, generator):
        sessions = [make_session() for _ in range(4)]
        report = generator.generate(sessions)
        assert report.summary_stats.total_sessions == 4

    def test_error_count(self, generator):
        sessions = [
            make_session(error_type="NameError"),
            make_session(error_type="TypeError"),
            make_session(success=True),
        ]
        report = generator.generate(sessions)
        assert report.summary_stats.total_errors == 2

    def test_average_clap_score(self, generator):
        sessions = [
            make_session(clap=4.0),
            make_session(clap=6.0),
        ]
        report = generator.generate(sessions)
        assert report.summary_stats.avg_clap_score == 5.0

    def test_average_mccabe_score(self, generator):
        sessions = [
            make_session(mccabe=2.0),
            make_session(mccabe=8.0),
        ]
        report = generator.generate(sessions)
        assert report.summary_stats.avg_mccabe_score == 5.0

    def test_most_frequent_error(self, generator):
        sessions = [
            make_session(error_type="NameError"),
            make_session(error_type="NameError"),
            make_session(error_type="TypeError"),
        ]
        report = generator.generate(sessions)
        assert report.summary_stats.most_frequent_error == "NameError"

    def test_most_frequent_error_none_when_no_errors(self, generator):
        sessions = [make_session(success=True) for _ in range(3)]
        report = generator.generate(sessions)
        assert report.summary_stats.most_frequent_error == "none"


# ──────────────────────────────────────────────
# 파일별 분석
# ──────────────────────────────────────────────

class TestFileEntries:

    def test_groups_by_file_path(self, generator):
        sessions = [
            make_session(file_path="a.py"),
            make_session(file_path="a.py"),
            make_session(file_path="b.py"),
        ]
        report = generator.generate(sessions)
        assert len(report.file_entries) == 2

    def test_session_count_per_file(self, generator):
        sessions = [
            make_session(file_path="a.py"),
            make_session(file_path="a.py"),
            make_session(file_path="b.py"),
        ]
        report = generator.generate(sessions)
        a_entry = next(e for e in report.file_entries if e.file_path == "a.py")
        assert a_entry.session_count == 2

    def test_sorted_by_session_count_desc(self, generator):
        sessions = [
            make_session(file_path="a.py"),
            make_session(file_path="b.py"),
            make_session(file_path="b.py"),
            make_session(file_path="b.py"),
        ]
        report = generator.generate(sessions)
        assert report.file_entries[0].file_path == "b.py"

    def test_success_rate_calculation(self, generator):
        sessions = [
            make_session(file_path="a.py", success=True),
            make_session(file_path="a.py", success=False, error_type="NameError"),
        ]
        report = generator.generate(sessions)
        assert report.file_entries[0].success_rate == 0.5

    def test_success_rate_zero_when_no_sessions(self):
        entry = FileReportEntry(file_path="x.py")
        assert entry.success_rate == 0.0

    def test_dominant_error_per_file(self, generator):
        sessions = [
            make_session(file_path="a.py", error_type="IndexError"),
            make_session(file_path="a.py", error_type="IndexError"),
            make_session(file_path="a.py", error_type="KeyError"),
        ]
        report = generator.generate(sessions)
        assert report.file_entries[0].dominant_error == "IndexError"


# ──────────────────────────────────────────────
# 오류 분석 (가이드 연동)
# ──────────────────────────────────────────────

class TestErrorEntries:

    def test_no_error_entries_when_all_success(self, generator):
        sessions = [make_session(success=True) for _ in range(3)]
        report = generator.generate(sessions)
        assert report.error_entries == []

    def test_error_entry_count(self, generator):
        sessions = [
            make_session(error_type="NameError"),
            make_session(error_type="TypeError"),
        ]
        report = generator.generate(sessions)
        assert len(report.error_entries) == 2

    def test_error_ratio_sums_to_one(self, generator):
        sessions = [
            make_session(error_type="NameError"),
            make_session(error_type="TypeError"),
            make_session(error_type="TypeError"),
        ]
        report = generator.generate(sessions)
        total_ratio = sum(e.ratio for e in report.error_entries)
        assert total_ratio == pytest.approx(1.0)

    def test_sorted_by_count_desc(self, generator):
        sessions = [
            make_session(error_type="NameError"),
            make_session(error_type="TypeError"),
            make_session(error_type="TypeError"),
        ]
        report = generator.generate(sessions)
        assert report.error_entries[0].error_type == "TypeError"

    def test_concept_pulled_from_guide(self, generator):
        sessions = [make_session(error_type="NameError")]
        report = generator.generate(sessions)
        assert report.error_entries[0].concept == "변수 정의와 스코프"

    def test_solution_pulled_from_guide(self, generator):
        sessions = [make_session(error_type="NameError")]
        report = generator.generate(sessions)
        assert len(report.error_entries[0].solution) > 0

    def test_unknown_error_falls_back(self, generator):
        sessions = [make_session(error_type="MysteryError")]
        report = generator.generate(sessions)
        assert report.error_entries[0].concept == "알 수 없음"


# ──────────────────────────────────────────────
# 추세 분석
# ──────────────────────────────────────────────

class TestTrend:

    def test_no_trend_when_too_few(self, generator):
        sessions = [make_session()]
        history = make_history(MIN_SESSIONS_FOR_TREND - 1)
        report = generator.generate(sessions, history)
        assert report.trend.has_trend is False

    def test_trend_present_with_enough_history(self, generator):
        sessions = [make_session()]
        history = make_history(MIN_SESSIONS_FOR_TREND)
        report = generator.generate(sessions, history)
        assert report.trend.has_trend is True

    def test_error_direction_down(self, generator):
        sessions = [make_session()]
        history = (
            make_history(3, error=2)
            + [
                HistoricalSession(
                    session_id=100 + i,
                    timestamp=f"2026-06-0{i + 1}T00:00:00",
                    error_count=0,
                )
                for i in range(3)
            ]
        )
        report = generator.generate(sessions, history)
        assert report.trend.error_direction == "down"

    def test_stable_direction_when_equal(self, generator):
        sessions = [make_session()]
        history = make_history(6, clap=5.0)
        report = generator.generate(sessions, history)
        assert report.trend.clap_direction == "stable"


# ──────────────────────────────────────────────
# 개선 제안
# ──────────────────────────────────────────────

class TestSuggestions:

    def test_always_has_at_least_one(self, generator):
        sessions = [make_session(success=True)]
        report = generator.generate(sessions)
        assert len(report.suggestions) >= 1

    def test_high_mccabe_triggers_suggestion(self, generator):
        sessions = [make_session(mccabe=15.0) for _ in range(3)]
        report = generator.generate(sessions)
        assert any("McCabe" in s for s in report.suggestions)

    def test_high_clap_triggers_suggestion(self, generator):
        sessions = [make_session(clap=9.0) for _ in range(3)]
        report = generator.generate(sessions)
        assert any("CLAP" in s for s in report.suggestions)

    def test_slow_execution_triggers_suggestion(self, generator):
        sessions = [make_session(elapsed=8.0) for _ in range(3)]
        report = generator.generate(sessions)
        assert any("실행 시간" in s for s in report.suggestions)

    def test_frequent_error_triggers_suggestion(self, generator):
        sessions = [make_session(error_type="NameError") for _ in range(5)]
        report = generator.generate(sessions)
        assert any("NameError" in s for s in report.suggestions)

    def test_stable_state_gets_default_message(self, generator):
        sessions = [make_session(clap=2.0, mccabe=2.0, elapsed=0.5, success=True)]
        report = generator.generate(sessions)
        assert any("안정적" in s for s in report.suggestions)


# ──────────────────────────────────────────────
# 렌더링
# ──────────────────────────────────────────────

class TestRendering:

    @pytest.fixture
    def report(self, generator):
        sessions = [
            make_session(file_path="a.py", error_type="NameError", clap=8.0),
            make_session(file_path="a.py", success=True),
            make_session(file_path="b.py", error_type="TypeError"),
        ]
        history = make_history(6, error=1)
        return generator.generate(sessions, history)

    def test_text_contains_title(self, renderer, report):
        assert "학습 분석 리포트" in renderer.render_text(report)

    def test_text_contains_file_path(self, renderer, report):
        assert "a.py" in renderer.render_text(report)

    def test_markdown_has_table_header(self, renderer, report):
        assert "| --- |" in renderer.render_markdown(report)

    def test_markdown_has_headings(self, renderer, report):
        md = renderer.render_markdown(report)
        assert "## 요약 통계" in md
        assert "## 오류 분석" in md

    def test_html_is_wrapped(self, renderer, report):
        html = renderer.render_html(report)
        assert html.startswith("<html>")
        assert html.endswith("</html>")

    def test_html_escapes_special_chars(self, renderer, generator):
        sessions = [make_session(file_path="<script>.py", success=True)]
        report = generator.generate(sessions)
        html = renderer.render_html(report)
        assert "<script>.py" not in html
        assert "&lt;script&gt;.py" in html
