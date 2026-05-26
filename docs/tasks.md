# 구현 계획: CLAP (Code Learning Analysis Program)

## 개요

MVC 패턴 기반의 Python 에듀테크 데스크톱 애플리케이션을 단계적으로 구현합니다. 데이터 모델 및 DB 레이어부터 시작하여 분석 엔진(Model), 컨트롤러, PyQt5 UI(View) 순서로 구현하고, 마지막에 전체를 연결합니다. 각 단계에서 핵심 기능을 검증하는 속성 기반 테스트와 단위 테스트를 함께 작성합니다.

## 태스크

- [ ] 1. 프로젝트 구조 설정 및 핵심 데이터 모델 정의
  - `src/models/`, `src/controllers/`, `src/views/`, `tests/` 디렉토리 구조 생성
  - `requirements.txt` 작성 (PyQt5, watchdog, radon, hypothesis, pytest)
  - `src/models/data_models.py`에 `ExecutionResult`, `ClapComponents`, `ASTResult`, `ErrorRecord`, `DifficultyScore`, `AnalysisSession`, `HistoricalSession`, `ChartData`, `DashboardData`, `SummaryStats` 데이터클래스 구현
  - `src/models/__init__.py`, `src/controllers/__init__.py`, `src/views/__init__.py` 초기화 파일 생성
  - _요구사항: 3.1, 3.2, 4.2, 5.2, 6.2_

- [ ] 2. DatabaseManager 구현
  - [ ] 2.1 DatabaseManager 클래스 구현
    - `src/models/database_manager.py`에 `DatabaseManager` 클래스 작성
    - `initialize_schema()`: sessions, folder_configs 테이블 및 인덱스 자동 생성
    - `save_session()`: AnalysisSession 직렬화 후 저장, 자동 증가 ID 반환, 실패 시 트랜잭션 롤백
    - `get_sessions()`: SQLite 레코드를 AnalysisSession 객체로 역직렬화하여 반환
    - `get_error_counts()`, `get_folder_configs()`, `save_folder_config()`, `delete_folder_config()`, `reset_all()`, `close()` 구현
    - context manager 패턴으로 연결 관리
    - _요구사항: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 11.1, 11.2, 11.3_

  - [ ]* 2.2 속성 테스트: 저장-조회 왕복 (속성 8)
    - **속성 8: 저장된 세션은 조회 가능 (저장-조회 왕복)**
    - **검증 대상: 요구사항 6.3, 11.3**
    - hypothesis로 임의의 유효한 AnalysisSession 생성 후 저장, get_sessions() 결과에 포함되는지 검증

  - [ ]* 2.3 속성 테스트: DB 쓰기 실패 시 데이터 무결성 (속성 9)
    - **속성 9: DB 쓰기 실패 시 데이터 무결성 유지**
    - **검증 대상: 요구사항 6.4**
    - 잘못된 세션 데이터로 save_session() 실패 시 get_sessions() 결과 수가 변하지 않음을 검증

  - [ ]* 2.4 속성 테스트: AnalysisSession 직렬화 왕복 (속성 10)
    - **속성 10: AnalysisSession 직렬화 왕복**
    - **검증 대상: 요구사항 11.3**
    - 저장 후 조회한 객체가 원본과 모든 필드(file_path, timestamp, error_type, mccabe_score, clap_score, difficulty_score, difficulty_label)에서 동등함을 검증

- [ ] 3. 체크포인트 - DatabaseManager 테스트 통과 확인
  - 모든 테스트가 통과하는지 확인하고, 문제가 있으면 사용자에게 질문하세요.

