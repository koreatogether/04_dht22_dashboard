#!/usr/bin/env python3
"""
간단한 메트릭스 실행 도구 (Windows 호환)

이모지 없이 Windows 환경에서 안전하게 실행되는 메트릭스 도구입니다.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def set_utf8_encoding():
    """UTF-8 인코딩 설정"""
    if os.name == 'nt':  # Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # Windows 콘솔 UTF-8 모드 활성화 시도
        try:
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass


def run_python_metrics():
    """Python 메트릭스 실행"""
    print("=" * 60)
    print("Python 코드 메트릭스 분석 시작")
    print("=" * 60)
    
    try:
        # 간단한 pytest 실행
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "--cov=src/python",
            "--cov-report=term-missing",
            "--cov-report=html:tools/metrics/reports/coverage_html",
            "-v"
        ], capture_output=True, text=True, encoding='utf-8')
        
        print("PYTEST 출력:")
        print(result.stdout)
        if result.stderr:
            print("PYTEST 오류:")
            print(result.stderr)
        
        # Radon 복잡도 분석
        print("\n" + "-" * 40)
        print("코드 복잡도 분석")
        print("-" * 40)
        
        cc_result = subprocess.run([
            sys.executable, "-m", "radon", "cc", "src/python", "-a"
        ], capture_output=True, text=True, encoding='utf-8')
        
        print("복잡도 분석 결과:")
        print(cc_result.stdout)
        
        return True
        
    except Exception as e:
        print(f"Python 메트릭스 실행 오류: {e}")
        return False


def run_arduino_metrics():
    """Arduino 메트릭스 실행"""
    print("\n" + "=" * 60)
    print("Arduino 코드 메트릭스 분석 시작")
    print("=" * 60)
    
    arduino_path = Path("src/arduino")
    if not arduino_path.exists():
        print("Arduino 소스 폴더를 찾을 수 없습니다.")
        return False
    
    arduino_files = list(arduino_path.rglob("*.ino"))
    cpp_files = list(arduino_path.rglob("*.cpp"))
    h_files = list(arduino_path.rglob("*.h"))
    
    all_files = arduino_files + cpp_files + h_files
    
    print(f"발견된 Arduino 파일: {len(all_files)}개")
    
    total_lines = 0
    code_lines = 0
    comment_lines = 0
    
    for file_path in all_files:
        print(f"분석 중: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            file_total = len(lines)
            file_code = 0
            file_comment = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                elif stripped.startswith("//") or stripped.startswith("/*"):
                    file_comment += 1
                else:
                    file_code += 1
            
            total_lines += file_total
            code_lines += file_code
            comment_lines += file_comment
            
            print(f"  총 라인: {file_total}, 코드: {file_code}, 주석: {file_comment}")
            
        except Exception as e:
            print(f"  파일 읽기 오류: {e}")
    
    print(f"\nArduino 코드 요약:")
    print(f"  총 파일: {len(all_files)}개")
    print(f"  총 라인: {total_lines}줄")
    print(f"  코드 라인: {code_lines}줄")
    print(f"  주석 라인: {comment_lines}줄")
    print(f"  주석 비율: {(comment_lines/max(total_lines,1)*100):.1f}%")
    
    return True


def generate_simple_report():
    """간단한 리포트 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path("tools/metrics/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = reports_dir / f"simple_metrics_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"""# DHT22 프로젝트 메트릭스 리포트

## 분석 시간
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 실행된 분석
- Python 코드 커버리지 테스트
- Python 코드 복잡도 분석 (Radon)
- Arduino 코드 라인 수 분석

## 결과 파일 위치
- 커버리지 HTML: tools/metrics/reports/coverage_html/index.html
- 이 리포트: {report_file}

## 권장사항
1. 커버리지 HTML 리포트를 브라우저에서 확인하세요
2. 복잡도가 높은 함수는 리팩토링을 고려하세요
3. 주석 비율을 15% 이상 유지하세요

## 다음 단계
- 더 상세한 분석을 위해 개별 도구를 실행하세요
- 정기적으로 메트릭스를 모니터링하세요
""")
    
    print(f"\n간단한 리포트 생성 완료: {report_file}")
    return report_file


def main():
    """메인 함수"""
    set_utf8_encoding()
    
    print("DHT22 프로젝트 메트릭스 분석 도구 (Windows 호환 버전)")
    print("=" * 60)
    
    # Python 메트릭스 실행
    python_success = run_python_metrics()
    
    # Arduino 메트릭스 실행
    arduino_success = run_arduino_metrics()
    
    # 간단한 리포트 생성
    report_file = generate_simple_report()
    
    print("\n" + "=" * 60)
    print("메트릭스 분석 완료!")
    print("=" * 60)
    print(f"Python 분석: {'성공' if python_success else '실패'}")
    print(f"Arduino 분석: {'성공' if arduino_success else '실패'}")
    print(f"리포트: {report_file}")
    
    if python_success:
        print("\n커버리지 리포트 확인:")
        print("  tools/metrics/reports/coverage_html/index.html")
    
    print("\n추가 분석을 위한 명령어:")
    print("  python -m pytest tests/ --cov=src/python -v")
    print("  python -m radon cc src/python -a")
    print("  python -m radon mi src/python")


if __name__ == "__main__":
    main()