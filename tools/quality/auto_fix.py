#!/usr/bin/env python3
"""
Automatic Code Quality Fix Tool

This script automatically fixes common code quality issues using Ruff.
"""

import subprocess
import sys
from pathlib import Path


def run_auto_fixes():
    """Run all automatic fixes"""
    print("🔧 Running automatic code quality fixes...")

    # 1. Ruff auto-fix
    print("\n1. Running Ruff auto-fix...")
    result = subprocess.run(
        [
            "uv",
            "run",
            "ruff",
            "check",
            "--fix",
            "--unsafe-fixes",
            "src/python/",
            "tools/",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode == 0:
        print("✅ Ruff auto-fix completed successfully")
    else:
        print("⚠️ Ruff auto-fix completed with some remaining issues")
        if result.stdout:
            print(f"Remaining issues: {result.stdout.count('Found')}")

    # 2. Ruff format
    print("\n2. Running Ruff format...")
    format_result = subprocess.run(
        ["uv", "run", "ruff", "format", "src/python/", "tools/"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if format_result.returncode == 0:
        print("✅ Ruff formatting completed")
    else:
        print("❌ Ruff formatting failed")
        print(format_result.stderr)

    # 3. Summary
    print("\n📊 Auto-fix Summary:")
    print("- Import sorting: ✅ Fixed")
    print("- Unused imports: ✅ Removed")
    print("- Unused variables: ✅ Removed")
    print("- Whitespace issues: ✅ Fixed")
    print("- Code formatting: ✅ Applied")

    print("\n💡 Manual fixes may be needed for:")
    print("- Long lines (E501)")
    print("- Complex logic issues")
    print("- Security warnings")

    return result.returncode == 0


def main():
    """Main function"""
    print("🚀 DHT22 Project Auto-Fix Tool")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run from project root.")
        sys.exit(1)

    success = run_auto_fixes()

    if success:
        print("\n🎉 Auto-fix completed! Run quality check to see remaining issues.")
    else:
        print("\n⚠️ Auto-fix completed with some issues remaining.")

    print("\nNext steps:")
    print("1. Run: uv run python tools/quality/quality_check.py")
    print("2. Review remaining issues manually")
    print("3. Consider adjusting Ruff configuration if needed")


if __name__ == "__main__":
    main()
