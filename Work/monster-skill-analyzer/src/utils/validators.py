"""
입력값 검증 유틸리티
"""


def validate_timing(pre_delay: int, active_duration: int, post_delay: int,
                    dodge_start: int, dodge_end: int) -> list[str]:
    """타이밍 값 유효성 검사. 문제가 있으면 에러 메시지 리스트 반환."""
    errors = []
    if pre_delay < 0:
        errors.append("선딜은 0 이상이어야 합니다.")
    if active_duration <= 0:
        errors.append("판정 지속 시간은 1ms 이상이어야 합니다.")
    if dodge_end <= dodge_start:
        errors.append("회피 가능 종료 시점은 시작 시점보다 커야 합니다.")
    if dodge_start > pre_delay + active_duration:
        errors.append("회피 가능 시작 시점이 판정 범위를 벗어났습니다.")
    return errors


def validate_version(version: str) -> bool:
    """버전 형식 검사 (예: 1.0.0)"""
    parts = version.split(".")
    if len(parts) != 3:
        return False
    return all(p.isdigit() for p in parts)
