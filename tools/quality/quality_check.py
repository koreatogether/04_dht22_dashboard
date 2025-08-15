#!/usr/bin/env python3
"""
통합 코드 품질 검사 도구

이 스크립트는 다음 검사를 수행합니다:
- Black: 코드 포맷팅 검사
- Ruff: 린팅 및 코드 스타일 검사
- MyPy: 타입 힌트 검사
- Pytest: 단위 테스트 실행
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """명령어를 실행하고 결과를 반환합니다."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=300,  # 5분 타임아웃
        )

        if result.returncode == 0:
            print(f"✅ {description} 통과")
            return True, result.stdout
        else:
            print(f"❌ {description} 실패")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} 타임아웃")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 {description} 오류: {str(e)}")
        return False, str(e)


def check_black() -> Tuple[bool, str]:
    """Black 코드 포맷팅 검사"""
    return run_command(
        ["uv", "run", "black", "--check", "--diff", "src/python/", "tools/"],
        "Black 포맷팅 검사",
    )


def check_ruff() -> Tuple[bool, str]:
    """Ruff 린팅 검사"""
    return run_command(
        ["uv", "run", "ruff", "check", "src/python/", "tools/"], "Ruff 린팅 검사"
    )


def check_ruff_format() -> Tuple[bool, str]:
    """Ruff 포맷팅 검사"""
    return run_command(
        ["uv", "run", "ruff", "format", "--check", "src/python/", "tools/"],
        "Ruff 포맷팅 검사",
    )


def check_mypy() -> Tuple[bool, str]:
    """MyPy 타입 검사"""
    return run_command(["uv", "run", "mypy", "src/python/"], "MyPy 타입 검사")


def run_tests() -> Tuple[bool, str]:
    """pytest 단위 테스트 실행"""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("📝 테스트 디렉토리가 없습니다. 테스트를 건너뜁니다.")
        return True, "No tests directory found"

    return run_command(["uv", "run", "pytest", "--tb=short"], "pytest 단위 테스트")


def check_imports() -> Tuple[bool, str]:
    """Python import 검사"""
    try:
        # 기본 import 테스트
        sys.path.insert(0, str(Path("src/python").absolute()))

        # 주요 모듈들 import 테스트
        from dashboard import app  # noqa: F401
        from utils import data_processor, serial_reader  # noqa: F401

        print("✅ Python import 검사 통과")
        return True, "All imports successful"

    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False, str(e)
    except Exception as e:
        print(f"💥 Import 검사 오류: {e}")
        return False, str(e)
    finally:
        # sys.path 복원
        if str(Path("src/python").absolute()) in sys.path:
            sys.path.remove(str(Path("src/python").absolute()))


def generate_report(results: Dict[str, Tuple[bool, str]]) -> None:
    """검사 결과 리포트 생성"""

    # 콘솔 요약
    print("\n" + "=" * 60)
    print("🎯 코드 품질 검사 결과 요약")
    print("=" * 60)

    passed = 0
    total = len(results)

    for check_name, (success, output) in results.items():
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{check_name:20} : {status}")
        if success:
            passed += 1

    print(f"\n📊 전체 결과: {passed}/{total} 통과")

    # JSON 리포트 생성
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
            name: {"passed": success, "output": output[:1000]}  # 출력 길이 제한
            for name, (success, output) in results.items()
        },
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"📄 상세 리포트: {report_file}")

    # 실패한 검사가 있으면 종료 코드 1
    if passed < total:
        print(f"\n💡 {total - passed}개의 검사가 실패했습니다. 위의 오류를 확인하세요.")
        sys.exit(1)
    else:
        print("\n🎉 모든 품질 검사를 통과했습니다!")


def main():
    """메인 함수"""
    # Windows 콘솔 인코딩 설정
    import codecs

    if sys.platform.startswith("win"):
        try:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
        except AttributeError:
            pass

    print("🚀 DHT22 프로젝트 코드 품질 검사 시작")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 프로젝트 루트에서 실행되고 있는지 확인
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml을 찾을 수 없습니다. 프로젝트 루트에서 실행해주세요.")
        sys.exit(1)

    # 각 검사 실행
    checks = {
        "Import 검사": check_imports(),
        "Black 포맷팅": check_black(),
        "Ruff 린팅": check_ruff(),
        "Ruff 포맷팅": check_ruff_format(),
        "MyPy 타입검사": check_mypy(),
        "단위 테스트": run_tests(),
    }

    # 결과 리포트 생성
    generate_report(checks)


if __name__ == "__main__":
    main()