- [ ] 4. CodeExecutor 구현
  - [ ] 4.1 CodeExecutor 클래스 구현
    - `src/models/code_executor.py`에 `CodeExecutor` 클래스 작성
    - `SUPPORTED_ERRORS` frozenset 정의 (SyntaxError, NameError, TypeError, IndentationError, IndexError, ValueError)
    - `execute()`: subprocess.run으로 파일 실행, stdout/stderr/elapsed_seconds 수집, 항상 ExecutionResult 반환 (예외 전파 금지)
    - `_parse_error_type()`: 정규식으로 stderr에서 오류 유형 파싱, 미지원 오류는 "UnknownError" 반환
    - timeout 초과 시 timed_out=True인 ExecutionResult 반환
    - _요구사항: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 4.2 속성 테스트: 오류 유형은 지원 목록 내에 있거나 None (속성 1)
    - **속성 1: 오류 유형은 지원 목록 내에 있거나 None**
    - **검증 대상: 요구사항 3.2**
    - hypothesis로 임의의 Python 코드 파일 생성 후 실행, error_type이 None이거나 지원 집합 내에 있음을 검증

  - [ ]* 4.3 속성 테스트: 정상 실행 시 error_type은 None (속성 2)
    - **속성 2: 정상 실행 시 error_type은 None**
    - **검증 대상: 요구사항 3.3**
    - 오류 없이 실행되는 Python 코드에 대해 error_type이 None임을 검증

  - [ ]* 4.4 단위 테스트: CodeExecutor 예외 케이스
    - SyntaxError, NameError, TypeError, IndentationError, IndexError, ValueError 각각에 대한 파일 실행 결과 검증
    - timeout=1.0으로 무한 루프 파일 실행 시 timed_out=True 검증
    - _요구사항: 3.2, 3.4_

- [ ] 5. ASTAnalyzer 구현
  - [ ] 5.1 ASTAnalyzer 클래스 구현
    - `src/models/ast_analyzer.py`에 `ASTAnalyzer` 클래스 작성
    - `analyze()`: ast.parse()로 파싱, 실패 시 valid=False인 ASTResult 반환, 항상 비어있지 않은 feedback_message 포함
    - `_compute_mccabe()`: radon.complexity.cc_visit()으로 McCabe 점수 산출, 레이블 결정 (≤10="단순", 11~20="중간", ≥21="복잡")
    - `_compute_clap_score()`: ast.walk()로 branch_count, loop_count, function_length 집계
    - `_max_nesting_depth()`: 재귀 DFS로 최대 중첩 깊이 계산 (If, For, While, With, Try, FunctionDef 노드 기준)
    - CLAP 공식 적용: `(branch × 1.0) + (loop × 1.2) + (depth × 1.5) + (func_len × 0.5)`
    - _요구사항: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

  - [ ]* 5.2 속성 테스트: AST 분석 결과의 수치 불변 속성 (속성 3)
    - **속성 3: AST 분석 결과의 수치 불변 속성**
    - **검증 대상: 요구사항 4.2**
    - hypothesis로 임의의 유효한 Python 소스 코드 생성, clap_components.score >= 0.0, nesting_depth >= 0, branch_count >= 0, loop_count >= 0 모두 만족함을 검증

  - [ ]* 5.3 속성 테스트: McCabe 레이블은 점수 범위와 일치 (속성 4)
    - **속성 4: McCabe 레이블은 점수 범위와 일치**
    - **검증 대상: 요구사항 4.3, 4.4, 4.5**
    - hypothesis로 임의의 유효한 Python 소스 코드 생성, mccabe_label이 mccabe_score 범위와 정확히 일치함을 검증

  - [ ]* 5.4 단위 테스트: ASTAnalyzer 예외 케이스
    - 중첩 깊이 3 이상 코드에서 nesting_depth >= 3, score > 0.0 검증
    - SyntaxError 코드에서 valid=False 검증
    - 빈 문자열 입력 처리 검증
    - _요구사항: 4.6, 4.7_

