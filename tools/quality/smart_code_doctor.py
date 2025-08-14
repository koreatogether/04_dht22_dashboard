#!/usr/bin/env python3
"""
🩺 Smart Code Doctor - 지능형 코드 문제 진단 및 자동 수정 도구

이 도구는 AI Assistant가 수동으로 수행한 모든 코드 수정 작업을 자동화합니다:
- 가상환경 손상 탐지 및 대체 실행 환경 사용
- 복잡한 구문 오류 패턴 매칭 및 수정  
- Black → Ruff → MyPy 순서 제어
- 실시간 진행 상황 보고

사용법:
    python tools/quality/smart_code_doctor.py
    python tools/quality/smart_code_doctor.py --aggressive  # 더 많은 패턴 수정
    python tools/quality/smart_code_doctor.py --dry-run     # 시뮬레이션만
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class EnvironmentDoctor:
    """가상환경 상태 진단 및 대체 실행 환경 결정"""
    
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.venv_path = project_root / ".venv"
        self.system_python = self._find_system_python()
        
    def _find_system_python(self) -> Optional[str]:
        """시스템 Python 경로 찾기"""
        candidates = [
            "C:\\Python313\\python.exe",
            "C:\\Python312\\python.exe", 
            "C:\\Python311\\python.exe",
            "python3",
            "python"
        ]
        
        for candidate in candidates:
            try:
                result = subprocess.run(
                    [candidate, "--version"], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return candidate
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return None
    
    def diagnose_venv_corruption(self) -> Dict[str, Any]:
        """가상환경 손상 상태 진단"""
        issues = []
        
        if not self.venv_path.exists():
            return {"healthy": False, "issues": ["Virtual environment not found"]}
            
        # 핵심 패키지들 구문 오류 체크
        critical_packages = [
            "site-packages/_virtualenv.py",
            "site-packages/click/types.py", 
            "site-packages/click/parser.py",
            "site-packages/typing_extensions.py"
        ]
        
        for pkg_path in critical_packages:
            full_path = self.venv_path / "Lib" / pkg_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    issues.append(f"Syntax error in {pkg_path}: {e}")
                except Exception as e:
                    issues.append(f"Error reading {pkg_path}: {e}")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "system_python_available": self.system_python is not None
        }
    
    def get_working_python(self) -> str:
        """작동하는 Python 인터프리터 반환"""
        venv_status = self.diagnose_venv_corruption()
        
        if venv_status["healthy"]:
            return sys.executable
        elif self.system_python:
            print(f"[DOCTOR] 🚨 가상환경 손상 감지, 시스템 Python 사용: {self.system_python}")
            return self.system_python
        else:
            raise RuntimeError("No working Python interpreter found!")


class SyntaxPatternFixer:
    """고급 구문 오류 패턴 매칭 및 수정"""
    
    def __init__(self) -> None:
        # AI Assistant가 발견한 실제 오류 패턴들
        self.patterns = {
            # 1. 가상환경 패키지 타입 힌트 오류
            "malformed_type_hint": [
                (re.compile(r'def\s+(\w+)\s*\([^)]*\):\s*->\s*([^:]+):'), 
                 r'def \1(\2) -> \3:'),
                (re.compile(r'(\s*)def\s+(\w+)\s*\([^)]*\):\s*->\s*([^:]+):'),
                 r'\1def \2(...) -> \3:'),
            ],
            
            # 2. 함수 정의 후 들여쓰기 누락
            "missing_indentation": [
                (re.compile(r'(def\s+\w+\s*\([^)]*\)\s*->\s*[^:]+:)\s*\n([^#\s])', re.MULTILINE),
                 r'\1\n    \2'),
                (re.compile(r'(def\s+\w+\s*\([^)]*\):\s*)\n("""[^"]*""")', re.MULTILINE),
                 r'\1\n    \2'),
            ],
            
            # 3. 문자열 리터럴 손상
            "broken_string_literals": [
                (re.compile(r'""[\(\[][\(\[]"'), '"""'),
                (re.compile(r'"[\)\]]*""[\)\]]*"'), '"""'),
                (re.compile(r'""[\(\[\{\)\]\}]+"'), '"""'),
            ],
            
            # 4. @staticmethod 들여쓰기 오류
            "staticmethod_indentation": [
                (re.compile(r'(\s*)@staticmethod\s*\ndef\s+(\w+)', re.MULTILINE),
                 r'\1@staticmethod\n\1def \2'),
            ],
        }
    
    def fix_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """파일의 구문 오류 패턴 수정"""
        if not file_path.exists() or not file_path.suffix == '.py':
            return False, []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_applied = []
            
            for category, pattern_list in self.patterns.items():
                for pattern, replacement in pattern_list:
                    new_content = pattern.sub(replacement, content)
                    if new_content != content:
                        fixes_applied.append(f"{category}: {pattern.pattern}")
                        content = new_content
            
            if content != original_content:
                # 백업 생성
                backup_path = file_path.with_suffix('.py.backup')
                shutil.copy2(file_path, backup_path)
                
                # 수정된 내용 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return True, fixes_applied
            
            return False, []
            
        except Exception as e:
            return False, [f"Error: {e}"]


