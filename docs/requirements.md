# 요구사항 문서: CLAP (Code Learning Analysis Program)

## 소개

CLAP(Code Learning Analysis Program)은 학생 개발자 및 주니어 개발자를 위한 에듀테크 데스크톱 애플리케이션입니다. 사용자가 지정한 학습 폴더를 실시간으로 감시하여 `.py` 파일이 저장될 때마다 자동으로 코드를 실행하고, AST 기반 정적 분석을 통해 복잡도를 산출하며, 오류 패턴과 학습 난이도를 시각화합니다. 외부 API 없이 로컬 환경에서 완전히 독립적으로 동작하며, MVC 패턴 기반의 확장 가능한 구조로 설계됩니다.

---

## 용어 정의 (Glossary)

- **CLAP**: Code Learning Analysis Program. 본 시스템 전체를 지칭합니다.
- **AppController**: View와 Model 사이의 모든 이벤트를 중재하는 컨트롤러 컴포넌트입니다.
- **FileWatcher**: watchdog 라이브러리를 사용하여 등록된 폴더의 `.py` 파일 변경을 감지하는 컴포넌트입니다.
- **AnalysisQueue**: 파일 변경 이벤트를 큐에 넣고 순차적으로 분석 파이프라인을 실행하는 컴포넌트입니다.
- **CodeExecutor**: Python 파일을 서브프로세스로 실행하고 stdout, stderr, 오류 유형을 수집하는 컴포넌트입니다.
- **ASTAnalyzer**: Python `ast` 모듈과 `radon` 라이브러리를 사용하여 코드 복잡도를 분석하는 컴포넌트입니다.
- **ErrorAnalyzer**: 실행 결과에서 오류 유형을 분류하고 DB 저장용 레코드를 생성하는 컴포넌트입니다.
- **DifficultyEstimator**: 오류 빈도, 코드 복잡도, 풀이 시간을 종합하여 학습 난이도 점수를 산출하는 컴포넌트입니다.
- **DatabaseManager**: SQLite3 데이터베이스의 모든 읽기/쓰기를 담당하는 컴포넌트입니다.
- **VisualizationEngine**: DatabaseManager에서 데이터를 조회하여 matplotlib Figure 객체를 생성하는 컴포넌트입니다.
- **MainWindow**: 애플리케이션의 최상위 PyQt5 윈도우 컴포넌트입니다.
- **DashboardView**: 최근 분석 결과 요약, 오류 목록, 난이도 점수를 실시간으로 표시하는 뷰 컴포넌트입니다.
- **ChartView**: matplotlib 기반 6종 차트를 표시하는 뷰 컴포넌트입니다.
- **SettingsView**: 학습 폴더 등록/해제, 데이터 초기화 기능을 제공하는 뷰 컴포넌트입니다.
- **McCabe 순환 복잡도**: radon 라이브러리로 산출하는 코드 복잡도 지표. 10 이하=단순, 11~20=중간, 21 이상=복잡.
- **CLAP 복잡도**: `(분기 수 × 1.0) + (루프 수 × 1.2) + (중첩 깊이 × 1.5) + (함수 길이 × 0.5)` 공식으로 산출하는 자체 복잡도 지표.
- **학습 난이도 점수**: `(정규화된 오류 × 0.4) + (정규화된 복잡도 × 0.3) + (정규화된 시간 × 0.3)` 공식으로 산출하는 0.0~1.0 범위의 점수.
- **AnalysisSession**: 하나의 파일 저장 이벤트에 대한 전체 분석 결과를 담는 데이터 구조.
- **ExecutionResult**: 코드 실행 결과를 담는 데이터 구조.
- **ASTResult**: AST 분석 결과를 담는 데이터 구조.
- **DifficultyScore**: 학습 난이도 추정 결과를 담는 데이터 구조.
- **지원 오류 유형**: SyntaxError, NameError, TypeError, IndentationError, IndexError, ValueError 6종.
- **Debounce**: 동일 파일에 대해 1초 이내 재이벤트를 무시하는 중복 이벤트 방지 메커니즘.

