"""
app_paths.py: 앱 데이터 경로 관리

exe(PyInstaller)로 패키징되면 실행 위치(cwd)가 일정하지 않아 상대 경로로
DB나 로그를 만들면 엉뚱한 곳에 생기거나 쓰기에 실패할 수 있다. 그래서
사용자 홈 아래의 고정 폴더(~/.clap)를 데이터 디렉터리로 사용한다.
"""

import os

APP_DIR_NAME = ".clap"


def data_dir() -> str:
    """앱 데이터 폴더 경로 (없으면 생성). 실패 시 현재 디렉터리로 폴백."""
    base = os.path.join(os.path.expanduser("~"), APP_DIR_NAME)
    try:
        os.makedirs(base, exist_ok=True)
        return base
    except OSError:
        return os.getcwd()


def db_path() -> str:
    return os.path.join(data_dir(), "clap.db")


def log_path() -> str:
    return os.path.join(data_dir(), "clap_error.log")
