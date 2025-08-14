#!/usr/bin/env python3
"""
AI 코딩 오류 종합 자동 수정 도구

AI들이 자주 만드는 구문 오류, 타입 힌트 오류, 인덴테이션 오류 등을
종합적으로 자동 수정하는 도구입니다.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path


class AICodeErrorFixer:
    """AI가 만드는 일반적인 코딩 오류들을 자동으로 수정"""

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root).resolve()
        self.target_dirs = ["src", "tools", "tests"]
        self.exclude_dirs = {
            ".venv",
            ".venv_broken_backup",
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            "backups"}

        # AI가 자주 만드는 오류 패턴들
        self.error_patterns = {
            # 1. 타입 힌트 구문 오류
            "malformed_type_hint": (
                re.compile(
                    r"def\s+(\w+)\s*\([^)]*\)\s*:\s*->\s*([^:]+):\s*$",
                    re.MULTILINE),
                r"def \1(\2):"
            ),

            # 2. 빈 타입 힌트 수정
            "empty_return_type": (
                re.compile(
                    r"def\s+(\w+)\s*\([^)]*\)\s*->\s*:\s*$",
                    re.MULTILINE),
                r"def \1():"
            ),

            # 3. 문자열 리터럴 구문 오류
            "broken_string_literal": (
                re.compile(r'"\s*\+\s*"', re.MULTILINE),
                '""'
            ),

            # 4. f-string 구문 오류
            "broken_fstring": (
                re.compile(r'f"\s*\{\s*([^}]+)\s*\}\s*"', re.MULTILINE),
                r'f"{\1}"'
            ),

            # 5. import 구문 정리
            "duplicate_imports": (
                re.compile(
                    r"(from\s+\w+\s+import\s+[^;]+);\s*\1",
                    re.MULTILINE),
                r"\1"
            ),

            # 6. 빈 except 블록
            "empty_except": (
                re.compile(r"except\s*:\s*pass\s*$", re.MULTILINE),
                "except Exception:\n    pass"
            ),

            # 7. 잘못된 인덴테이션 (간단한 케이스)
            "wrong_indentation": (
                re.compile(r"^(\s{1,3})def\s+", re.MULTILINE),
                r"    def "
            ),

            # 8. 세미콜론 제거 (Python에서 불필요)
            "remove_semicolon": (
                re.compile(r";$", re.MULTILINE),
                ""
            )
        }

    def fix_syntax_with_tools(self, file_path: Path) -> bool:
        """외부 도구들을 사용한 구문 수정"""
        changed = False

        # 1. autopep8로 기본 포맷팅
        try:
            result = subprocess.run([
                sys.executable, "-m", "autopep8", "--in-place",
                "--aggressive", "--aggressive", str(file_path)
            ], capture_output=True, text=True)
            if result.returncode == 0:
                changed = True
        except Exception:
            pass

        # 2. autoflake로 불필요한 import 제거
        try:
            result = subprocess.run([
                sys.executable, "-m", "autoflake", "--in-place",
                "--remove-all-unused-imports", "--remove-unused-variables",
                str(file_path)
            ], capture_output=True, text=True)
            if result.returncode == 0:
                changed = True
        except Exception:
            pass

        # 3. isort로 import 정리
        try:
            result = subprocess.run([
                sys.executable, "-m", "isort", str(file_path)
            ], capture_output=True, text=True)
            if result.returncode == 0:
                changed = True
        except Exception:
            pass

        return changed

    def fix_pattern_errors(self, content: str) -> tuple[str, int]:
        """패턴 기반 오류 수정"""
        fixes_applied = 0

        for pattern_name, (pattern,
                           replacement) in self.error_patterns.items():
            new_content = pattern.sub(replacement, content)
            if new_content != content:
                content = new_content
                fixes_applied += 1

        return content, fixes_applied

    def fix_encoding_issues(self, content: str) -> str:
        """인코딩 관련 문제 수정"""
        # 이모지를 ASCII 대체 문자로 변환
        emoji_replacements = {
            "[SEARCH]": "[SEARCH]",
            "[OK]": "[OK]",
            "[ERROR]": "[ERROR]",
            "[WARNING]": "[WARNING]",
            "[SUCCESS]": "[SUCCESS]",
            "[DATA]": "[DATA]",
            "[TOOL]": "[TOOL]",
            "[TIP]": "[TIP]",
            "[TARGET]": "[TARGET]"
        }

        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)

        return content

    def is_target_file(self, file_path: Path) -> bool:
        """파일이 수정 대상인지 확인"""
        # 제외 디렉토리 체크
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False

        # 대상 디렉토리 체크
        try:
            rel_path = file_path.relative_to(self.project_root)
            return any(
                rel_path.parts[0] == target_dir for target_dir in self.target_dirs)
        except ValueError:
            return False

    def fix_file(self, file_path: Path) -> dict[str, int]:
        """단일 파일 종합 수정"""
        stats = {"pattern_fixes": 0, "tool_fixes": 0, "encoding_fixes": 0}

        try:
            # 백업 생성
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy2(file_path, backup_path)

            # 파일 읽기
            with file_path.open("r", encoding="utf-8") as f:
                original_content = f.read()

            content = original_content

            # 1. 패턴 기반 수정
            content, pattern_fixes = self.fix_pattern_errors(content)
            stats["pattern_fixes"] = pattern_fixes

            # 2. 인코딩 문제 수정
            old_content = content
            content = self.fix_encoding_issues(content)
            if content != old_content:
                stats["encoding_fixes"] = 1

            # 변경사항이 있으면 파일 저장
            if content != original_content:
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(content)

            # 3. 외부 도구로 추가 수정
            if self.fix_syntax_with_tools(file_path):
                stats["tool_fixes"] = 1

            # 백업 파일 정리
            if backup_path.exists():
                backup_path.unlink()

            return stats

        except Exception as e:
            # 오류 시 백업에서 복원
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                backup_path.unlink()
            print(f"  [ERROR] {file_path.relative_to(self.project_root)}: {e}")
            return stats

    def fix_all(self) -> None:
        """모든 대상 파일에 대해 종합 수정 실행"""
        print("[START] AI 코딩 오류 종합 자동 수정 시작...")
        print(f"[ROOT] 프로젝트 루트: {self.project_root}")
        print(f"[TARGET] 대상 디렉토리: {', '.join(self.target_dirs)}")

        fixed_files = []
        total_stats = {
            "pattern_fixes": 0,
            "tool_fixes": 0,
            "encoding_fixes": 0}

        # 모든 Python 파일 처리
        for file_path in self.project_root.glob("**/*.py"):
            if self.is_target_file(file_path):
                stats = self.fix_file(file_path)

                if any(stats.values()):
                    fixed_files.append(
                        (file_path.relative_to(
                            self.project_root), stats))
                    for key in total_stats:
                        total_stats[key] += stats[key]

        # 결과 출력
        print(f"\n[SUMMARY] 수정 완료!")
        print(f"[FILES] 수정된 파일: {len(fixed_files)}개")
        print(f"[STATS] 패턴 수정: {total_stats['pattern_fixes']}개")
        print(f"[STATS] 도구 수정: {total_stats['tool_fixes']}개")
        print(f"[STATS] 인코딩 수정: {total_stats['encoding_fixes']}개")

        if fixed_files:
            print(f"\n[DETAILS] 수정된 파일들:")
            for file_path, stats in fixed_files[:10]:
                print(
                    f"  - {file_path} (패턴:{
                        stats['pattern_fixes']}, 도구:{
                        stats['tool_fixes']}, 인코딩:{
                        stats['encoding_fixes']})")
            if len(fixed_files) > 10:
                print(f"  ... 및 {len(fixed_files) - 10}개 더")

def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI 코딩 오류 종합 자동 수정",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
수정하는 오류들:
- 타입 힌트 구문 오류 (def func() -> Type:)
- 문자열 리터럴 오류 ("" → "")
- f-string 구문 오류
- 잘못된 인덴테이션
- 불필요한 세미콜론
- 중복 import문
- 인코딩 문제 (이모지 → ASCII)
- autopep8, autoflake, isort 자동 적용

대상: src/, tools/, tests/ 디렉토리
"""
    )

    parser.add_argument("--root", default=".", help="프로젝트 루트 디렉토리")
    parser.add_argument(
        "--keep-emoji",
        action="store_true",
        help="이모지 유지 (변환하지 않음)")

    args = parser.parse_args()

    fixer = AICodeErrorFixer(args.root)
    if args.keep_emoji:
        # 이모지 변환 비활성화
        fixer.error_patterns = {k: v for k, v in fixer.error_patterns.items()
                                if k != "encoding_fixes"}

    fixer.fix_all()


if __name__ == "__main__":
    main()
