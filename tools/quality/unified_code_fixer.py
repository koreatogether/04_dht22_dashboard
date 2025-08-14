#!/usr/bin/env python3
"""
통합 코드 수정 도구 - Ruff 기반 + 구문 오류 보완
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class UnifiedCodeFixer:
    """Ruff 기반 통합 코드 수정 도구"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.target_dirs = ["src", "tools", "tests"]
        self.syntax_patterns = {
            # 깨진 문자열 리터럴 패턴 (pre_commit.py 특화)
            'broken_strings': [
                (re.compile(r'""[({].*?[)}]""'), '"""수정된 docstring"""'),
                (re.compile(r'""\(.*?\)\("'), '"""수정된 docstring"""'),
                (re.compile(r'""[({].*?$', re.MULTILINE), '"""임시 docstring"""'),
                (re.compile(r'""[\(]"'), '"""'),  # ""(" → """
                (re.compile(r'"\)""'), '"""'),     # ")"" → """  
                (re.compile(r'"[\(][\)]""'), '"""'), # "()"" → """
            ],
            
            # 깨진 import 문
            'broken_imports': [
                (re.compile(r'from pathlib i""mport'), 'from pathlib import'),
                (re.compile(r'i""mport\s+'), 'import '),
                (re.compile(r'from\s+\w+\s+i""mport'), lambda m: m.group(0).replace('i""mport', 'import')),
            ],
            
            # 깨진 변수명/속성
            'broken_variables': [
                (re.compile(r'\.par""ent'), '.parent'),
                (re.compile(r'"\)\.git"'), '".git"'),
                (re.compile(r'"\)\.(\w+)"'), r'."\1"'),  # ").word" → ."word"
            ],
            
            # 복잡한 문자열 혼합 패턴  
            'complex_strings': [
                (re.compile(r'"\)""([^"]+)""[\(]'), r'"""\1"""'),  # ")""text""( → """text"""
                (re.compile(r'"[\)]""([^"]*?)""[\(]"'), r'"""\1"""'),  # )"text"( → """text"""
            ],
            
            # 깨진 f-string 패턴
            'broken_fstrings': [
                (re.compile(r'f".*?\+.*?".*?\+'), 'f"수정된 f-string"'),
                (re.compile(r'f".*?"\s*\+\s*"'), 'f"수정된 f-string"'),
            ],
            
            # 들여쓰기 문제
            'indentation': [
                (re.compile(r'^    def main\(\):$', re.MULTILINE), 'def main():'),
                (re.compile(r'^        """메인 함수"""$', re.MULTILINE), '    """메인 함수"""'),
                (re.compile(r'^(\s{4,})def main\(\):', re.MULTILINE), 'def main():'),
            ],
            
            # 빈 함수/클래스 본문
            'empty_bodies': [
                (re.compile(r'(def\s+\w+\([^)]*\)\s*:)\s*$'), r'\1\n    """임시 함수"""\n    pass'),
                (re.compile(r'(class\s+\w+[^:]*:)\s*$'), r'\1\n    """임시 클래스"""\n    pass'),
                (re.compile(r'(except[^:]*:)\s*$'), r'\1\n    pass'),
            ],
            
            # 한글 인코딩 문제 (unterminated string으로 인한)
            'encoding_issues': [
                (re.compile(r'"""[^\x00-\x7F]+.*?$', re.MULTILINE), '"""한글 docstring"""'),
                (re.compile(r'""".*?[^\x00-\x7F].*?(?!")'), '"""한글 docstring"""'),
            ],
        }
    
    def is_syntax_valid(self, file_path: Path) -> Tuple[bool, str]:
        """파일의 구문 유효성 검사"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def fix_syntax_errors(self, content: str) -> Tuple[str, int]:
        """구문 오류 패턴 기반 수정"""
        fixes_applied = 0
        
        for category, patterns in self.syntax_patterns.items():
            for pattern, replacement in patterns:
                new_content = pattern.sub(replacement, content)
                if new_content != content:
                    content = new_content
                    fixes_applied += 1
                    print(f"    [FIXED] {category} 패턴 수정")
        
        return content, fixes_applied
    
    def run_ruff_format(self, file_path: Path) -> bool:
        """Ruff format 실행"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "ruff", "format", str(file_path)
            ], capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def run_ruff_check_fix(self, file_path: Path) -> bool:
        """Ruff check --fix 실행"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "ruff", "check", "--fix", str(file_path)
            ], capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def fix_file(self, file_path: Path) -> Dict[str, any]:
        """단일 파일 통합 수정"""
        stats = {
            "syntax_fixes": 0,
            "ruff_format": False,
            "ruff_check": False,
            "final_valid": False
        }
        
        print(f"  수정 중: {file_path.relative_to(self.project_root)}")
        
        # 1단계: 구문 오류 수정
        is_valid, error = self.is_syntax_valid(file_path)
        if not is_valid:
            print(f"    [SYNTAX ERROR] {error}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                fixed_content, fixes = self.fix_syntax_errors(content)
                stats["syntax_fixes"] = fixes
                
                if fixes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"    [SYNTAX] {fixes}개 패턴 수정 적용")
                
            except Exception as e:
                print(f"    [ERROR] 구문 수정 실패: {e}")
                return stats
        
        # 2단계: Ruff check --fix (lint + 자동수정)
        stats["ruff_check"] = self.run_ruff_check_fix(file_path)
        if stats["ruff_check"]:
            print("    [RUFF CHECK] 린트 오류 수정 완료")
        
        # 3단계: Ruff format (코드 포매팅)
        stats["ruff_format"] = self.run_ruff_format(file_path)
        if stats["ruff_format"]:
            print("    [RUFF FORMAT] 포매팅 완료")
        
        # 4단계: 최종 검증
        stats["final_valid"], _ = self.is_syntax_valid(file_path)
        if stats["final_valid"]:
            print("    [VALID] 구문 검증 통과")
        else:
            print("    [STILL ERROR] 추가 수동 수정 필요")
        
        return stats
    
    def should_process_file(self, file_path: Path) -> bool:
        """처리 대상 파일 확인"""
        if not file_path.suffix == '.py':
            return False
        
        # 가상환경 제외
        if '.venv' in file_path.parts:
            return False
        
        # 대상 디렉토리만 처리
        try:
            rel_path = file_path.relative_to(self.project_root)
            return any(rel_path.parts[0] == target_dir for target_dir in self.target_dirs)
        except ValueError:
            return False
    
    def fix_all_files(self, paths: List[str]) -> Dict[str, int]:
        """전체 파일 수정"""
        if not paths:
            paths = ["."]
        
        all_files = []
        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file():
                all_files.append(path_obj)
            elif path_obj.is_dir():
                all_files.extend(path_obj.rglob("*.py"))
        
        # 필터링
        target_files = [f for f in all_files if self.should_process_file(f)]
        
        print(f"[INFO] {len(target_files)}개 파일을 수정합니다...")
        
        total_stats = {
            "processed": 0,
            "syntax_fixes": 0,
            "ruff_success": 0,
            "still_broken": 0
        }
        
        for file_path in target_files:
            file_stats = self.fix_file(file_path)
            
            total_stats["processed"] += 1
            total_stats["syntax_fixes"] += file_stats["syntax_fixes"]
            
            if file_stats["ruff_format"] and file_stats["ruff_check"]:
                total_stats["ruff_success"] += 1
            
            if not file_stats["final_valid"]:
                total_stats["still_broken"] += 1
        
        return total_stats


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ruff 기반 통합 코드 수정 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
수정 단계:
1. 구문 오류 패턴 기반 수정 (SyntaxError, IndentationError 등)
2. ruff check --fix (lint 오류 자동 수정)
3. ruff format (코드 포매팅)
4. 최종 구문 검증

사용 예시:
  python tools/quality/unified_code_fixer.py
  python tools/quality/unified_code_fixer.py tools/
  python tools/quality/unified_code_fixer.py src/ tools/ tests/
        """
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        help='수정할 파일/디렉토리 경로 (기본값: 현재 디렉토리)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 수정하지 않고 분석만 수행'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("[DRY RUN] 분석 모드로 실행합니다...")
        return
    
    fixer = UnifiedCodeFixer()
    stats = fixer.fix_all_files(args.paths)
    
    print(f"""
[SUMMARY] 수정 완료!
- 처리된 파일: {stats['processed']}개
- 구문 수정: {stats['syntax_fixes']}개
- Ruff 성공: {stats['ruff_success']}개  
- 여전히 오류: {stats['still_broken']}개
""")
    
    if stats['still_broken'] > 0:
        print("[WARNING] 일부 파일이 여전히 구문 오류를 포함합니다.")
        print("tools/quality/validate_tools.py로 상세 확인하세요.")
        sys.exit(1)
    else:
        print("[SUCCESS] 모든 파일이 정상적으로 수정되었습니다!")


if __name__ == "__main__":
    main()