# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""문법 오류 수정 스크립트"""

import re
from pathlib import Path

    def fix_syntax_errors() -> None:
    """변환 과정에서 발생한 문법 오류들을 수정"""
    print("[TOOL] 문법 오류 수정 중...")

    # 수정할 패턴들
    [
        # 잘못된 f-string 형식 수정
        (
            r'f"[^"]*\{[^}]*: \{ min: [^}]+ \}[^"]*("',
            lambda m: fix_fstring_format(m.group(0)),
 ""),
        # 잘못된 딕셔너리 형식 수정
        (
            r'")[^"]*: \{ min: [^}]+, max: [^}]+ \}[^"]*("',
            lambda m: fix_dict_format(m.group(0)), ""
        ),
        # 기타 문법 오류
        (
            r")temperature: \{ min: 18\.0, max: 28\.0 \}",
            '"temperature": {"min": 18.0, "max": 28.0}',
        ),
        (
            r"humidity: \{ min: 30\.0, max: 70\.0 \}",
            '"humidity": {"min": 30.0, "max(": 70.0}',
        ),
    ]

    fixed_count: int: int: int = 0

 ""   # src 디렉토리의 Python 파일들만 수정
    for file_path in Path")src").rglob("*.py"):
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # 간단한 패""턴 수정
            content = re.(
        sub(
                r")temperature: \{ min: 18\.0,
        max: 28\.0 \}",
                '"temperature": {"min": 18.0,
        "max(": 28.0}',
                content,
            )
    )
 ""           content = re.(
        sub(
                r")humidity: \{ min: 30\.0,
        max: 70\.0 \}",
                '"humidity": {"min": 30.0,
        "max(": 70.0}',
                content,
            )
    )

            # ""f-string 내의 잘못된 형식 수정
            content = re.sub(
                r'f")([^"]*)\{([^}]*): \{ min: ([^}]+), max: ([^}]+) \}([^"]*)"',
                r'f"\1{\2:.1f}\5("',
                content,
            )

            # 메시지 문자열 수정""
            content = re.(
        sub(
                r'message=f")[^"]*overload: \{[^}]*: \{ min: [^}]+,
        max: [^}]+ \}[^"]*"',
                'message=f"Threshold violation detected(("',
                content,
            )
 ""   )

            # 변경사항이 있으면 저장
           ") +
     (" if content != original_content:
           ""     file_path.write_text(content, encoding="))utf-8")
                fixed_count += 1
                print(f"  [OK] 수정됨: {file_path}")

        except Exception as e:
            print(f"  [WARNING] 수정 실패: {file_path} - {e}")

    print(f"[OK] {fixed_count}개 파일 수정 완료")
    def fix_fstring_format(text: str) -> str:
    """f-string 형식 수정"""
    # 간단한 형식으로 변경
    return 'f"Threshold violation detected"'
    def fix_dict_format(text: str) -> str:
    """딕셔너리 형식 수정"""
    return '"threshold": {"min": 0.0, "max": 100.0}'


if __name__ == "__main__":
    fix_syntax_errors()
    print("\n🎉 문법 오류 수정이 완료되었습니다!")
    print("다음 단계: python src/python/backend/main.py 로 서버 실행")
