"""
PyInstaller .exe 빌드용 런처
Streamlit을 subprocess로 실행하고 브라우저를 자동으로 엽니다.
"""
import sys
import os
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

PORT = 8501
URL = f"http://localhost:{PORT}"


def open_browser():
    """서버가 뜰 때까지 잠시 대기 후 브라우저 열기"""
    time.sleep(3)
    webbrowser.open(URL)


def main():
    # 실행 파일 기준 경로 설정
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent

    app_path = base_dir / "src" / "app.py"

    # 브라우저 열기 (백그라운드)
    threading.Thread(target=open_browser, daemon=True).start()

    # Streamlit 실행
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ])


if __name__ == "__main__":
    main()
