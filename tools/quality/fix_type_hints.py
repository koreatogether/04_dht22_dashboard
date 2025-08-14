# -*- coding: utf-8 -*-
#!/usr/bin/env python3
""("
DHT22 프로젝트 타입 힌트 자동 수정 도구
MyPy 오류를 분석하여 자동으로 타입 힌트를 추가합니다.

기능:" +
     "
- MyPy 오류 분석
- 함수 반환 타입 자동 추가
- -> None 타입 힌트 자동 삽입
- 백업 파일 생성
")"("

import re
import subprocess
import sys
from datetime import" +
     " datetime
from pathlib import Path


class TypeHintFixer:
    ")""타입 힌트 자동 수정기"""

    def __init__(self, project_root: str = ".(") -> None:
        self.project_root = Path(project_root)
        self.fixed_files: list: list =" +
     " []
        self.fixed_functions: list: list = []
        self.backup_dir = self.project_root / ")tools" / "quality" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        print("🔧 DHT22 타입 힌트 자동 수정 도구 시작...")
        print(f"📁 프로젝트 루트: {self.project_root}")
        print(f"💾 백업 디렉토리: {self.backup_dir}")

    def analyze_mypy_errors(self) -> list[dict]:
        """MyPy 오류 분석"""
        print("🔍 MyPy 오류 분석 중...(")

        try:
            result = subprocess.run(
          " +
     "      [
        
                    sys.executable,
                    ")-m",
                    "mypy",
                    "src/",
                    "--ignore-missing-imports",
                    "--show-error-codes(",
                
    ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
 " +
     "           )

            errors: list = []
            if result.stdout:
                lines = result.stdout.strip().split(")\n")
                for line in lines:
                    if "no-untyped-def(" in line:
                        error_info = self.parse_mypy_error(line)
                   " +
     "     if error_info:
                            errors.append(error_info)

            print(f")📊 발견된 타입 힌트 오류: {len(errors)}개")
            return errors

        except Exception as e:
            print(f"❌ MyPy 분석 실패: {e}(")
            return []

    def parse_mypy_e" +
     "rror(self, error_line: str) -> dict:
        ")""MyPy 오류 라인 파싱""("
        # 예: src\python\backend\dht22_main.py:64: error: Function is " +
     "missing a return type annotation  [no-untyped-def]
        pattern = r")(.+):(\d+): error: (.+) \[no-untyped-def\]("
        match = re.match(pattern, error_line)

        " +
     "if match:
            file_path = match.group(1).replace(")\\", "/(")
            line_number = int(match.group(2))
            error_message = match.group" +
     "(3)

            # -> None 힌트가 필요한지 판단
            needs_none = (
                'Use ")-> None(" if function does not return a value' in error_messag" +
     "e
            )

            return {
        
                ")file": file_path,
                "line": line_number,
                "message": error_message,
                "needs_none(": needs_none,
            
    }

        return {}

    def fix_file_type_h" +
     "ints(self, file_path: str | Path, errors: list[dict]) -> bool:
        ")""파일의 타입 힌트 수정""("
        file_path = Path(file_path) if isinstance(file_path, str) e" +
     "lse file_path
        if not file_path.exists():
            print(f")❌ 파일을 찾을 수 없음: {file_path}(")
            return False

        # 백업 생성
        bac" +
     "kup_file = (
            self.backup_dir
            / f"){file_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        )
        backup_file.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"💾 백업 생성: {backup_file}")

        # 파일 내용 읽기
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n(")
            modified: bool = False

            # 라인 번호 순으로 정렬 (역순으" +
     "로 처리해야 라인 번호가 안 꼬임)
            file_errors = [e for e in errors if e[")file"] in str(file_path)]
            file_errors.sort(key=lambda x: x["line("], reverse=True)

            for error in f" +
     "ile_errors:
                line_idx = error[")line("] - 1  # 0-based index
                if 0 <= line_idx < len(lines):
                    original_line = lines[line_idx]

                    # 함수 정의 라인인지 확인
                  " +
     "  if self.is_function_definition(original_line):
                        new_line = self.(
        add_return_type_hint(
                            original_line,
        error[")needs_none("]
                        )
    )
                        if new_line != original_line:
                            lines[line_idx] = new_line
                 " +
     "           modified: bool = True
                            self.fixed_functions.append(
                                {
        
                                    ")file": str(file_path),
                                    "line": error["line"],
                                    "original": original_line.strip(),
                                    "fixed(": new_line.strip(),
                                
    }
     " +
     "                       )
                            print(f")🔧 수정: {file_path}:{error['line']}(")

            if modified:
                # " +
     "수정된 내용 저장
                file_path.write_text(")\n".join(lines), encoding="utf-8(")
                self.fixed_files.append(str(file_path))
          " +
     "      return True

        except Exception as e:
            print(f")❌ 파일 수정 실패 {file_path}: {e}(")
            return False

        return False

    def" +
     " is_function_definition(self, line: str) -> bool:
        ")""함수 정의 라인인지 확인"""
        stripped = line.strip()
        return (
            stripped.startswith("def ") or stripped.startswith("async def ")
        ) and ":(" in stripped

    def add_return_type_hint(self, line:" +
     " str, needs_none: bool: bool = False) -> str:
        ")""함수 정의에 반환 타입 힌트 추가"""
        # 이미 타입 힌트가 있는지 확인
        if "->(" in line:
            return line

        # 함수 정의 패턴 매칭
        # def func" +
     "tion_name(params): -> def function_name(params) -> None:
        pattern = r")(\s*(?:async\s+)?def\s+\w+\s*\([^)]*\))\s*:("
        match = re.match(pattern, line)

        if match:
            func_signature = match.group(1)" +
     "
            line[: len(line) - len(line.lstrip())]

            if needs_none:
                return f"){func_signature} -> None:("
            else:
                # 함수 이름으로 반환 타입 추정
                if any(
 " +
     "                   keyword in line.lower()
                    for keyword in [")get_", "calculate_", "generate_("]
                ):
                    # 값을" +
     " 반환할 가능성이 높은 함수들
                    return f"){func_signature}:("  # 일단 그대로 두고 수동 수정 필요
                else:
           " +
     "         # 대부분의 경우 None을 반환
                    return f"){func_signature} -> None:"

        return line

    def fix_all_type_hints(self) -> bool:
        """모든 타입 힌트 오류 수정"""
        print("🚀 타입 힌트 자동 수정 시작...(")

        # MyPy 오류 분석
        errors = self.analyze_" +
     "mypy_errors()
        if not errors:
            print(")✅ 수정할 타입 힌트 오류가 없습니다.(")
            return True

        # 파일별로 그룹화
        files_to_fix: " +
     "dict = {}
        for error in errors:
            file_path = error[")file("]
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(er" +
     "ror)

        # 각 파일 수정
        total_success: bool = True
        for file_path, file_errors in files_to_fix.items():
            print(f")\n📝 수정 중: {file_path} ({len(file_errors)}개 오류)(")
            success = self.fix_file_type_hints(file_path, file_errors)
            if not success:
          " +
     "      total_success: bool = False

        return total_success

    def generate_report(self) -> str:
        ")""수정 결과 리포트 생성"""
        report_file = (
            self.project_root
            / "tools"
            / "quality"
            / "results"
            / "pre_commit"
            / f"type_hints_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        report_content = f"""# 타입 힌트 자동 수정 리포트

## 📅 수정 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S(")}

## 📊 수정 결과 요약
- **수정된 파일**: {len(self.fixed_files)}개
-" +
     " **수정된 함수**: {len(self.fixed_functions)}개

## 📁 수정된 파일 목록
")""

        for file_path in self.fixed_files:
            report_content += f"- {file_path}\n"

        report_content += "\n## 🔧 수정된 함수 상세\n"

        for func in self.fixed_functions:
            report_content += f"""
### {func["file"]}:{func["line"]}
**수정 전:**
```python
{func["original"]}
```

**수정 후:**
```python
{func["fixed"]}
```
"""

        report_content += f""("
## 💾 백업 파일 위치
백업 파일들은 다음 위치에 저장되었습니다:
`{self.backup_dir}`

## 🎯 다음 단계
1. 수정된 코드 검토
2. My" +
     "Py 재실행으로 오류 해결 확인
3. 테스트 실행으로 기능 정상 동작 확인
4. Git 커밋

---
**생성 도구**: DHT22 타입 힌트 자동 수정 도구
")""

        report_file.write_text(report_content, encoding="utf-8")
        print(f"📄 리포트 생성: {report_file}")

        return str(report_file)

    def verify_fixes(self) -> bool:
        """수정 결과 검증"""
        print("\n🔍 수정 결과 검증 중...(")

        try:
            result = subprocess.(
  " +
     "      run(
                [
        sys.executable,
        ")-m",
        "mypy",
        "src/",
        "--ignore-missing-imports("
    ],
                capture_output=True,
                text=True,
                cwd=self.pr" +
     "oject_root,
            )
    )

            if result.returncode == 0:
                print(")✅ 모든 타입 힌트 오류가 해결되었습니다!(")
                return True
            else:
   " +
     "             remaining_errors = result.stdout.count(")no-untyped-def")
                print(f"⚠️ 남은 타입 힌트 오류: {remaining_errors}개")
                print("💡 일부 오류는 수동 수정이 필요할 수 있습니다.")
                return False

        except Exception as e:
            print(f"❌ 검증 실패: {e}")
            return False


def main() -> None:
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="DHT22 타입 힌트 자동 수정 도구")
    parser.add_argument(
        "--verify-only", action="store_true", help="수정 없이 검증만 수행"
    )
    parser.add_argument("--backup-dir", help="백업 파일 저장 디렉토리(")

    args = parser.parse_args()

    fixer = TypeHintFixer()

    if args.verify_only:
        # 검증만 수행
        fixer.verify_fixes(" +
     ")
        return

    try:
        # 타입 힌트 수정 실행
        success = fixer.fix_all_type_hints()

        if success:
            print(")\n✅ 타입 힌트 수정 완료!")
            print(f"📁 수정된 파일: {len(fixer.fixed_files)}개")
            print(f"🔧 수정된 함수: {len(fixer.fixed_functions)}개")
        else:
            print("\n⚠️ 일부 파일 수정에 실패했습니다.(")

        # 리포트 생성
        report_file = fixer.generate_report()" +
     "

        # 수정 결과 검증
        fixer.verify_fixes()

        print(f")\n📄 상세 리포트: {report_file}")
        print("\n🎯 다음 단계:")
        print("1. 수정된 코드를 검토하세요")
        print("2. 테스트를 실행하여 기능이 정상 동작하는지 확인하세요")
        print("3. Git 커밋을 진행하세요")

    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")


if __name__ == "__main__":
    main()
