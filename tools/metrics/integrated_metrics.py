#!/usr/bin/env python3
"""
통합 메트릭스 관리 시스템

Python과 Arduino 코드의 메트릭스를 통합 분석하고 관리합니다.
- 전체 프로젝트 메트릭스 대시보드
- 시간별 메트릭스 추이 분석
- 품질 목표 대비 현황 추적
- 자동화된 리포트 생성
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import pandas as pd


class IntegratedMetricsManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.metrics_dir = self.project_root / "tools" / "metrics"
        self.reports_dir = self.metrics_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 품질 목표 설정
        self.quality_targets = {
            "python": {
                "coverage": 80.0,  # 80% 이상
                "quality_issues": 20,  # 20개 이하
                "comment_ratio": 10.0,  # 10% 이상
                "max_complexity": 10  # 함수당 복잡도 10 이하
            },
            "arduino": {
                "comment_ratio": 15.0,  # 15% 이상
                "avg_complexity": 8.0,  # 평균 복잡도 8 이하
                "max_flash": 25000,  # 25KB 이하
                "max_ram": 1500  # 1.5KB 이하
            }
        }
    
    def run_all_analyses(self) -> Dict[str, Any]:
        """모든 메트릭스 분석 실행"""
        print("🚀 통합 메트릭스 분석 시작")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "python": None,
            "arduino": None,
            "integration": {}
        }
        
        # Python 메트릭스 실행
        print("\n🐍 Python 메트릭스 분석 실행 중...")
        try:
            python_result = subprocess.run([
                sys.executable, str(self.metrics_dir / "python_coverage.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if python_result.returncode == 0:
                print("✅ Python 분석 완료")
                results["python"] = self._load_latest_python_report()
            else:
                print(f"❌ Python 분석 실패: {python_result.stderr}")
                results["python"] = {"error": python_result.stderr}
        except Exception as e:
            print(f"❌ Python 분석 오류: {e}")
            results["python"] = {"error": str(e)}
        
        # Arduino 메트릭스 실행
        print("\n🔧 Arduino 메트릭스 분석 실행 중...")
        try:
            arduino_result = subprocess.run([
                sys.executable, str(self.metrics_dir / "arduino_metrics.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if arduino_result.returncode == 0:
                print("✅ Arduino 분석 완료")
                results["arduino"] = self._load_latest_arduino_report()
            else:
                print(f"❌ Arduino 분석 실패: {arduino_result.stderr}")
                results["arduino"] = {"error": arduino_result.stderr}
        except Exception as e:
            print(f"❌ Arduino 분석 오류: {e}")
            results["arduino"] = {"error": str(e)}
        
        # 통합 분석
        results["integration"] = self._perform_integration_analysis(results)
        
        return results
    
    def _load_latest_python_report(self) -> Optional[Dict]:
        """최신 Python 리포트 로드"""
        python_reports = list(self.reports_dir.glob("python_metrics_*.json"))
        if not python_reports:
            return None
        
        latest_report = max(python_reports, key=lambda x: x.stat().st_mtime)
        try:
            with open(latest_report, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Python 리포트 로드 실패: {e}")
            return None
    
    def _load_latest_arduino_report(self) -> Optional[Dict]:
        """최신 Arduino 리포트 로드"""
        arduino_reports = list(self.reports_dir.glob("arduino_metrics_*.json"))
        if not arduino_reports:
            return None
        
        latest_report = max(arduino_reports, key=lambda x: x.stat().st_mtime)
        try:
            with open(latest_report, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Arduino 리포트 로드 실패: {e}")
            return None
    
    def _perform_integration_analysis(self, results: Dict) -> Dict[str, Any]:
        """통합 분석 수행"""
        integration = {
            "project_health": "unknown",
            "quality_score": 0,
            "recommendations": [],
            "achievements": [],
            "total_lines": 0,
            "total_files": 0,
            "language_distribution": {}
        }
        
        python_data = results.get("python")
        arduino_data = results.get("arduino")
        
        # 전체 통계 계산
        if python_data and "summary" in python_data:
            py_summary = python_data["summary"]
            integration["total_lines"] += py_summary.get("total_lines", 0)
            integration["total_files"] += py_summary.get("total_files", 0)
            integration["language_distribution"]["Python"] = {
                "lines": py_summary.get("code_lines", 0),
                "files": py_summary.get("total_files", 0)
            }
        
        if arduino_data and "summary" in arduino_data:
            ard_summary = arduino_data["summary"]
            integration["total_lines"] += ard_summary.get("total_lines", 0)
            integration["total_files"] += ard_summary.get("total_files", 0)
            integration["language_distribution"]["Arduino"] = {
                "lines": ard_summary.get("code_lines", 0),
                "files": ard_summary.get("total_files", 0)
            }
        
        # 품질 점수 계산
        quality_score = 0
        max_score = 0
        
        # Python 품질 평가
        if python_data and "summary" in python_data:
            py_summary = python_data["summary"]
            targets = self.quality_targets["python"]
            
            # 커버리지 점수 (25점)
            coverage = py_summary.get("total_coverage", 0)
            if coverage >= targets["coverage"]:
                quality_score += 25
                integration["achievements"].append(f"Python 커버리지 목표 달성: {coverage:.1f}%")
            else:
                quality_score += (coverage / targets["coverage"]) * 25
                integration["recommendations"].append(f"Python 커버리지를 {targets['coverage']}%까지 향상시키세요 (현재: {coverage:.1f}%)")
            max_score += 25
            
            # 품질 이슈 점수 (25점)
            issues = py_summary.get("quality_issues", 0)
            if issues <= targets["quality_issues"]:
                quality_score += 25
                integration["achievements"].append(f"Python 품질 이슈 목표 달성: {issues}개")
            else:
                quality_score += max(0, (targets["quality_issues"] - issues) / targets["quality_issues"] * 25)
                integration["recommendations"].append(f"Python 품질 이슈를 {targets['quality_issues']}개 이하로 줄이세요 (현재: {issues}개)")
            max_score += 25
        
        # Arduino 품질 평가
        if arduino_data and "summary" in arduino_data:
            ard_summary = arduino_data["summary"]
            targets = self.quality_targets["arduino"]
            
            # 복잡도 점수 (25점)
            avg_complexity = ard_summary.get("avg_complexity", 0)
            if avg_complexity <= targets["avg_complexity"]:
                quality_score += 25
                integration["achievements"].append(f"Arduino 복잡도 목표 달성: {avg_complexity:.1f}")
            else:
                quality_score += max(0, (targets["avg_complexity"] - avg_complexity) / targets["avg_complexity"] * 25)
                integration["recommendations"].append(f"Arduino 평균 복잡도를 {targets['avg_complexity']} 이하로 줄이세요 (현재: {avg_complexity:.1f})")
            max_score += 25
            
            # 메모리 사용량 점수 (25점)
            flash_usage = ard_summary.get("estimated_flash", 0)
            if flash_usage <= targets["max_flash"]:
                quality_score += 25
                integration["achievements"].append(f"Arduino Flash 메모리 목표 달성: {flash_usage:,}B")
            else:
                quality_score += max(0, (targets["max_flash"] - flash_usage) / targets["max_flash"] * 25)
                integration["recommendations"].append(f"Arduino Flash 사용량을 {targets['max_flash']:,}B 이하로 줄이세요 (현재: {flash_usage:,}B)")
            max_score += 25
        
        # 최종 품질 점수 계산
        if max_score > 0:
            integration["quality_score"] = (quality_score / max_score) * 100
        
        # 프로젝트 건강도 평가
        if integration["quality_score"] >= 90:
            integration["project_health"] = "excellent"
        elif integration["quality_score"] >= 75:
            integration["project_health"] = "good"
        elif integration["quality_score"] >= 60:
            integration["project_health"] = "fair"
        else:
            integration["project_health"] = "needs_improvement"
        
        return integration
    
    def generate_dashboard_report(self, results: Dict) -> None:
        """대시보드 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 리포트
        json_report = self.reports_dir / f"integrated_metrics_{timestamp}.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Markdown 대시보드
        md_report = self.reports_dir / f"metrics_dashboard_{timestamp}.md"
        self._generate_dashboard_markdown(md_report, results)
        
        # 시각화 차트 생성 (matplotlib 사용 가능한 경우)
        try:
            self._generate_charts(results, timestamp)
        except ImportError:
            print("⚠️  matplotlib를 설치하면 시각화 차트를 생성할 수 있습니다: pip install matplotlib")
        except Exception as e:
            print(f"⚠️  차트 생성 실패: {e}")
        
        print(f"\n📊 통합 대시보드 생성 완료:")
        print(f"   JSON: {json_report}")
        print(f"   Dashboard: {md_report}")
    
    def _generate_dashboard_markdown(self, report_path: Path, results: Dict) -> None:
        """대시보드 Markdown 생성"""
        integration = results.get("integration", {})
        python_data = results.get("python")
        arduino_data = results.get("arduino")
        
        health_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "fair": "🟠",
            "needs_improvement": "🔴",
            "unknown": "⚪"
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# 📊 DHT22 프로젝트 메트릭스 대시보드

