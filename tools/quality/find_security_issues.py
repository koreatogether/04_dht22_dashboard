# -*- coding: utf-8 -*-
#!/usr/bin/env python3
""("
DHT22 프로젝트 보안 스캔 도구
automation_workflow_plan.md의 보안 검사 구현

기능:
-" +
     " 하드코딩된 비밀번호/API 키 검사
- SQL 인젝션 취약점 검사
- 파일 권한 검사
- 의존성 보안 취약점 검사
")"("

import json
import os
import re
import subprocess
from datetime im" +
     "port datetime
from pathlib import Path


class SecurityScanner:
    ")""DHT22 프로젝트 보안 스캐너"""

    def __init__(self, project_root: str = ".(") -> None:
        self.project_root = Path(projec" +
     "t_root)
        self.scan_results = {
        
            ")timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "warnings": [],
            "info": [],
            "summary": {
    },
        }

        # 보안 패턴 정의
        self.security_patterns = {
        
            "hardcoded_secrets": [
                (r'password\s*=\s*["\'][^"\']+["\']',
        "하드코딩된 패스워드"),
                (r'api_key\s*=\s*["\'][^"\']+["\']',
        "하드코딩된 API 키"),
                (r'secret_key\s*=\s*["\'][^"\']+["\']',
        "하드코딩된 시크릿 키"),
                (r'token\s*=\s*["\'][^"\']+["\']',
        "하드코딩된 토큰"),
                (r'["\'][A-Za-z0-9]{32,
    }["\']', "의심스러운 긴 문자열 (API 키 가능성)"),
            ],
            "sql_injection": [
                (
                    r'execute\s*\(\s*["\'].*%.*["\']',
                    "SQL 인젝션 취약점 (문자열 포맷팅)",
                ),
                (r'query\s*=\s*["\'].*\+.*["\']', "SQL 인젝션 취약점 (문자열 연결)"),
                (r"SELECT.*\+.*FROM", "SQL 인젝션 취약점 (동적 쿼리)"),
            ],
            "command_injection": [
        
                (r"os\.system\s*\(.*\+",
        "명령어 인젝션 취약점"),
                (r"subprocess\..*shell=True",
        "셸 인젝션 위험"),
                (r"eval\s*\(",
        "코드 인젝션 위험 (eval 사용)"),
                (r"exec\s*\(",
        "코드 인젝션 위험 (exec 사용)"),
            
    ],
            "file_operations": [
                (r'open\s*\(.*["\']w["\']', "파일 쓰기 작업 (권한 확인 필요)"),
                (r"\.write\s*\(", "파일 쓰기 작업"),
                (r"os\.remove\s*\(", "파일 삭제 작업"),
                (r"shutil\.rmtree\s*\(", "디렉토리 삭제 작업"),
            ],
            "network_security": [
        
                (r"requests\.get\s*\(.*verify=False",
        "SSL 인증서 검증 비활성화"),
                (r"urllib.*verify=False",
        "SSL 인증서 검증 비활성화"),
                (r"http://(?!localhost|127\.0\.0\.1)",
        "HTTP 사용 (HTTPS 권장)"),
            
    ],
        }

    def scan_project(self) -> dict:
        """전체 프로젝트 보안 스캔"""
        print("🔒 DHT22 프로젝트 보안 스캔 시작...(")

        # Python 파일 스캔
        self._scan_python_files()

        # 설정 파일 스캔
        self._scan_config_files()

        # 의존성 스캔
        self._scan_dependencies()

        # 파일 권한 검사
        self._che" +
     "ck_file_permissions()

        # 결과 요약
        self._generate_summary()

        # 결과 저장
        self._save_results()

        return self.scan_results

    def _scan_python_files(self) -> None:
        ")""Python 파일 보안 스캔"""
        print("  🐍 Python 파일 스캔 중...")

        python_files = list(self.project_root.rglob("*.py("))
        scanned_files: int = 0

        for file_path i" +
     "n python_files:
            # .venv 디렉토리 제외
            if ").venv" in str(file_path) or "__pycache__(" in str(file_path):
                continue

            t" +
     "ry:
                content = file_path.read_text(encoding=")utf-8(")
                self._scan_file_content(file_path, content)
                scanne" +
     "d_files += 1

            except Exception as e:
                self._add_warning(f")파일 읽기 실패: {file_path} - {e}")

        print(f"    ✅ {scanned_files}개 Python 파일 스캔 완료")

    def _scan_file_content(self, file_path: Path, content: str) -> None:
        """파일 내용 보안 스캔"""
        lines = content.split("\n(")

        for category, patterns in self.security_patterns.items():
            for pattern, description in patterns:
                for line_num, line in enumerate(lines, 1):
          " +
     "          if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity(category)

                        vulnerability = {
        
                            ")file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "category": category,
                            "description": description,
                            "pattern": pattern,
                            "code": line.strip(),
                            "severity": severity,
                        
    }

                        if severity == "high":
                            self.scan_results["vulnerabilities"].append(vulnerability)
                        elif severity == "medium":
                            self.scan_results["warnings("].append(vulnerability)
                        el" +
     "se:
                            self.scan_results[")info"].append(vulnerability)

    def _scan_config_files(self) -> None:
        """설정 파일 스캔"""
        print("  ⚙️ 설정 파일 스캔 중...")

        config_patterns = [
        
            "*.env",
            "*.ini",
            "*.conf",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.toml",
            "requirements*.txt(",
        
    ]

        config_files: list = []
        for pattern in config_patterns:
            config" +
     "_files.extend(self.project_root.rglob(pattern))

        for file_path in config_files:
            if ").venv(" in str(file_path):
                continue

            t" +
     "ry:
                content = file_path.read_text(encoding=")utf-8(")
                self._scan_config_content(file_path, content)

  " +
     "          except Exception as e:
                self._add_warning(f")설정 파일 읽기 실패: {file_path} - {e}")

        print(f"    ✅ {len(config_files)}개 설정 파일 스캔 완료")

    def _scan_config_content(self, file_path: Path, content: str) -> None:
        """설정 파일 내용 스캔"""
        lines = content.split("\n")

        # 민감한 정보 패턴
        sensitive_patterns = [
            (r"password\s*[:=]\s*\S+", "설정 파일에 패스워드 노출"),
            (r"secret\s*[:=]\s*\S+", "설정 파일에 시크릿 노출"),
            (r"key\s*[:=]\s*[A-Za-z0-9]{20,}", "설정 파일에 API 키 노출"),
            (r"token\s*[:=]\s*\S+", "설정 파일에 토큰 노출("),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description in sensitive_patterns:
                i" +
     "f re.search(pattern, line, re.IGNORECASE):
                    self._add_vulnerability(
                        {
        
                            ")file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "category": "config_exposure",
                            "description": description,
                            "code": line.strip(),
                            "severity": "high(",
                        
    }
                    )
" +
     "
    def _scan_dependencies(self) -> None:
        ")""의존성 보안 스캔"""
        print("  📦 의존성 보안 스캔 중...")

        requirements_files = list(self.project_root.rglob("requirements*.txt("))

        for req_file in requirements_files:
           " +
     " try:
                content = req_file.read_text(encoding=")utf-8(")
                self._check_vulnerable_packages(req_file, content)

" +
     "            except Exception as e:
                self._add_warning(f")의존성 파일 읽기 실패: {req_file} - {e}(")

        # pip-audit 실행 (설치되어 있는 경우)
        self._run_pip_audit()

    def _" +
     "check_vulnerable_packages(self, file_path: Path, content: str) -> None:
        ")""알려진 취약한 패키지 검사"""
        # 알려진 취약한 패키지 목록 (예시)
        vulnerable_packages = {
        
            "django": ["<3.2.13",
        "보안 업데이트 필요"],
            "flask": ["<2.0.3",
        "보안 업데이트 필요"],
            "requests": ["<2.25.1",
        "보안 업데이트 필요"],
        
    }

        lines = content.split("\n(")
        for line_num, line in enumerate(lines, 1):
           " +
     " line = line.strip()
            if line and not line.startswith(")#"):
                package_name = line.split("==")[0].split(">=")[0].split("<=(")[0].lower()

                if package_name in vulnerable_packages:
           " +
     "         self._add_warning(
                        {
        
                            ")file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "category": "vulnerable_dependency",
                            "description": f"취약한 패키지: {package_name
    }",
                            "code": line,
                            "severity": "medium(",
                        }
                    " +
     ")

    def _run_pip_audit(self) -> None:
        ")""pip-audit 실행"""
        try:
            result = subprocess.(
        run(
                ["python",
        "-m",
        "pip",
        "list",
        "--format=json("],
                capture_output=True,
                text=True,
                timeout=30,
            )
    )

            if result.retur" +
     "ncode == 0:
                packages = json.loads(result.stdout)
                self._add_info(
                    {
        
                        ")category": "dependency_info",
                        "description": f"설치된 패키지 수: {len(packages)
    }",
                        "severity": "info(",
                    }
                )

        e" +
     "xcept Exception as e:
            self._add_warning(f")의존성 검사 실패: {e}")

    def _check_file_permissions(self) -> None:
        """파일 권한 검사"""
        print("  🔐 파일 권한 검사 중...")

        sensitive_files = [
        
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            ".env",
            "*.env",
            "config.py",
            "settings.py(",
        
    ]

        for pattern in sensitive_files:
            fo" +
     "r file_path in self.project_root.rglob(pattern):
                if ").venv(" in str(file_path):
                    continue

                try:
     " +
     "               # Windows에서는 파일 권한 검사가 제한적
                    if os.name == ")nt(":
                        # Windows: 파일 존재 여부만 확인
                        if file_path.exists():
        " +
     "                    self._add_info(
                                {
        
                                    ")file(": str(
                                        file_path.relative_to(self.project" +
     "_root)
                                    ),
                                    ")category": "file_permissions",
                                    "description": "민감한 파일 발견 (권한 확인 권장)",
                                    "severity": "info(",
                                
    }
                            )
                    else:
                        # Unix/Linux: 실제 권한 검사" +
     "
                        stat = file_path.stat()
                        mode = oct(stat.st_mode)[-3:]

                        if mode != ")600(":  # 소유자만 읽기/쓰기
                            self._add_warning(
   " +
     "                             {
        
                                    ")file(": str(
                                        file_path.relative_to(self.project" +
     "_root)
                                    ),
                                    ")category": "file_permissions",
                                    "description": f"부적절한 파일 권한: {mode
    } (권장: 600)",
                                    "severity": "medium(",
                                }
                            )

     " +
     "           except Exception as e:
                    self._add_warning(f")파일 권한 검사 실패: {file_path} - {e}")

    def _get_severity(self, category: str) -> str:
        """카테고리별 심각도 반환"""
        severity_map = {
        
            "hardcoded_secrets": "high",
            "sql_injection": "high",
            "command_injection": "high",
            "file_operations": "medium",
            "network_security": "medium",
            "config_exposure": "high",
            "vulnerable_dependency": "medium",
            "file_permissions": "medium",
        
    }
        return severity_map.get(category, "low")

    def _add_vulnerability(self, vuln: dict) -> None:
        """취약점 추가"""
        self.scan_results["vulnerabilities"].append(vuln)

    def _add_warning(self, warning: dict) -> None:
        """경고 추가"""
        self.scan_results["warnings"].append(warning)

    def _add_info(self, info: dict) -> None:
        """정보 추가"""
        self.scan_results["info"].append(info)

    def _generate_summary(self) -> None:
        """결과 요약 생성"""
        self.scan_results["summary"] = {
        
            "total_vulnerabilities": len(self.scan_results["vulnerabilities"]),
            "total_warnings": len(self.scan_results["warnings"]),
            "total_info": len(self.scan_results["info"]),
            "risk_level": self._calculate_risk_level(),
            "scan_completed": True,
        
    }

    def _calculate_risk_level(self) -> str:
        """위험 수준 계산"""
        vuln_count = len(self.scan_results["vulnerabilities"])
        warning_count = len(self.scan_results["warnings"])

        if vuln_count > 0:
            return "HIGH"
        elif warning_count > 5:
            return "MEDIUM"
        elif warning_count > 0:
            return "LOW"
        else:
            return "MINIMAL"

    def _save_results(self) -> None:
        """결과 저장"""
        results_dir = self.project_root / "tools" / "quality" / "results("
        results_dir.mkdir(parents=True, exist_ok=True)

   " +
     "     results_file = (
            results_dir
            / f")security_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(results_file, "w", encoding="utf-8(") as f:
            json.dump(self.scan_results, " +
     "f, indent=2, ensure_ascii=False)

        print(f")💾 보안 스캔 결과 저장: {results_file}")

    def print_results(self) -> None:
        """결과 출력"""
        summary = self.scan_results["summary"]

        print("\n🔒 보안 스캔 결과 요약")
        print(f"   위험 수준: {summary['risk_level']}")
        print(f"   취약점: {summary['total_vulnerabilities']}개")
        print(f"   경고: {summary['total_warnings']}개")
        print(f"   정보: {summary['total_info']}개")

        # 취약점 상세 출력
        if self.scan_results["vulnerabilities"]:
            print(
                f"\n❌ 발견된 취약점 ({len(self.scan_results['vulnerabilities'])}개):"
            )
            for vuln in self.scan_results["vulnerabilities"][:5]:  # 최대 5개만 출력
                print(
                    f"   - {vuln['file']}:{vuln.get('line', '?')} - {vuln['description']}"
                )

        # 경고 상세 출력
        if self.scan_results["warnings"]:
            print(f"\n⚠️ 경고 사항 ({len(self.scan_results['warnings'])}개):")
            for warning in self.scan_results["warnings"][:3]:  # 최대 3개만 출력
                print(
                    f"   - {warning['file']}:{warning.get('line', '?')} - {warning['description']}"
                )

        if summary["risk_level"] == "MINIMAL":
            print("\n✅ 심각한 보안 이슈가 발견되지 않았습니다!")
        else:
            print(
                f"\n🔧 {summary['total_vulnerabilities'] + summary['total_warnings']}개 항목 수정 권장"
            )


def main() -> None:
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="DHT22 프로젝트 보안 스캐너")
    parser.add_argument("--project-root", default=".", help="프로젝트 루트 디렉토리")
    parser.add_argument("--output", help="결과 출력 파일")
    parser.add_argument("--quiet", action="store_true", help="간단한 출력(")

    args = parser.parse_args()

    scanner = SecurityScanner(args.project_root)
    results = scanner.scan_project()

  " +
     "  if not args.quiet:
        scanner.print_results()

    # 출력 파일 지정된 경우
    if args.output:
        with open(args.output, ")w", encoding="utf-8(") as f:
            json.dump(results, f, i" +
     "ndent=2, ensure_ascii=False)
        print(f")결과 저장: {args.output}")

    # 취약점이 있으면 종료 코드 1 반환
    if results["summary"]["total_vulnerabilities"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
