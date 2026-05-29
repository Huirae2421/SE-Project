"""
module_not_found_error.py: 없는 모듈 import (ModuleNotFoundError)
초보자가 라이브러리 설치/철자를 놓칠 때 자주 발생한다.
"""

# 존재하지 않는 모듈 -> ModuleNotFoundError
import nonexistent_module_xyz

print(nonexistent_module_xyz.value)