---

## 요구사항

### 요구사항 1: 학습 폴더 등록 및 관리

**사용자 스토리:** 학습자로서, 나는 학습 폴더를 CLAP에 등록하고 관리하고 싶다. 그래야 내가 작업하는 Python 파일들이 자동으로 감시되고 분석될 수 있다.

#### 인수 기준

1. WHEN 사용자가 SettingsView에서 유효한 폴더 경로를 입력하고 등록 버튼을 클릭하면, THE AppController SHALL 해당 경로를 DatabaseManager를 통해 folder_configs 테이블에 저장하고 FileWatcher를 시작한다.
2. WHEN 사용자가 존재하지 않는 폴더 경로를 등록하려 하면, THE AppController SHALL 등록을 거부하고 SettingsView에 "경로를 찾을 수 없습니다" 오류 메시지를 표시한다.
3. WHEN 폴더가 성공적으로 등록되면, THE SettingsView SHALL 등록된 폴더 목록을 갱신하여 표시한다.
4. WHEN 사용자가 등록된 폴더를 해제하면, THE AppController SHALL FileWatcher를 중지하고 DatabaseManager를 통해 folder_configs 테이블에서 해당 경로를 삭제한다.
5. THE AppController SHALL 애플리케이션 시작 시 DatabaseManager에서 저장된 folder_configs를 불러와 FileWatcher를 자동으로 재시작한다.

---

### 요구사항 2: 파일 변경 감지 및 분석 트리거

**사용자 스토리:** 학습자로서, 나는 Python 파일을 저장할 때마다 자동으로 분석이 시작되기를 원한다. 그래야 별도의 조작 없이 즉각적인 피드백을 받을 수 있다.

#### 인수 기준

1. WHEN 등록된 폴더 내의 `.py` 파일이 저장(수정)되면, THE FileWatcher SHALL 해당 파일 경로와 타임스탬프를 AnalysisQueue에 전달한다.
2. WHILE FileWatcher가 동일 파일에 대한 이벤트를 1초 이내에 재수신하면, THE FileWatcher SHALL 해당 중복 이벤트를 무시한다 (Debounce).
3. THE AnalysisQueue SHALL 파일 분석을 백그라운드 스레드에서 실행하여 MainWindow UI가 블로킹되지 않도록 한다.
4. WHEN 등록된 폴더가 외부에서 삭제되면, THE FileWatcher SHALL 해당 폴더의 감시를 중지하고 AppController를 통해 MainWindow 상태 표시줄에 "폴더를 찾을 수 없습니다: {경로}" 경고를 표시한다.
5. WHEN 파일 분석이 완료되면, THE AnalysisQueue SHALL 파일 저장 후 3초 이내에 on_complete 콜백을 호출하여 UI 갱신을 트리거한다.

---

### 요구사항 3: 코드 실행 및 오류 수집

**사용자 스토리:** 학습자로서, 나는 내 Python 코드가 실행되고 발생한 오류가 자동으로 분류되기를 원한다. 그래야 어떤 종류의 오류를 자주 범하는지 파악할 수 있다.

#### 인수 기준

1. WHEN CodeExecutor가 Python 파일을 실행하면, THE CodeExecutor SHALL subprocess를 사용하여 파일을 실행하고 stdout, stderr, 경과 시간을 포함한 ExecutionResult를 반환한다.
2. WHEN 코드 실행 중 오류가 발생하면, THE CodeExecutor SHALL stderr에서 오류 유형을 파싱하여 SyntaxError, NameError, TypeError, IndentationError, IndexError, ValueError 중 하나로 분류하거나, 해당하지 않으면 "UnknownError"로 분류한다.
3. WHEN 코드가 오류 없이 정상 실행되면, THE CodeExecutor SHALL ExecutionResult의 error_type을 None으로 설정한다.
4. WHEN 코드 실행 시간이 10초를 초과하면, THE CodeExecutor SHALL 프로세스를 강제 종료하고 timed_out=True인 ExecutionResult를 반환한다.
5. THE CodeExecutor SHALL 예외 발생 여부와 관계없이 항상 ExecutionResult 인스턴스를 반환하며, 호출자에게 예외를 전파하지 않는다.
6. THE CodeExecutor SHALL UI 컴포넌트와 직접 결합되지 않는다.

