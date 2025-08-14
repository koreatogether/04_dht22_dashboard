# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DHT22 환경 모니터링 시스템 - TruffleHog 보안 스캔 도구
====================================================

DHT22 프로젝트 특화 보안 검사:
 - FastAPI 백엔드 내 하드코딩된 시크릿 키
 - Python 코드 내 데이터베이스 연결 정보  
 - 설정 파일 내 API 키 및 토큰
 - 개인정보 데이터 (센서 위치, 사용자 정보)
 - 네트워크 설정 정보 (IP, 포트, 비밀번호)

작성: DHT22 프로젝트 팀
버전: 3.0.0 (2025-08-14)
"""
import argparse
import json
import subprocess
import sys
import shutil
import re
import platform
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# DHT22 프로젝트 설정
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_NAME = "DHT22 환경 모니터링 시스템"
TRUFFLEHOG_PATH = Path(__file__).with_name("trufflehog.exe")

# 시스템에 설치된 trufflehog 확인
if not TRUFFLEHOG_PATH.exists():
    TRUFFLEHOG_PATH = shutil.which("trufflehog")
    if TRUFFLEHOG_PATH:
        TRUFFLEHOG_PATH = Path(TRUFFLEHOG_PATH)

LOG_DIR = PROJECT_ROOT / "logs" / "security"
LOG_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# DHT22 보안 패턴
DHT22_SENSITIVE_PATTERNS = [
    r'secret.*key',
    r'api.*key', 
    r'auth.*token',
    r'database.*password',
    r'sensor.*location',
    r'device.*location',
    r'user.*info',
    r'personal.*data',
    r'wifi.*password',
    r'admin.*password',
]

DHT22_EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '.git',
    '.venv',
    'logs/*',
    'data/*',
    'temp/*',
    '*.bak',
    '*.tmp',
]

DHT22_CRITICAL_PATHS = [
    'src/python/backend/dht22_main.py',
    'src/python/backend/dht22_dev_server.py',
    'docker-compose.yml',
    '.env*',
    'config*.json',
]

class DHT22ScanResult:
    """DHT22 보안 스캔 결과 관리"""
    
    def __init__(self) -> None:
        self.data: dict[str, Any] = {
            "project": PROJECT_NAME,
            "timestamp": TIMESTAMP,
            "tool": "trufflehog",
            "version": None,
            "platform": platform.system(),
            "project_root": str(PROJECT_ROOT),
            "scans": {},
            "summary": {
                "total_scans": 0,
                "successful_scans": 0,
                "total_findings": 0,
                "critical_findings": 0,
                "privacy_findings": 0,
                "high_risk_files": [],
                "scan_duration": 0.0
            }
        }
        self.any_findings = False
        self.critical_findings = False
        self.privacy_mode = False
        self.start_time = datetime.now()

    def set_privacy_mode(self, enabled: bool) -> None:
        self.privacy_mode = enabled

    def add_scan(self, name: str, success: bool, findings: list[dict[str, Any]], 
                 raw_stdout: str, raw_stderr: str, command: str, duration: float, 
                 target_path: str = "", error: Optional[str] = None) -> None:
        if findings:
            self.any_findings = True
            critical_count = self._analyze_findings_severity(findings, target_path)
            if critical_count > 0:
                self.critical_findings = True
        
        self.data["scans"][name] = {
            "success": success,
            "target_path": target_path,
            "findings_count": len(findings),
            "critical_findings": self._count_critical_findings(findings),
            "privacy_findings": self._count_privacy_findings(findings),
            "findings": findings,
            "command": command,
            "duration_sec": round(duration, 2),
            "error": error,
        }
        
        # 요약 정보 업데이트
        self.data["summary"]["total_scans"] += 1
        if success:
            self.data["summary"]["successful_scans"] += 1
        self.data["summary"]["total_findings"] += len(findings)
        self.data["summary"]["critical_findings"] += self._count_critical_findings(findings)
        self.data["summary"]["privacy_findings"] += self._count_privacy_findings(findings)
        self.data["summary"]["scan_duration"] += duration

    def _analyze_findings_severity(self, findings: list[dict[str, Any]], target_path: str) -> int:
        critical_count = 0
        for finding in findings:
            if any(critical_path in target_path for critical_path in DHT22_CRITICAL_PATHS):
                finding['dht22_severity'] = 'CRITICAL'
                critical_count += 1
                if target_path not in self.data["summary"]["high_risk_files"]:
                    self.data["summary"]["high_risk_files"].append(target_path)
            elif self._matches_dht22_patterns(finding):
                finding['dht22_severity'] = 'HIGH'
                critical_count += 1
            else:
                finding['dht22_severity'] = 'MEDIUM'
        return critical_count

    def _matches_dht22_patterns(self, finding: dict[str, Any]) -> bool:
        text_to_check = str(finding.get('Raw', '')).lower()
        detector_type = str(finding.get('DetectorType', '')).lower()
        
        for pattern in DHT22_SENSITIVE_PATTERNS:
            if re.search(pattern, text_to_check) or re.search(pattern, detector_type):
                return True
        return False

    def _count_critical_findings(self, findings: list[dict[str, Any]]) -> int:
        return sum(1 for f in findings if f.get('dht22_severity') in ['CRITICAL', 'HIGH'])

    def _count_privacy_findings(self, findings: list[dict[str, Any]]) -> int:
        return sum(1 for f in findings if f.get('dht22_severity') == 'PRIVACY_HIGH')

    def set_version(self, version: str) -> None:
        self.data["version"] = version

    def save(self) -> tuple[Path, Path, Path]:
        # JSON 결과 파일
        json_path = LOG_DIR / f"trufflehog_scan_{TIMESTAMP}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        # 텍스트 요약 파일
        txt_path = LOG_DIR / f"trufflehog_summary_{TIMESTAMP}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            self._write_text_summary(f)
        
        # HTML 리포트 파일  
        html_path = LOG_DIR / f"trufflehog_report_{TIMESTAMP}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            self._write_html_report(f)
        
        return json_path, txt_path, html_path

    def _write_text_summary(self, f) -> None:
        f.write(f"{PROJECT_NAME} - TruffleHog 보안 스캔 리포트\n")
        f.write("="*60 + "\n")
        f.write(f"스캔 시간: {TIMESTAMP}\n")
        f.write(f"프로젝트 루트: {self.data.get('project_root')}\n")
        if self.privacy_mode:
            f.write(f"개인정보 보호 모드: 활성화\n")
        f.write("\n")
        
        summary = self.data["summary"]
        f.write("스캔 요약\n")
        f.write(f"총 스캔 수: {summary['total_scans']}\n")
        f.write(f"총 발견 항목: {summary['total_findings']}\n")
        f.write(f"중요 발견 항목: {summary['critical_findings']}\n")
        if self.privacy_mode:
            f.write(f"개인정보 관련 항목: {summary['privacy_findings']}\n")
        
        if self.critical_findings:
            f.write("\n중요: 중대한 보안 위험이 발견되었습니다!\n")
        elif self.any_findings:
            f.write("\n주의: 일부 민감 정보가 발견되었습니다.\n")
        else:
            f.write("\n양호: 민감 정보 노출 징후가 발견되지 않았습니다.\n")

    def _write_html_report(self, f) -> None:
        f.write(f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{PROJECT_NAME} - 보안 스캔 리포트</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ margin: 20px 0; }}
        .card {{ background: #f8f9fa; padding: 15px; margin: 10px; border-radius: 6px; }}
        .success {{ border-left: 4px solid #28a745; }}
        .warning {{ border-left: 4px solid #ffc107; }}
        .critical {{ border-left: 4px solid #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{PROJECT_NAME}</h1>
        <h2>TruffleHog 보안 스캔 리포트</h2>
        <p>스캔 시간: {TIMESTAMP}</p>
    </div>
    
    <div class="summary">
        <div class="card {'critical' if self.data['summary']['total_findings'] > 0 else 'success'}">
            <h3>스캔 결과</h3>
            <p>총 발견 항목: {self.data['summary']['total_findings']}</p>
            <p>중요 항목: {self.data['summary']['critical_findings']}</p>
            {'<p>개인정보 항목: ' + str(self.data['summary']['privacy_findings']) + '</p>' if self.privacy_mode else ''}
        </div>
    </div>
    
    <div class="card {'success' if not self.any_findings else 'critical'}">
        <h3>최종 결론</h3>
        <p>{'✅ DHT22 프로젝트의 보안 상태가 양호합니다.' if not self.any_findings else '⚠️ 보안 검토가 필요합니다.'}</p>
    </div>
</body>
</html>
""")

