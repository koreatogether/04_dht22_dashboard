# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
MyPy Type Hint Error Simple Fix Script
"""

# Windows UTF-8 console support
import io
import sys

if sys.platform == "win32":
    import os

    os.system("chcp 65001 > nul")
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace")
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer,
        encoding="utf-8",
        errors="replace")
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

import re
from pathlib import Path

def fix_common_function_signatures() -> None:
    """Fix commonly used function signatures"""

    # Fix specific functions
    specific_fixes = {
        "def calculate_heat_index(temp_c, humidity) -> None:": "def calculate_heat_index(temp_c: float, humidity: float) -> float:",
        "def calculate_dew_point(temp_c, humidity):": "def calculate_dew_point(temp_c: float, humidity: float) -> float:",
        "def setup_dht22_project() -> None:": "def setup_dht22_project() -> None:",
        "def test_precommit_hook() -> None:": "def test_precommit_hook() -> bool:",
        "def show_usage_guide() -> None:": "def show_usage_guide() -> None:",
        "def main() -> None:": "def main() -> None:",
    }

    tools_dir = Path("tools")
    fixed_count: int = 0

    for py_file in tools_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Apply specific fixes
            for old_sig, new_sig in specific_fixes.items():
                if old_sig in content:
                    content = content.replace(old_sig, new_sig)
                    print(f"  [TOOL] Fixed: {py_file.name} - {old_sig}")

            # Fix simple patterns
            # Functions without parameters
            content = re.sub(
                r"def (\w+)\(\):\s*$", r"def \1() -> None:", content, flags=re.MULTILINE
            )

            # Save if there are changes
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                fixed_count += 1
                print(f"[OK] Fix completed: {py_file}")

        except Exception as e:
            print(f"[ERROR] Error occurred {py_file}: {e}")
            continue

    return fixed_count


if __name__ == "__main__":
    print("[TOOL] Starting MyPy simple fix...")

    fixed = fix_common_function_signatures()
    print(f"\n[OK] Total {fixed} files fixed!")

    print("🧪 Checking results with MyPy...")
    import subprocess
    import sys

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mypy",
                "tools/",
                "--ignore-missing-imports"
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.stdout:
            errors = result.stdout.count("error:")
            print(f"[DATA] Remaining MyPy errors: {errors}")
        else:
            print("[OK] No MyPy errors!")

    except Exception as e:
        print(f"[WARNING] MyPy check failed: {e}")

    print("[TARGET] Simple fix completed!")