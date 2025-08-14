# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DHT22 프로젝트 보안 스캔 도구
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class SecurityScanner:
    """프로젝트 보안 문제를 검색하는 스캐너"""
    
    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root)
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "warnings": [],
            "info": [],
            "summary": {}
        }
        
        # 보안 패턴 정의
        self.security_patterns = {
            "hardcoded_secrets": [
                (r'password\s*=\s*["\'][^"\']{3,}["\']', "하드코딩된 패스워드"),
                (r'api_key\s*=\s*["\'][^"\']{10,}["\']', "하드코딩된 API 키"),
                (r'secret\s*=\s*["\'][^"\']{8,}["\']', "하드코딩된 시크릿"),
                (r'token\s*=\s*["\'][^"\']{10,}["\']', "하드코딩된 토큰"),
            ],
            "sql_injection": [
                (r'\.execute\s*\(\s*["\'][^"\']*%s[^"\']*["\']', "SQL 인젝션 위험"),
                (r'\.format\s*\([^)]*\)\s*(?=.*SELECT|INSERT|UPDATE|DELETE)', "SQL 포맷 인젝션"),
            ],
            "command_injection": [
                (r'os\.system\s*\([^)]*\+', "명령어 인젝션 위험"),
                (r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', "쉘 인젝션 위험"),
            ],
            "file_operations": [
                (r'open\s*\([^)]*\.\./', "경로 순회 위험"),
                (r'\.write\s*\([^)]*request\.', "사용자 입력 파일 쓰기"),
            ]
        }

    def scan_file(self, file_path: Path) -> None:
        """개별 파일 스캔"""
        try:
            content = file_path.read_text(encoding='utf-8')
            relative_path = file_path.relative_to(self.project_root)
            
            for category, patterns in self.security_patterns.items():
                for pattern, description in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        issue = {
                            "file": str(relative_path),
                            "line": line_num,
                            "category": category,
                            "description": description,
                            "pattern": pattern,
                            "match": match.group(0)[:100],  # 처음 100자만
                            "severity": self._get_severity(category)
                        }
                        
                        if issue["severity"] == "HIGH":
                            self.scan_results["vulnerabilities"].append(issue)
                        elif issue["severity"] == "MEDIUM":
                            self.scan_results["warnings"].append(issue)
                        else:
                            self.scan_results["info"].append(issue)
                            
        except Exception as e:
            self.scan_results["warnings"].append({
                "file": str(file_path),
                "description": f"파일 스캔 실패: {e}",
                "severity": "LOW"
            })

    def _get_severity(self, category: str) -> str:
        """카테고리별 심각도 반환"""
        severity_map = {
            "hardcoded_secrets": "HIGH",
            "sql_injection": "HIGH", 
            "command_injection": "HIGH",
            "file_operations": "MEDIUM"
        }
        return severity_map.get(category, "LOW")

    def scan_project(self) -> dict[str, Any]:
        """프로젝트 전체 스캔"""
        print("🔒 DHT22 프로젝트 보안 스캔 시작...")
        
        python_files = list(self.project_root.rglob("*.py"))
        scanned_files = 0
        
        for file_path in python_files:
            # 가상환경, 캐시 폴더 제외
            if any(exclude in str(file_path) for exclude in [".venv", "__pycache__", ".git"]):
                continue
                
            self.scan_file(file_path)
            scanned_files += 1
            
        print(f"  ✅ {scanned_files}개 Python 파일 스캔 완료")
        
        # 요약 정보 계산
        total_vuln = len(self.scan_results["vulnerabilities"])
        total_warn = len(self.scan_results["warnings"])
        total_info = len(self.scan_results["info"])
        
        if total_vuln > 0:
            risk_level = "HIGH"
        elif total_warn > 0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        self.scan_results["summary"] = {
            "total_files_scanned": scanned_files,
            "total_vulnerabilities": total_vuln,
            "total_warnings": total_warn,
            "total_info": total_info,
            "risk_level": risk_level,
            "scan_completed": True
        }
        
        return self.scan_results

    def print_results(self) -> None:
        """스캔 결과 출력"""
        summary = self.scan_results["summary"]
        
        print("\n🔒 보안 스캔 결과 요약")
        print("=" * 50)
        print(f"   📁 스캔한 파일: {summary['total_files_scanned']}개")
        print(f"   🔴 취약점: {summary['total_vulnerabilities']}개")
        print(f"   🟡 경고: {summary['total_warnings']}개")
        print(f"   🔵 정보: {summary['total_info']}개")
        print(f"   📊 위험 수준: {summary['risk_level']}")
        
        # 상세 결과 출력
        if self.scan_results["vulnerabilities"]:
            print("\n🔴 발견된 취약점:")
            for vuln in self.scan_results["vulnerabilities"]:
                print(f"   📄 {vuln['file']}:{vuln['line']}")
                print(f"      💥 {vuln['description']}")
                print(f"      🔍 패턴: {vuln['match']}")
                
        if self.scan_results["warnings"]:
            print("\n🟡 경고 사항:")
            for warn in self.scan_results["warnings"]:
                print(f"   📄 {warn.get('file', 'N/A')}")
                print(f"      ⚠️  {warn['description']}")
                
        if summary["total_vulnerabilities"] == 0 and summary["total_warnings"] == 0:
            print("\n✅ 심각한 보안 이슈가 발견되지 않았습니다!")
        else:
            print(f"\n⚠️  총 {summary['total_vulnerabilities'] + summary['total_warnings']}개의 보안 이슈를 검토해주세요.")

    def save_results(self, output_file: str = "security_scan_results.json") -> None:
        """결과를 JSON 파일로 저장"""
        output_path = self.project_root / "tools" / "quality" / "results" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
            
        print(f"📄 결과가 {output_path}에 저장되었습니다.")


def main() -> int:
    """메인 함수"""
    scanner = SecurityScanner(".")
    results = scanner.scan_project()
    scanner.print_results()
    
    # 결과 저장
    scanner.save_results()
    
    # 취약점이 있으면 경고 종료 코드 반환
    if results["summary"]["total_vulnerabilities"] > 0:
        print("\n❌ 보안 취약점이 발견되어 주의가 필요합니다.")
        return 1
    else:
        print("\n✅ 보안 스캔이 성공적으로 완료되었습니다.")
        return 0


if __name__ == "__main__":
    exit(main())