COLOR = sys.stdout.isatty()

def c(text: str, color_code: str) -> str:
    if not COLOR:
        return text
    return f"\033[{color_code}m{text}\033[0m"

class Runner:
    def __init__(self, timeout: int) -> None:
        self.timeout = timeout

    def run(self, args: list[str]) -> dict[str, Any]:
        import time
        start = time.time()
        try:
            proc = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout, encoding='utf-8', errors='replace')
            duration = time.time() - start
            return {
                'ok': proc.returncode in (0, 1),  # 0=clean, 1=found secrets
                'stdout': proc.stdout,
                'stderr': proc.stderr,
                'returncode': proc.returncode,
                'duration': duration,
            }
        except subprocess.TimeoutExpired:
            return {'ok': False, 'stdout': '', 'stderr': f'timeout after {self.timeout}s', 'returncode': -1, 'duration': self.timeout}
        except Exception as e:
            return {'ok': False, 'stdout': '', 'stderr': str(e), 'returncode': -1, 'duration': 0}

def ensure_trufflehog() -> bool:
    if TRUFFLEHOG_PATH and Path(TRUFFLEHOG_PATH).exists():
        return True
    
    print(c("❌ TruffleHog를 찾을 수 없습니다.", '31'))
    print(c(f"   시도한 경로: {TRUFFLEHOG_PATH}", '90'))
    print(c("📥 설치 방법:", '33'))
    
    if platform.system() == "Windows":
        print(c("   1. https://github.com/trufflesecurity/trufflehog/releases 에서 다운로드", '36'))
        print(c("   2. trufflehog.exe를 tools/git_commit_check/ 폴더에 복사", '36'))
    else:
        print(c("   curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh", '36'))
    
    return False

