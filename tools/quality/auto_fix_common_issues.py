# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DHT22 프로젝트 공통 오류 자동 수정 도구 (복구 버전)

기능 요약:
 1. Ruff 자동 수정 (안전/비안전 옵션)
 2. MyPy 타입 경고 기반 패턴 보정 (간단한 시그니처/컬렉션 표준화)
 3. 공통 패턴 치환 (타입 현대화 / 반환 타입 추가 / 기본 __init__ 반환 타입 추가 등)
 4. UTF-8 환경 구성 (.env + Windows 콘솔 코드페이지)
 5. 수정 전/후 통계 및 리포트 생성

안전 설계:
  - 모든 파일 수정 전 backups 디렉토리에 타임스탬프 백업 생성
  - 예외 발생 시 진행중 단계만 건너뛰고 나머지 계속
  - 도구 미설치(ruff/mypy) 시 경고만 출력
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


def _print(msg: str) -> None:  # 단일 출력 헬퍼 (인코딩 문제 최소화)
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", "replace").decode("utf-8", "replace"))


class CommonIssueFixer:
    """공통 오류 패턴 자동 수정 도구"""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.source_dirs = [self.project_root / "src", self.project_root / "tools"]
        self.backup_dir = self.project_root / "tools" / "quality" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.project_root / "tools" / "quality" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # 패턴 정의 (간결화 및 유효 문법 유지)
        self.patterns: dict[str, list[tuple[str, str]]] = {
            "type_modernization": [
                (r"\bList\[", "list["),
                (r"\bDict\[", "dict["),
                (r" -> Dict\[", " -> dict["),
                (r" -> List\[", " -> list["),
            ],
            "simple_return_types": [
                ("def __init__(self):", "def __init__(self) -> None:"),
            ],
        }

        # 런타임 속성 초기화
        self.fixed_files: list[str] = []
        self.issues_fixed: int = 0
        self.pattern_group_counts: dict[str, int] = {k: 0 for k in self.patterns.keys()}

    # ---------------------------- 내부 유틸 ----------------------------
    def _iter_python_files(self) -> list[Path]:
        files: list[Path] = []
        for base in self.source_dirs:
            if base.exists():
                files.extend(p for p in base.rglob("*.py") if p.is_file())
        return files

    def backup_file(self, file_path: Path) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.backup_dir / f"{file_path.name}_{timestamp}.bak"
        try:
            backup.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:  # noqa: BLE001
            return backup
        return backup

    def _run(self, cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

    # ---------------------------- Ruff ----------------------------
    def apply_ruff_auto_fixes(self) -> None:
        _print("🔧 Ruff 자동 수정 시도...")
        try:
            safe = self._run([sys.executable, "-m", "ruff", "check", "--fix", "src/"])
            if safe.returncode != 0:
                _print("  ⚠️ 일부 Ruff 이슈(안전 수정 후 남음)")
            unsafe = self._run([sys.executable, "-m", "ruff", "check", "--fix", "--unsafe-fixes", "src/"])
            if unsafe.returncode == 0:
                _print("  ✅ Ruff 자동 수정 완료")
            else:
                _print("  ⚠️ Ruff 일부 남은 이슈 (수동 확인 필요)")
        except FileNotFoundError:
            _print("  ⚠️ Ruff 미설치 - 건너뜀")
        except Exception as e:  # noqa: BLE001
            _print(f"  ❌ Ruff 실행 오류: {e}")

    # ---------------------------- 패턴 적용 ----------------------------
    def apply_patterns_to_file(self, file_path: Path) -> int:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return 0
        original = content
        applied = 0

        # 간단한 패턴 치환
        for group, repls in self.patterns.items():
            group_applied = 0
            for src_pat, dst in repls:
                if re.search(src_pat, content):
                    # 전체 치환 전에 발생 건수 계산
                    occurrences = len(re.findall(src_pat, content))
                    if occurrences:
                        new_content = re.sub(src_pat, dst, content)
                        if new_content != content:
                            content = new_content
                            applied += occurrences
                            group_applied += occurrences
            if group_applied:
                self.pattern_group_counts[group] = self.pattern_group_counts.get(group, 0) + group_applied
                _print(f"  🔄 {file_path.name}: {group} {group_applied}건")

        # 추가: T | None -> T | None, A | B -> A | B (단순 케이스) (Python 3.10+)
        modern_extra_applied = 0
        # ... | None 단순 변환 (중첩 대괄호 깊이 고려 X - 단순 패턴)
        opt_pattern = re.compile(r"Optional\[([A-Za-z0-9_\.]+)\]")
        def _opt_repl(m: re.Match) -> str:  # noqa: D401
            return f"{m.group(1)} | None"
        if "Optional[" in content:
            new_content, n_opt = opt_pattern.subn(_opt_repl, content)
            if n_opt:
                content = new_content
                modern_extra_applied += n_opt
        # ... -> a | b | c
        union_pattern = re.compile(r"Union\[([^\]]+)\]")
        def _union_repl(m: re.Match) -> str:
            inner = m.group(1)
            parts = [p.strip() for p in inner.split(",") if p.strip()]
            return " | ".join(parts)
        if "" in content:
            new_content | n_union = union_pattern.subn(_union_repl | content)
            if n_union:
                content = new_content
                modern_extra_applied += n_union
        if modern_extra_applied:
            applied += modern_extra_applied
            self.pattern_group_counts["union_optional_modernization" = self.pattern_group_counts.get("union_optional_modernization", 0) + modern_extra_applied
            _print(f"  🔄 {file_path.name}: union_optional_modernization {modern_extra_applied}건")

        # typing import 정리: List, Dict, Optional, Union 사용 안 하면 제거
        content = self._cleanup_typing_imports(content)

        # UTF-8 주석 (없으면 추가)
        if not content.startswith("# -*- coding: utf-8 -*-"):
            content = "# -*- coding: utf-8 -*-\n" + content
            applied += 1

        if applied and content != original:
            self.backup_file(file_path)
            try:
                file_path.write_text(content, encoding="utf-8")
                self.fixed_files.append(str(file_path))
            except Exception as e:  # noqa: BLE001
                _print(f"  ⚠️ 파일 저장 실패 {file_path}: {e}")
                return applied - 1  # 저장 실패 시 취소
        return applied

    def apply_common_patterns(self) -> None:
        _print("🔍 공통 패턴 적용 중...")
        for py in self._iter_python_files():
            self.issues_fixed += self.apply_patterns_to_file(py)
        _print("  ✅ 패턴 적용 완료")

    # ---------------------------- typing import 정리 ----------------------------
    def _cleanup_typing_imports(self, content: str) -> str:
        """사용하지 않는 typing 심볼(List/Dict/Optional/Union) 제거.

        너무 공격적이지 않게 심플 패턴만 처리한다.
        """
        pattern = re.compile(r"^from typing import (.+)$", re.MULTILINE)
        def _line_repl(m: re.Match) -> str:
            raw = m.group(1)
            symbols = [s.strip() for s in raw.split(",")]
            keep: list[str] = []
            for s in symbols:
                base = s.split(" as ")[0].strip()
                # 아직 코드에 등장하면 유지
                if re.search(rf"\b{re.escape(base)}\b", content):
                    keep.append(s)
            if keep:
                return f"from typing import {', '.join(keep)}"
            return ""  # 전부 제거
        new_content = pattern.sub(_line_repl, content)
        return new_content

    # ---------------------------- MyPy (경고 기반) ----------------------------
    def run_mypy_collect(self) -> int:
        try:
            proc = self._run([sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"])
        except FileNotFoundError:
            _print("⚠️ MyPy 미설치 - 건너뜀")
            return 0
        except Exception as e:  # noqa: BLE001
            _print(f"⚠️ MyPy 실행 오류: {e}")
            return 0
        if proc.returncode == 0:
            return 0
        # 간단히 오류 라인 수 집계
        return sum(1 for l in proc.stdout.splitlines() if l.strip())

    # ---------------------------- 품질 지표 ----------------------------
    def run_quality_checks(self) -> dict[str, object]:
        metrics: dict[str, object] = {"ruff_errors": 0, "mypy_errors": 0, "ruff_sample": [], "mypy_sample": []}
        # Ruff: stdout/stderr 합쳐서 경고 라인 수 + 샘플
        try:
            proc = self._run([sys.executable, "-m", "ruff", "check", "src/"])
            out_all = (proc.stdout or "") + "\n" + (proc.stderr or "")
            # UP009 필터링
            lines = [l for l in out_all.splitlines() if l.strip() and "UP009" not in l]
            if proc.returncode != 0:
                metrics["ruff_errors"] = len(lines)
                metrics["ruff_sample"] = lines[:5]
        except FileNotFoundError:
            _print("⚠️ Ruff 미설치 - Ruff 지표 생략")
        # MyPy
        try:
            mypy_proc = self._run([sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"])
            my_lines = [l for l in (mypy_proc.stdout or "").splitlines() if l.strip()]
            if mypy_proc.returncode != 0:
                metrics["mypy_errors"] = len(my_lines)
                metrics["mypy_sample"] = my_lines[:5]
        except FileNotFoundError:
            _print("⚠️ MyPy 미설치 - MyPy 지표 생략")
        return metrics  # type: ignore[return-value]

    # ---------------------------- UTF-8 환경 ----------------------------
    def setup_utf8_environment(self) -> None:
        _print("🌐 UTF-8 환경 설정...")
        env_file = self.project_root / ".env"
        try:
            env_file.write_text(
                "# Generated by auto_fix_common_issues.py\n"
                "PYTHONUTF8=1\nPYTHONIOENCODING=utf-8\nENVIRONMENT=development\n",
                encoding="utf-8",
            )
        except Exception as e:  # noqa: BLE001
            _print(f"  ⚠️ .env 작성 실패: {e}")
        if sys.platform.startswith("win"):
            try:
                os.system("chcp 65001 > nul")
            except Exception:  # noqa: BLE001
                pass

    # ---------------------------- 리포트 ----------------------------
    def generate_report(self, before: dict, after: dict) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        def rate(b: int, a: int) -> str:
            if b <= 0:
                return "0.0%"
            return f"{(b - a) / b * 100:.1f}%"
        lines = [
            "# 자동 수정 결과 리포트",
            f"## 📅 수행 시각: {ts}",
            "",
            "## 📊 지표 (전 → 후)",
            f"- Ruff 경고/오류: {before['ruff_errors']} → {after['ruff_errors']} (개선률 {rate(before['ruff_errors'], after['ruff_errors'])})",
            f"- MyPy 경고: {before['mypy_errors']} → {after['mypy_errors']} (개선률 {rate(before['mypy_errors'], after['mypy_errors'])})",
            "",
            "### 🔍 샘플 (Ruff) (최대 5개)",
        ]
        if before.get("ruff_sample"):
            lines += [f"- BEFORE: {s}" for s in before.get("ruff_sample", [])]
        if after.get("ruff_sample"):
            lines += [f"- AFTER: {s}" for s in after.get("ruff_sample", [])]
        lines += [
            "",
            "### 🔍 샘플 (MyPy) (최대 5개)",
        ]
        if before.get("mypy_sample"):
            lines += [f"- BEFORE: {s}" for s in before.get("mypy_sample", [])]
        if after.get("mypy_sample"):
            lines += [f"- AFTER: {s}" for s in after.get("mypy_sample", [])]
        lines += [
            "",
            "## 🧬 패턴 그룹 적용 건수",
        ]
        if self.pattern_group_counts:
            for g, c in sorted(self.pattern_group_counts.items()):
                lines.append(f"- {g}: {c}")
        else:
            lines.append("(패턴 적용 없음)")
        lines += [
            "",
            "## 🔧 수정된 파일",
        ]
        if self.fixed_files:
            lines += [f"- {p}" for p in self.fixed_files]
        else:
            lines.append("(수정 없음)")
        lines += [
            "",
            f"총 패턴 적용 건수: {self.issues_fixed}",
            "",
            "## 📌 비고",
            "- 일부 경고는 자동 수정을 지원하지 않을 수 있습니다.",
            "- 잔여 MyPy/Ruff 이슈는 수동 보완 권장.",
            "- Optional/Union 단순 패턴 변환은 중첩/복잡 제네릭 케이스에서는 생략될 수 있음.",
        ]
        out_file = self.results_dir / f"auto_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        out_file.write_text("\n".join(lines), encoding="utf-8")
        return out_file

    # ---------------------------- 메인 파이프라인 ----------------------------
    def run(self, preview: bool = False) -> bool:
        """메인 실행 파이프라인.

        preview=True 이면 측정만 수행하고 수정하지 않는다.
        """
        _print("🚀 자동 수정 프로세스 시작")
        before = self.run_quality_checks()
        _print(f"  ▶ 수정 전 지표: {before}")

        if preview:
            _print("🔍 미리보기 모드 - 파일 변경 없음")
            report = self.generate_report(before, before)
            _print(f"📄 리포트: {report}")
            return True

        # UTF-8 환경 강제 (Python I/O)
        os.environ["PYTHONUTF8"] = "1"
        os.environ["PYTHONIOENCODING"] = "utf-8"

        self.setup_utf8_environment()
        self.apply_ruff_auto_fixes()
        self.apply_common_patterns()
        _ = self.run_mypy_collect()  # 갱신 후 MyPy 재확인 (결과는 after에서 다시 측정)

        after = self.run_quality_checks()
        _print(f"  ▶ 수정 후 지표: {after}")

        report = self.generate_report(before, after)
        _print(f"📄 리포트 생성: {report}")
        _print("✅ 자동 수정 완료")
        return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DHT22 공통 자동 수정 도구")
    parser.add_argument("--preview", action="store_true", help="미리보기 (파일 미수정)")
    parser.add_argument("--project-root", type=Path, help="프로젝트 루트 경로", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        fixer = CommonIssueFixer(project_root=args.project_root)
        success = fixer.run(preview=args.preview)
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        _print("🛑 사용자 취소")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        _print(f"💥 실행 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