- [ ] 6. ErrorAnalyzer 및 DifficultyEstimator 구현
  - [ ] 6.1 ErrorAnalyzer 클래스 구현
    - `src/models/error_analyzer.py`에 `ErrorAnalyzer` 클래스 작성
    - `classify()`: ExecutionResult에서 ErrorRecord 생성 (error_type, timestamp, file_path)
    - `get_error_summary()`: 세션 ID 기반 오류 유형별 카운트 딕셔너리 반환
    - _요구사항: 3.2, 7.1_

  - [ ] 6.2 DifficultyEstimator 클래스 구현
    - `src/models/difficulty_estimator.py`에 `DifficultyEstimator` 클래스 작성
    - `estimate()`: history 길이 < 5이면 is_relative=False, label="데이터 수집 중" 반환; 5 이상이면 z-score + sigmoid 정규화 후 가중 합산
    - `_normalize()`: z-score 계산 후 sigmoid 변환으로 0~1 범위 반환, stdev=0이면 0.5 반환
    - `_label()`: score >= 0.75 → "매우 어려움", score >= 0.55 AND (norm_error > 0.6 OR norm_complexity > 0.6) → "평소보다 어려운 코드", score >= 0.4 → "보통", else → "쉬움"
    - 난이도 공식: `(normalized_error × 0.4) + (normalized_complexity × 0.3) + (normalized_time × 0.3)`
    - _요구사항: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

  - [ ]* 6.3 속성 테스트: 데이터 5회 미만 시 is_relative=False (속성 5)
    - **속성 5: 데이터 5회 미만 시 is_relative=False**
    - **검증 대상: 요구사항 5.1**
    - hypothesis로 길이 0~4인 임의의 히스토리 목록 생성, is_relative가 False임을 검증

  - [ ]* 6.4 속성 테스트: 정규화된 난이도 점수는 0~1 범위 (속성 6)
    - **속성 6: 정규화된 난이도 점수는 0~1 범위**
    - **검증 대상: 요구사항 5.2**
    - hypothesis로 길이 5 이상인 임의의 히스토리 목록 생성, score가 0.0~1.0 범위이고 is_relative=True임을 검증

  - [ ]* 6.5 속성 테스트: 난이도 레이블은 정의된 집합 내에 있음 (속성 7)
    - **속성 7: 난이도 레이블은 정의된 집합 내에 있음**
    - **검증 대상: 요구사항 5.3, 5.4, 5.5, 5.6**
    - hypothesis로 임의의 입력 생성, label이 {"쉬움", "보통", "평소보다 어려운 코드", "매우 어려움", "데이터 수집 중"} 집합 내에 있음을 검증

- [ ] 7. 체크포인트 - Model 레이어 테스트 통과 확인
  - 모든 Model 클래스 테스트가 통과하는지 확인하고, 문제가 있으면 사용자에게 질문하세요.

- [ ] 8. VisualizationEngine 구현
  - [ ] 8.1 VisualizationEngine 클래스 구현
    - `src/models/visualization_engine.py`에 `VisualizationEngine` 클래스 작성
    - `build_chart_data()`: 6개 내부 메서드를 호출하여 ChartData 객체 반환, 세션 수 < 5이면 has_enough_data=False
    - `_error_bar_data()`: 오류 유형별 빈도 딕셔너리 반환
    - `_activity_line_data()`: 날짜별 학습 활동 횟수 리스트 반환
    - `_mccabe_line_data()`, `_clap_line_data()`: 시간 순서 복잡도 변화 데이터 반환
    - `_difficulty_area_data()`: 시간 순서 난이도 변화 데이터 반환 (값은 0.0~1.0)
    - `_error_pie_data()`: 오류 유형별 비율 딕셔너리 반환
    - _요구사항: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ]* 8.2 속성 테스트: VisualizationEngine 차트 데이터 형식 불변 속성 (속성 11)
    - **속성 11: VisualizationEngine 차트 데이터 형식 불변 속성**
    - **검증 대상: 요구사항 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
    - hypothesis로 임의의 세션 데이터 저장 후 build_chart_data() 호출, error_bar 값 ≥ 0, activity_line 카운트 ≥ 0, mccabe_line/clap_line 점수 ≥ 0.0, difficulty_area 점수 0.0~1.0 범위 모두 만족함을 검증

