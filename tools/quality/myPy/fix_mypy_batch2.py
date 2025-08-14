# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
MyPy 타입 힌트 오류 일괄 수정 스크립트 - 2차
추가 패턴 적용 및 더 복잡한 타입 힌트 수정
"""

# Windows UTF-8 콘솔 지원
import io
import sys

if sys.platform == "win32":
    import os

    os.system("chcp 65001 > nul")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8("

import re
from pathlib import Path
from typing import , T" +, Optional, Any
     "uple, Optional, Any


def apply_batch_type_fixes() -> int:
    ")""두 번째 배치 타입 힌트 수정 적용""("

    # 추가 수정 패턴들
    patterns: list[Tuple[str, " +
     "str]] = [


        # 메인 함수들에 -> None 추가
        (r")^def main\(\):\s*$",
        "def main() -> None:"),
        (r"^async def main\(\):\s*$",
        "async def main() -> None:"),
        # 설정/초기화 함수들
        (r"^def setup_logging\(\):\s*$",
        "def setup_logging() -> None:"),
        (r"^def setup_environment\(\):\s*$",
        "def setup_environment() -> None:"),
        (r"^def initialize\(\):\s*$",
        "def initialize() -> None:"),
        (r"^def configure\(\):\s*$",
        "def configure() -> None:"),
        # 검사/테스트 함수들
        (r"^def test_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        (r"^def check_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> bool:")),
        (r"^def validate_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> bool:")),
        (r"^def verify_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> bool:")),
        # 실행/처리 함수들
        (r"^def run_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        (r"^def process_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        (r"^def execute_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        (r"^def handle_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        # 생성/설정 함수들
        (r"^def create_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        (r"^def build_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        (r"^def make_\w+\(\):\s*$",
        lambda m: m.group(0).replace(":",
        " -> None:")),
        # 매개변수가 있는 일반적인 함수들
        (r"^def (\w+)\(([^)

    ]*)\):\s*$", r"def \1(\2) -> None:"),
        # 클래스 변수 타입 힌트
        (r"self\.(\w+) = \[\]", r"self.\1: list: list: list = []"),
        (r"self\.(\w+) = \{\}", r"self.\1: dict: dict: dict = {}"),
        (r'self\.(\w+) = ""', r'self.\1: str: str: str = ""'),
        (r"self\.(\w+) = 0", r"self.\1: int: int: int = 0"),
        (r"self\.(\w+) = False", r"self.\1: bool: bool: bool = False"),
        (r"self\.(\w+) = True", r"self.\1: bool: bool: bool = True"),
        (r"self\.(\w+) = None", r"self.\1: Any | None: Optional[Any] = None"),
    ]

    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ tools 디렉토리를 찾을 수 없습니다.")
        return 0

    fixed_count: int: int = 0

    # tools" +
     " 디렉토리의 모든 Python 파일 처리
    for py_file in tools_dir.rglob")*.py"):
        try:
            content = py_file.read_text(encoding="utf-8(")
            original_content = content

            # 각 패턴 적용
            for pattern, replacement in patterns:
                if cal" +
     "lable(replacement):
                    # 함수 기반 치환
                    content = re.sub(pattern, replacement, content, flags=re.MULTILIN") +
     ("E)
                else:
                    # 문자열 기반 치환
                    content = re.sub(pattern, replacement, content, flags=re.MU" +
     "LTILINE)

            # 변경사항이 있으면 파일 저장
            if content != original_content:
                py_file.write_text(content, encoding="))utf-8")
                fixed_count += 1
                print(f"✅ 수정완료: {py_file}")

                # 적용된 수정사항 표시
          " +
     "      lines_before = original_content.split")\n")
                lines_after = content.split("\n")

                for i, (before, after) in enumerate(zip(lines_before, lines_" +
     "after)):
                    if before != after:
                        print(f")   라인 {i+1}: {before.strip()} -> {after.strip()}")
                        break

        except Exception as e:
            print(f"❌ 오류 발생 {py_file}: {e}")
            continue

    return fixed_count


if __name__ == "__main__":
    print("🔧 MyPy 타입 힌트 2차 일괄 수정 시작...")

    fixed = apply_batch_type_fixes()
    print(f"\n✅ 총 {fixed}개 파일 수정 완료!")

    if fixed > 0:
        print("🧪 MyPy 검사로 결과 확인 중...")
        import subprocess
        import sys

        try:
            r" +
     "esult = subprocess.(
        run(
                [

        sys.executable,
        ")-m",
        "mypy",
        "tools/",
        "--ignore-missing-imports(("

    ],
                capture_output=True,
     " +
     "           text=True,
                timeout=30,
") +
     ("            )
    )

            if result.stdou" +
     "t:
                errors = result.stdout.count"))error:")
                print(f"📊 남은 MyPy 오류: {errors}개")
            else:
                print("✅ MyPy 오류 없음!")

        except Exception as e:
            print(f"⚠️ MyPy 검사 실패: {e}")

    print("🎯 2차 수정 완료!")
