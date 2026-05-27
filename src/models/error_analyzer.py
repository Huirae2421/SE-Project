"""
error_analyzer.py: 오류 분류 및 패턴 그룹화
"""

from datetime import datetime
from typing import Dict, List
from .data_models import ExecutionResult, ErrorRecord


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

ERROR_GROUPS = {
    "NameError":        "변수 미정의 그룹",
    "IndentationError": "들여쓰기 오류 그룹",
    "TypeError":        "타입 불일치 그룹",
    "SyntaxError":      "문법 오류 그룹",
    "IndexError":       "인덱스 오류 그룹",
    "ValueError":       "값 오류 그룹",
}


# ──────────────────────────────────────────────
# ErrorAnalyzer
# ──────────────────────────────────────────────

class ErrorAnalyzer:

    def classify(self, result: ExecutionResult) -> ErrorRecord | None:
        if result.success or result.error_type is None:
            return None

        error_group = ERROR_GROUPS.get(result.error_type, "기타 오류 그룹")

        return ErrorRecord(
            error_type=result.error_type,
            error_message=result.error_message,
            file_path=result.file_path,
            timestamp=datetime.now().isoformat(),
            error_group=error_group
        )

    # ──────────────────────────────────────────────
    # 오류 요약 통계
    # ──────────────────────────────────────────────

    def get_error_summary(self, error_records: List[ErrorRecord]) -> Dict[str, int]:
        summary: Dict[str, int] = {}

        for record in error_records:
            error_type = record.error_type
            summary[error_type] = summary.get(error_type, 0) + 1

        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))

    def get_group_summary(self, error_records: List[ErrorRecord]) -> Dict[str, int]:
        summary: Dict[str, int] = {}

        for record in error_records:
            group = record.error_group or ERROR_GROUPS.get(record.error_type, "기타 오류 그룹")
            summary[group] = summary.get(group, 0) + 1

        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))

    def get_most_frequent(self, error_records: List[ErrorRecord]) -> str:
        if not error_records:
            return "없음"

        summary = self.get_error_summary(error_records)
        return max(summary, key=lambda x: summary[x])