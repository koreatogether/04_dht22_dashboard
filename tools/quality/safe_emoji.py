#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전한 이모지 출력 모듈

환경에 따라 이모지 또는 ASCII 대체 문자를 선택적으로 사용합니다.
"""

import os
import sys


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
            if os.environ.get(
                'PYTHONIOENCODING',
                    '').lower().startswith('utf'):
                return True

            # stdout 인코딩 확인
            if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower():
                # 간단한 이모지 출력 테스트
                test_emoji = "[OK]"
                test_emoji.encode(sys.stdout.encoding)
                return True
        except Exception:
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
