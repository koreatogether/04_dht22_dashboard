#!/usr/bin/env python3
"""
종합적인 Python 구문 오류 수정 도구 (autopep8 + autoflake + pyupgrade 통합)

이 도구는 다음과 같은 구문 오류들을 자동으로 수정합니다:
1. 잘못된 타입 힌트 문법 (def func() -> Type: → def func() -> Type:)
2. 손상된 문자열 리터럴 및 따옴표 문제
3. 들여쓰기 문제
4. 사용되지 않는 import 제거 (autoflake)
5. 코드 스타일 정리 (autopep8)
6. Python 버전 업그레이드 문법 (pyupgrade)
"""

import re
import subprocess
import sys
from pathlib import Path
import argparse


class PythonSyntaxFixer:
    """Python 구문 오류 종합 수정 도구"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.fixed_files: list[str] = []
        self.error_files: list[str] = []
        self.backup_dir = self.project_root / "tools" / "quality" / "backups" / "syntax_fixes"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, file_path: Path) -> None:
        """파일 백업 생성"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"  [BACKUP] 백업 생성: {backup_path}")

    def fix_type_hint_syntax(self, content: str) -> tuple[str, int]:
        """잘못된 타입 힌트 문법 수정: def func() -> Type: → def func() -> Type:"""
        fixes = 0

        # 패턴 1: def function() -> Type:
        pattern1 = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:\s*->\s*([^:]+):'
        def replace1(match):
            nonlocal fixes
            fixes += 1
            func_name = match.group(1)
            full_params = match.group(0).split('): ->')[0] + ')'
            return_type = match.group(2).strip()
            return f"{full_params} -> {return_type}:"

        content = re.sub(pattern1, replace1, content)

        # 패턴 2: async def function() -> Type:
        pattern2 = r'async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:\s*->\s*([^:]+):'
        def replace2(match):
            nonlocal fixes
            fixes += 1
            func_name = match.group(1)
            full_params = match.group(0).split('): ->')[0] + ')'
            return_type = match.group(2).strip()
            return f"{full_params} -> {return_type}:"

        content = re.sub(pattern2, replace2, content)

        return content, fixes

    def fix_string_literals(self, content: str) -> tuple[str, int]:
        """손상된 문자열 리터럴 수정"""
        fixes = 0

        # 패턴: " + 으로 잘못 나뉜 문자열들
        pattern = r'"\s*\+\s*\n\s*\("([^"]+)"\s*\+?\s*'
        def replace_broken_strings(match):
            nonlocal fixes
            fixes += 1
            return f'"{match.group(1)}'

        content = re.sub(pattern, replace_broken_strings, content, flags=re.MULTILINE)

        # 잘못된 따옴표 시퀀스 수정
        content = content.replace('"git"', '"git"')
        content = content.replace('"]', '"]')
        content = content.replace('["', '["')
        content = content.replace('")', '")')

        return content, fixes

    def fix_indentation_errors(self, content: str) -> tuple[str, int]:
        """들여쓰기 오류 수정"""
        fixes = 0
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # class 정의 후 함수가 잘못 들여쓰기된 경우
            if i > 0 and lines[i-1].strip().startswith('class ') and lines[i-1].strip().endswith(':'):
                if line.startswith('def ') and not line.startswith('    def '):
                    fixed_lines.append('    ' + line)
                    fixes += 1
                    continue

            # async def가 잘못 들여쓰기된 경우
            if line.strip().startswith('async def') and not line.startswith('    '):
                # 이전 라인이 class나 함수 내부인지 확인
                if i > 0 and any(prev_line.strip().startswith(('class ', 'def ', 'async def')) for prev_line in lines[max(0, i-3):i]):
                    fixed_lines.append('    ' + line.strip())
                    fixes += 1
                    continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), fixes

    def run_external_tools(self, file_path: Path) -> dict[str, bool]:
        """외부 도구들(autopep8, autoflake, pyupgrade) 실행"""
        results = {}

        # 1. pyupgrade로 Python 문법 업그레이드
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pyupgrade',
                '--py39-plus',  # Python 3.9+ 문법 사용
                str(file_path)
            ], capture_output=True, text=True, cwd=self.project_root)
            results['pyupgrade'] = result.returncode == 0
            if result.returncode != 0:
                print(f"    [WARN] pyupgrade 경고: {result.stderr.strip()}")
        except FileNotFoundError:
            results['pyupgrade'] = False
            print("    [ERROR] pyupgrade가 설치되지 않음")

        # 2. autoflake로 사용되지 않는 import 제거
        try:
            result = subprocess.run([
                sys.executable, '-m', 'autoflake',
                '--in-place',
                '--remove-all-unused-imports',
                '--remove-unused-variables',
                '--remove-duplicate-keys',
                str(file_path)
            ], capture_output=True, text=True, cwd=self.project_root)
            results['autoflake'] = result.returncode == 0
        except FileNotFoundError:
            results['autoflake'] = False
            print("    [ERROR] autoflake가 설치되지 않음")

        # 3. autopep8로 코드 스타일 정리 (구문 오류가 없을 때만)
        try:
            # 먼저 --check로 구문 오류 확인
            check_result = subprocess.run([
                sys.executable, '-c', f'compile(open(r"{file_path}").read(), r"{file_path}", "exec")'
            ], capture_output=True, text=True)

            if check_result.returncode == 0:
                result = subprocess.run([
                    sys.executable, '-m', 'autopep8',
                    '--in-place',
                    '--max-line-length=79',
                    '--aggressive',
                    '--aggressive',
                    str(file_path)
                ], capture_output=True, text=True, cwd=self.project_root)
                results['autopep8'] = result.returncode == 0
            else:
                results['autopep8'] = False
                print(f"    [WARN] autopep8 건너뜀 (구문 오류 존재): {check_result.stderr.strip()}")
        except FileNotFoundError:
            results['autopep8'] = False
            print("    [ERROR] autopep8가 설치되지 않음")

        return results

    def fix_file(self, file_path: Path, create_backup: bool = True) -> bool:
        """단일 파일의 구문 오류 수정"""
        print(f"\n[FIXING] 수정 중: {file_path.relative_to(self.project_root)}")

        try:
            # 원본 파일 읽기
            content = file_path.read_text(encoding='utf-8')
            original_content = content

            if create_backup:
                self.create_backup(file_path)

            total_fixes = 0

            # 1. 타입 힌트 문법 수정
            content, type_fixes = self.fix_type_hint_syntax(content)
            total_fixes += type_fixes
            if type_fixes > 0:
                print(f"  [OK] 타입 힌트 문법 수정: {type_fixes}개")

            # 2. 문자열 리터럴 수정
            content, string_fixes = self.fix_string_literals(content)
            total_fixes += string_fixes
            if string_fixes > 0:
                print(f"  [OK] 문자열 리터럴 수정: {string_fixes}개")

            # 3. 들여쓰기 오류 수정
            content, indent_fixes = self.fix_indentation_errors(content)
            total_fixes += indent_fixes
            if indent_fixes > 0:
                print(f"  [OK] 들여쓰기 수정: {indent_fixes}개")

            # 수정된 내용을 파일에 저장
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"  [SAVE] 파일 저장 완료 (총 {total_fixes}개 수정)")

            # 4. 외부 도구들 실행
            print(f"  [TOOLS] 외부 도구 실행 중...")
            tool_results = self.run_external_tools(file_path)

            success_tools = [tool for tool, success in tool_results.items() if success]
            if success_tools:
                print(f"  [OK] 성공한 도구들: {', '.join(success_tools)}")

            self.fixed_files.append(str(file_path.relative_to(self.project_root)))
            return True

        except Exception as e:
            print(f"  [ERROR] 오류 발생: {e}")
            self.error_files.append(str(file_path.relative_to(self.project_root)))
            return False

    def find_python_files(self, directories: list[str]) -> list[Path]:
        """Python 파일 찾기"""
        python_files = []
        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.is_absolute():
                dir_path = self.project_root / dir_path

            if dir_path.is_file() and dir_path.suffix == '.py':
                python_files.append(dir_path.resolve())
            elif dir_path.is_dir():
                python_files.extend([f.resolve() for f in dir_path.rglob('*.py')])
        return python_files

    def run(self, directories: list[str], dry_run: bool = False) -> None:
        """메인 실행 함수"""
        print(f"[START] Python 구문 오류 수정 도구 시작")
        print(f"[ROOT] 프로젝트 루트: {self.project_root}")
        print(f"[TARGET] 대상 디렉토리: {', '.join(directories)}")

        if dry_run:
            print("[DRY-RUN] DRY RUN 모드: 실제 파일은 수정하지 않습니다")

        python_files = self.find_python_files(directories)
        print(f"[FILES] 발견된 Python 파일: {len(python_files)}개")

        if not python_files:
            print("[ERROR] 수정할 Python 파일이 없습니다")
            return

        # 파일별로 수정 실행
        for file_path in python_files:
            if not dry_run:
                self.fix_file(file_path)
            else:
                print(f"[DRY-RUN] 검사할 파일: {file_path.relative_to(self.project_root)}")

        # 결과 요약
        print(f"\n[SUMMARY] 수정 완료!")
        print(f"[SUCCESS] 성공: {len(self.fixed_files)}개 파일")
        print(f"[FAILED] 실패: {len(self.error_files)}개 파일")

        if self.fixed_files:
            print(f"\n[SUCCESS-LIST] 수정된 파일들:")
            for file in self.fixed_files:
                print(f"  - {file}")

        if self.error_files:
            print(f"\n[ERROR-LIST] 오류 발생 파일들:")
            for file in self.error_files:
                print(f"  - {file}")


def main():
    parser = argparse.ArgumentParser(
        description='Python 구문 오류 종합 수정 도구 (autopep8 + autoflake + pyupgrade)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python fix_syntax_errors_with_autopep8_autoflake_pyupgrade.py src/ tools/
  python fix_syntax_errors_with_autopep8_autoflake_pyupgrade.py --dry-run src/
  python fix_syntax_errors_with_autopep8_autoflake_pyupgrade.py single_file.py
        """
    )

    parser.add_argument(
        'directories',
        nargs='+',
        help='수정할 디렉토리 또는 파일들'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 수정하지 않고 검사만 수행'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='백업 파일 생성하지 않음'
    )

    args = parser.parse_args()

    # 프로젝트 루트 찾기
    current_dir = Path.cwd()
    project_root = current_dir
    while project_root.parent != project_root:
        if (project_root / '.git').exists():
            break
        project_root = project_root.parent

    fixer = PythonSyntaxFixer(project_root)
    fixer.run(args.directories, dry_run=args.dry_run)


if __name__ == "__main__":
    main()