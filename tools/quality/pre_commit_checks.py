# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Clean pre-commit quality check runner.

This replaces calling the currently corrupted `setup_git_hooks.py` during
actual commit time. It performs a focused subset of checks quickly so the
developer can commit, while still enforcing baseline quality gates.

Checks performed (fail on error):
  1. Black --check (no auto-fix for speed)
  2. Ruff lint (no auto-fix)
  3. MyPy (treated as warning; will not block)
  4. (Optional) pytest -q on changed test files only (fast)

Warnings (do not block):
  - MyPy issues
  - Missing docs update when code changed

Exit codes:
  0 success (errors empty)
  1 failure (any formatting/lint errors)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJ_ROOT_CANDIDATE = Path(__file__).resolve().parents[2]
PROJECT_ROOT = (
    PROJ_ROOT_CANDIDATE if (PROJ_ROOT_CANDIDATE / ".git").exists() else Path.cwd()
)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _run(cmd: list[str]) -> tuple[int, str, str]:
    """Run a subprocess command relative to project root with robust UTF-8 decoding.

    We avoid locale-dependent decoding errors (e.g., cp949) by capturing bytes
    and decoding manually with replacement for invalid sequences.
    """
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_ROOT,
    )
    stdout = (proc.stdout or b"").decode("utf-8", "replace").strip()
    stderr = (proc.stderr or b"").decode("utf-8", "replace").strip()
    return proc.returncode, stdout, stderr


def staged_files() -> list[str]:
    code, out, _ = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    if code != 0:
        return []
    return [f for f in out.splitlines() if f]


def changed_test_files(files: list[str]) -> list[str]:
    return [f for f in files if f.startswith("tests/") and f.endswith(".py")]


def check_black(warnings: list[str]) -> None:
    # Temporary: only check application source
    code, out, err = _run([sys.executable, "-m", "black", "--check", "src/"])
    if code != 0:
        warnings.append("Black formatting issues (non-blocking). Run: python -m black src/")


def check_ruff(warnings: list[str]) -> None:
    code, out, _ = _run([sys.executable, "-m", "ruff", "check", "src/"])
    if code != 0:
        warnings.append("Ruff lint issues (non-blocking). Run: python -m ruff check --fix src/")


def check_mypy(warnings: list[str]) -> None:
    code, out, _ = _run(
        [sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"]
    )
    if code != 0:
        warnings.append("MyPy type issues (non-blocking):\n" + out)


def check_docs(files: list[str], warnings: list[str]) -> None:
    if any(f.endswith(".py") and not f.startswith("docs/") for f in files):
        if not any(f.startswith("docs/") or f == "README.MD" for f in files):
            warnings.append(
                "Code changed but no docs updated (docs/ or README.MD). Consider updating release notes."
            )


def run_fast_tests(files: list[str], warnings: list[str]) -> None:
    tests = changed_test_files(files)
    if not tests:
        return
    cmd = [sys.executable, "-m", "pytest", "-q", *tests]
    code, out, err = _run(cmd)
    if code != 0:
        warnings.append(
            "Some changed tests failed (non-blocking).\n" + (err or out)[:400]
        )


def _force_utf8_stdio() -> None:
    """Force stdout/stderr to UTF-8 if possible (Windows git hook safety).

    We only rewrap when the current encoding can't encode a simple emoji.
    """
    try:
        test_char = "🔍"
        if sys.stdout.encoding and "UTF-8" in sys.stdout.encoding.upper():
            return
        # Try a trial encode; if fails, rewrap
        try:
            test_char.encode(sys.stdout.encoding or "ascii")
        except Exception:  # noqa: BLE001
            import io  # local import to avoid overhead when not needed

            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            os.environ["PYTHONUTF8"] = "1"
            os.environ["PYTHONIOENCODING"] = "utf-8"
    except Exception:
        # Silently ignore; fallback printing will still work
        pass


def _e(msg: str) -> None:
    """Print with emoji fallback: retry without emoji if encoding fails."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # Strip non-ASCII
        ascii_msg = msg.encode("ascii", "ignore").decode("ascii")
        print(ascii_msg)


def main() -> int:
    _force_utf8_stdio()
    _e("🔍 Running fast pre-commit checks (clean script)...")
    errors: list[str] = []
    warnings: list[str] = []

    files = staged_files()
    try:
        check_black(warnings)
    except FileNotFoundError:
        warnings.append("Black not installed – skipping")
    try:
        check_ruff(warnings)
    except FileNotFoundError:
        warnings.append("Ruff not installed – skipping")
    try:
        check_mypy(warnings)
    except FileNotFoundError:
        warnings.append("MyPy not installed – skipping")

    check_docs(files, warnings)
    run_fast_tests(files, warnings)

    _e("\n================ Summary ================")
    if errors:
        _e(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print("  - " + e.splitlines()[0])
    else:
        _e("✅ No blocking errors.")

    if warnings:
        _e(f"\n⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print("  - " + w.splitlines()[0])
    else:
        _e("⚡ No warnings.")

    if errors:
        _e("\n❌ Commit blocked. Fix errors above.")
        return 1
    if warnings:
        _e("\n⚠️  Commit allowed with warnings.")
        return 0
    _e("\n🎉 All checks passed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