## 🎯 프로젝트 건강도
- **전체 품질 점수**: {integration.get('quality_score', 0):.1f}/100
- **프로젝트 상태**: {health_emoji.get(integration.get('project_health', 'unknown'), '⚪')} {integration.get('project_health', 'unknown').replace('_', ' ').title()}
- **분석 시간**: {results.get('timestamp', 'N/A')}

## 📈 전체 통계
- **총 파일 수**: {integration.get('total_files', 0)}개
- **총 라인 수**: {integration.get('total_lines', 0):,}줄

### 언어별 분포
""")
            
            for lang, stats in integration.get("language_distribution", {}).items():
                f.write(f"- **{lang}**: {stats['files']}개 파일, {stats['lines']:,}줄\n")
            
            f.write(f"""
## 🐍 Python 메트릭스
""")
            
            if python_data and "summary" in python_data:
                py_summary = python_data["summary"]
                f.write(f"""- **커버리지**: {py_summary.get('total_coverage', 0):.1f}%
- **품질 이슈**: {py_summary.get('quality_issues', 0)}개
- **코드 라인**: {py_summary.get('code_lines', 0):,}줄
- **파일 수**: {py_summary.get('total_files', 0)}개
""")
            else:
                f.write("- ❌ Python 분석 데이터 없음\n")
            
            f.write(f"""
