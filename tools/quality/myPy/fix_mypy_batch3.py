# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
MyPy Type Hint Error Batch Fix Script - Phase 3
Complete remaining function and variable type hints
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

def apply_final_type_fixes() -> int:
    """Apply final type hint fixes"""

    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("[ERROR] Cannot find tools directory.")
        return 0

    fixed_count: int = 0

    # Batch fix all Python files
    for py_file in tools_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # 1. Specify return types for functions without parameters
            patterns_to_fix = [
                # Functions without parameters - bool return
                (
                    r"^(\s*)def (check|verify|validate|test)_[a-zA-Z_]+\(\):\s*$",
                    r"\1def \2_\3() -> bool:",
                ),
                (r"^(\s*)def is_[a-zA-Z_]+\(\):\s*$", r"\1def is_\2() -> bool:"),
                (r"^(\s*)def has_[a-zA-Z_]+\(\):\s*$", r"\1def has_\2() -> bool:"),
                # Functions without parameters - None return
                (
                    r"^(\s*)def (setup|init|configure|install)_[a-zA-Z_]+\(\):\s*$",
                    r"\1def \2_\3() -> None:",
                ),
                (
                    r"^(\s*)def (show|print|display)_[a-zA-Z_]+\(\):\s*$",
                    r"\1def \2_\3() -> None:",
                ),
                (
                    r"^(\s*)def (run|execute|start)_[a-zA-Z_]+\(\):\s*$",
                    r"\1def \2_\3() -> None:",
                ),
                # Functions without parameters - other
                (r"^(\s*)def get_[a-zA-Z_]+\(\):\s*$", r"\1def get_\2() -> dict:"),
                (r"^(\s*)def load_[a-zA-Z_]+\(\):\s*$", r"\1def load_\2() -> dict:"),
                (
                    r"^(\s*)def generate_[a-zA-Z_]+\(\):\s*$",
                    r"\1def generate_\2() -> str:",
                ),
                # Functions with parameters add type hints
                (
                    r"^(\s*)def ([a-zA-Z_]+)\(([^)]*[^:])\):\s*$",
                    r"\1def \2(\3) -> None:",
                ),
            ]

            for pattern, replacement in patterns_to_fix:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    print(f"  [TOOL] Pattern fix applied: {py_file.name}")

            # 2. Add typing import (if needed)
            if (
                "def " in content
                and "-> " in content
                and "from typing import" not in content
            ):
                # Add typing import at the top of the file
                if content.startswith("#!/usr/bin/env python3"):
                    lines = content.split("\n")
                    insert_pos = 1
                    # Insert after docstring if present
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip().startswith('"""') and line.strip().endswith(
                            '"""'
                        ):
                            insert_pos = i + 1
                            break
                        elif line.strip().startswith('"""'):
                            # Find multi-line docstring
                            for j in range(i + 1, len(lines)):
                                if lines[j].strip().endswith('"""'):
                                    insert_pos = j + 1
                                    break
                            break
                        elif line.strip() and not line.startswith("#"):
                            break

                    # Check if typing import already exists
                    has_typing_import = any(
                        "from typing import" in line or "import typing" in line
                        for line in lines
                    )
                    if not has_typing_import:
                        lines.insert(insert_pos, "from typing import Optional, Any")
                        lines.insert(insert_pos + 1, "")
                        content = "\n".join(lines)
                        print(f"  📝 Added typing import: {py_file.name}")

            # Save file if there are changes
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                fixed_count += 1
                print(f"[OK] Fix completed: {py_file}")

        except Exception as e:
            print(f"[ERROR] Error occurred {py_file}: {e}")
            continue

    return fixed_count


if __name__ == "__main__":
    print("[TOOL] Starting MyPy type hint phase 3 final fix...")

    fixed = apply_final_type_fixes()
    print(f"\n[OK] Total {fixed} files fixed!")

    if fixed > 0:
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

                if errors > 0:
                    print("\n[TARGET] Main remaining errors:")
                    lines = result.stdout.split("\n")
                    error_lines = [line for line in lines if "error:" in line][:5]
                    for error_line in error_lines:
                        print(f"   {error_line}")
            else:
                print("[OK] No MyPy errors!")

        except Exception as e:
            print(f"[WARNING] MyPy check failed: {e}")

    print("🏁 Phase 3 final fix completed!")