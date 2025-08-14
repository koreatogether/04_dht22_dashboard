#!/usr/bin/env python3
"""도구 파일들의 구문 오류를 검증하는 스크립트"""

import ast
import subprocess
import sys
from pathlib import Path


class ToolValidator:
    """도구 파일들의 구문을 검증하는 클래스"""

    def __init__(self, tools_dir: str = "tools"):
        self.tools_dir = Path(tools_dir)
        self.errors: list[tuple[Path, str]] = []

    def validate_python_syntax(self, file_path: Path) -> bool:
        """Python 파일의 구문을 검증"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # AST 파싱으로 구문 오류 체크
            ast.parse(content)
            return True

        except SyntaxError as e:
            self.errors.append((file_path, f"SyntaxError: {e}"))
            return False
        except Exception as e:
            self.errors.append((file_path, f"Error: {e}"))
            return False

    def validate_importability(self, file_path: Path) -> bool:
        """Python 파일이 import 가능한지 검증"""
        try:
            # python -m py_compile로 컴파일 체크
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.errors.append((file_path, f"Compile Error: {result.stderr}"))
                return False
            return True

        except Exception as e:
            self.errors.append((file_path, f"Import Error: {e}"))
            return False

    def validate_all_tools(self) -> bool:
        """모든 도구 파일들을 검증"""
        if not self.tools_dir.exists():
            print(f"[ERROR] 도구 디렉토리가 존재하지 않습니다: {self.tools_dir}")
            return False

        python_files = list(self.tools_dir.rglob("*.py"))
        if not python_files:
            print(f"[ERROR] {self.tools_dir}에서 Python 파일을 찾을 수 없습니다")
            return False

        print(f"[INFO] {len(python_files)}개의 도구 파일을 검증 중...")

        valid_count = 0
        for file_path in python_files:
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = str(file_path)

            print(f"  검증 중: {rel_path}")

            # 구문 검증
            syntax_ok = self.validate_python_syntax(file_path)

            # 컴파일 검증
            compile_ok = self.validate_importability(file_path)

            if syntax_ok and compile_ok:
                valid_count += 1
                print("    [OK] 유효함")
            else:
                print("    [ERROR] 오류 발견")

        print(f"\n[RESULT] 검증 결과: {valid_count}/{len(python_files)} 파일이 유효")

        if self.errors:
            print("\n[ERRORS] 발견된 오류들:")
            for file_path, error in self.errors:
                try:
                    rel_path = file_path.relative_to(Path.cwd())
                except ValueError:
                    rel_path = str(file_path)
                print(f"  {rel_path}: {error}")
            return False
        else:
            print("[SUCCESS] 모든 도구 파일이 유효합니다!")
            return True


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="도구 파일들의 구문 검증")
    parser.add_argument(
        "--tools-dir", default="tools", help="도구 디렉토리 경로 (기본값: tools)"
    )

    args = parser.parse_args()

    validator = ToolValidator(args.tools_dir)
    is_valid = validator.validate_all_tools()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
