# CLAP - Code Learning Analysis Program

학생/주니어 개발자의 코딩 학습 패턴과 코드 복잡도를 자동 분석하는 에듀테크 데스크톱 앱.
폴더를 등록해두면 그 안의 `.py` 파일이 저장될 때마다 자동으로 실행·분석되어
오류 패턴, 코드 복잡도(McCabe / CLAP), 학습 난이도를 시각화한다.

작성자: 20211873 김희래 / 과목: 소프트웨어공학

## 아키텍처 (MVC 분리 원칙)

- **Model** (`src/models/`): 분석·데이터 로직. UI와 직접 결합 금지.
  - `code_executor`, `ast_analyzer`, `error_analyzer`, `difficulty_estimator`
  - `visualization_engine`, `database_manager`, `data_models`
  - `error_guide` (오류별 해결 가이드), `report_generator` (학습 리포트 생성/렌더링)
- **Controller** (`src/controllers/`): 흐름 제어.
  - `app_controller`, `analysis_queue`(백그라운드 분석), `file_watcher`(watchdog 감시)
- **View** (`src/views/`): PyQt5 UI. `QStackedWidget` 기반 페이지 전환.
  - `main_window`, `dashboard_view`, `chart_view`, `settings_view`, `report_view`
  - `nav_bar`(상단 고정 네비게이션), `styles`(공통 폰트/색상)

## 실행 / 테스트

```bash
python -m src.main              # 앱 실행
python -m pytest                # 전체 테스트 (현재 159개 통과)
python seed_demo_data.py        # 데모용 샘플 데이터 채우기 (clap.db)
```

- Windows 콘솔 한글 출력 시 `PYTHONIOENCODING=utf-8` 필요할 수 있음.
- DB 파일: `clap.db` (SQLite). 폴더 설정/세션 기록 저장.

## 진행 상황 메모

- [완료] 학습 리포트 기능: `report_generator.py` + 리포트 화면(`report_view`).
  텍스트/Markdown/HTML/PDF 출력. 대시보드 상단 네비 → 📄 리포트.
- [완료] UI 정리: 상단 고정 네비게이션 바(`nav_bar.py`), 난이도별 색상 강조,
  빈 상태 안내, 공통 스타일 `styles.py`.
- [완료] 초보자 빈출 오류 확장: AttributeError(클래스), KeyError, ZeroDivisionError,
  ModuleNotFoundError, UnboundLocalError, RecursionError 분류 + 가이드 + fixtures.
  code_executor subprocess UTF-8(errors=replace)로 한글 출력 깨짐 수정.
- [제거] 연습/퀴즈 기능(hint_engine, practice_recommender, practice_view) — 사용자가
  퀴즈 형태가 학습에 도움 안 된다고 판단해 삭제. 대신 '코드 실수 보강' 방향으로 진행.
- [완료] 오류 도우미(`error_helper_view.py`, 🩹 탭): 최근 오류를 잡아 쉬운 해석 +
  해결법 + ❌잘못된 예/✅올바른 예 코드 비교 + 학습 개념 표시. error_guide 를
  한/영 이중 언어로 확장(cause_en/solution_en/concept_en), UI 언어 따라 한·영 출력.
- [완료] 인터페이스 다국어(한국어/English): `i18n.py`(tr/STRINGS), 설정 화면 언어
  선택 버튼, 즉시 전환(각 뷰 retranslate_ui), DB(app_settings) 저장으로 유지.
  ※ 인터페이스 라벨만 번역. 리포트 본문/힌트/문제 등 '내용'은 한국어 유지.
- [완료] 자기주도 학습 코치(`study_coach.py`): 최근 7일 '이번 주 약점' 진단 +
  약점 기반 'AI에게 물어볼 질문' 자동 생성(개별 + 전체 포괄 종합 질문). 리포트에
  '이번 주 약점' / 'AI에게 물어볼 질문' 섹션으로 통합(텍스트/MD/HTML/PDF).
  → AI 에이전트 앞단의 자기 진단 도구로 포지셔닝(차별점).
- 테스트 209개 통과. 실질 코드 줄(주석/공백 제외) 5,000 초과 달성.

## 요구사항 보강 (문서 점검 후 추가)

- 폴더 삭제 감지(요구사항 2.4): `file_watcher` on_deleted → 감시 해제 + 상태표시줄 경고.
- 분석 진행 표시(요구사항 7.4): AnalysisQueue.on_start → "분석 중: {파일}".
- 저장 실패 알림(요구사항 9.2): save_session 실패 시 on_save_failed → 상태표시줄 빨강 경고.
- MainWindow.show_notification(message, level) 추가(info/warning/error 색상).
- (참고) mccabe/난이도 레이블 영어, 지원오류 6→12 등은 의도적으로 유지(문서만 추후 갱신).

## 경로 / exe 대비 (중요)

- 모든 데이터 경로는 `src/app_paths.py`에서 관리: `~/.clap/` 아래에 `clap.db`,
  `clap_error.log`. (exe 실행 위치와 무관하게 동작하도록 절대경로화 완료)
- 사용자 코드 실행 인터프리터: `code_executor.resolve_python()` — 개발 시
  `sys.executable`, exe(frozen)면 PATH에서 시스템 파이썬을 찾음.

## 향후 할 일 (사용자 요청 — 기억)

- **★ exe 빌드**: PyInstaller로 단일 .exe (더블클릭 실행)가 목표.
  - 예상 명령: `pyinstaller --noconsole --onefile --name CLAP src/main.py`
  - 주의: matplotlib/PyQt5 hidden imports, 폰트(맑은 고딕) 의존, watchdog/radon 동봉.
  - 사용자 머신에 파이썬이 설치돼 있어야 코드 실행/분석 가능(resolve_python 참고).
  - DB/로그는 ~/.clap 에 생기므로 별도 처리 불필요.
- 줄 수 목표: 주석/공백/import 제외하고도 충분하도록 실질 코드(기능+테스트) 위주로 확보.
