#!/usr/bin/env python3
"""
Arduino 코드 메트릭스 분석 도구

이 스크립트는 다음을 수행합니다:
- Arduino 코드 라인 수 분석
- 함수 복잡도 분석
- 메모리 사용량 추정
- 라이브러리 의존성 분석
- 코드 품질 메트릭스
"""

import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json


class ArduinoMetricsAnalyzer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.arduino_path = self.project_root / "src" / "arduino"
        self.reports_dir = self.project_root / "tools" / "metrics" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Arduino 파일들 찾기
        self.arduino_files = list(self.arduino_path.rglob("*.ino"))
        self.cpp_files = list(self.arduino_path.rglob("*.cpp"))
        self.h_files = list(self.arduino_path.rglob("*.h"))
        
        self.all_files = self.arduino_files + self.cpp_files + self.h_files
        
    def analyze_line_metrics(self) -> Dict[str, Any]:
        """라인 수 메트릭스 분석"""
        print("📏 Arduino 라인 수 분석 중...")
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "summary": {
                "total_files": 0,
                "total_lines": 0,
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "preprocessor_lines": 0
            }
        }
        
        for file_path in self.all_files:
            file_metrics = self._analyze_single_file(file_path)
            metrics["files"][str(file_path)] = file_metrics
            
            # 요약에 추가
            metrics["summary"]["total_files"] += 1
            metrics["summary"]["total_lines"] += file_metrics["total_lines"]
            metrics["summary"]["code_lines"] += file_metrics["code_lines"]
            metrics["summary"]["comment_lines"] += file_metrics["comment_lines"]
            metrics["summary"]["blank_lines"] += file_metrics["blank_lines"]
            metrics["summary"]["preprocessor_lines"] += file_metrics["preprocessor_lines"]
        
        print(f"✅ 라인 분석 완료 - {metrics['summary']['total_files']}개 파일")
        return metrics
    
    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """단일 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # UTF-8이 안되면 다른 인코딩 시도
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"⚠️  파일 읽기 오류 {file_path}: {e}")
                return {"error": str(e)}
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "preprocessor_lines": 0,
            "functions": [],
            "includes": [],
            "defines": []
        }
        
        in_multiline_comment = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 빈 줄
            if not stripped:
                metrics["blank_lines"] += 1
                continue
            
            # 멀티라인 주석 처리
            if "/*" in stripped and "*/" in stripped:
                # 한 줄에 시작과 끝이 모두 있는 경우
                metrics["comment_lines"] += 1
                continue
            elif "/*" in stripped:
                in_multiline_comment = True
                metrics["comment_lines"] += 1
                continue
            elif "*/" in stripped:
                in_multiline_comment = False
                metrics["comment_lines"] += 1
                continue
            elif in_multiline_comment:
                metrics["comment_lines"] += 1
                continue
            
            # 단일 라인 주석
            if stripped.startswith("//"):
                metrics["comment_lines"] += 1
                continue
            
            # 전처리기 지시문
            if stripped.startswith("#"):
                metrics["preprocessor_lines"] += 1
                
                # include 분석
                if stripped.startswith("#include"):
                    include_match = re.search(r'#include\s*[<"]([^>"]+)[>"]', stripped)
                    if include_match:
                        metrics["includes"].append(include_match.group(1))
                
                # define 분석
                elif stripped.startswith("#define"):
                    define_match = re.search(r'#define\s+(\w+)', stripped)
                    if define_match:
                        metrics["defines"].append(define_match.group(1))
                continue
            
            # 함수 정의 찾기
            function_match = re.search(r'(\w+\s+)?(\w+)\s*\([^)]*\)\s*\{?', stripped)
            if function_match and not stripped.startswith("if") and not stripped.startswith("while"):
                func_name = function_match.group(2)
                if func_name not in ["if", "while", "for", "switch"]:
                    metrics["functions"].append({
                        "name": func_name,
                        "line": i,
                        "signature": stripped
                    })
            
            # 일반 코드 라인
            metrics["code_lines"] += 1
        
        return metrics
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """코드 복잡도 분석"""
        print("🧮 Arduino 복잡도 분석 중...")
        
        complexity_data = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "summary": {
                "total_functions": 0,
                "avg_complexity": 0,
                "max_complexity": 0,
                "complex_functions": []
            }
        }
        
        total_complexity = 0
        
        for file_path in self.all_files:
            file_complexity = self._analyze_file_complexity(file_path)
            complexity_data["files"][str(file_path)] = file_complexity
            
            for func in file_complexity.get("functions", []):
                complexity_data["summary"]["total_functions"] += 1
                func_complexity = func.get("complexity", 0)
                total_complexity += func_complexity
                
                if func_complexity > complexity_data["summary"]["max_complexity"]:
                    complexity_data["summary"]["max_complexity"] = func_complexity
                
                if func_complexity > 10:  # 복잡도 10 이상은 복잡한 함수
                    complexity_data["summary"]["complex_functions"].append({
                        "file": str(file_path),
                        "function": func["name"],
                        "complexity": func_complexity
                    })
        
        if complexity_data["summary"]["total_functions"] > 0:
            complexity_data["summary"]["avg_complexity"] = total_complexity / complexity_data["summary"]["total_functions"]
        
        print(f"✅ 복잡도 분석 완료 - 평균 복잡도: {complexity_data['summary']['avg_complexity']:.1f}")
        return complexity_data
    
    def _analyze_file_complexity(self, file_path: Path) -> Dict[str, Any]:
        """파일별 복잡도 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                return {"error": str(e)}
        
        # 함수별 복잡도 계산
        functions = []
        
        # 간단한 함수 추출 (정확하지 않지만 근사치)
        function_pattern = r'(\w+\s+)?(\w+)\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        matches = re.finditer(function_pattern, content, re.DOTALL)
        
        for match in matches:
            func_name = match.group(2)
            func_body = match.group(3)
            
            if func_name in ["if", "while", "for", "switch"]:
                continue
            
            # 순환 복잡도 계산 (간단한 버전)
            complexity = 1  # 기본 복잡도
            
            # 조건문 카운트
            complexity += len(re.findall(r'\bif\b', func_body))
            complexity += len(re.findall(r'\belse\b', func_body))
            complexity += len(re.findall(r'\bwhile\b', func_body))
            complexity += len(re.findall(r'\bfor\b', func_body))
            complexity += len(re.findall(r'\bswitch\b', func_body))
            complexity += len(re.findall(r'\bcase\b', func_body))
            complexity += len(re.findall(r'\bcatch\b', func_body))
            complexity += len(re.findall(r'\b&&\b', func_body))
            complexity += len(re.findall(r'\b\|\|\b', func_body))
            
            functions.append({
                "name": func_name,
                "complexity": complexity,
                "lines": len(func_body.split('\n'))
            })
        
        return {"functions": functions}
    
    def analyze_memory_usage(self) -> Dict[str, Any]:
        """메모리 사용량 추정"""
        print("💾 Arduino 메모리 사용량 추정 중...")
        
        memory_data = {
            "timestamp": datetime.now().isoformat(),
            "estimated_flash": 0,
            "estimated_ram": 0,
            "libraries": [],
            "large_arrays": [],
            "string_literals": []
        }
        
        for file_path in self.all_files:
            file_memory = self._estimate_file_memory(file_path)
            memory_data["estimated_flash"] += file_memory["flash"]
            memory_data["estimated_ram"] += file_memory["ram"]
            memory_data["libraries"].extend(file_memory["libraries"])
            memory_data["large_arrays"].extend(file_memory["large_arrays"])
            memory_data["string_literals"].extend(file_memory["string_literals"])
        
        # 중복 제거
        memory_data["libraries"] = list(set(memory_data["libraries"]))
        
        print(f"✅ 메모리 추정 완료 - Flash: ~{memory_data['estimated_flash']}B, RAM: ~{memory_data['estimated_ram']}B")
        return memory_data
    
    def _estimate_file_memory(self, file_path: Path) -> Dict[str, Any]:
        """파일별 메모리 사용량 추정"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception:
                return {"flash": 0, "ram": 0, "libraries": [], "large_arrays": [], "string_literals": []}
        
        memory_data = {
            "flash": 0,
            "ram": 0,
            "libraries": [],
            "large_arrays": [],
            "string_literals": []
        }
        
        # 라이브러리 include 찾기
        includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
        memory_data["libraries"] = includes
        
        # 각 라이브러리의 대략적인 메모리 사용량 (추정)
        library_flash_cost = {
            "DHT.h": 2000,
            "ArduinoJson.h": 8000,
            "WiFi.h": 15000,
            "Ethernet.h": 12000,
            "SoftwareSerial.h": 1500,
            "Wire.h": 1000,
            "SPI.h": 800
        }
        
        for lib in includes:
            memory_data["flash"] += library_flash_cost.get(lib, 500)  # 기본 500바이트
        
        # 큰 배열 찾기
        array_pattern = r'(\w+)\s+(\w+)\s*\[\s*(\d+)\s*\]'
        arrays = re.findall(array_pattern, content)
        
        for array_type, array_name, array_size in arrays:
            size = int(array_size)
            if size > 50:  # 50개 이상의 요소를 가진 배열
                type_size = self._get_type_size(array_type)
                memory_usage = size * type_size
                memory_data["ram"] += memory_usage
                memory_data["large_arrays"].append({
                    "name": array_name,
                    "type": array_type,
                    "size": size,
                    "memory": memory_usage
                })
        
        # 문자열 리터럴 찾기
        string_literals = re.findall(r'"([^"]*)"', content)
        for literal in string_literals:
            if len(literal) > 10:  # 10자 이상의 문자열
                memory_data["ram"] += len(literal) + 1  # null terminator
                memory_data["string_literals"].append(literal)
        
        # 기본 코드 크기 추정 (매우 대략적)
        code_lines = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('//')])
        memory_data["flash"] += code_lines * 4  # 라인당 평균 4바이트 추정
        
        return memory_data
    
    def _get_type_size(self, type_name: str) -> int:
        """데이터 타입별 크기 반환"""
        type_sizes = {
            "char": 1,
            "byte": 1,
            "int": 2,
            "unsigned int": 2,
            "long": 4,
            "unsigned long": 4,
            "float": 4,
            "double": 4,  # Arduino에서는 float와 같음
            "bool": 1,
            "boolean": 1
        }
        return type_sizes.get(type_name.lower(), 4)  # 기본 4바이트
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """의존성 분석"""
        print("📦 Arduino 의존성 분석 중...")
        
        deps_data = {
            "timestamp": datetime.now().isoformat(),
            "libraries": {},
            "custom_includes": [],
            "defines": [],
            "dependency_graph": {}
        }
        
        all_includes = set()
        all_defines = set()
        
        for file_path in self.all_files:
            file_deps = self._analyze_file_dependencies(file_path)
            
            # 라이브러리 정보 수집
            for lib in file_deps["libraries"]:
                if lib not in deps_data["libraries"]:
                    deps_data["libraries"][lib] = {
                        "used_in": [],
                        "type": "external" if lib.endswith(".h") and not lib.startswith("Arduino") else "system"
                    }
                deps_data["libraries"][lib]["used_in"].append(str(file_path))
                all_includes.add(lib)
            
            deps_data["custom_includes"].extend(file_deps["custom_includes"])
            all_defines.update(file_deps["defines"])
            
            deps_data["dependency_graph"][str(file_path)] = file_deps
        
        deps_data["defines"] = list(all_defines)
        deps_data["custom_includes"] = list(set(deps_data["custom_includes"]))
        
        print(f"✅ 의존성 분석 완료 - {len(all_includes)}개 라이브러리")
        return deps_data
    
    def _analyze_file_dependencies(self, file_path: Path) -> Dict[str, Any]:
        """파일별 의존성 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception:
                return {"libraries": [], "custom_includes": [], "defines": []}
        
        # Include 분석
        includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
        
        # 시스템 라이브러리와 커스텀 include 구분
        libraries = []
        custom_includes = []
        
        for include in includes:
            if include.endswith('.h') and ('/' not in include or include.startswith('Arduino')):
                libraries.append(include)
            else:
                custom_includes.append(include)
        
        # Define 분석
        defines = re.findall(r'#define\s+(\w+)', content)
        
        return {
            "libraries": libraries,
            "custom_includes": custom_includes,
            "defines": defines
        }
    
    def generate_comprehensive_report(self, line_metrics: Dict, complexity_data: Dict, 
                                    memory_data: Dict, deps_data: Dict) -> None:
        """종합 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 리포트
        comprehensive_data = {
            "timestamp": datetime.now().isoformat(),
            "project": "DHT22 Arduino Environmental Sensor",
            "line_metrics": line_metrics,
            "complexity": complexity_data,
            "memory": memory_data,
            "dependencies": deps_data,
            "summary": {
                "total_files": line_metrics["summary"]["total_files"],
                "total_lines": line_metrics["summary"]["total_lines"],
                "code_lines": line_metrics["summary"]["code_lines"],
                "total_functions": complexity_data["summary"]["total_functions"],
                "avg_complexity": complexity_data["summary"]["avg_complexity"],
                "estimated_flash": memory_data["estimated_flash"],
                "estimated_ram": memory_data["estimated_ram"],
                "library_count": len(deps_data["libraries"])
            }
        }
        
        json_report = self.reports_dir / f"arduino_metrics_{timestamp}.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        # Markdown 리포트
        md_report = self.reports_dir / f"arduino_metrics_{timestamp}.md"
        self._generate_markdown_report(md_report, comprehensive_data)
        
        print(f"\n📄 Arduino 종합 리포트 생성 완료:")
        print(f"   JSON: {json_report}")
        print(f"   Markdown: {md_report}")
    
    def _generate_markdown_report(self, report_path: Path, data: Dict) -> None:
        """Markdown 리포트 생성"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Arduino 코드 메트릭스 리포트