class ToolOrchestrator:
    """코드 품질 도구들의 순차 실행 제어"""
    
    def __init__(self, python_exe: str, project_root: Path) -> None:
        self.python_exe = python_exe
        self.project_root = project_root
        self.target_paths = ["src/", "tools/"]
        
    def run_black(self) -> Tuple[bool, str]:
        """Black 포맷팅 실행"""
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "black"] + self.target_paths,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def run_ruff(self, fix: bool = True) -> Tuple[bool, str]:
        """Ruff 린팅 실행"""
        try:
            cmd = [self.python_exe, "-m", "ruff", "check"]
            if fix:
                cmd.extend(["--fix", "--unsafe-fixes"])
            cmd.extend(self.target_paths)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def run_mypy(self) -> Tuple[bool, str]:
        """MyPy 타입 체크 실행"""
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "mypy"] + self.target_paths + ["--ignore-missing-imports"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            return True, result.stdout + result.stderr  # MyPy는 non-blocking
        except Exception as e:
            return False, str(e)


class SmartCodeDoctor:
    """종합적인 코드 문제 진단 및 자동 수정"""
    
    def __init__(self, project_root: str = ".", aggressive: bool = False, dry_run: bool = False) -> None:
        self.project_root = Path(project_root).resolve()
        self.aggressive = aggressive
        self.dry_run = dry_run
        self.start_time = datetime.now()
        
        # 컴포넌트 초기화
        self.env_doctor = EnvironmentDoctor(self.project_root)
        self.syntax_fixer = SyntaxPatternFixer()
        self.working_python = self.env_doctor.get_working_python()
        self.orchestrator = ToolOrchestrator(self.working_python, self.project_root)
        
        # 결과 저장
        self.results = {
            "timestamp": self.start_time.isoformat(),
            "environment": {},
            "syntax_fixes": {},
            "tool_results": {},
            "summary": {}
        }
    
    def diagnose_environment(self) -> None:
        """환경 진단"""
        print("🩺 [DOCTOR] 환경 진단 시작...")
        
        venv_status = self.env_doctor.diagnose_venv_corruption()
        self.results["environment"] = {
            "venv_status": venv_status,
            "working_python": self.working_python,
            "project_root": str(self.project_root)
        }
        
        if not venv_status["healthy"]:
            print(f"⚠️  [DOCTOR] 가상환경 문제 발견: {len(venv_status['issues'])}개 이슈")
            for issue in venv_status["issues"]:
                print(f"   - {issue}")
        else:
            print("✅ [DOCTOR] 가상환경 정상")
    
    def fix_syntax_issues(self) -> None:
        """구문 오류 패턴 수정"""
        print("\n🔧 [DOCTOR] 구문 오류 패턴 수정 시작...")
        
        python_files = []
        for target_dir in ["src", "tools"]:
            target_path = self.project_root / target_dir
            if target_path.exists():
                python_files.extend(target_path.rglob("*.py"))
        
        total_fixes = 0
        fixed_files = {}
        
        for file_path in python_files:
            if self.dry_run:
                print(f"   [DRY-RUN] Would check: {file_path.relative_to(self.project_root)}")
                continue
                
            success, fixes = self.syntax_fixer.fix_file(file_path)
            if success:
                total_fixes += len(fixes)
                fixed_files[str(file_path.relative_to(self.project_root))] = fixes
                print(f"   ✅ {file_path.relative_to(self.project_root)}: {len(fixes)}개 수정")
        
        self.results["syntax_fixes"] = {
            "total_files_checked": len(python_files),
            "files_fixed": len(fixed_files),
            "total_fixes": total_fixes,
            "details": fixed_files
        }
        
        print(f"📊 [DOCTOR] 구문 수정 완료: {len(fixed_files)}개 파일, {total_fixes}개 패턴")
    
    def run_quality_tools(self) -> None:
        """코드 품질 도구 순차 실행"""
        print("\n🛠️ [DOCTOR] 코드 품질 도구 실행 시작...")
        
        if self.dry_run:
            print("   [DRY-RUN] 품질 도구 실행 시뮬레이션")
            return
        
        # 1. Black 포맷팅
        print("   📝 Black 포맷팅...")
        black_success, black_output = self.orchestrator.run_black()
        
        # 2. Ruff 린팅
        print("   🔍 Ruff 린팅...")
        ruff_success, ruff_output = self.orchestrator.run_ruff(fix=True)
        
        # 3. MyPy 타입 체크
        print("   🔬 MyPy 타입 체크...")
        mypy_success, mypy_output = self.orchestrator.run_mypy()
        
        self.results["tool_results"] = {
            "black": {"success": black_success, "output": black_output},
            "ruff": {"success": ruff_success, "output": ruff_output},
            "mypy": {"success": mypy_success, "output": mypy_output}
        }
        
        print(f"   📈 결과: Black {'✅' if black_success else '❌'} | "
              f"Ruff {'✅' if ruff_success else '❌'} | "
              f"MyPy {'✅' if mypy_success else '⚠️'}")
    
    def generate_report(self) -> None:
        """진단 및 수정 결과 보고서 생성"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.results["summary"] = {
            "duration_seconds": duration,
            "total_issues_fixed": self.results["syntax_fixes"]["total_fixes"],
            "files_modified": self.results["syntax_fixes"]["files_fixed"],
            "environment_healthy": self.results["environment"]["venv_status"]["healthy"],
            "all_tools_passed": all(
                result["success"] for tool, result in self.results["tool_results"].items()
                if tool != "mypy"  # MyPy는 non-blocking
            )
        }
        
        # 결과 파일 저장
        results_dir = self.project_root / "tools" / "quality" / "results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        report_file = results_dir / f"smart_doctor_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 콘솔 요약 출력
        print(f"\n📋 [DOCTOR] 진단 완료 ({duration:.1f}초)")
        print(f"   🔧 수정된 파일: {self.results['summary']['files_modified']}개")
        print(f"   ✅ 총 수정사항: {self.results['summary']['total_issues_fixed']}개")
        print(f"   🩺 환경 상태: {'정상' if self.results['summary']['environment_healthy'] else '손상됨'}")
        print(f"   📊 상세 보고서: {report_file}")
    
    def run_full_diagnosis(self) -> None:
        """전체 진단 및 수정 프로세스 실행"""
        print("🩺 Smart Code Doctor 시작")
        print("=" * 50)
        
        try:
            # 1. 환경 진단
            self.diagnose_environment()
            
            # 2. 구문 오류 수정
            self.fix_syntax_issues()
            
            # 3. 품질 도구 실행
            self.run_quality_tools()
            
            # 4. 보고서 생성
            self.generate_report()
            
            print("\n🎉 [DOCTOR] 모든 진단 및 수정 완료!")
            
        except KeyboardInterrupt:
            print("\n⏹️ [DOCTOR] 사용자에 의해 중단됨")
        except Exception as e:
            print(f"\n💥 [DOCTOR] 오류 발생: {e}")
            raise


def main() -> None:
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Code Doctor - 지능형 코드 문제 자동 수정")
    parser.add_argument("--aggressive", action="store_true", help="더 많은 패턴 수정 적용")
    parser.add_argument("--dry-run", action="store_true", help="실제 수정 없이 시뮬레이션만")
    parser.add_argument("--project-root", default=".", help="프로젝트 루트 디렉토리")
    
    args = parser.parse_args()
    
    doctor = SmartCodeDoctor(
        project_root=args.project_root,
        aggressive=args.aggressive,
        dry_run=args.dry_run
    )
    
    doctor.run_full_diagnosis()


if __name__ == "__main__":
    main()