#!/usr/bin/env python3
"""
DHT22 Project Security Scanner Tool
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class SecurityScanner:
    """Scanner to search for project security issues"""

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root)
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "warnings": [],
            "info": [],
        }

        # Security patterns to detect
        self.security_patterns = {
            "hardcoded_secrets": [
                (
                    re.compile(r"password\s*=\s*['\"][^'\"]{3,}['\"]", re.IGNORECASE),
                    "Hardcoded password detected",
                ),
                (
                    re.compile(r"api_key\s*=\s*['\"][^'\"]{10,}['\"]", re.IGNORECASE),
                    "Hardcoded API key detected",
                ),
                (
                    re.compile(r"secret\s*=\s*['\"][^'\"]{10,}['\"]", re.IGNORECASE),
                    "Hardcoded secret detected",
                ),
                (
                    re.compile(r"token\s*=\s*['\"][^'\"]{10,}['\"]", re.IGNORECASE),
                    "Hardcoded token detected",
                ),
            ],
            "sql_injection": [
                (
                    re.compile(r"execute\(['\"].*%s.*['\"]", re.IGNORECASE),
                    "Potential SQL injection vulnerability",
                ),
                (
                    re.compile(r"query\(['\"].*%s.*['\"]", re.IGNORECASE),
                    "Potential SQL injection vulnerability",
                ),
            ],
            "command_injection": [
                (
                    re.compile(r"os\.system\(['\"].*['\"]", re.IGNORECASE),
                    "Command injection risk - use subprocess instead",
                ),
                (
                    re.compile(r"subprocess\.call\(['\"].*['\"]", re.IGNORECASE),
                    "Command injection risk - validate input",
                ),
            ],
            "weak_crypto": [
                (re.compile(r"md5\(", re.IGNORECASE), "Weak hash algorithm MD5 used"),
                (re.compile(r"sha1\(", re.IGNORECASE), "Weak hash algorithm SHA1 used"),
            ],
            "debug_info": [
                (
                    re.compile(r"print\(.*password.*\)", re.IGNORECASE),
                    "Password printed in debug output",
                ),
                (
                    re.compile(r"print\(.*secret.*\)", re.IGNORECASE),
                    "Secret printed in debug output",
                ),
            ],
        }

    def scan_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan a single file for security issues"""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            for category, patterns in self.security_patterns.items():
                for pattern, description in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            issues.append(
                                {
                                    "file": str(
                                        file_path.relative_to(self.project_root)
                                    ),
                                    "line": line_num,
                                    "category": category,
                                    "description": description,
                                    "code": line.strip(),
                                    "severity": self._get_severity(category),
                                }
                            )

        except Exception as e:
            issues.append(
                {
                    "file": str(file_path.relative_to(self.project_root)),
                    "line": 0,
                    "category": "scan_error",
                    "description": f"Failed to scan file: {e}",
                    "code": "",
                    "severity": "info",
                }
            )

        return issues

    def _get_severity(self, category: str) -> str:
        """Get severity level for category"""
        severity_map = {
            "hardcoded_secrets": "high",
            "sql_injection": "high",
            "command_injection": "high",
            "weak_crypto": "medium",
            "debug_info": "low",
        }
        return severity_map.get(category, "medium")

    def scan_project(self) -> dict[str, Any]:
        """Scan entire project for security issues"""
        print("[SECURITY] Starting security scan...")

        # Target directories to scan
        scan_dirs = ["src", "tools", "tests"]

        for dir_name in scan_dirs:
            scan_dir = self.project_root / dir_name
            if scan_dir.exists():
                print(f"Scanning directory: {dir_name}")

                for py_file in scan_dir.rglob("*.py"):
                    # Skip backup files and cache
                    if any(
                        skip in str(py_file)
                        for skip in ["__pycache__", ".backup", "backups"]
                    ):
                        continue

                    issues = self.scan_file(py_file)

                    # Categorize by severity
                    for issue in issues:
                        if issue["severity"] == "high":
                            self.scan_results["vulnerabilities"].append(issue)
                        elif issue["severity"] == "medium":
                            self.scan_results["warnings"].append(issue)
                        else:
                            self.scan_results["info"].append(issue)

        return self.scan_results

    def print_results(self) -> None:
        """Print scan results to console"""
        results = self.scan_results

        print("\n" + "=" * 60)
        print("SECURITY SCAN RESULTS")
        print("=" * 60)

        vuln_count = len(results["vulnerabilities"])
        warn_count = len(results["warnings"])
        info_count = len(results["info"])

        print(f"Vulnerabilities (HIGH): {vuln_count}")
        print(f"Warnings (MEDIUM): {warn_count}")
        print(f"Information (LOW): {info_count}")

        if vuln_count > 0:
            print("\n[HIGH] VULNERABILITIES:")
            for issue in results["vulnerabilities"]:
                print(f"  {issue['file']}:{issue['line']} - {issue['description']}")
                print(f"    Code: {issue['code']}")

        if warn_count > 0:
            print("\n[MEDIUM] WARNINGS:")
            for issue in results["warnings"]:
                print(f"  {issue['file']}:{issue['line']} - {issue['description']}")

        if info_count > 0:
            print("\n[LOW] INFORMATION:")
            for issue in results["info"]:
                print(f"  {issue['file']}:{issue['line']} - {issue['description']}")

        print("\n" + "=" * 60)

        if vuln_count == 0 and warn_count == 0:
            print("No security issues found!")
        else:
            print(f"Total issues: {vuln_count + warn_count + info_count}")

    def save_results(self, output_path: str = None) -> None:
        """Save results to JSON file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"security_scan_results_{timestamp}.json"

        output_file = Path(output_path)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {output_path}")


def main() -> int:
    """Main function"""
    scanner = SecurityScanner(".")
    results = scanner.scan_project()
    scanner.print_results()

    # Save results
    results_dir = Path("tools/quality/results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"security_scan_{timestamp}.json"
    scanner.save_results(str(output_path))

    # Return appropriate exit code
    vuln_count = len(results["vulnerabilities"])
    return 1 if vuln_count > 0 else 0


if __name__ == "__main__":
    exit(main())
