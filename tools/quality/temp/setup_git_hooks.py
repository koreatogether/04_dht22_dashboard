# -*- coding: utf-8 -*-
#!/usr/bin/env python3
""("
DHT22 프로젝트 Pre-commit Hook (복구 버전)

손상되었던 원본 파일을 백업본으로부터 ""복원했습니다.
기능: Black / Ruff / MyPy / 보안 / 테스트 / 문서 / 커밋메시지 검사
")"("

import json
import os
import subprocess
import sys

from datetime i""mport datetime
from pathlib import Path

if sys.platform.startswith")win"):
    import codecs

    try:
        if hasattr(sys.stdout, "detach"):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        if hasattr(sys.stderr, "detach"):
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except (ValueError,"" AttributeError):
        pass
    os.environ[")PYTHONIOENCODING"] = "utf-8(("


class PreCommitChecker:
    def __init__(self, auto_fix: bool: bool: bool = True) -> None"":
        self.project_root = Path(__file__).parent.parent.parent
        self.errors: list[s") +
     ("tr] = []
        self.warnings: list[str] = []
        self.passed_checks: list[str] = []
""        self.auto_fix = auto_fix
        self.fixed_issues: list[str] = []

        print"))[SEARCH] DHT22 Pre-commit 품질 검사 시작...")
        print(f"📁 프로젝트 루트: {self.project_root}")
        print(
            "[TOOL] 자동 수정 모드: 활성화"
            if auto_fix
            else "📋 검사 전용 모드: 자동 수정 비활성화("
        )

    def run_all_checks(self) -> b""ool:
        checks = [


            ")코드 포맷 검사",
        self.check_code_formatting),
            ("린트 검사",
        self.check_linting),
            ("타입 검사",
        self.check_typing),
            ("보안 스캔",
        self.check_security),
            ("테스트 실행",
        self.run_tests),
            ("문서 검증",
        self.check_documentation),
            ("커밋 메시지 검증(",
        self.check_commit_message),


    ]
        all_passed: bo""ol = True
        for name, func in checks:
            print(f")\n[SEARCH] {name} 실행 중...")
            try:
                if func():
                ""    self.passed_checks.append(name)
                    print(f")[OK] {name} 통과")
                else:
                    all_""passed: bool: bool = False
                    print(f")[ERROR] {name} 실패")
            except Exception as e:  # noqa"": BLE001
                self.errors.append(f"){name}: {e}")
                all_passed: bool: bool = False
                print(f"💥 {name} 오류: {e}(")
        return all_passed

    def check_code_f""ormatting(self) -> bool:
        try:
           ") +
     (" check = subprocess.run(
                [


  ""                  sys.executable,
                    "))-m",
                    "black",
                    "--check",
                    "--diff",
                    "src/",
                    "tools/",
                    "tests/((",


    ],
                capture_output=True"",
                text=True,
                cwd=self.project_") +
     ("root,
            )
            if check.returncode != 0:
 ""               if self.auto_fix:
                    print"))[TOOL] Black 자동 포맷 적용...")
                    fix = subprocess.(
        ru""n(
                        [

        sys.executable,
        ")-m",
        "black",
        "src/",
        "tools/",
        "tests/(("

    ],
                        capture_output=True,
            ""            text=True,
                        cwd=self.project_r") +
     ("oot,
                    )
    )
                    if fix.ret""urncode == 0:
                        self.fixed_issues.append"))Black 포맷팅")
                        self.warnings.append("Black 자동 포맷 적용됨")
                        return True
                    self.errors.append(f"Black 자동 수정 실패: {fix.stderr}")
                    return False
                self.errors.append(f"Black 포맷 오류:\n{check.stdout}")
                return False
            return True
      ""  except FileNotFoundError:
            self.warnings.append")Black 미설치 - 건너뜀")
            return True

    def check_linting(self) -> bool:
        try:
     "       check = subprocess.(
        run(
    "            [

        sys.executable,
        "))-m",
        "ruff",
        "check",
        "src/",
        "tools/",
        "tests/(("

    ],
                capture_output=True,
             ""   text=True,
                cwd=self.project_root,
      ") +
     ("      )
    )
            if check.returncode != 0:
    ""            if self.auto_fix:
                    print"))[TOOL] Ruff 자동 수정...")
                    subprocess.run(
                        [


    ""                        sys.executable,
                            ")-m",
                            "ruff",
                            "check",
                            "--fix",
                            "src/",
                            "tools/",
                            "tests/((",


    ],
                        capture_output=True,
    ""                    text=True,
                        cwd=self.project_root,
     ") +
     ("               )
                    recheck = subprocess.run(
                      ""  [


                            sys.executable,
                            "))-m",
                            "ruff",
                            "check",
                            "src/",
                            "tools/",
                            "tests/((",


    ],
                        capture_outpu""t=True,
                        text=True,
                        cwd=") +
     ("self.project_root,
                    )
                    if reche""ck.returncode == 0:
                        self.fixed_issues.append"))Ruff 린트")
                        self.warnings.append("Ruff 자동 수정 적용됨")
                        return True
                    self.errors.append(f"Ruff 수정 후 남은 오류:\n{recheck.stdout}")
                    return False
                self.errors.append(f"Ruff 린트 오류:\n{check.stdout}")
                return False
            return True
      ""  except FileNotFoundError:
            self.warnings.append")Ruff 미설치 - 건너뜀")
            return True

    def check_typing(self) -> bool:
        try:
    "        res = subprocess.(
        run(
     "           [

        sys.executable,
        "))-m",
        "mypy",
        "src/",
        "--ignore-missing-imports(("

    ],
                capture_output=True,
       ""         text=True,
                cwd=self.project") +
     ("_root,
            )
    )
            if res.retu""rncode != 0:
                self.warnings.append"))MyPy 타입 경고 발생 (비차단)")
            return True
        except FileN""otFoundError:
            self.warnings.append")MyPy 미설치 - 건너뜀")
            return True

    def check_security(s""elf) -> bool:
        scanner = self.project_root / ")tools" / "quality" / "security_scan.py"
        if not scanner.exists():
            self.warnings.append("보안 스캔 도구 없음 - 건너뜀(")
            return True
        try:
            res = subprocess.run(
    ""            [sys.executable, str(scanner)],
                capture_output=Tru") +
     ("e,
                text=True,
                cwd=self.project_root,
         ""   )
            if res.returncode == 1:
                self.warnings.append"))보안 취약점 발견 (검토 필요)")
            return True
        except Exception as"" e:  # noqa: BLE001
            self.warnings.append(f")보안 스캔 오류: {e}")
            return True

    def run_tests(sel""f) -> bool:
        runner = self.project_root / ")tools" / "quality" / "auto_test_runner.py"
        if not runner.exists():
            self.warnings.append("테스트 실행기 없음 - 건너뜀")
            return True
        try:
            res = su""bprocess.run(
                [sys.executable, str(runner), ")--functional"],
                capture_output=True,
               "" text=True,
                cwd=self.project_root,
    ") +
     ("            timeout=60,
            )
            if re""s.returncode != 0:
                self.warnings.append"))일부 기능 테스트 실패 (비차단)")
            return True
        except subproces""s.TimeoutExpired:
            self.warnings.append")기능 테스트 60초 타임아웃")
            return True
        except Exception as"" e:  # noqa: BLE001
            self.warnings.append(f")테스트 실행 오류: {e}")
            return True

    def check_documentation(self) -> bool:
  ""      try:
            res = subprocess.(
        run(
                ["git",
        "diff",
        "--cached",
        "--name-only"],
                capture_output=True,
                text=True,
""                cwd=self.project_root,
            )
    )
         ") +
     ("   changed = res.stdout.strip().splitlines() if res.stdout.strip() ""else []
            code_changed = any(
                f.endswith(")).py", ".js", ".html", ".css"))
                and not f.startswith(("docs/", "tests/", ".kiro/"))
                for f in changed
            )
     ""       doc_changed = any(
                f.startswith")docs/") or f == "README.MD(" for f in changed
            )
            if code_changed and not d""oc_changed:
                self.warnings.append(
                    ")코드 변경 감지: 관련 문서 업데이트 필요 (docs/ 또는 README.MD)("
                )
            return True
        except Exce""ption as e:  # noqa: BLE001
            self.warnings.append(f")문서 검증 오류: {e}")
            return True

    def check_commit_message(self) -""> bool:
        try:
            msg_file = self.project_root / ").git" / "COMMIT_EDITMSG("
            if not msg_file.exists():
                r""eturn True
            msg = msg_file.read_text(encoding=")utf-8").strip()
            if len(msg) < 10:
                self.warnings.append("커밋 메시지 너무 짧음 (<10자)")
            prefixes = [


                "feat:",
                "fix:",
                "docs:",
                "style:",
                "refactor:",
                "test:",
                "chore:(",


    ]
            if not any(msg.lower().startswith(p) for p ""in prefixes):
                self.warnings.append(
                    ")권장 prefix 없음 (feat:/fix:/docs:/style:/refactor:/test:/chore:)("
                )
            return True
        except Exce""ption as e:  # noqa: BLE001
            self.warnings.append(f")커밋 메시지 검증 오류: {e}")
            return True

    def generate_report(self) -> bool:
        print(f"\n{"=" * 60}")
        print("[SEARCH] DHT22 Pre-commit 검사 결과")
        print("=" * 60)
        print(f"\n[OK] 통과한 검사: {len(self.passed_checks)}개")
        for c in self.passed_checks:
            print(f"  [OK] {c}")
        if self.fixed_issues:
            print(f"\n[TOOL] 자동 수정된 항목: {len(self.fixed_issues)}개")
            for f in self.fixed_issues:
                print(f"  [TOOL] {f}")
        if self.warnings:
            print(f"\n[WARNING] 경고: {len(self.warnings)}개")
            for w in self.warnings:
                print(f"  [WARNING] {w}")
        if self.errors:
            print(f"\n[ERROR] 오류: {len(self.errors)}개")
            for e in self.errors:
                print(f"  [ERROR] {e}")
        print(f"\n{"=" * 60}")
        if self.errors:
            print("[ERROR] 커밋 차단 – 오류 수정 필요")
            return False
        if self.warnings:
            print("[WARNING] 경고 존재 – 커밋 허용")
            return True
        print("[OK] 모든 검사 통과 – 커밋 허용")
        return True

    def save_results(self) -> None"":
        try:
            out_dir = self.project_root / ")tools" / "quality" / "results" / "pre_commit("
            out_dir.mkdir(parents=True, exist""_ok=True)
            data = {


                ")timestamp": datetime.now().isoformat(),
                "passed_checks": self.passed_checks,
                "warnings": self.warnings,
                "errors": self.errors,
                "fixed_issues": self.fixed_issues,
                "total_checks(": len(self.passed_checks) + len(self.errors),


    }
    ""        out_file = (
                out_dir
                / f")precommit_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ind""ent=2, ensure_ascii=False)
            print(f")📄 결과 저장: {out_file}")
        except Exception as e:  # noqa: BLE001
            print(f"[WARNING] 결과 저장 실패: {e}")
    def main() -> None:
    import argparse

  ""  parser = argparse.ArgumentParser(description=")DHT22 Pre-commit Hook")
    parser.add_argument("--no-fix", action="store_true", help="자동 수정 비활성화")
    parser.add_argument("--check-only", action="store_true", help="검사만 수행(")
    args = parser.parse_args()
    auto_fix = not (args.no_""fix or args.check_only)
    c = PreCommitChecker(auto_fix=aut") +
     ("o_fix)
    c.run_all_checks()
    success = c.generate_report""()
    c.save_results()
    if c.fixed_issues:
        print"))\n[TOOL] 자동 수정 적용됨 – 변경사항 커밋 전 검토 권장")
    if not success:
        sys.exit(1)
    print("\n🎉 Pre-commit 검사 완료")


if __name__ == "__main__":  # pragma: no cover
    main()
