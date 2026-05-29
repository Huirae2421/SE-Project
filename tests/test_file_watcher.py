"""
test_file_watcher.py: FileWatcher / PythonFileHandler 단위 테스트

debounce(중복 이벤트 무시), .py 필터, 폴더 삭제 감지, 감시 시작/중지를 검증한다.
"""

import time
import pytest

from src.controllers.file_watcher import (
    FileWatcher, PythonFileHandler, DEBOUNCE_SECONDS,
)


# 가짜 watchdog 이벤트
class FakeEvent:
    def __init__(self, src_path, is_directory=False):
        self.src_path = src_path
        self.is_directory = is_directory


# ──────────────────────────────────────────────
# 파일 변경 핸들러
# ──────────────────────────────────────────────

class TestModifiedHandler:

    def test_py_file_triggers_callback(self):
        calls = []
        h = PythonFileHandler(lambda p: calls.append(p))
        h.on_modified(FakeEvent("/x/a.py"))
        assert calls == ["/x/a.py"]

    def test_non_py_ignored(self):
        calls = []
        h = PythonFileHandler(lambda p: calls.append(p))
        h.on_modified(FakeEvent("/x/a.txt"))
        assert calls == []

    def test_directory_event_ignored(self):
        calls = []
        h = PythonFileHandler(lambda p: calls.append(p))
        h.on_modified(FakeEvent("/x/sub", is_directory=True))
        assert calls == []

    def test_debounce_ignores_rapid_duplicate(self):
        calls = []
        h = PythonFileHandler(lambda p: calls.append(p))
        h.on_modified(FakeEvent("/x/a.py"))
        h.on_modified(FakeEvent("/x/a.py"))  # 즉시 재이벤트 → 무시
        assert len(calls) == 1

    def test_debounce_allows_after_interval(self):
        calls = []
        h = PythonFileHandler(lambda p: calls.append(p))
        h.on_modified(FakeEvent("/x/a.py"))
        # 마지막 이벤트 시각을 과거로 돌려 debounce 창을 벗어나게 함
        h._last_event_times["/x/a.py"] = time.time() - DEBOUNCE_SECONDS - 1
        h.on_modified(FakeEvent("/x/a.py"))
        assert len(calls) == 2


# ──────────────────────────────────────────────
# 폴더 삭제 감지
# ──────────────────────────────────────────────

class TestFolderDeletion:

    def test_watched_folder_deleted_fires(self):
        removed = []
        h = PythonFileHandler(
            lambda p: None,
            watched_path="/x/watched",
            on_folder_removed=lambda p: removed.append(p),
        )
        h.on_deleted(FakeEvent("/x/watched", is_directory=True))
        assert removed == ["/x/watched"]

    def test_other_folder_deleted_ignored(self):
        removed = []
        h = PythonFileHandler(
            lambda p: None,
            watched_path="/x/watched",
            on_folder_removed=lambda p: removed.append(p),
        )
        h.on_deleted(FakeEvent("/x/other", is_directory=True))
        assert removed == []

    def test_file_deletion_ignored(self):
        removed = []
        h = PythonFileHandler(
            lambda p: None,
            watched_path="/x/watched",
            on_folder_removed=lambda p: removed.append(p),
        )
        h.on_deleted(FakeEvent("/x/watched/a.py", is_directory=False))
        assert removed == []


# ──────────────────────────────────────────────
# 감시 시작/중지
# ──────────────────────────────────────────────

class TestWatching:

    def test_start_and_is_watching(self, tmp_path):
        fw = FileWatcher(on_file_changed=lambda p: None)
        ok = fw.start_watching(str(tmp_path))
        try:
            assert ok is True
            assert fw.is_watching(str(tmp_path)) is True
            assert str(tmp_path) in fw.get_watching_folders()
        finally:
            fw.stop_all()

    def test_stop_watching(self, tmp_path):
        fw = FileWatcher(on_file_changed=lambda p: None)
        fw.start_watching(str(tmp_path))
        fw.stop_watching(str(tmp_path))
        assert fw.is_watching(str(tmp_path)) is False

    def test_start_invalid_folder_returns_false(self):
        fw = FileWatcher(on_file_changed=lambda p: None)
        ok = fw.start_watching("/nonexistent/path/xyz123")
        assert ok is False
