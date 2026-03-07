"""
주간 자동 업데이트 실행 모듈
Windows Task Scheduler에서 run_collector.py를 직접 호출하는 것을 권장.
이 파일은 스케줄러 설정 헬퍼 및 수동 실행용.
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def run() -> None:
    """run_collector.py를 서브프로세스로 실행"""
    collector_script = BASE_DIR / "run_collector.py"
    result = subprocess.run(
        [sys.executable, str(collector_script)],
        cwd=str(BASE_DIR),
    )
    sys.exit(result.returncode)


def print_task_scheduler_guide() -> None:
    """Windows Task Scheduler 설정 가이드 출력"""
    script_path = BASE_DIR / "run_collector.py"
    print(f"""
Windows Task Scheduler 설정 방법:
1. 작업 스케줄러 열기 (taskschd.msc)
2. [작업 만들기] → 이름: "MMORPG Collector Weekly"
3. [트리거] → 매주 원하는 요일/시간 설정
4. [동작] → 새로 만들기
   - 프로그램: {sys.executable}
   - 인수: {script_path}
   - 시작 위치: {BASE_DIR}
5. [조건] → 네트워크 연결 시에만 실행 체크
""")


if __name__ == "__main__":
    if "--guide" in sys.argv:
        print_task_scheduler_guide()
    else:
        run()