## 📊 프로젝트 개요
- **프로젝트**: {data['project']}
- **분석 시간**: {data['timestamp']}
- **총 파일 수**: {data['summary']['total_files']}개
- **총 라인 수**: {data['summary']['total_lines']}줄

## 📏 라인 수 통계
- **코드 라인**: {data['summary']['code_lines']}줄
- **주석 라인**: {data['line_metrics']['summary']['comment_lines']}줄
- **빈 라인**: {data['line_metrics']['summary']['blank_lines']}줄
- **전처리기**: {data['line_metrics']['summary']['preprocessor_lines']}줄
- **주석 비율**: {(data['line_metrics']['summary']['comment_lines'] / max(data['summary']['total_lines'], 1) * 100):.1f}%

## 🧮 복잡도 분석
- **총 함수 수**: {data['summary']['total_functions']}개
- **평균 복잡도**: {data['summary']['avg_complexity']:.1f}
- **최대 복잡도**: {data['complexity']['summary']['max_complexity']}
- **복잡한 함수**: {len(data['complexity']['summary']['complex_functions'])}개

## 💾 메모리 사용량 추정
- **Flash 메모리**: ~{data['summary']['estimated_flash']:,}바이트
- **RAM 사용량**: ~{data['summary']['estimated_ram']:,}바이트
- **사용 라이브러리**: {data['summary']['library_count']}개

