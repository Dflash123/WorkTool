"""
Monster Skill Analyzer - 앱 런처
Flask 서버를 시작하고 브라우저를 자동으로 엽니다.
run.bat이 이 파일을 실행합니다.
"""
import sys
import os
import subprocess
import threading
import time
import webbrowser
import socket

PORT = 5000
URL = f"http://localhost:{PORT}"


def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def open_browser_when_ready():
    """서버가 응답할 때까지 대기 후 브라우저 자동 열기"""
    for _ in range(40):  # 최대 20초 대기
        time.sleep(0.5)
        try:
            s = socket.create_connection(("localhost", PORT), timeout=1)
            s.close()
            break
        except OSError:
            continue
    webbrowser.open(URL)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 50)
    print("  Monster Skill Analyzer")
    print("  Flask Web App")
    print("=" * 50)
    print()

    # 포트 사용 중이면 브라우저만 열기
    if not is_port_free(PORT):
        print(f"[INFO] Port {PORT} already in use. Opening browser...")
        webbrowser.open(URL)
        return

    # 브라우저를 백그라운드 스레드에서 서버 준비 후 열기
    t = threading.Thread(target=open_browser_when_ready, daemon=True)
    t.start()

    print(f"[START] Server starting at {URL}")
    print("[INFO]  Browser will open automatically.")
    print("[STOP]  Press Ctrl+C or close this window to stop.")
    print()

    # Flask 실행
    server_path = os.path.join(base_dir, "src", "server.py")
    try:
        subprocess.run(
            [sys.executable, server_path],
            check=True,
        )
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Server exited with code {e.returncode}")
    finally:
        print()
        print("[STOPPED] App has been stopped.")
        input("Press Enter to close...")


if __name__ == "__main__":
    main()