---

### 요구사항 4: AST 기반 코드 복잡도 분석

**사용자 스토리:** 학습자로서, 나는 내 코드의 복잡도가 자동으로 측정되기를 원한다. 그래야 코드 구조가 얼마나 복잡해지고 있는지 추적할 수 있다.

#### 인수 기준

1. WHEN ASTAnalyzer가 유효한 Python 소스 코드를 분석하면, THE ASTAnalyzer SHALL radon 라이브러리를 사용하여 McCabe 순환 복잡도를 산출하고 ASTResult에 포함한다.
2. WHEN ASTAnalyzer가 유효한 Python 소스 코드를 분석하면, THE ASTAnalyzer SHALL CLAP 복잡도 공식 `(분기 수 × 1.0) + (루프 수 × 1.2) + (중첩 깊이 × 1.5) + (함수 길이 × 0.5)`를 적용하여 ClapComponents와 CLAP 점수를 산출한다.
3. WHEN McCabe 점수가 10 이하이면, THE ASTAnalyzer SHALL mccabe_label을 "단순"으로 설정한다.
4. WHEN McCabe 점수가 11 이상 20 이하이면, THE ASTAnalyzer SHALL mccabe_label을 "중간"으로 설정한다.
5. WHEN McCabe 점수가 21 이상이면, THE ASTAnalyzer SHALL mccabe_label을 "복잡"으로 설정한다.
6. WHEN 소스 코드가 파싱 불가능한 경우(SyntaxError), THE ASTAnalyzer SHALL valid=False인 ASTResult를 반환한다.
7. THE ASTAnalyzer SHALL 분석 결과에 항상 비어있지 않은 feedback_message를 포함한다.
8. THE ASTAnalyzer SHALL UI 컴포넌트와 직접 결합되지 않는다.

---

### 요구사항 5: 학습 난이도 추정

**사용자 스토리:** 학습자로서, 나는 각 코딩 세션의 학습 난이도가 자동으로 추정되기를 원한다. 그래야 내 학습 곡선을 객관적으로 파악할 수 있다.

#### 인수 기준

1. WHEN DifficultyEstimator가 누적 세션 데이터가 5회 미만인 상태에서 호출되면, THE DifficultyEstimator SHALL is_relative=False이고 label="데이터 수집 중"인 DifficultyScore를 반환한다.
2. WHEN DifficultyEstimator가 누적 세션 데이터가 5회 이상인 상태에서 호출되면, THE DifficultyEstimator SHALL z-score 정규화와 sigmoid 변환을 적용하여 0.0~1.0 범위의 난이도 점수를 산출하고 is_relative=True인 DifficultyScore를 반환한다.
3. WHEN 난이도 점수가 0.75 이상이면, THE DifficultyEstimator SHALL label을 "매우 어려움"으로 설정한다.
4. WHEN 난이도 점수가 0.55 이상이고 정규화된 오류 또는 복잡도 값이 0.6을 초과하면, THE DifficultyEstimator SHALL label을 "평소보다 어려운 코드"로 설정한다.
5. WHEN 난이도 점수가 0.4 이상 0.55 미만이면, THE DifficultyEstimator SHALL label을 "보통"으로 설정한다.
6. WHEN 난이도 점수가 0.4 미만이면, THE DifficultyEstimator SHALL label을 "쉬움"으로 설정한다.
7. THE DifficultyEstimator SHALL 난이도 공식 `(정규화된 오류 × 0.4) + (정규화된 복잡도 × 0.3) + (정규화된 시간 × 0.3)`을 적용하여 최종 점수를 산출한다.
8. THE DifficultyEstimator SHALL UI 컴포넌트와 직접 결합되지 않는다.

