#!/usr/bin/env python3
"""
DHT22 프로젝트 빠른 자동 수정 도구 (Cross-platform)
Windows, Linux, macOS 모두에서 실행 가능
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
    os.environ["PYTHONIOENCODING"] = "utf-8"

import subprocess
import sys
from pathlib import Path


def run_quick_fix(): -> None:
    """빠른 자동 수정 실행"""

    print()
    print("=" * 50)
    print("🚀 DHT22 프로젝트 빠른 자동 수정 도구")
    print("=" * 50)
    print()
    print("💡 이전 프로젝트에서 학습한 패턴으로 자동 수정:")
    print("  - Ruff 린트 오류 자동 수정")
    print("  - MyPy 타입 힌트 자동 추가")
    print("  - UTF-8 인코딩 문제 해결")
    print("  - 공통 코드 스타일 통일")
    print()

    # 현재 상태 확인
    print("📊 현재 코드 품질 상태 확인...")

    # Ruff 검사
    try:
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "src/", "tools/", "tests/"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        ruff_errors = ruff_result.stdout.count("error") if ruff_result.stdout else 0
        print(f"  🔍 Ruff 오류: {ruff_errors}개")
    except:
        print("  ⚠️ Ruff 검사 실패")

    # MyPy 검사
    try:
        mypy_result = subprocess.run(
            [sys.executable, "-m", "mypy", "tools/", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        mypy_errors = mypy_result.stdout.count("error:") if mypy_result.stdout else 0
        print(f"  🎯 MyPy 오류: {mypy_errors}개")
    except:
        print("  ⚠️ MyPy 검사 실패")

    print()
    print("🔧 자동 수정 도구 실행 중...")

    # 1. 기본 자동 수정 도구 실행
    auto_fix_script = Path("tools/quality/auto_fix_common_issues.py")

    if auto_fix_script.exists():
        try:
            print("🔧 기본 자동 수정 실행 중...")
            result = subprocess.run(
                [sys.executable, str(auto_fix_script)],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                print("✅ 기본 자동 수정 완료")
            else:
                print("⚠️ 기본 자동 수정에서 일부 문제 발생")
        except Exception as e:
            print(f"⚠️ 기본 자동 수정 오류: {e}")

    # 2. 고급 자동 수정 도구 실행
    advanced_fix_script = Path("quick_fix_advanced.py")

    if advanced_fix_script.exists():
        try:
            print("🚀 고급 자동 수정 실행 중...")
            result = subprocess.run(
                [sys.executable, str(advanced_fix_script)],
                capture_output=True,
                text=True,
                timeout=180,
            )

            print("📋 자동 수정 결과:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️ 경고/오류: {result.stderr}")

            if result.returncode == 0:
                print("✅ 자동 수정 완료!")
                print("📁 결과 확인: tools/quality/results/")
            else:
                print("❌ 자동 수정 중 일부 오류 발생")
                print("💡 수동 확인이 필요합니다")

        except subprocess.TimeoutExpired:
            print("⏰ 자동 수정 시간 초과 (2분)")
        except Exception as e:
            print(f"💥 실행 오류: {e}")
    else:
        print(f"❌ 자동 수정 스크립트를 찾을 수 없음: {auto_fix_script}")

    print()
    print("=" * 50)


if __name__ == "__main__":
    try:
        run_quick_fix()
    except KeyboardInterrupt:
        print("\n🛑 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
