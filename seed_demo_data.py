"""
seed_demo_data.py: 대시보드 확인용 샘플 데이터 생성 스크립트

fixtures 폴더의 샘플 코드를 실제 분석 파이프라인에 통과시켜 clap.db에
학습 세션 데이터를 채운다. 차트가 단조롭게 보이지 않도록 파일마다 등장
횟수를 다르게 주고, 세션을 지난 며칠에 걸쳐 분산시켜 오류 분포·날짜별
활동·난이도 추이가 다채롭게 나오도록 한다.

실행:
    python seed_demo_data.py          # clap.db 초기화 후 샘플 채우기
    python seed_demo_data.py --keep   # 기존 데이터 유지하고 추가
"""

import os
import sys
import random
from datetime import datetime, timedelta

from src.models.database_manager import DatabaseManager
from src.models.code_executor import CodeExecutor
from src.models.ast_analyzer import ASTAnalyzer
from src.models.error_analyzer import ErrorAnalyzer
from src.models.difficulty_estimator import DifficultyEstimator
from src.models.data_models import AnalysisSession


FIXTURES_DIR = "fixtures"

# 파일별 등장 횟수 (서로 다르게 주어 오류 분포를 다채롭게 만든다)
FIXTURE_WEIGHTS = {
    "name_error.py":             6,
    "value_error.py":            5,
    "attribute_error.py":        5,
    "type_error.py":             4,
    "clean_code.py":             4,
    "module_not_found_error.py": 4,
    "key_error.py":              3,
    "index_error.py":            3,
    "indentation_error.py":      3,
    "zero_division_error.py":    3,
    "syntax_error.py":           2,
    "long_function.py":          2,
    "deep_nesting.py":           2,
    "unbound_local_error.py":    2,
    "recursion_error.py":        2,
    "dangerous_code.py":         1,
}
DEFAULT_WEIGHT = 2

# 세션을 분산시킬 기간(일)
DAYS_SPREAD = 14

# 재현 가능하도록 난수 고정
random.seed(42)


def analyze_fixtures(executor, analyzer, classifier):
    """각 샘플을 한 번씩 실제 분석하여 기준 결과를 만든다."""
    base = {}
    fixtures = sorted(
        f for f in os.listdir(FIXTURES_DIR) if f.endswith(".py")
    )
    for name in fixtures:
        path = os.path.join(FIXTURES_DIR, name)
        execution_result = executor.execute(path)
        ast_result = analyzer.analyze(path)
        error_record = classifier.classify(execution_result)
        base[name] = (path, execution_result, ast_result, error_record)
    return base


def build_instances(base):
    """등장 횟수와 분산된 타임스탬프를 적용한 세션 인스턴스 목록을 만든다."""
    now = datetime.now()
    instances = []

    for name, (path, er, ar, rec) in base.items():
        weight = FIXTURE_WEIGHTS.get(name, DEFAULT_WEIGHT)
        for _ in range(weight):
            day_offset = random.randint(0, DAYS_SPREAD)
            timestamp = now - timedelta(
                days=DAYS_SPREAD - day_offset,
                hours=random.randint(0, 9),
                minutes=random.randint(0, 59),
            )
            instances.append((timestamp, path, er, ar, rec))

    # 시간 순으로 정렬하여 난이도 추세가 자연스럽게 누적되도록 한다
    instances.sort(key=lambda item: item[0])
    return instances


def main() -> None:
    keep = "--keep" in sys.argv

    if not os.path.isdir(FIXTURES_DIR):
        print(f"fixtures 폴더를 찾을 수 없습니다: {FIXTURES_DIR}")
        return

    db = DatabaseManager()
    if not keep:
        db.reset_all()
        print("기존 데이터를 초기화했습니다.")

    executor = CodeExecutor()
    analyzer = ASTAnalyzer()
    classifier = ErrorAnalyzer()
    estimator = DifficultyEstimator()

    base = analyze_fixtures(executor, analyzer, classifier)
    instances = build_instances(base)

    print(f"{len(base)}개 샘플로 {len(instances)}개의 세션을 생성합니다...")
    for timestamp, path, er, ar, rec in instances:
        history = db.get_historical_sessions()
        difficulty = estimator.estimate(
            history=history,
            current_error_count=1 if rec else 0,
            current_clap_score=ar.clap_components.score,
            current_elapsed=er.elapsed_seconds,
        )
        session = AnalysisSession(
            file_path=path,
            timestamp=timestamp.isoformat(),
            execution_result=er,
            ast_result=ar,
            error_record=rec,
            difficulty_score=difficulty,
        )
        db.save_session(session)

    # 생성된 오류 분포를 보기 좋게 출력
    counts = db.get_error_counts()
    print(f"\n완료! 총 세션 {len(db.get_sessions(limit=1000))}개")
    print("오류 유형별 발생 횟수:")
    for error_type, count in counts.items():
        print(f"  - {error_type}: {count}")
    print("\n'python -m src.main' 으로 앱을 실행해 차트를 확인하세요.")

    db.close()


if __name__ == "__main__":
    main()