---

### 요구사항 6: 분석 데이터 영속성 관리

**사용자 스토리:** 학습자로서, 나는 모든 분석 결과가 로컬 데이터베이스에 안전하게 저장되기를 원한다. 그래야 과거 학습 이력을 언제든지 조회하고 시각화할 수 있다.

#### 인수 기준

1. THE DatabaseManager SHALL 애플리케이션 시작 시 SQLite 데이터베이스를 초기화하고, sessions 테이블과 folder_configs 테이블이 없으면 자동으로 생성한다.
2. WHEN AnalysisQueue가 분석을 완료하면, THE DatabaseManager SHALL AnalysisSession의 모든 필드(file_path, timestamp, elapsed_seconds, error_type, mccabe_score, clap_score, branch_count, loop_count, nesting_depth, function_length, difficulty_score, difficulty_label)를 sessions 테이블에 저장하고 자동 증가 ID를 반환한다.
3. WHEN DatabaseManager가 세션을 저장하면, THE DatabaseManager SHALL 저장된 세션이 get_sessions() 조회 결과에 포함되도록 보장한다.
4. IF SQLite 쓰기 작업이 실패하면, THEN THE DatabaseManager SHALL 트랜잭션을 롤백하여 데이터 무결성을 유지하고 예외를 발생시킨다.
5. THE DatabaseManager SHALL context manager 패턴으로 데이터베이스 연결을 관리한다.
6. WHEN 사용자가 데이터 초기화를 확인하면, THE DatabaseManager SHALL reset_all()을 통해 sessions 테이블의 모든 데이터를 삭제한다.

---

### 요구사항 7: 대시보드 시각화

**사용자 스토리:** 학습자로서, 나는 최근 분석 결과와 누적 통계를 대시보드에서 한눈에 확인하고 싶다. 그래야 현재 학습 상태를 즉시 파악할 수 있다.

#### 인수 기준

1. WHEN AnalysisQueue가 분석을 완료하면, THE DashboardView SHALL 최신 AnalysisSession의 오류 유형별 카운트 테이블을 갱신한다.
2. WHEN AnalysisQueue가 분석을 완료하면, THE DashboardView SHALL 최신 DifficultyScore의 점수와 레이블을 배지 형태로 갱신한다.
3. THE DashboardView SHALL 총 세션 수, 평균 McCabe 복잡도, 평균 난이도 점수를 포함한 누적 통계 요약을 표시한다.
4. WHEN 분석 파이프라인이 실행 중이면, THE MainWindow SHALL 상태 표시줄에 분석 진행 상태를 표시한다.

---

### 요구사항 8: 차트 시각화

**사용자 스토리:** 학습자로서, 나는 오류 패턴, 복잡도 변화, 난이도 추이를 다양한 차트로 시각화하여 확인하고 싶다. 그래야 시간에 따른 학습 성장을 직관적으로 파악할 수 있다.

#### 인수 기준

1. THE VisualizationEngine SHALL 오류 유형별 빈도를 막대 그래프 데이터로 제공한다.
2. THE VisualizationEngine SHALL 날짜별 학습 활동 횟수를 꺾은선 그래프 데이터로 제공한다.
3. THE VisualizationEngine SHALL 시간 순서에 따른 McCabe 복잡도 변화를 꺾은선 그래프 데이터로 제공한다.
4. THE VisualizationEngine SHALL 시간 순서에 따른 CLAP 복잡도 변화와 평균선을 꺾은선 그래프 데이터로 제공한다.
5. THE VisualizationEngine SHALL 시간 순서에 따른 학습 난이도 변화를 영역 그래프 데이터로 제공한다.
6. THE VisualizationEngine SHALL 오류 유형별 비율을 파이 그래프 데이터로 제공한다.
7. WHEN 누적 세션 수가 5회 미만이면, THE ChartView SHALL 차트 대신 "데이터가 충분하지 않습니다 (최소 5회 필요)" 안내 메시지를 표시한다.
8. WHEN AnalysisQueue가 분석을 완료하면, THE ChartView SHALL VisualizationEngine을 통해 모든 차트를 갱신한다.

