# CLAP - Code Learning Analysis Program

> 코딩 학습 패턴 및 코드 복잡도 분석 시스템

---

## 프로젝트 소개

**CLAP**은 초보 프로그래머 및 학생 개발자가 코딩 학습 과정에서 반복되는 오류와 취약한 문법 패턴을 **스스로 파악**할 수 있도록 돕는 에듀테크 데스크탑 애플리케이션입니다.

학습 중 사용하는 폴더를 등록해두면, `.py` 파일이 저장될 때마다 자동으로 코드를 수집·실행·분석하여 학습 패턴과 코드 복잡도를 시각화하고 학습 리포트를 생성합니다.

정답을 대신 써주는 AI 도구와 달리, CLAP은 **내 오류 패턴을 진단하고 무엇을 더 공부할지 스스로 찾도록 돕는 자기주도 학습 도구**입니다. 외부 LLM API·인터넷 없이 로컬에서 독립 실행됩니다.

---

## 주요 기능

- **자동 분석 파이프라인**: `watchdog`로 폴더를 감시하여 파일 저장만으로 코드 실행 → 오류 분류 → AST 복잡도 분석 → 난이도 추정 → DB 저장을 백그라운드에서 수행
- **실시간 대시보드**: 총 분석 횟수, 총 오류 수, 평균 McCabe/CLAP 점수, 현재 난이도(색상 강조), 최빈 오류를 즉시 갱신
- **6종 시각화 차트**: 오류 발생 횟수, 날짜별 학습 활동, McCabe/CLAP 복잡도 변화, 난이도 변화, 오류 유형 분포 (matplotlib)
- **학습 리포트**: 요약·파일별 분석·오류 분석·개선 제안·이번 주 약점·AI에게 물어볼 질문을 텍스트/Markdown/HTML/**PDF**로 출력
- **오류 도우미**: 최근 오류의 쉬운 해석 + 해결법 + ❌잘못된 예/✅올바른 예 코드 비교 (한국어/English)
- **자기주도 학습 코치**: 최근 7일 약점 진단 + 약점 기반 AI 질문 자동 생성
- **다국어 인터페이스**: 한국어 / English 즉시 전환 (설정 저장)

### 지원 오류 유형 (12종)

`SyntaxError`, `NameError`, `TypeError`, `IndentationError`, `IndexError`, `ValueError`,
`AttributeError`, `KeyError`, `ZeroDivisionError`, `ModuleNotFoundError`, `UnboundLocalError`, `RecursionError`

---

## 기술 스택

| 항목 | 내용 |
|---|---|
| Language | Python 3.10 이상 |
| GUI | PyQt5 |
| Database | SQLite3 |
| File Watching | watchdog |
| Code Analysis | ast, radon |
| Visualization | matplotlib |
| Packaging | PyInstaller |
| Test | pytest, hypothesis (202개 통과) |
| Version Control | GitHub |

---

## 프로젝트 구조

```
SE-Project/
├── docs/                          # 요구사항/설계/구현계획 (Kiro)
├── src/
│   ├── app_paths.py               # 데이터 경로(~/.clap) 관리
│   ├── main.py                    # 애플리케이션 진입점
│   ├── models/                    # 분석·데이터 로직 (UI 비결합)
│   │   ├── data_models.py
│   │   ├── database_manager.py    # SQLite 연동 (스레드 안전)
│   │   ├── code_executor.py       # 코드 실행 및 오류 수집
│   │   ├── ast_analyzer.py        # AST 기반 복잡도 분석
│   │   ├── error_analyzer.py      # 오류 패턴 분류
│   │   ├── difficulty_estimator.py
│   │   ├── visualization_engine.py
│   │   ├── error_guide.py         # 오류별 해결 가이드 (한/영)
│   │   ├── report_generator.py    # 학습 리포트 생성/렌더링
│   │   └── study_coach.py         # 약점 진단 + AI 질문 생성
│   ├── controllers/
│   │   ├── analysis_queue.py      # 백그라운드 분석 파이프라인
│   │   ├── file_watcher.py        # 폴더 감시 (삭제 감지 포함)
│   │   └── app_controller.py      # 전체 흐름 제어
│   └── views/                     # PyQt5 UI
│       ├── main_window.py         # 메인 윈도우 + 상단 네비게이션
│       ├── dashboard_view.py
│       ├── chart_view.py
│       ├── settings_view.py       # 폴더 관리 + 언어 설정
│       ├── report_view.py         # 리포트 화면 (HTML/PDF 저장)
│       ├── error_helper_view.py   # 오류 도우미
│       ├── nav_bar.py, styles.py, i18n.py
├── tests/                         # 단위·속성·통합 테스트 (202개)
├── fixtures/                      # 오류 유형별 샘플 코드
├── seed_demo_data.py              # 데모 데이터 생성 스크립트
├── run_clap.py                    # exe 빌드용 진입점
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
python -m src.main

# (선택) 테스트 / 데모 데이터
python -m pytest
python seed_demo_data.py
```

- 요구 환경: Windows, Python 3.10+, PyQt5
- 데이터는 사용자 홈의 `~/.clap/` 아래(`clap.db`, `clap_error.log`)에 저장되어 실행 위치와 무관하게 동작합니다.

### 사용법

1. 상단 **⚙️ 설정**에서 학습 폴더를 등록합니다.
2. 편집기(VS Code 등)에서 그 폴더의 `.py` 파일을 저장(Ctrl+S)하면 자동 분석됩니다.
3. **🏠 대시보드 / 📊 차트 / 📄 리포트 / 🩹 오류 도우미**에서 결과를 확인합니다.

---

## 실행 파일(.exe) 빌드

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name CLAP run_clap.py
# → dist/CLAP.exe (더블클릭 실행)
```

> exe는 사용자 코드를 실행·분석하므로 대상 PC에 Python이 설치되어 있어야 합니다.

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
데이터 5회 미만: McCabe 점수만 표시 · 5회 이상: 누적 평균 대비 상대 기준 활성화

---

## 개발자

| 이름 | 학번 |
|---|---|
| 김희래 | 20211873 |

## 과목

소프트웨어공학 (2026년 1학기)