- [ ] 9. AnalysisQueue 및 FileWatcher 구현
  - [ ] 9.1 AnalysisQueue 클래스 구현
    - `src/controllers/analysis_queue.py`에 `AnalysisQueue` 클래스 작성
    - `enqueue()`: threading.Thread로 `_process()`를 백그라운드에서 실행
    - `_process()`: CodeExecutor → ASTAnalyzer → ErrorAnalyzer → DifficultyEstimator → DatabaseManager.save_session() → on_complete() 콜백 순서로 파이프라인 실행
    - 예외 발생 시 clap_error.log에 기록 후 다음 항목 처리 계속
    - _요구사항: 2.3, 2.5, 9.1_

  - [ ] 9.2 FileWatcher 클래스 구현
    - `src/controllers/file_watcher.py`에 `FileWatcher` 클래스 작성
    - watchdog Observer와 FileSystemEventHandler 활용
    - `.py` 파일의 on_modified 이벤트만 처리
    - debounce: 동일 파일 1초 이내 재이벤트 무시 (마지막 이벤트 시각 딕셔너리로 관리)
    - `start_watching()`, `stop_watching()`, `stop_all()` 구현
    - 폴더 삭제 감지 시 AppController를 통해 경고 표시
    - _요구사항: 2.1, 2.2, 2.4_

  - [ ]* 9.3 단위 테스트: AnalysisQueue 파이프라인
    - Mock 객체로 각 Model 컴포넌트를 대체하여 파이프라인 순서 및 on_complete 콜백 호출 검증
    - 파이프라인 중 예외 발생 시 다음 항목 처리 계속됨을 검증
    - _요구사항: 2.3, 2.5, 9.1_

- [ ] 10. AppController 구현
  - [ ] 10.1 AppController 클래스 구현
    - `src/controllers/app_controller.py`에 `AppController` 클래스 작성
    - `register_folder()`: 경로 유효성 검사 → DatabaseManager.save_folder_config() → FileWatcher.start_watching(), 실패 시 Result 오류 반환
    - `unregister_folder()`: FileWatcher.stop_watching() → DatabaseManager.delete_folder_config()
    - `on_file_changed()`: AnalysisQueue.enqueue() 호출
    - `get_dashboard_data()`: DatabaseManager에서 DashboardData 조합하여 반환
    - `get_chart_data()`: VisualizationEngine.build_chart_data() 반환
    - `reset_all_data()`: DatabaseManager.reset_all() 호출
    - 앱 시작 시 저장된 folder_configs 불러와 FileWatcher 자동 재시작
    - _요구사항: 1.1, 1.2, 1.3, 1.4, 1.5, 10.5_

  - [ ]* 10.2 단위 테스트: AppController 폴더 등록/해제
    - 유효한 경로 등록 시 FileWatcher 시작 및 DB 저장 검증
    - 존재하지 않는 경로 등록 시 오류 반환 검증
    - 폴더 해제 시 FileWatcher 중지 및 DB 삭제 검증
    - _요구사항: 1.1, 1.2, 1.4_

- [ ] 11. 체크포인트 - Controller 레이어 테스트 통과 확인
  - 모든 Controller 클래스 테스트가 통과하는지 확인하고, 문제가 있으면 사용자에게 질문하세요.

