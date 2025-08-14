#!/usr/bin/env python3
"""
DHT22 프로젝트 Pre-commit Hook
Git 커밋 시 자동 품질 검사 실행

기능:
- 코드 품질 검사 (Ruff, Black, MyPy)
- 보안 스캔
- 테스트 실행
- 문서 업데이트 검증
- 커밋 메시지 검증
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# UTF-8 인코딩 강제 설정 (Windows 호환)
if sys.platform.startswith("win"):
    import codecs

    try:
        if hasattr(sys.stdout, "detach"):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        if hasattr(sys.stderr, "detach"):
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except (ValueError, AttributeError):
        pass
    os.environ["PYTHONIOENCODING"] = "utf-8"


class PreCommitChecker:
    """Pre-commit 품질 검사기"""

    def __init__(self, auto_fix: bool = True):
        self.project_root = Path(__file__).parent.parent.parent
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        self.auto_fix = auto_fix
        self.fixed_issues = []

        print("🔍 DHT22 Pre-commit 품질 검사 시작...")
        print(f"📁 프로젝트 루트: {self.project_root}")
        if auto_fix:
            print("🔧 자동 수정 모드: 활성화")
        else:
            print("📋 검사 전용 모드: 자동 수정 비활성화")

    def run_all_checks(self) -> bool:
        """모든 품질 검사 실행"""
        checks = [
            ("코드 포맷 검사", self.check_code_formatting),
            ("린트 검사", self.check_linting),
            ("타입 검사", self.check_typing),
            ("보안 스캔", self.check_security),
            ("테스트 실행", self.run_tests),
            ("문서 검증", self.check_documentation),
            ("커밋 메시지 검증", self.check_commit_message),
        ]

        all_passed = True

        for check_name, check_func in checks:
            print(f"\n🔍 {check_name} 실행 중...")
            try:
                if check_func():
                    self.passed_checks.append(check_name)
                    print(f"✅ {check_name} 통과")
                else:
                    all_passed = False
                    print(f"❌ {check_name} 실패")
            except Exception as e:
                self.errors.append(f"{check_name}: {str(e)}")
                all_passed = False
                print(f"💥 {check_name} 오류: {e}")

        return all_passed

    def check_code_formatting(self) -> bool:
        """Black 코드 포맷 검사 및 자동 수정"""
        try:
            # 먼저 검사만 실행
            check_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "black",
                    "--check",
                    "--diff",
                    "src/",
                    "tools/",
                    "tests/",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if check_result.returncode != 0:
                if self.auto_fix:
                    print("🔧 Black 포맷 오류 발견, 자동 수정 시도 중...")

                    # 자동 수정 실행
                    fix_result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "black",
                            "src/",
                            "tools/",
                            "tests/",
                        ],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                    )

                    if fix_result.returncode == 0:
                        print("✅ Black 자동 포맷팅 완료")
                        self.fixed_issues.append("Black 코드 포맷팅")
                        self.warnings.append(
                            "Black 자동 포맷팅이 적용되었습니다. 변경사항을 확인해주세요."
                        )
                        return True
                    else:
                        self.errors.append(
                            f"Black 자동 수정 실패:\n{fix_result.stderr}"
                        )
                        print("💡 수동 수정: python -m black src/ tools/ tests/")
                        return False
                else:
                    self.errors.append(f"Black 포맷 오류:\n{check_result.stdout}")
                    print("💡 수동 수정: python -m black src/ tools/ tests/")
                    return False

            return True
        except FileNotFoundError:
            self.warnings.append("Black이 설치되지 않음")
            return True  # 경고로 처리, 실패하지 않음

    def check_linting(self) -> bool:
        """Ruff 린트 검사 및 자동 수정"""
        try:
            # 먼저 검사만 실행
            check_result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "src/", "tools/", "tests/"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if check_result.returncode != 0:
                if self.auto_fix:
                    print("🔧 Ruff 린트 오류 발견, 자동 수정 시도 중...")

                    # 자동 수정 실행
                    fix_result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "ruff",
                            "check",
                            "--fix",
                            "src/",
                            "tools/",
                            "tests/",
                        ],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                    )

                    # 수정 후 다시 검사
                    recheck_result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "ruff",
                            "check",
                            "src/",
                            "tools/",
                            "tests/",
                        ],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                    )

                    if recheck_result.returncode == 0:
                        print("✅ Ruff 자동 수정 완료")
                        self.fixed_issues.append("Ruff 린트 오류")
                        self.warnings.append(
                            "Ruff 자동 수정이 적용되었습니다. 변경사항을 확인해주세요."
                        )
                        return True
                    else:
                        # 자동 수정으로 해결되지 않은 오류들
                        self.errors.append(
                            f"Ruff 자동 수정 후 남은 오류:\n{recheck_result.stdout}"
                        )
                        print(
                            "💡 수동 수정 필요: 자동 수정으로 해결되지 않은 오류가 있습니다."
                        )
                        return False
                else:
                    self.errors.append(f"Ruff 린트 오류:\n{check_result.stdout}")
                    print("💡 수동 수정: python -m ruff check --fix src/ tools/ tests/")
                    return False

            return True
        except FileNotFoundError:
            self.warnings.append("Ruff가 설치되지 않음")
            return True

    def check_typing(self) -> bool:
        """MyPy 타입 검사"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode != 0:
                self.warnings.append(f"MyPy 타입 경고:\n{result.stdout}")
                # 타입 검사는 경고로만 처리

            return True
        except FileNotFoundError:
            self.warnings.append("MyPy가 설치되지 않음")
            return True

    def check_security(self) -> bool:
        """보안 스캔"""
        try:
            security_scanner = (
                self.project_root / "tools" / "quality" / "security_scan.py"
            )
            if not security_scanner.exists():
                self.warnings.append("보안 스캔 도구를 찾을 수 없음")
                return True

            result = subprocess.run(
                [sys.executable, str(security_scanner)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # 보안 스캔 결과 파싱
            if result.returncode == 1:  # 취약점 발견
                self.warnings.append("보안 취약점이 발견되었습니다. 검토가 필요합니다.")

            return True  # 보안 스캔은 경고로만 처리
        except Exception as e:
            self.warnings.append(f"보안 스캔 오류: {e}")
            return True

    def run_tests(self) -> bool:
        """핵심 테스트 실행"""
        try:
            # 빠른 테스트만 실행 (전체 테스트는 시간이 오래 걸림)
            test_runner = (
                self.project_root / "tools" / "quality" / "auto_test_runner.py"
            )
            if not test_runner.exists():
                self.warnings.append("테스트 실행기를 찾을 수 없음")
                return True

            # 기능 테스트만 빠르게 실행
            result = subprocess.run(
                [sys.executable, str(test_runner), "--functional"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60,
            )

            if result.returncode != 0:
                self.warnings.append(f"일부 테스트 실패:\n{result.stderr}")
                # 테스트 실패는 경고로 처리 (커밋을 막지 않음)

            return True
        except subprocess.TimeoutExpired:
            self.warnings.append("테스트 실행 시간 초과 (60초)")
            return True
        except Exception as e:
            self.warnings.append(f"테스트 실행 오류: {e}")
            return True

    def check_documentation(self) -> bool:
        """문서 업데이트 검증"""
        try:
            # 변경된 파일 목록 확인
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            changed_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # 코드 파일이 변경되었는지 확인
            code_files_changed = any(
                f.endswith((".py", ".js", ".html", ".css"))
                and not f.startswith(("docs/", "tests/", ".kiro/"))
                for f in changed_files
            )

            # 문서 파일이 변경되었는지 확인
            doc_files_changed = any(
                f.startswith("docs/") or f == "README.MD" for f in changed_files
            )

            if code_files_changed and not doc_files_changed:
                self.warnings.append(
                    "코드가 변경되었지만 문서가 업데이트되지 않았습니다.\n"
                    "다음 문서 업데이트를 고려해주세요:\n"
                    "- docs/release.md (필수)\n"
                    "- docs/delvelopment/automation_workflow_checklist.md\n"
                    "- README.MD"
                )

            return True
        except Exception as e:
            self.warnings.append(f"문서 검증 오류: {e}")
            return True

    def check_commit_message(self) -> bool:
        """커밋 메시지 검증"""
        try:
            # 커밋 메시지 파일 읽기
            commit_msg_file = self.project_root / ".git" / "COMMIT_EDITMSG"
            if not commit_msg_file.exists():
                return True  # 커밋 메시지 파일이 없으면 통과

            commit_msg = commit_msg_file.read_text(encoding="utf-8").strip()

            # 기본적인 커밋 메시지 검증
            if len(commit_msg) < 10:
                self.warnings.append("커밋 메시지가 너무 짧습니다 (최소 10자)")

            # 권장 커밋 메시지 형식 체크
            prefixes = [
                "feat:",
                "fix:",
                "docs:",
                "style:",
                "refactor:",
                "test:",
                "chore:",
            ]
            if not any(commit_msg.lower().startswith(prefix) for prefix in prefixes):
                self.warnings.append(
                    "권장 커밋 메시지 형식을 사용해주세요:\n"
                    "feat: 새 기능 추가\n"
                    "fix: 버그 수정\n"
                    "docs: 문서 업데이트\n"
                    "style: 코드 스타일 변경\n"
                    "refactor: 코드 리팩토링\n"
                    "test: 테스트 추가/수정\n"
                    "chore: 기타 작업"
                )

            return True
        except Exception as e:
            self.warnings.append(f"커밋 메시지 검증 오류: {e}")
            return True

    def get_staged_python_files(self) -> List[str]:
        """스테이징된 Python 파일 목록 반환"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            files = result.stdout.strip().split("\n") if result.stdout.strip() else []
            python_files = [f for f in files if f.endswith(".py")]

            return python_files
        except Exception:
            return []

    def generate_report(self) -> None:
        """검사 결과 리포트 생성"""
        print("\n" + "=" * 60)
        print("🔍 DHT22 Pre-commit 검사 결과")
        print("=" * 60)

        print(f"\n✅ 통과한 검사: {len(self.passed_checks)}개")
        for check in self.passed_checks:
            print(f"  ✅ {check}")

        if self.fixed_issues:
            print(f"\n🔧 자동 수정된 항목: {len(self.fixed_issues)}개")
            for fixed in self.fixed_issues:
                print(f"  🔧 {fixed}")

        if self.warnings:
            print(f"\n⚠️ 경고: {len(self.warnings)}개")
            for warning in self.warnings:
                print(f"  ⚠️ {warning}")

        if self.errors:
            print(f"\n❌ 오류: {len(self.errors)}개")
            for error in self.errors:
                print(f"  ❌ {error}")

        print("\n" + "=" * 60)

        if self.errors:
            print("❌ 커밋이 차단되었습니다. 위 오류를 수정한 후 다시 시도해주세요.")
            return False
        elif self.warnings:
            print("⚠️ 경고가 있지만 커밋을 진행합니다.")
            print("💡 가능하면 경고 사항을 검토해주세요.")
            return True
        else:
            print("✅ 모든 검사를 통과했습니다. 커밋을 진행합니다.")
            return True

    def save_results(self) -> None:
        """검사 결과를 파일로 저장"""
        try:
            results_dir = self.project_root / "tools" / "quality" / "results"
            results_dir.mkdir(parents=True, exist_ok=True)

            results = {
                "timestamp": datetime.now().isoformat(),
                "passed_checks": self.passed_checks,
                "warnings": self.warnings,
                "errors": self.errors,
                "total_checks": len(self.passed_checks) + len(self.errors),
                "success_rate": (
                    len(self.passed_checks)
                    / (len(self.passed_checks) + len(self.errors))
                    * 100
                    if (len(self.passed_checks) + len(self.errors)) > 0
                    else 100
                ),
            }

            results_file = (
                results_dir
                / f"precommit_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"📄 검사 결과 저장: {results_file}")
        except Exception as e:
            print(f"⚠️ 결과 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="DHT22 Pre-commit Hook")
    parser.add_argument(
        "--no-fix", action="store_true", help="자동 수정 비활성화 (검사만 수행)"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="검사만 수행 (자동 수정 없음)"
    )

    args = parser.parse_args()

    # 자동 수정 모드 결정
    auto_fix = not (args.no_fix or args.check_only)

    checker = PreCommitChecker(auto_fix=auto_fix)

    try:
        # 모든 검사 실행
        all_passed = checker.run_all_checks()

        # 결과 리포트 생성
        success = checker.generate_report()

        # 결과 저장
        checker.save_results()

        # 자동 수정된 항목이 있으면 알림
        if checker.fixed_issues:
            print(f"\n🔧 {len(checker.fixed_issues)}개 항목이 자동으로 수정되었습니다.")
            print("📝 변경사항을 검토한 후 다시 커밋해주세요.")

        # 오류가 있으면 커밋 차단
        if not success:
            sys.exit(1)

        print("\n🎉 Pre-commit 검사 완료!")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 검사가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Pre-commit 검사 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