## 🔧 Arduino 메트릭스
""")
            
            if arduino_data and "summary" in arduino_data:
                ard_summary = arduino_data["summary"]
                f.write(f"""- **평균 복잡도**: {ard_summary.get('avg_complexity', 0):.1f}
- **Flash 메모리**: ~{ard_summary.get('estimated_flash', 0):,}바이트
- **RAM 사용량**: ~{ard_summary.get('estimated_ram', 0):,}바이트
- **함수 수**: {ard_summary.get('total_functions', 0)}개
- **라이브러리**: {ard_summary.get('library_count', 0)}개
""")
            else:
                f.write("- ❌ Arduino 분석 데이터 없음\n")
            
            f.write(f"""
## 🏆 달성 사항
""")
            
            achievements = integration.get("achievements", [])
            if achievements:
                for achievement in achievements:
                    f.write(f"- ✅ {achievement}\n")
            else:
                f.write("- 아직 달성한 목표가 없습니다.\n")
            
            f.write(f"""
## 🎯 개선 권장사항
""")
            
            recommendations = integration.get("recommendations", [])
            if recommendations:
                for rec in recommendations:
                    f.write(f"- 🔧 {rec}\n")
            else:
                f.write("- 🎉 모든 품질 목표를 달성했습니다!\n")
            
            f.write(f"""
## 📊 품질 목표
### Python
- 커버리지: {self.quality_targets['python']['coverage']}% 이상
- 품질 이슈: {self.quality_targets['python']['quality_issues']}개 이하
- 주석 비율: {self.quality_targets['python']['comment_ratio']}% 이상

