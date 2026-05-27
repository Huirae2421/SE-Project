"""
file_watcher.py: 폴더 감시 및 파일 변경 감지
"""

import time
import logging
from typing import Callable, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

DEBOUNCE_SECONDS = 1.0


# ──────────────────────────────────────────────
# 이벤트 핸들러
# ──────────────────────────────────────────────

class PythonFileHandler(FileSystemEventHandler):

    def __init__(self, on_file_changed: Callable[[str], None]):
        super().__init__()
        self.on_file_changed = on_file_changed
        self._last_event_times: Dict[str, float] = {}

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory:
            return
        if not event.src_path.endswith(".py"):
            return

        now = time.time()
        last = self._last_event_times.get(event.src_path, 0.0)

        if now - last < DEBOUNCE_SECONDS:
            return

        self._last_event_times[event.src_path] = now
        self.on_file_changed(event.src_path)


# ──────────────────────────────────────────────
# FileWatcher
# ──────────────────────────────────────────────

class FileWatcher:

    def __init__(self, on_file_changed: Callable[[str], None]):
        self.on_file_changed = on_file_changed
        self._observers: Dict[str, Observer] = {}

    # ──────────────────────────────────────────────
    # 폴더 감시 시작
    # ──────────────────────────────────────────────

    def start_watching(self, folder_path: str) -> bool:
        if folder_path in self._observers:
            return True

        try:
            handler = PythonFileHandler(self.on_file_changed)
            observer = Observer()
            observer.schedule(handler, folder_path, recursive=True)
            observer.start()
            self._observers[folder_path] = observer
            return True

        except Exception as e:
            logging.error(f"폴더 감시 시작 실패 [{folder_path}]: {e}")
            return False

    # ──────────────────────────────────────────────
    # 폴더 감시 중지
    # ──────────────────────────────────────────────

    def stop_watching(self, folder_path: str) -> None:
        observer = self._observers.pop(folder_path, None)
        if observer:
            observer.stop()
            observer.join()

    def stop_all(self) -> None:
        for folder_path in list(self._observers.keys()):
            self.stop_watching(folder_path)

    # ──────────────────────────────────────────────
    # 감시 중인 폴더 목록
    # ──────────────────────────────────────────────

    def get_watching_folders(self) -> list:
        return list(self._observers.keys())

    def is_watching(self, folder_path: str) -> bool:
        return folder_path in self._observers