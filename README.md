# CLAP - Code Learning Analysis Program

> 코딩 학습 패턴 및 코드 복잡도 분석 시스템

---

## 프로젝트 소개

**CLAP**은 초보 프로그래머 및 학생 개발자가 코딩 학습 과정에서 반복되는 오류와 취약한 문법 패턴을 스스로 파악할 수 있도록 돕는 에듀테크 데스크탑 애플리케이션입니다.

학습 중 사용하는 폴더를 등록해두면, `.py` 파일이 저장될 때마다 자동으로 코드를 수집하고 분석하여 학습 패턴과 코드 복잡도를 시각화해줍니다.

---

## 주요 기능

- **자동 파일 감시**: `watchdog` 기반으로 등록된 폴더의 `.py` 파일 변경을 실시간 감지
- **오류 로그 분석**: SyntaxError, NameError, TypeError 등 6가지 오류 유형 분류 및 패턴 분석
- **AST 기반 복잡도 분석**: Python `ast` 모듈 + `radon`(McCabe 순환 복잡도)으로 코드 구조 정적 분석
- **학습 난이도 추정**: 오류 빈도, 코드 복잡도, 풀이 시간을 종합한 상대적 난이도 산출
- **데이터 시각화**: matplotlib 기반 6종 그래프로 학습 흐름 시각화

---

## 기술 스택

| 항목 | 내용 |
|---|---|
| Language | Python 3.10 이상 |
| GUI | PyQt5 |
| Database | SQLite3 |
| File Watching | watchdog |
| Code Analysis | ast, radon |
| Data Analysis | pandas, numpy |
| Visualization | matplotlib |
| Test | pytest, hypothesis |
| Version Control | GitHub |

---

## 프로젝트 구조

```
SE-Project/
├── docs/
│   ├── requirements.md       # 요구사항 정의서 (Kiro)
│   ├── design.md             # 설계 문서 SDD (Kiro)
│   └── tasks.md              # 구현 계획 (Kiro)
├── src/
│   ├── models/
│   │   ├── data_models.py        # 데이터 클래스 정의
│   │   ├── database_manager.py   # SQLite 연동
│   │   ├── code_executor.py      # 코드 실행 및 오류 수집
│   │   ├── ast_analyzer.py       # AST 기반 복잡도 분석
│   │   ├── error_analyzer.py     # 오류 패턴 분류
│   │   ├── difficulty_estimator.py # 학습 난이도 추정
│   │   └── visualization_engine.py # 차트 데이터 생성
│   ├── controllers/
│   │   ├── analysis_queue.py     # 분석 파이프라인
│   │   ├── file_watcher.py       # 파일 감시
│   │   └── app_controller.py     # 전체 흐름 제어
│   ├── views/
│   │   ├── main_window.py        # 메인 윈도우
│   │   ├── dashboard_view.py     # 대시보드 화면
│   │   ├── chart_view.py         # 그래프 화면
│   │   └── settings_view.py      # 설정 화면
│   └── main.py                   # 애플리케이션 진입점
├── tests/
│   ├── test_database_manager.py
│   ├── test_code_executor.py
│   ├── test_ast_analyzer.py
│   ├── test_difficulty_estimator.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

---

## 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/Huirae2421/SE-Project.git
cd SE-Project

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 실행
python src/main.py
```

---

## 복잡도 분석 알고리즘

### McCabe 순환 복잡도 (절대 평가)
`radon` 라이브러리로 산출하며 아래 기준으로 평가합니다.

| 점수 | 평가 |
|---|---|
| 10 이하 | 단순한 코드 |
| 11 ~ 20 | 중간 복잡도 |
| 21 이상 | 복잡한 코드, 리팩토링 권장 |

### CLAP 복잡도 (상대 평가)
```
complexity_score = (branch_count × 1.0) + (loop_count × 1.2)
                 + (nesting_depth × 1.5) + (function_length × 0.5)
```
사용자의 누적 평균 대비 상대적으로 해석됩니다.

### 학습 난이도 추정
```
difficulty_score = (normalized_error × 0.4)
                 + (normalized_complexity × 0.3)
                 + (normalized_time × 0.3)
```
데이터 5회 미만: McCabe 점수만 표시  
데이터 5회 이상: 누적 평균 대비 상대 기준 활성화

---

## 개발 일정

| 날짜 | 내용 |
|---|---|
| 2025.05.12 | 주제 선정 및 요구사항 수립 |
| 2025.05.19 | SDD 및 테스트 문서 작성 |
| 2025.05.26 | 구현 |
| 2025.06.02 | 시연 및 평가 |

---

## 개발자

| 이름 | 학번 |
|---|---|
| 김희래 | 20211873 |

---

## 과목

소프트웨어공학 (2025년 1학기)

