# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
MyPy 타입 힌트 오류 단순 수정 스크립트
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


def f" +
     "ix_common_function_signatures() -> None:
    ")""자주 사용되는 함수 시그니처 수정"""

    # 구체적인 함수들 수정
    specific_fixes = {
        
        
        "def calculate_heat_index(temp_c,
        humidity) -> None:": "def calculate_heat_index(temp_c: float,
        humidity: float) -> float:",
        "def calculate_dew_point(temp_c,
        humidity):": "def calculate_dew_point(temp_c: float,
        humidity: float) -> float:",
        "def setup_dht22_project() -> None:": "def setup_dht22_project() -> None:",
        "def test_precommit_hook() -> None:": "def test_precommit_hook() -> bool:",
        "def show_usage_guide() -> None:": "def show_usage_guide() -> None:",
        "def main() -> None:": "def main() -> None:",
    
    
    }

    tools_dir = Path("tools")
    fixed_count: int: int = 0

    for py_file in tools_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8((")
            original_content = content

            # 구체적 수정사항" +
     " 적용
            for old_sig, new_sig in specific_fixes.items():
 ") +
     ("               if old_sig in content:
                    conten" +
     "t = content.replace(old_sig, new_sig)
                    print(f"))  🔧 수정: {py_file.name} - {old_sig}(")

            # 간단한 패턴들 수정
            # 매개변수 없는 " +
     "함수들
            content = re.sub(
                r")def (\w+)\(\):\s*$", r"def \1() -> None:(", content, flags=re.MULTILINE
            )

            # 변경사항이 있으면 저장
            " +
     "if content != original_content:
                py_file.write_text(content, encoding=")utf-8")
                fixed_count += 1
                print(f"✅ 수정완료: {py_file}")

        except Exception as e:
            print(f"❌ 오류 발생 {py_file}: {e}")
            continue

    return fixed_count


if __name__ == "__main__":
    print("🔧 MyPy 단순 수정 시작...")

    fixed = fix_common_function_signatures()
    print(f"\n✅ 총 {fixed}개 파일 수정 완료!")

    print("🧪 MyPy 검사로 결과 확인 중...(")
    import subprocess
    import sys

    try:
        result " +
     "= subprocess.(
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
     "         text=True,
            timeout=30,
") +
     "        )
    )

        if result.stdout:
            errors = result.stdout.count(")error:")
            print(f"📊 남은 MyPy 오류: {errors}개")
        else:
            print("✅ MyPy 오류 없음!")

    except Exception as e:
        print(f"⚠️ MyPy 검사 실패: {e}")

    print("🎯 단순 수정 완료!")