### 주요 라이브러리
""")
            
            for lib, info in data['dependencies']['libraries'].items():
                f.write(f"- **{lib}**: {len(info['used_in'])}개 파일에서 사용\n")
            
            f.write(f"""
## 🎯 권장사항
""")
            
            # 권장사항 생성
            recommendations = []
            
            if data['summary']['avg_complexity'] > 10:
                recommendations.append("- 평균 복잡도가 높습니다. 함수를 더 작게 분할하는 것을 고려하세요")
            
            if len(data['complexity']['summary']['complex_functions']) > 0:
                recommendations.append(f"- {len(data['complexity']['summary']['complex_functions'])}개의 복잡한 함수가 있습니다. 리팩토링을 고려하세요")
            
            comment_ratio = data['line_metrics']['summary']['comment_lines'] / max(data['summary']['total_lines'], 1) * 100
            if comment_ratio < 15:
                recommendations.append("- 주석 비율을 15% 이상으로 늘리는 것을 권장합니다")
            
            if data['summary']['estimated_flash'] > 20000:
                recommendations.append("- Flash 메모리 사용량이 높습니다. 코드 최적화를 고려하세요")
            
            if data['summary']['estimated_ram'] > 1500:
                recommendations.append("- RAM 사용량이 높습니다. 큰 배열이나 문자열을 최적화하세요")
            
            if not recommendations:
                recommendations.append("- 현재 코드 품질이 우수합니다! 🎉")
            
            for rec in recommendations:
                f.write(f"{rec}\n")


def main():
    """메인 함수"""
    print("🔧 Arduino 코드 메트릭스 분석 시작")
    print("=" * 60)
    
    analyzer = ArduinoMetricsAnalyzer()
    
    if not analyzer.all_files:
        print("❌ Arduino 파일을 찾을 수 없습니다.")
        print(f"   경로 확인: {analyzer.arduino_path}")
        return
    
    print(f"📁 발견된 파일: {len(analyzer.all_files)}개")
    for file_path in analyzer.all_files:
        print(f"   - {file_path}")
    
    # 분석 실행
    line_metrics = analyzer.analyze_line_metrics()
    complexity_data = analyzer.analyze_complexity()
    memory_data = analyzer.analyze_memory_usage()
    deps_data = analyzer.analyze_dependencies()
    
    # 종합 리포트 생성
    analyzer.generate_comprehensive_report(line_metrics, complexity_data, memory_data, deps_data)
    
    print("\n🎉 Arduino 메트릭스 분석 완료!")


if __name__ == "__main__":
    main()