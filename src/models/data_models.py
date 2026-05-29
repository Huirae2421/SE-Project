"""
data_models.py: 핵심 데이터 클래스 정의
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List


# ──────────────────────────────────────────────
# 코드 실행 결과
# ──────────────────────────────────────────────

@dataclass
class ExecutionResult:
    file_path: str
    stdout: str = ""
    stderr: str = ""
    error_type: Optional[str] = None
    error_message: str = "" 
    elapsed_seconds: float = 0.0
    timed_out: bool = False
    success: bool = False 


# ──────────────────────────────────────────────
# AST 분석 결과
# ──────────────────────────────────────────────

@dataclass
class ClapComponents:
    branch_count: int = 0
    loop_count: int = 0
    nesting_depth: int = 0
    function_length: float = 0.0
    score: float = 0.0


@dataclass
class ASTResult:
    file_path: str
    valid: bool = True
    line_count: int = 0
    function_count: int = 0
    clap_components: ClapComponents = field(default_factory=ClapComponents)
    mccabe_score: float = 0.0
    mccabe_label: str = "simple"
    feedback_message: str = ""

# ──────────────────────────────────────────────
# 오류 기록
# ──────────────────────────────────────────────

@dataclass
class ErrorRecord:
    error_type: str
    error_message: str
    file_path: str
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    error_group: str = ""

# ──────────────────────────────────────────────
# 학습 난이도
# ──────────────────────────────────────────────

@dataclass
class DifficultyScore:
    score: float = 0.0
    label: str = "collecting data" 
    is_relative: bool = False
    normalized_error: float = 0.0
    normalized_complexity: float = 0.0
    normalized_time: float = 0.0


# ──────────────────────────────────────────────
# 학습 세션
# ──────────────────────────────────────────────

@dataclass
class AnalysisSession:
    file_path: str
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    execution_result: ExecutionResult = field(
        default_factory=lambda: ExecutionResult(file_path="")
    )
    ast_result: ASTResult = field(
        default_factory=lambda: ASTResult(file_path="")
    )
    error_record: Optional[ErrorRecord] = None
    difficulty_score: DifficultyScore = field(
        default_factory=DifficultyScore
    )
    session_id: Optional[int] = None


@dataclass
class HistoricalSession:
    session_id: int
    timestamp: str
    error_count: int = 0
    clap_score: float = 0.0
    mccabe_score: float = 0.0
    elapsed_seconds: float = 0.0
    difficulty_score: float = 0.0
    difficulty_label: str = "collecting data"


# ──────────────────────────────────────────────
# 시각화 데이터
# ──────────────────────────────────────────────

@dataclass
class ChartData:

    has_enough_data: bool = False

    error_bar: Dict[str, int] = field(default_factory=dict)

    activity_line: List[Dict] = field(default_factory=list)

    mccabe_line: List[Dict] = field(default_factory=list)

    clap_line: List[Dict] = field(default_factory=list)
    clap_average: float = 0.0

    difficulty_area: List[Dict] = field(default_factory=list)

    error_pie: Dict[str, float] = field(default_factory=dict)


# ──────────────────────────────────────────────
# 대시보드 데이터
# ──────────────────────────────────────────────

@dataclass
class SummaryStats:
    total_sessions: int = 0
    total_errors: int = 0
    avg_mccabe_score: float = 0.0
    avg_clap_score: float = 0.0
    avg_elapsed_seconds: float = 0.0
    most_frequent_error: str = "none"


@dataclass
class DashboardData:
    latest_session: Optional[AnalysisSession] = None
    difficulty_score: DifficultyScore = field(
        default_factory=DifficultyScore
    )
    error_counts: Dict[str, int] = field(default_factory=dict)
    summary_stats: SummaryStats = field(default_factory=SummaryStats)
    registered_folders: List[str] = field(default_factory=list)