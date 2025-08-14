# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
MyPy Type Hint Error Batch Fix Script - Phase 2
Apply additional patterns and fix more complex type hints
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
from typing import Tuple, Optional, Any

def apply_batch_type_fixes() -> int:
    """Apply second batch type hint fixes"""

    # Additional fix patterns
    patterns: list[Tuple[str, str]] = [
        # Add -> None to main functions
        (r"^def main\(\):\s*$",
         "def main() -> None:"),
        (r"^async def main\(\):\s*$",
         "async def main() -> None:"),
        # Setup/initialization functions
        (r"^def setup_logging\(\):\s*$",
         "def setup_logging() -> None:"),
        (r"^def setup_environment\(\):\s*$",
         "def setup_environment() -> None:"),
        (r"^def initialize\(\):\s*$",
         "def initialize() -> None:"),
        (r"^def configure\(\):\s*$",
         "def configure() -> None:"),
        # Check/test functions
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
        # Run/process functions
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
        # Create/build functions
        (r"^def create_\w+\(\):\s*$",
         lambda m: m.group(0).replace(":",
         " -> None:")),
        (r"^def build_\w+\(\):\s*$",
         lambda m: m.group(0).replace(":",
         " -> None:")),
        (r"^def make_\w+\(\):\s*$",
         lambda m: m.group(0).replace(":",
         " -> None:")),
        # General functions with parameters
        (r"^def (\w+)\(([^)]*)\):\s*$", r"def \1(\2) -> None:"),
        # Class variable type hints
        (r"self\.(\w+) = \[\]", r"self.\1: list = []"),
        (r"self\.(\w+) = \{\}", r"self.\1: dict = {}"),
        (r'self\.(\w+) = ""', r'self.\1: str = ""'),
        (r"self\.(\w+) = 0", r"self.\1: int = 0"),
        (r"self\.(\w+) = False", r"self.\1: bool = False"),
        (r"self\.(\w+) = True", r"self.\1: bool = True"),
        (r"self\.(\w+) = None", r"self.\1: Optional[Any] = None"),
    ]

    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("[ERROR] Cannot find tools directory.")
        return 0

    fixed_count: int = 0

    # Process all Python files in tools directory
    for py_file in tools_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Apply each pattern
            for pattern, replacement in patterns:
                if callable(replacement):
                    # Function-based substitution
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    # String-based substitution
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            # Save file if there are changes
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                fixed_count += 1
                print(f"[OK] Fix completed: {py_file}")

                # Display applied fixes
                lines_before = original_content.split("\n")
                lines_after = content.split("\n")

                for i, (before, after) in enumerate(zip(lines_before, lines_after)):
                    if before != after:
                        print(f"   Line {i+1}: {before.strip()} -> {after.strip()}")
                        break

        except Exception as e:
            print(f"[ERROR] Error occurred {py_file}: {e}")
            continue

    return fixed_count


if __name__ == "__main__":
    print("[TOOL] Starting MyPy type hint phase 2 batch fix...")

    fixed = apply_batch_type_fixes()
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
            else:
                print("[OK] No MyPy errors!")

        except Exception as e:
            print(f"[WARNING] MyPy check failed: {e}")

    print("[TARGET] Phase 2 fix completed!")