### Arduino
- 평균 복잡도: {self.quality_targets['arduino']['avg_complexity']} 이하
- Flash 메모리: {self.quality_targets['arduino']['max_flash']:,}바이트 이하
- RAM 사용량: {self.quality_targets['arduino']['max_ram']:,}바이트 이하
- 주석 비율: {self.quality_targets['arduino']['comment_ratio']}% 이상
""")
    
    def _generate_charts(self, results: Dict, timestamp: str) -> None:
        """시각화 차트 생성"""
        integration = results.get("integration", {})
        
        # 언어별 분포 파이 차트
        lang_dist = integration.get("language_distribution", {})
        if lang_dist:
            plt.figure(figsize=(10, 6))
            
            # 라인 수 분포
            plt.subplot(1, 2, 1)
            languages = list(lang_dist.keys())
            lines = [lang_dist[lang]["lines"] for lang in languages]
            plt.pie(lines, labels=languages, autopct='%1.1f%%', startangle=90)
            plt.title('언어별 코드 라인 분포')
            
            # 파일 수 분포
            plt.subplot(1, 2, 2)
            files = [lang_dist[lang]["files"] for lang in languages]
            plt.pie(files, labels=languages, autopct='%1.1f%%', startangle=90)
            plt.title('언어별 파일 수 분포')
            
            plt.tight_layout()
            chart_path = self.reports_dir / f"language_distribution_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   차트: {chart_path}")
        
        # 품질 점수 게이지 차트
        quality_score = integration.get("quality_score", 0)
        plt.figure(figsize=(8, 6))
        
        # 간단한 바 차트로 품질 점수 표시
        categories = ['품질 점수']
        scores = [quality_score]
        colors = ['green' if quality_score >= 80 else 'orange' if quality_score >= 60 else 'red']
        
        bars = plt.bar(categories, scores, color=colors, alpha=0.7)
        plt.ylim(0, 100)
        plt.ylabel('점수')
        plt.title(f'프로젝트 품질 점수: {quality_score:.1f}/100')
        
        # 점수 텍스트 추가
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{score:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        chart_path = self.reports_dir / f"quality_score_{timestamp}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   차트: {chart_path}")
    
    def analyze_trends(self) -> Dict[str, Any]:
        """메트릭스 추이 분석"""
        print("\n📈 메트릭스 추이 분석 중...")
        
        # 최근 리포트들 수집
        all_reports = list(self.reports_dir.glob("integrated_metrics_*.json"))
        
        if len(all_reports) < 2:
            print("⚠️  추이 분석을 위해서는 최소 2개의 리포트가 필요합니다.")
            return {"error": "insufficient_data"}
        
        # 시간순 정렬
        all_reports.sort(key=lambda x: x.stat().st_mtime)
        
        trends = {
            "timestamp": datetime.now().isoformat(),
            "report_count": len(all_reports),
            "time_range": {},
            "quality_trend": [],
            "coverage_trend": [],
            "complexity_trend": []
        }
        
        for report_path in all_reports[-10:]:  # 최근 10개만
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timestamp = data.get("timestamp", "")
                integration = data.get("integration", {})
                python_data = data.get("python", {})
                
                trends["quality_trend"].append({
                    "timestamp": timestamp,
                    "quality_score": integration.get("quality_score", 0)
                })
                
                if python_data and "summary" in python_data:
                    trends["coverage_trend"].append({
                        "timestamp": timestamp,
                        "coverage": python_data["summary"].get("total_coverage", 0)
                    })
                
            except Exception as e:
                print(f"⚠️  리포트 읽기 실패 {report_path}: {e}")
        
        if trends["quality_trend"]:
            first_report = datetime.fromisoformat(trends["quality_trend"][0]["timestamp"].replace('Z', '+00:00'))
            last_report = datetime.fromisoformat(trends["quality_trend"][-1]["timestamp"].replace('Z', '+00:00'))
            trends["time_range"] = {
                "start": first_report.isoformat(),
                "end": last_report.isoformat(),
                "days": (last_report - first_report).days
            }
        
        print(f"✅ 추이 분석 완료 - {len(trends['quality_trend'])}개 데이터 포인트")
        return trends


def main():
    """메인 함수"""
    print("📊 DHT22 통합 메트릭스 관리 시스템")
    print("=" * 60)
    
    manager = IntegratedMetricsManager()
    
    # 전체 분석 실행
    results = manager.run_all_analyses()
    
    # 대시보드 리포트 생성
    manager.generate_dashboard_report(results)
    
    # 추이 분석 (선택적)
    trends = manager.analyze_trends()
    if "error" not in trends:
        print(f"\n📈 추이 분석: {trends['report_count']}개 리포트, {trends['time_range'].get('days', 0)}일간")
    
    # 요약 출력
    integration = results.get("integration", {})
    print(f"\n🎯 최종 결과:")
    print(f"   품질 점수: {integration.get('quality_score', 0):.1f}/100")
    print(f"   프로젝트 상태: {integration.get('project_health', 'unknown')}")
    print(f"   총 파일: {integration.get('total_files', 0)}개")
    print(f"   총 라인: {integration.get('total_lines', 0):,}줄")
    print(f"   달성 사항: {len(integration.get('achievements', []))}개")
    print(f"   개선 권장: {len(integration.get('recommendations', []))}개")
    
    print("\n🎉 통합 메트릭스 분석 완료!")


if __name__ == "__main__":
    main()