def detect_version(runner: Runner) -> str:
    result = runner.run([str(TRUFFLEHOG_PATH), '--version'])
    if result['ok']:
        return result['stdout'].strip().splitlines()[0] if result['stdout'].strip() else 'unknown'
    return 'unknown'

def parse_json_lines(output: str) -> list[dict[str, Any]]:
    findings = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                obj = json.loads(line)
                if any(k in obj for k in ('DetectorName','DetectorType','Raw','SourceMetadata')):
                    findings.append(obj)
            except json.JSONDecodeError:
                continue
    return findings

def scan_filesystem(runner: Runner, results: DHT22ScanResult, exclude_patterns: list[str], verbose: bool = False) -> None:
    """파일 시스템 스캔"""
    print(c('🔍 DHT22 프로젝트 파일 시스템 스캔', '34'))
    if verbose:
        print(c(f'   대상: {PROJECT_ROOT}', '90'))
    
    cmd = [str(TRUFFLEHOG_PATH), 'filesystem', '--directory', str(PROJECT_ROOT), '--json', '--no-verification']
    
    for pattern in exclude_patterns:
        cmd.extend(['--exclude-paths', pattern])
    
    run_res = runner.run(cmd)
    findings = parse_json_lines(run_res['stdout']) if run_res['stdout'] else []
    
    results.add_scan('filesystem', run_res['ok'], findings, run_res['stdout'], run_res['stderr'], 
                    ' '.join(cmd), run_res['duration'], target_path=str(PROJECT_ROOT),
                    error=None if run_res['ok'] else run_res['stderr'])
    
    print(c(f"  ➜ 발견 항목: {len(findings)}", '36'))
    if verbose and findings:
        critical_count = sum(1 for f in findings if f.get('dht22_severity') in ['CRITICAL', 'HIGH'])
        print(c(f"  ➜ 중요 항목: {critical_count}", '31' if critical_count > 0 else '36'))

