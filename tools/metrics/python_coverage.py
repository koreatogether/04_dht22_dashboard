#!/usr/bin/env python3
"""
Python 코드 커버리지 및 메트릭스 분석 도구

이 스크립트는 다음을 수행합니다:
- 코드 커버리지 측정 (pytest-cov)
- 코드 복잡도 분석 (radon)
- 코드 품질 메트릭스 (pylint)
- 라인 수 통계 (cloc)
- 의존성 분석
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import tempfile


class PythonMetricsAnalyzer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.src_path = self.project_root / "src" / "python"
        self.tools_path = self.project_root / "tools"
        self.tests_path = self.project_root / "tests"
        self.reports_dir = self.project_root / "tools" / "metrics" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 분석할 Python 파일들
        self.python_files = list(self.src_path.rglob("*.py"))
        self.tool_files = list(self.tools_path.rglob("*.py"))
        
    def check_dependencies(self) -> Dict[str, bool]:
        """필요한 도구들이 설치되어 있는지 확인"""
        dependencies = {
            "pytest": False,
            "pytest-cov": False,
            "radon": False,
            "pylint": False,
            "cloc": False
        }
        
        print("🔍 의존성 검사 중...")
        
        # Python 패키지 확인
        for package in ["pytest", "pytest-cov", "radon", "pylint"]:
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {package.replace('-', '_')}"],
                    capture_output=True,
                    text=True
                )
                dependencies[package] = result.returncode == 0
                status = "✅" if dependencies[package] else "❌"
                print(f"  {status} {package}")
            except Exception:
                print(f"  ❌ {package}")
        
        # cloc 확인 (외부 도구)
        try:
            result = subprocess.run(["cloc", "--version"], capture_output=True, text=True)
            dependencies["cloc"] = result.returncode == 0
            print(f"  {'✅' if dependencies['cloc'] else '❌'} cloc")
        except Exception:
            print("  ❌ cloc")
        
        return dependencies
    
    def install_missing_dependencies(self, dependencies: Dict[str, bool]) -> None:
        """누락된 의존성 설치"""
        missing = [pkg for pkg, installed in dependencies.items() if not installed and pkg != "cloc"]
        
        if missing:
            print(f"\n📦 누락된 패키지 설치 중: {', '.join(missing)}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install"
                ] + missing, check=True)
                print("✅ 패키지 설치 완료")
            except subprocess.CalledProcessError as e:
                print(f"❌ 패키지 설치 실패: {e}")
        
        if not dependencies["cloc"]:
            print("\n⚠️  cloc이 설치되지 않았습니다.")
            print("   Windows: choco install cloc")
            print("   Linux: sudo apt-get install cloc")
            print("   macOS: brew install cloc")
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """코드 커버리지 분석 실행"""
        print("\n📊 코드 커버리지 분석 중...")
        
        coverage_data = {
            "timestamp": datetime.now().isoformat(),
            "total_coverage": 0,
            "files": {},
            "missing_lines": {},
            "summary": {}
        }
        
        try:
            # pytest-cov로 커버리지 측정
            cmd = [
                sys.executable, "-m", "pytest",
                "--cov=src/python",
                "--cov-report=json",
                f"--cov-report=json:{self.reports_dir}/coverage.json",
                "--cov-report=html:" + str(self.reports_dir / "coverage_html"),
                "--cov-report=term-missing",
                "tests/",
                "-v"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ 커버리지 분석 완료")
                
                # JSON 리포트 읽기
                coverage_json = self.reports_dir / "coverage.json"
                if coverage_json.exists():
                    with open(coverage_json, 'r') as f:
                        coverage_raw = json.load(f)
                    
                    coverage_data["total_coverage"] = coverage_raw.get("totals", {}).get("percent_covered", 0)
                    coverage_data["files"] = coverage_raw.get("files", {})
                    coverage_data["summary"] = coverage_raw.get("totals", {})
                    
                    print(f"📈 전체 커버리지: {coverage_data['total_coverage']:.1f}%")
                else:
                    print("⚠️  커버리지 JSON 리포트를 찾을 수 없습니다")
            else:
                print(f"❌ 커버리지 분석 실패: {result.stderr}")
                coverage_data["error"] = result.stderr
                
        except Exception as e:
            print(f"❌ 커버리지 분석 오류: {e}")
            coverage_data["error"] = str(e)
        
        return coverage_data
    
    def run_complexity_analysis(self) -> Dict[str, Any]:
        """코드 복잡도 분석 (Radon)"""
        print("\n🧮 코드 복잡도 분석 중...")
        
        complexity_data = {
            "timestamp": datetime.now().isoformat(),
            "cyclomatic_complexity": {},
            "maintainability_index": {},
            "halstead_metrics": {}
        }
        
        try:
            # Cyclomatic Complexity
            cc_cmd = [sys.executable, "-m", "radon", "cc", str(self.src_path), "-j"]
            cc_result = subprocess.run(cc_cmd, capture_output=True, text=True)
            
            if cc_result.returncode == 0:
                complexity_data["cyclomatic_complexity"] = json.loads(cc_result.stdout)
                print("✅ 순환 복잡도 분석 완료")
            
            # Maintainability Index
            mi_cmd = [sys.executable, "-m", "radon", "mi", str(self.src_path), "-j"]
            mi_result = subprocess.run(mi_cmd, capture_output=True, text=True)
            
            if mi_result.returncode == 0:
                complexity_data["maintainability_index"] = json.loads(mi_result.stdout)
                print("✅ 유지보수성 지수 분석 완료")
            
            # Halstead Metrics
            hal_cmd = [sys.executable, "-m", "radon", "hal", str(self.src_path), "-j"]
            hal_result = subprocess.run(hal_cmd, capture_output=True, text=True)
            
            if hal_result.returncode == 0:
                complexity_data["halstead_metrics"] = json.loads(hal_result.stdout)
                print("✅ Halstead 메트릭스 분석 완료")
                
        except Exception as e:
            print(f"❌ 복잡도 분석 오류: {e}")
            complexity_data["error"] = str(e)
        
        return complexity_data
    
    def run_quality_analysis(self) -> Dict[str, Any]:
        """코드 품질 분석 (Pylint)"""
        print("\n🔍 코드 품질 분석 중...")
        
        quality_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "files": {},
            "issues": []
        }
        
        try:
            for py_file in self.python_files:
                if "__pycache__" in str(py_file):
                    continue
                
                cmd = [
                    sys.executable, "-m", "pylint",
                    str(py_file),
                    "--output-format=json",
                    "--disable=C0114,C0115,C0116"  # 문서화 관련 경고 비활성화
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Pylint는 점수가 낮아도 0이 아닌 exit code를 반환할 수 있음
                if result.stdout:
                    try:
                        issues = json.loads(result.stdout)
                        quality_data["files"][str(py_file)] = {
                            "issues": issues,
                            "issue_count": len(issues)
                        }
                        quality_data["issues"].extend(issues)
                    except json.JSONDecodeError:
                        # JSON이 아닌 경우 텍스트로 처리
                        pass
            
            print(f"✅ 품질 분석 완료 - 총 {len(quality_data['issues'])}개 이슈 발견")
            
        except Exception as e:
            print(f"❌ 품질 분석 오류: {e}")
            quality_data["error"] = str(e)
        
        return quality_data
    
    def run_line_count_analysis(self) -> Dict[str, Any]:
        """라인 수 통계 분석 (cloc)"""
        print("\n📏 라인 수 통계 분석 중...")
        
        line_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "by_language": {},
            "by_file": {}
        }
        
        try:
            cmd = ["cloc", str(self.src_path), "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                cloc_data = json.loads(result.stdout)
                line_data["summary"] = cloc_data.get("SUM", {})
                line_data["by_language"] = {
                    k: v for k, v in cloc_data.items() 
                    if k not in ["header", "SUM"]
                }
                print("✅ 라인 수 통계 완료")
                
                # 요약 출력
                summary = line_data["summary"]
                if summary:
                    print(f"📊 총 파일: {summary.get('nFiles', 0)}개")
                    print(f"📊 총 라인: {summary.get('nLines', 0)}줄")
                    print(f"📊 코드 라인: {summary.get('nCode', 0)}줄")
                    print(f"📊 주석 라인: {summary.get('nComment', 0)}줄")
                    print(f"📊 빈 라인: {summary.get('nBlank', 0)}줄")
            else:
                print("⚠️  cloc을 사용할 수 없습니다. 수동 라인 계산을 시도합니다.")
                line_data = self._manual_line_count()
                
        except Exception as e:
            print(f"❌ 라인 수 분석 오류: {e}")
            line_data["error"] = str(e)
            line_data = self._manual_line_count()
        
        return line_data
    
    def _manual_line_count(self) -> Dict[str, Any]:
        """수동 라인 수 계산"""
        line_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"nFiles": 0, "nLines": 0, "nCode": 0, "nComment": 0, "nBlank": 0},
            "by_file": {}
        }
        
        for py_file in self.python_files:
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                total_lines = len(lines)
                code_lines = 0
                comment_lines = 0
                blank_lines = 0
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        blank_lines += 1
                    elif stripped.startswith('#'):
                        comment_lines += 1
                    else:
                        code_lines += 1
                
                file_data = {
                    "nLines": total_lines,
                    "nCode": code_lines,
                    "nComment": comment_lines,
                    "nBlank": blank_lines
                }
                
                line_data["by_file"][str(py_file)] = file_data
                line_data["summary"]["nFiles"] += 1
                line_data["summary"]["nLines"] += total_lines
                line_data["summary"]["nCode"] += code_lines
                line_data["summary"]["nComment"] += comment_lines
                line_data["summary"]["nBlank"] += blank_lines
                
            except Exception as e:
                print(f"⚠️  파일 읽기 오류 {py_file}: {e}")
        
        return line_data
    
    def generate_comprehensive_report(self, coverage_data: Dict, complexity_data: Dict, 
                                    quality_data: Dict, line_data: Dict) -> None:
        """종합 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 리포트
        comprehensive_data = {
            "timestamp": datetime.now().isoformat(),
            "project": "DHT22 Environmental Monitoring",
            "coverage": coverage_data,
            "complexity": complexity_data,
            "quality": quality_data,
            "lines": line_data,
            "summary": {
                "total_coverage": coverage_data.get("total_coverage", 0),
                "total_files": line_data.get("summary", {}).get("nFiles", 0),
                "total_lines": line_data.get("summary", {}).get("nLines", 0),
                "code_lines": line_data.get("summary", {}).get("nCode", 0),
                "quality_issues": len(quality_data.get("issues", [])),
            }
        }
        
        json_report = self.reports_dir / f"python_metrics_{timestamp}.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        # Markdown 리포트
        md_report = self.reports_dir / f"python_metrics_{timestamp}.md"
        self._generate_markdown_report(md_report, comprehensive_data)
        
        print(f"\n📄 종합 리포트 생성 완료:")
        print(f"   JSON: {json_report}")
        print(f"   Markdown: {md_report}")
        if coverage_data.get("total_coverage", 0) > 0:
            print(f"   HTML 커버리지: {self.reports_dir}/coverage_html/index.html")
    
    def _generate_markdown_report(self, report_path: Path, data: Dict) -> None:
        """Markdown 리포트 생성"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Python 코드 메트릭스 리포트

## 📊 프로젝트 개요
- **프로젝트**: {data['project']}
- **분석 시간**: {data['timestamp']}
- **총 파일 수**: {data['summary']['total_files']}개
- **총 라인 수**: {data['summary']['total_lines']}줄

## 📈 커버리지 분석
- **전체 커버리지**: {data['summary']['total_coverage']:.1f}%
- **커버리지 상태**: {'🟢 우수' if data['summary']['total_coverage'] >= 80 else '🟡 보통' if data['summary']['total_coverage'] >= 60 else '🔴 개선 필요'}

## 🧮 코드 복잡도
- **분석 완료**: {'✅' if 'error' not in data['complexity'] else '❌'}

## 🔍 코드 품질
- **품질 이슈**: {data['summary']['quality_issues']}개
- **품질 상태**: {'🟢 우수' if data['summary']['quality_issues'] <= 10 else '🟡 보통' if data['summary']['quality_issues'] <= 50 else '🔴 개선 필요'}

## 📏 라인 수 통계
- **코드 라인**: {data['summary']['code_lines']}줄
- **주석 비율**: {(data['lines']['summary'].get('nComment', 0) / max(data['summary']['total_lines'], 1) * 100):.1f}%

## 🎯 권장사항
""")
            
            # 권장사항 생성
            recommendations = []
            
            if data['summary']['total_coverage'] < 80:
                recommendations.append("- 테스트 커버리지를 80% 이상으로 향상시키세요")
            
            if data['summary']['quality_issues'] > 20:
                recommendations.append("- 코드 품질 이슈를 20개 이하로 줄이세요")
            
            comment_ratio = data['lines']['summary'].get('nComment', 0) / max(data['summary']['total_lines'], 1) * 100
            if comment_ratio < 10:
                recommendations.append("- 주석 비율을 10% 이상으로 늘리세요")
            
            if not recommendations:
                recommendations.append("- 현재 코드 품질이 우수합니다! 🎉")
            
            for rec in recommendations:
                f.write(f"{rec}\n")


def main():
    """메인 함수"""
    print("🐍 Python 코드 메트릭스 및 커버리지 분석 시작")
    print("=" * 60)
    
    analyzer = PythonMetricsAnalyzer()
    
    # 의존성 확인 및 설치
    dependencies = analyzer.check_dependencies()
    analyzer.install_missing_dependencies(dependencies)
    
    # 분석 실행
    coverage_data = analyzer.run_coverage_analysis()
    complexity_data = analyzer.run_complexity_analysis()
    quality_data = analyzer.run_quality_analysis()
    line_data = analyzer.run_line_count_analysis()
    
    # 종합 리포트 생성
    analyzer.generate_comprehensive_report(coverage_data, complexity_data, quality_data, line_data)
    
    print("\n🎉 Python 메트릭스 분석 완료!")


if __name__ == "__main__":
    main()