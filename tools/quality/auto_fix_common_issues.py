#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일반적인 코드 품질 문제를 자동으로 수정합니다.

프로젝트 파일(src/, tools/, tests/)만 대상으로 하며,
가상환경(.venv) 및 외부 라이브러리 파일은 제외합니다.
"""

import re
from pathlib import Path
from typing import Tuple


class CodeFixer:
    """일반적인 코드 품질 문제 자동 수정 도구"""

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root).resolve()

        # 수정할 디렉토리 (프로젝트 파일만)
        self.target_dirs = ["src", "tools", "tests"]

        # 제외할 디렉토리
        self.exclude_dirs = {".venv", ".venv_broken_backup", "__pycache__", ".git",
                           ".pytest_cache", "node_modules", "backups"}

        # 수정 패턴들
        self.patterns = {
            # 구식 typing import를 현대식으로 변경
            "modernize_typing_dict": (
                re.compile(r"from typing import.*", re.MULTILINE),
                lambda m: m.group(0).replace("Dict", "")
            ),
            "modernize_typing_list": (
                re.compile(r"from typing import.*", re.MULTILINE),
                lambda m: m.group(0).replace("List", "")
            ),
            "modernize_type_hints_dict": (
                re.compile(r":\s*Dict\["),
                ": dict["
            ),
            "modernize_type_hints_list": (
                re.compile(r":\s*List\["),
                ": list["
            ),

            # Exception 처리 개선
            "fix_bare_except": (
                re.compile(r"except Exception:\s*\n\s*raise ([^\n]+)"),
                r"except Exception as e:\n    raise \1 from e"
            ),

            # 라인 끝 공백 제거
            "remove_trailing_whitespace": (
                re.compile(r"[ \t]+$", re.MULTILINE),
                ""
            ),

            # 불필요한 import 정리 (간단한 케이스만)
            "clean_unused_typing": (
                re.compile(r"from typing import\s*\n"),
                ""
            )
        }

    def is_target_file(self, file_path: Path) -> bool:
        """파일이 수정 대상인지 확인"""
        # 제외 디렉토리 체크
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False

        # 대상 디렉토리 체크
        rel_path = file_path.relative_to(self.project_root)
        return any(rel_path.parts[0] == target_dir for target_dir in self.target_dirs)

    def fix(self) -> None:
        """모든 대상 파일에 대해 자동 수정 실행"""
        print("[START] 일반적인 코드 품질 문제 자동 수정 시작...")
        print(f"[ROOT] 프로젝트 루트: {self.project_root}")
        print(f"[TARGET] 대상 디렉토리: {', '.join(self.target_dirs)}")

        fixed_files = []

        # 모든 Python 파일 찾기
        for pattern in ["**/*.py"]:
            for file_path in self.project_root.glob(pattern):
                if self.is_target_file(file_path):
                    if self.fix_file(file_path):
                        fixed_files.append(file_path.relative_to(self.project_root))

        # 결과 출력
        print(f"\n[SUMMARY] 수정 완료!")
        print(f"[SUCCESS] 수정된 파일: {len(fixed_files)}개")

        if fixed_files:
            print(f"\n[FILES] 수정된 파일들:")
            for file in fixed_files[:10]:  # 처음 10개만 표시
                print(f"  - {file}")
            if len(fixed_files) > 10:
                print(f"  ... 및 {len(fixed_files) - 10}개 더")
        else:
            print("수정할 파일이 없습니다.")

    def fix_file(self, file_path: Path) -> bool:
        """단일 파일 수정"""
        try:
            # 파일 읽기
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            fixes_applied = 0

            # 각 패턴 적용
            for pattern_name, (pattern, replacement) in self.patterns.items():
                if callable(replacement):
                    # 람다 함수인 경우
                    new_content = pattern.sub(replacement, content)
                else:
                    # 문자열 치환인 경우
                    new_content = pattern.sub(replacement, content)

                if new_content != content:
                    content = new_content
                    fixes_applied += 1

            # 변경사항이 있으면 파일 저장
            if content != original_content:
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(content)

                print(f"  [OK] {file_path.relative_to(self.project_root)} ({fixes_applied}개 패턴 적용)")
                return True

            return False

        except Exception as e:
            print(f"  [ERROR] {file_path.relative_to(self.project_root)}: {e}")
            return False


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="일반적인 코드 품질 문제 자동 수정",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
수정하는 항목들:
- 구식 typing import (Dict, List → dict, list)
- 타입 힌트 현대화 (Dict[str, int] → dict[str, int])
- Exception 처리 개선 (from e 추가)
- 라인 끝 공백 제거
- 불필요한 import 정리

대상 디렉토리: src/, tools/, tests/
제외 디렉토리: .venv, __pycache__, .git 등
        """
    )

    parser.add_argument(
        "--root",
        default=".",
        help="프로젝트 루트 디렉토리 (기본: 현재 디렉토리)"
    )

    args = parser.parse_args()

    fixer = CodeFixer(args.root)
    fixer.fix()


if __name__ == "__main__":
    main()