def main() -> int:
    parser = argparse.ArgumentParser(
        description=f'{PROJECT_NAME} - TruffleHog 보안 스캔 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('--filesystem', action='store_true', help='파일 시스템 스캔')
    parser.add_argument('--all', action='store_true', help='모든 기본 스캔 실행')
    parser.add_argument('--fail-on-find', action='store_true', help='민감정보 발견 시 실패 (CI/CD용)')
    parser.add_argument('--timeout', type=int, default=300, help='스캔 최대 시간(초)')
    parser.add_argument('--exclude-patterns', nargs='*', default=DHT22_EXCLUDE_PATTERNS, help='제외할 파일 패턴')
    parser.add_argument('--privacy-mode', action='store_true', help='개인정보 보호 강화 모드')
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 출력')
    parser.add_argument('--no-color', action='store_true', help='컬러 출력 비활성화')
    parser.add_argument('--quiet', '-q', action='store_true', help='최소 출력')
    
    args = parser.parse_args()

    global COLOR
    if args.no_color:
        COLOR = False

    if not ensure_trufflehog():
        print('TruffleHog 설치 후 다시 실행하세요.')
        return 1

    runner = Runner(timeout=args.timeout)
    results = DHT22ScanResult()
    results.set_version(detect_version(runner))
    
    if args.privacy_mode:
        results.set_privacy_mode(True)
        if not args.quiet:
            print(c('🔒 개인정보 보호 강화 모드 활성화', '35'))

    if not args.quiet:
        print(c(f'🚀 {PROJECT_NAME} - TruffleHog 보안 스캔 시작', '32'))
        print(c(f"   프로젝트 루트: {PROJECT_ROOT}", '90'))

    # 기본적으로 파일시스템 스캔 실행
    if args.all or args.filesystem or not any([args.filesystem]):
        scan_filesystem(runner, results, args.exclude_patterns, args.verbose)

    # 결과 저장 및 출력
    json_path, txt_path, html_path = results.save()

    if not args.quiet:
        print(c('\n📄 결과 파일:', '35'))
        print(f"  JSON 리포트: {json_path}")
        print(f"  텍스트 요약: {txt_path}")
        print(f"  HTML 리포트: {html_path}")
        
        summary = results.data['summary']
        print(c('\n📊 스캔 요약:', '35'))
        print(f"  총 스캔 수: {summary['total_scans']}")
        print(f"  총 발견 항목: {summary['total_findings']}")
        print(f"  중요 발견 항목: {summary['critical_findings']}")
        if args.privacy_mode:
            print(f"  개인정보 관련 항목: {summary['privacy_findings']}")

    # 최종 결과 판정
    if results.critical_findings:
        if not args.quiet:
            print(c('\n🚨 중요: 중대한 보안 위험이 발견되었습니다!', '31'))
            print(c('   공개 전에 반드시 해결해야 합니다.', '31'))
        if args.fail_on_find:
            return 2
    elif results.any_findings:
        if not args.quiet:
            print(c('\n⚠️  주의: 일부 민감 정보가 발견되었습니다.', '33'))
            print(c('   검토 후 필요시 조치하세요.', '33'))
        if args.fail_on_find:
            return 1
    else:
        if not args.quiet:
            print(c('\n✅ 양호: 민감 정보 노출 징후가 발견되지 않았습니다.', '32'))
            print(c('   DHT22 프로젝트의 보안 상태가 양호합니다.', '32'))

    return 0

if __name__ == '__main__':
    sys.exit(main())