- [ ] 12. PyQt5 View 레이어 구현
  - [ ] 12.1 MainWindow 구현
    - `src/views/main_window.py`에 `MainWindow(QMainWindow)` 클래스 작성
    - `setup_ui()`: QTabWidget으로 DashboardView, ChartView, SettingsView 탭 구성
    - `show_notification()`: 상태 표시줄에 메시지 표시 (info/warning/error 레벨)
    - `closeEvent()`: FileWatcher.stop_all() 및 DatabaseManager.close() 호출
    - _요구사항: 9.4, 10.2_

  - [ ] 12.2 DashboardView 구현
    - `src/views/dashboard_view.py`에 `DashboardView(QWidget)` 클래스 작성
    - `refresh()`: AnalysisSession 수신 후 오류 테이블, 난이도 배지, 누적 통계 갱신
    - `update_error_table()`: QTableWidget으로 오류 유형별 카운트 표시
    - `update_difficulty_badge()`: DifficultyScore의 label과 score를 배지 형태로 표시
    - `update_summary_stats()`: 총 세션 수, 평균 McCabe, 평균 난이도 표시
    - _요구사항: 7.1, 7.2, 7.3, 7.4_

  - [ ] 12.3 ChartView 구현
    - `src/views/chart_view.py`에 `ChartView(QWidget)` 클래스 작성
    - FigureCanvasQTAgg로 matplotlib Figure를 PyQt5 위젯에 임베드
    - `render_all()`: ChartData.has_enough_data가 False이면 "데이터가 충분하지 않습니다 (최소 5회 필요)" 메시지 표시
    - `render_error_bar()`, `render_activity_line()`, `render_mccabe_line()`, `render_clap_line()`, `render_difficulty_area()`, `render_error_pie()` 각 차트 렌더링 메서드 구현
    - _요구사항: 8.7, 8.8_

  - [ ] 12.4 SettingsView 구현
    - `src/views/settings_view.py`에 `SettingsView(QWidget)` 클래스 작성
    - `get_folder_path()`: QLineEdit에서 폴더 경로 반환
    - `show_registered_folders()`: 등록된 폴더 목록을 QListWidget으로 표시
    - `confirm_reset()`: "모든 학습 데이터가 삭제됩니다. 계속하시겠습니까?" 확인 팝업 표시 후 bool 반환
    - 등록/해제 버튼 클릭 시 AppController 메서드 호출
    - _요구사항: 1.1, 1.2, 1.3, 1.4, 9.5_

- [ ] 13. 애플리케이션 진입점 및 전체 연결
  - [ ] 13.1 main.py 작성 및 컴포넌트 연결
    - `src/main.py`에 애플리케이션 진입점 작성
    - DatabaseManager 초기화 및 스키마 생성
    - CodeExecutor, ASTAnalyzer, ErrorAnalyzer, DifficultyEstimator, VisualizationEngine 인스턴스 생성
    - AnalysisQueue 생성 (on_complete 콜백으로 DashboardView.refresh 및 ChartView.render_all 연결)
    - FileWatcher 생성 (콜백으로 AppController.on_file_changed 연결)
    - AppController 생성 및 저장된 폴더 자동 감시 재시작
    - MainWindow 생성 후 QApplication 실행
    - _요구사항: 1.5, 2.3, 10.1, 10.2, 10.3, 10.4_

  - [ ] 13.2 스레드 안전 UI 갱신 처리
    - AnalysisQueue의 on_complete 콜백에서 PyQt5 시그널/슬롯을 사용하여 메인 스레드에서 UI 갱신 보장
    - QMetaObject.invokeMethod 또는 커스텀 QObject 시그널로 백그라운드 스레드 → 메인 스레드 전달 구현
    - _요구사항: 2.3, 2.5_

  - [ ]* 13.3 통합 테스트: 전체 분석 파이프라인
    - 임시 폴더에 .py 파일 저장 → FileWatcher 감지 → AnalysisQueue 처리 → DB 저장 → UI 갱신 콜백 호출까지 전체 흐름 검증
    - _요구사항: 2.1, 2.5, 10.1_

- [ ] 14. 최종 체크포인트 - 전체 테스트 통과 확인
  - 모든 단위 테스트, 속성 테스트, 통합 테스트가 통과하는지 확인하고, 문제가 있으면 사용자에게 질문하세요.

## 참고 사항

- `*` 표시된 태스크는 선택 사항으로, MVP 구현 시 건너뛸 수 있습니다.
- 각 태스크는 이전 태스크를 기반으로 구축되며, 고아 코드 없이 단계적으로 통합됩니다.
- 속성 테스트는 [hypothesis](https://hypothesis.readthedocs.io/) 라이브러리를 사용합니다.
- Model 클래스는 UI 코드와 직접 결합하지 않으므로 독립적으로 테스트 가능합니다.
- 체크포인트에서 테스트 실패 시 해당 컴포넌트로 돌아가 수정 후 진행합니다.
