#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이모지 호환성 테스트 도구

현재 환경에서 이모지가 제대로 출력되는지 테스트하고,
안전한 이모지 사용 방법을 제공합니다.
"""

import os
import sys
from pathlib import Path


def test_emoji_output():
    """이모지 출력 테스트"""

    test_emojis = [
        ("[SEARCH]", "SEARCH"),
        ("[OK]", "CHECK_MARK"),
        ("[ERROR]", "CROSS_MARK"),
        ("[WARNING]", "WARNING"),
        ("[SUCCESS]", "ROCKET"),
        ("[DATA]", "BAR_CHART"),
        ("[TOOL]", "WRENCH"),
        ("[TIP]", "LIGHT_BULB"),
        ("[TARGET]", "DART"),
        ("🔒", "LOCK"),
        ("📅", "CALENDAR"),
        ("🛠️", "HAMMER_WRENCH"),
    ]

    print("=== 이모지 호환성 테스트 ===\n")

    # 환경 정보 출력
    print(f"Python 버전: {sys.version}")
    print(f"플랫폼: {sys.platform}")
    print(f"기본 인코딩: {sys.getdefaultencoding()}")
    print(f"파일 시스템 인코딩: {sys.getfilesystemencoding()}")
    print(f"stdout 인코딩: {sys.stdout.encoding}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")
    print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8', 'Not set')}")
    print()

    # 이모지 출력 테스트
    successful_emojis = []
    failed_emojis = []

    for emoji, name in test_emojis:
        try:
            # 출력 시도
            print(f"{emoji} {name}", end="")
            # 인코딩 테스트
            emoji.encode(sys.stdout.encoding or 'utf-8')
            print(" - OK")
            successful_emojis.append((emoji, name))
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            print(f" - FAILED: {e}")
            failed_emojis.append((emoji, name))
        except Exception as e:
            print(f" - ERROR: {e}")
            failed_emojis.append((emoji, name))

    print(f"\n=== 테스트 결과 ===")
    print(
        f"성공: {
            len(successful_emojis)}/{
            len(test_emojis)} ({
            len(successful_emojis) / len(test_emojis) * 100:.1f}%)")
    print(
        f"실패: {
            len(failed_emojis)}/{
            len(test_emojis)} ({
            len(failed_emojis) / len(test_emojis) * 100:.1f}%)")

    return len(failed_emojis) == 0
    def create_safe_emoji_module():
    """안전한 이모지 사용을 위한 모듈 생성"""

    safe_emoji_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전한 이모지 출력 모듈

환경에 따라 이모지 또는 ASCII 대체 문자를 선택적으로 사용합니다.
"""

import sys
import os


class SafeEmoji:
    """안전한 이모지 출력 클래스"""

    def __init__(self):
        self.emoji_support = self._test_emoji_support()

        # 이모지와 ASCII 대체 매핑
        self.emoji_map = {
            "search": ("[SEARCH]", "[검색]"),
            "ok": ("[OK]", "[OK]"),
            "error": ("[ERROR]", "[ERROR]"),
            "warning": ("[WARNING]", "[WARNING]"),
            "rocket": ("[SUCCESS]", "[성공]"),
            "chart": ("[DATA]", "[데이터]"),
            "tool": ("[TOOL]", "[도구]"),
            "idea": ("[TIP]", "[아이디어]"),
            "target": ("[TARGET]", "[목표]"),
            "lock": ("🔒", "[보안]"),
            "calendar": ("📅", "[날짜]"),
            "build": ("🛠️", "[빌드]"),
        }

    def _test_emoji_support(self) -> bool:
        """현재 환경의 이모지 지원 여부 확인"""
        try:
            # UTF-8 환경변수 확인
            if os.environ.get('PYTHONUTF8') == '1':
                return True
            if os.environ.get('PYTHONIOENCODING', '').lower().startswith('utf'):
                return True

            # stdout 인코딩 확인
            if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower():
                # 간단한 이모지 출력 테스트
                test_emoji = "[OK]"
                test_emoji.encode(sys.stdout.encoding)
                return True
        except Exception:
    pass
        return False

    def get(self, name: str) -> str:
        """이모지 또는 대체 문자 반환"""
        if name in self.emoji_map:
            emoji, ascii_alt = self.emoji_map[name]
            return emoji if self.emoji_support else ascii_alt
        return f"[{name.upper()}]"

    def print(self, *args, **kwargs):
        """안전한 이모지 포함 출력"""
        try:
            print(*args, **kwargs)
        except UnicodeEncodeError:
            # 이모지를 ASCII로 변환 후 재시도
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    # 간단한 이모지 → ASCII 변환
                    safe_arg = (arg.replace("[SEARCH]", "[검색]")
                                  .replace("[OK]", "[OK]")
                                  .replace("[ERROR]", "[ERROR]")
                                  .replace("[WARNING]", "[WARNING]")
                                  .replace("[SUCCESS]", "[성공]")
                                  .replace("[DATA]", "[데이터]")
                                  .replace("[TOOL]", "[도구]")
                                  .replace("[TIP]", "[아이디어]")
                                  .replace("[TARGET]", "[목표]")
                                  .replace("🔒", "[보안]")
                                  .replace("📅", "[날짜]")
                                  .replace("🛠️", "[빌드]"))
                    safe_args.append(safe_arg)
                else:
                    safe_args.append(arg)
            print(*safe_args, **kwargs)


# 전역 인스턴스
safe_emoji = SafeEmoji()

# 편의 함수들
def get_emoji(name: str) -> str:
    """이모지 또는 대체 문자 반환"""
    return safe_emoji.get(name)
    def safe_print(*args, **kwargs):
    """안전한 출력"""
    safe_emoji.print(*args, **kwargs)
    def is_emoji_supported() -> bool:
    """이모지 지원 여부 반환"""
    return safe_emoji.emoji_support
'''

    # 모듈 파일 생성
    module_path = Path("tools/quality/safe_emoji.py")
    module_path.parent.mkdir(parents=True, exist_ok=True)

    with open(module_path, "w", encoding="utf-8") as f:
        f.write(safe_emoji_content)

    print(f"안전한 이모지 모듈 생성: {module_path}")
    return module_path
    def main():
    """메인 함수"""
    print("DHT22 프로젝트 이모지 호환성 테스트 도구\\n")

    # 이모지 테스트
    emoji_works = test_emoji_output()

    # 안전한 이모지 모듈 생성
    print("\\n=== 안전한 이모지 모듈 생성 ===")
    module_path = create_safe_emoji_module()

    # 권장사항 출력
    print("\\n=== 권장사항 ===")
    if emoji_works:
        print("[OK] 현재 환경에서 이모지가 정상 출력됩니다!")
        print("[TIP] 이모지를 자유롭게 사용하셔도 됩니다.")
    else:
        print("[WARNING] 현재 환경에서 이모지 출력에 문제가 있을 수 있습니다.")
        print("[TIP] 생성된 safe_emoji 모듈 사용을 권장합니다:")
        print("   from tools.quality.safe_emoji import get_emoji, safe_print")
        print("   print(get_emoji('ok'), '작업 완료')")

    print("\\n=== 환경 개선 방법 ===")
    print("1. 환경변수 설정:")
    print("   set PYTHONUTF8=1")
    print("   set PYTHONIOENCODING=utf-8")
    print("\\n2. 코드에서 UTF-8 강제 설정:")
    print("   import sys, io")
    print("   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')")


if __name__ == "__main__":
    main()
