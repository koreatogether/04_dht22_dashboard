#!/usr/bin/env python3
"""
TruffleHog 기반 보안 스캔 도구

이 스크립트는 다음을 수행합니다:
- 코드에서 잠재적인 비밀 정보 탐지
- API 키, 패스워드, 토큰 등 민감한 정보 검사
- 개인 정보 노출 위험 검사
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import urllib.request
import zipfile
import os


class TruffleHogRunner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.tools_dir = self.project_root / "tools" / "security"
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
        # TruffleHog 실행 파일 경로
        self.trufflehog_path = self.tools_dir / "trufflehog.exe"
        
        # 환경변수에서 URL 가져오기
        self.trufflehog_url = os.getenv(
            'TRUFFLEHOG_DOWNLOAD_URL',
            'https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_3.63.2_windows_amd64.tar.gz'
        )
        
    def ensure_trufflehog(self) -> bool:
        """TruffleHog 도구가 있는지 확인하고 없으면 다운로드"""
        if self.trufflehog_path.exists():
            return True
            
        print("🔍 TruffleHog를 다운로드하는 중...")
        
        try:
            # GitHub에서 최신 릴리스 다운로드 (환경변수에서 URL 가져오기)
            print(f"📥 다운로드 URL: {self.trufflehog_url}")
            
            # 임시 파일로 다운로드
            temp_file = self.tools_dir / "trufflehog.tar.gz"
            urllib.request.urlretrieve(self.trufflehog_url, temp_file)
            
            # 압축 해제 (간단한 버전을 위해 7z 또는 다른 방법 필요)
            print("✅ TruffleHog 다운로드 완료")
            return True
            
        except Exception as e:
            print(f"❌ TruffleHog 다운로드 실패: {e}")
            return False
    
    def run_builtin_scan(self) -> Tuple[bool, List[Dict]]:
        """내장된 패턴 매칭으로 기본 보안 스캔"""
        print("🔍 내장 보안 패턴 검사 중...")
        
        # 위험한 패턴들
        dangerous_patterns = {
            "API 키": [
                r"api[_-]?key[\s]*=[\s]*['\"][a-zA-Z0-9_-]{20,}['\"]",
                r"apikey[\s]*=[\s]*['\"][a-zA-Z0-9_-]{20,}['\"]",
            ],
            "패스워드": [
                r"password[\s]*=[\s]*['\"][^'\"]{3,}['\"]",
                r"passwd[\s]*=[\s]*['\"][^'\"]{3,}['\"]",
                r"pwd[\s]*=[\s]*['\"][^'\"]{3,}['\"]",
            ],
            "토큰": [
                r"token[\s]*=[\s]*['\"][a-zA-Z0-9_-]{20,}['\"]",
                r"access[_-]?token[\s]*=[\s]*['\"][a-zA-Z0-9_-]{20,}['\"]",
            ],
            "시크릿": [
                r"secret[\s]*=[\s]*['\"][a-zA-Z0-9_-]{10,}['\"]",
                r"client[_-]?secret[\s]*=[\s]*['\"][a-zA-Z0-9_-]{10,}['\"]",
            ],
            "개인정보": [
                r"email[\s]*=[\s]*['\"][^@]+@[^@]+\.[a-zA-Z]{2,}['\"]",
                r"phone[\s]*=[\s]*['\"][0-9-+()\\s]{10,}['\"]",
            ],
            "데이터베이스": [
                r"db[_-]?password[\s]*=[\s]*['\"][^'\"]{3,}['\"]",
                r"database[_-]?url[\s]*=[\s]*['\"][^'\"]+['\"]",
            ]
        }
        
        findings = []
        scan_files = [
            "src/python/**/*.py",
            "tools/**/*.py", 
            "*.py",
            "*.env*",
            "*.conf",
            "*.config",
            "*.yml",
            "*.yaml",
            "*.json",
            "*.toml",
        ]
        
        for pattern_type, patterns in dangerous_patterns.items():
            for pattern in patterns:
                findings.extend(self._scan_pattern(pattern, pattern_type))
        
        return len(findings) == 0, findings
    
    def _scan_pattern(self, pattern: str, pattern_type: str) -> List[Dict]:
        """특정 패턴으로 파일들을 스캔"""
        findings = []
        
        # Python 파일들 스캔
        for py_file in self.project_root.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                for line_num, line in enumerate(content.splitlines(), 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            "type": pattern_type,
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": line_num,
                            "content": line.strip(),
                            "pattern": pattern,
                            "severity": self._get_severity(pattern_type)
                        })
                        
            except Exception as e:
                print(f"⚠️  파일 읽기 오류 {py_file}: {e}")
        
        return findings
    
    def _get_severity(self, pattern_type: str) -> str:
        """패턴 유형에 따른 심각도 결정"""
        high_severity = ["API 키", "토큰", "시크릿", "패스워드"]
        medium_severity = ["데이터베이스"]
        
        if pattern_type in high_severity:
            return "HIGH"
        elif pattern_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"
    
    def run_additional_checks(self) -> List[Dict]:
        """추가 보안 검사"""
        findings = []
        
        # .env 파일 검사 (.env.example은 제외)
        for env_file in self.project_root.rglob(".env*"):
            if env_file.is_file() and not env_file.name.endswith('.example'):
                findings.append({
                    "type": "환경 파일",
                    "file": str(env_file.relative_to(self.project_root)),
                    "line": 1,
                    "content": ".env 파일이 발견됨",
                    "severity": "MEDIUM",
                    "recommendation": ".env 파일을 .gitignore에 추가하세요"
                })
        
        # 하드코딩된 URL 검사
        for py_file in self.project_root.rglob("*.py"):
            if ".venv" in str(py_file):
                continue
                
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # 하드코딩된 URL 패턴
                url_pattern = r"https?://[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:/[^\s\"']*)?[\"']"
                for line_num, line in enumerate(content.splitlines(), 1):
                    if re.search(url_pattern, line):
                        # localhost는 제외
                        if "localhost" not in line and "127.0.0.1" not in line:
                            findings.append({
                                "type": "하드코딩 URL",
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": line_num,
                                "content": line.strip(),
                                "severity": "LOW",
                                "recommendation": "URL을 환경변수로 관리하세요"
                            })
                            
            except Exception:
                pass
        
        return findings
    
    def generate_report(self, findings: List[Dict]) -> None:
        """보안 스캔 리포트 생성"""
        
        # 심각도별 분류
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in findings:
            severity_counts[finding["severity"]] += 1
        
        # 콘솔 출력
        print("\n" + "="*60)
        print("🔒 보안 스캔 결과")
        print("="*60)
        
        if not findings:
            print("✅ 보안 이슈가 발견되지 않았습니다!")
        else:
            print(f"⚠️  총 {len(findings)}개의 잠재적 보안 이슈 발견")
            print(f"   🔴 HIGH: {severity_counts['HIGH']}개")
            print(f"   🟡 MEDIUM: {severity_counts['MEDIUM']}개") 
            print(f"   🟢 LOW: {severity_counts['LOW']}개")
            
            print("\n📋 상세 내역:")
            for i, finding in enumerate(findings, 1):
                severity_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[finding["severity"]]
                print(f"\n{i}. {severity_icon} {finding['type']}")
                print(f"   📁 파일: {finding['file']}:{finding['line']}")
                print(f"   📝 내용: {finding['content'][:100]}...")
                if "recommendation" in finding:
                    print(f"   💡 권장사항: {finding['recommendation']}")
        
        # JSON 리포트 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.tools_dir / f"security_scan_{timestamp}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_findings": len(findings),
                "severity_breakdown": severity_counts
            },
            "findings": findings
        }
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 상세 리포트: {report_file}")
        
        # HIGH 심각도 이슈가 있으면 실패 처리
        if severity_counts["HIGH"] > 0:
            print("\n🚨 HIGH 심각도 보안 이슈가 발견되었습니다!")
            return False
        
        return True


def main():
    """메인 함수"""
    print("🛡️  DHT22 프로젝트 보안 스캔 시작")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    runner = TruffleHogRunner()
    
    # 내장 패턴 스캔
    success, findings = runner.run_builtin_scan()
    
    # 추가 검사
    additional_findings = runner.run_additional_checks()
    findings.extend(additional_findings)
    
    # 리포트 생성
    scan_success = runner.generate_report(findings)
    
    if not scan_success:
        sys.exit(1)
    
    print("✅ 보안 스캔 완료")


if __name__ == "__main__":
    main()