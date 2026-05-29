"""
run_clap.py: exe 빌드용 진입점 런처

PyInstaller로 단일 실행 파일을 만들 때 사용한다. 프로젝트 루트에서
src 패키지를 임포트할 수 있도록 하는 얇은 래퍼이며, 실제 로직은
src/main.py 의 main() 에 있다.

빌드 예시:
    pyinstaller --noconsole --onefile --name CLAP run_clap.py
"""

from src.main import main

if __name__ == "__main__":
    main()