---

### 요구사항 9: 오류 처리 및 시스템 안정성

**사용자 스토리:** 학습자로서, 나는 예상치 못한 오류가 발생해도 애플리케이션이 계속 동작하기를 원한다. 그래야 학습 흐름이 끊기지 않는다.

#### 인수 기준

1. WHEN AnalysisQueue의 분석 파이프라인에서 예외가 발생하면, THE AnalysisQueue SHALL 해당 예외를 로그 파일에 기록하고 다음 분석 항목 처리를 계속한다.
2. IF DatabaseManager의 쓰기 작업이 실패하면, THEN THE DatabaseManager SHALL 트랜잭션을 롤백하고 오류를 clap_error.log 파일에 기록하며 MainWindow를 통해 "데이터 저장 실패" 알림을 표시한다.
3. WHEN 코드 실행 시간이 10초를 초과하면, THE CodeExecutor SHALL 서브프로세스를 강제 종료하고 DashboardView에 "실행 시간 초과" 메시지가 표시될 수 있도록 timed_out=True인 ExecutionResult를 반환한다.
4. WHEN 사용자가 MainWindow를 닫으면, THE MainWindow SHALL FileWatcher의 모든 Observer를 정리하고 DatabaseManager 연결을 종료한다.
5. WHEN 사용자가 SettingsView에서 "데이터 초기화" 버튼을 클릭하면, THE SettingsView SHALL "모든 학습 데이터가 삭제됩니다. 계속하시겠습니까?" 확인 팝업을 표시하고 사용자 확인 후에만 DatabaseManager.reset_all()을 실행한다.

---

### 요구사항 10: 성능 및 환경 요구사항

**사용자 스토리:** 학습자로서, 나는 일반 교육용 PC에서 파일 저장 후 빠르게 분석 결과를 받고 싶다. 그래야 코딩 흐름을 방해받지 않는다.

#### 인수 기준

1. WHEN Python 파일이 저장되면, THE CLAP SHALL 파일 저장 후 3초 이내에 분석 결과를 DashboardView와 ChartView에 표시한다.
2. THE CLAP SHALL Windows 운영체제, Python 3.10 이상, PyQt5가 설치된 환경에서 동작한다.
3. THE CLAP SHALL RAM 4GB 이상의 일반 교육용 PC에서 정상 동작한다.
4. THE CLAP SHALL 외부 LLM API 또는 인터넷 연결 없이 완전히 로컬 환경에서 독립적으로 동작한다.
5. THE CLAP SHALL 언어별 분석 모듈(CodeExecutor, ASTAnalyzer)을 독립적으로 설계하여 향후 Java, C 등 다른 언어 분석 모듈 추가가 가능한 구조를 유지한다.

---

### 요구사항 11: 파서 및 직렬화 (데이터 저장/복원)

**사용자 스토리:** 개발자로서, 나는 AnalysisSession 데이터가 SQLite에 저장되고 정확하게 복원되기를 원한다. 그래야 분석 이력이 손실 없이 유지된다.

#### 인수 기준

1. WHEN DatabaseManager가 AnalysisSession을 저장하면, THE DatabaseManager SHALL 모든 필드를 SQLite 호환 형식(timestamp는 ISO 8601 문자열)으로 직렬화하여 저장한다.
2. WHEN DatabaseManager가 저장된 세션을 조회하면, THE DatabaseManager SHALL SQLite 레코드를 AnalysisSession 객체로 역직렬화하여 반환한다.
3. FOR ALL 유효한 AnalysisSession 객체에 대해, 저장 후 조회하면 THE DatabaseManager SHALL 원본과 동등한 객체를 반환한다 (직렬화 왕복 속성).
