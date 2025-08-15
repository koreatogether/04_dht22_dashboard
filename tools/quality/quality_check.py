#!/usr/bin/env python3
"""
Integrated Code Quality Check Tool

This script performs the following checks:
- Black: Code formatting check
- Ruff: Linting and code style check
- MyPy: Type hint check
- Pytest: Unit test execution
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd: list[str], description: str) -> tuple[bool, str]:
    """Execute command and return results."""
    print(f"Checking {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=300,  # 5 minute timeout
            encoding="utf-8",
            errors="replace",  # Use replacement character for decode errors
        )

        if result.returncode == 0:
            print(f"{description} passed")
            return True, result.stdout
        else:
            print(f"{description} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"{description} timed out")
        return False, "Command timed out"
    except Exception as e:
        print(f"{description} error: {str(e)}")
        return False, str(e)


def check_ruff() -> tuple[bool, str]:
    """Ruff linting check"""
    return run_command(
        ["uv", "run", "ruff", "check", "src/python/", "tools/"], "Ruff linting"
    )


def fix_ruff() -> tuple[bool, str]:
    """Ruff auto-fix"""
    return run_command(
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
        "Ruff auto-fix",
    )


def check_ruff_format() -> tuple[bool, str]:
    """Ruff formatting check"""
    return run_command(
        ["uv", "run", "ruff", "format", "--check", "src/python/", "tools/"],
        "Ruff formatting",
    )


def check_mypy() -> tuple[bool, str]:
    """MyPy type check"""
    return run_command(["uv", "run", "mypy", "src/python/"], "MyPy type check")


def run_tests() -> tuple[bool, str]:
    """pytest unit test execution"""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("No tests directory found. Skipping tests.")
        return True, "No tests directory found"

    return run_command(["uv", "run", "pytest", "--tb=short"], "pytest unit tests")


def check_imports() -> tuple[bool, str]:
    """Python import check"""
    try:
        # Basic import test
        sys.path.insert(0, str(Path("src/python").absolute()))

        # Test importing main modules
        from dashboard import app  # noqa: F401
        from utils import data_processor, serial_reader  # noqa: F401

        print("Python import check passed")
        return True, "All imports successful"

    except ImportError as e:
        print(f"Import error: {e}")
        return False, str(e)
    except Exception as e:
        print(f"Import check error: {e}")
        return False, str(e)
    finally:
        # Restore sys.path
        if str(Path("src/python").absolute()) in sys.path:
            sys.path.remove(str(Path("src/python").absolute()))


def generate_report(results: dict[str, tuple[bool, str]]) -> None:
    """Generate check results report"""

    # Console summary
    print("\n" + "=" * 60)
    print("Code Quality Check Results Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for check_name, (success, _output) in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{check_name:20} : {status}")
        if success:
            passed += 1

    print(f"\nOverall results: {passed}/{total} passed")

    # Generate JSON report
    report_dir = Path("tools/quality/reports")
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"quality_report_{timestamp}.json"

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": round((passed / total) * 100, 2) if total > 0 else 0,
        },
        "results": {
            name: {"passed": success, "output": output[:1000]}  # Limit output length
            for name, (success, output) in results.items()
        },
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Detailed report: {report_file}")

    # Exit with code 1 if any checks failed
    if passed < total:
        print(f"\n{total - passed} checks failed. Please review the errors above.")
        sys.exit(1)
    else:
        print("\nAll quality checks passed!")


def main():
    """Main function"""
    # Set Windows console encoding
    import codecs

    if sys.platform.startswith("win"):
        try:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
        except AttributeError:
            pass

    print("DHT22 Project Code Quality Check Starting")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if running from project root
    if not Path("pyproject.toml").exists():
        print("pyproject.toml not found. Please run from project root.")
        sys.exit(1)

    # Run each check
    checks = {
        "Import Check": check_imports(),
        "Ruff Linting": check_ruff(),
        "Ruff Formatting": check_ruff_format(),
        "MyPy Type Check": check_mypy(),
        "Unit Tests": run_tests(),
    }

    # Generate results report
    generate_report(checks)


if __name__ == "__main__":
    main()
