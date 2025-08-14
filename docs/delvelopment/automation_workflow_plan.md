# DHT22 프로젝트 자동화 워크플로우 계획서

## 📅 작성일: 2025-08-14
## 🎯 목적: INA219 경험 기반 DHT22 프로젝트 개발 시간 50% 단축

---

## 🚀 **핵심 자동화 전략**

### 1. 프로젝트 초기화 자동화 (5분 → 1분)

#### `tools/setup_dht22_project.py`
```python
#!/usr/bin/env python3
"""DHT22 프로젝트 자동 초기화 스크립트"""

import os
import shutil
import re
from pathlib import Path

def setup_dht22_project():
    """INA219 템플릿을 DHT22용으로 자동 변환"""
    
    # 1. 기본 구조 복사
    source = Path("03_P_ina219_powerMonitoring")
    target = Path("04_P_dht22_monitoring")
    
    if target.exists():
        print("DHT22 프로젝트가 이미 존재합니다.")
        return
    
    # 핵심 파일들만 선별 복사
    copy_structure(source, target)
    
    # 2. 자동 코드 변환
    convert_files(target)
    
    # 3. 의존성 파일 생성
    setup_dependencies(target)
    
    print("✅ DHT22 프로젝트 초기화 완료!")

def copy_structure(source, target):
    """필요한 구조만 복사"""
    copy_dirs = ["src", "tests", "tools", "docker"]
    copy_files = ["requirements.txt", "pyproject.toml", "docker-compose.yml"]
    
    target.mkdir(exist_ok=True)
    
    for dir_name in copy_dirs:
        if (source / dir_name).exists():
            shutil.copytree(source / dir_name, target / dir_name)
    
    for file_name in copy_files:
        if (source / file_name).exists():
            shutil.copy2(source / file_name, target / file_name)

def convert_files(target):
    """파일 내용 자동 변환"""
    conversions = {
        r'INA219': 'DHT22',
        r'power_monitoring': 'environmental_monitoring',
        r'voltage': 'temperature',
        r'current': 'humidity',
        r'power': 'heat_index',
        r'전력': '환경',
        r'전압': '온도',
        r'전류': '습도'
    }
    
    for file_path in target.rglob("*.py"):
        convert_file_content(file_path, conversions)

if __name__ == "__main__":
    setup_dht22_project()
```

#### `scripts/quick_setup.sh`
```bash
#!/bin/bash
# DHT22 프로젝트 1분 셋업 스크립트

echo "🚀 DHT22 프로젝트 자동 셋업 시작..."

# 1. 프로젝트 구조 생성
python tools/setup_dht22_project.py

# 2. 개발 환경 설정
cd 04_P_dht22_monitoring
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install uv
uv pip install -r requirements-dev.txt

# 4. 코드 품질 도구 설정
uv run ruff check --fix src/
uv run black src/

echo "✅ DHT22 프로젝트 셋업 완료! (1분 소요)"
```

### 2. AI 요청 템플릿 자동화

#### `tools/ai_request_templates.py`
```python
"""AI 요청 템플릿 자동 생성기"""

class DHT22AITemplates:
    def __init__(self):
        self.project_context = """
프로젝트: DHT22 온습도 모니터링 웹 대시보드
기반: INA219 전력 모니터링 시스템 (성공 사례)
목표: 개발시간 50% 단축, 품질 2배 향상
기술스택: Arduino UNO R4 WiFi, DHT22, FastAPI, Chart.js, SQLite
"""
    
    def phase1_simulator_request(self):
        return f"""
{self.project_context}

Phase 1: DHT22 시뮬레이터 구현을 요청합니다.

요구사항:
- 센서: DHT22 (온도: -40~80°C, 습도: 0~100%RH)
- 5가지 시뮬레이션 모드: Normal, Hot, Cold, Humid, Dry
- JSON 프로토콜: timestamp, temperature, humidity, heat_index, sequence
- 계산값: 열지수, 이슬점, 불쾌지수 자동 계산

완료 기준:
□ 5가지 모드별 시뮬레이션 데이터 생성
□ JSON 스키마 검증
□ 30초 이상 안정적 데이터 출력
□ Python 인터페이스 연동

기존 INA219 패턴을 유지하면서 DHT22 특성에 맞게 구현해주세요.
"""
    
    def phase2_dashboard_request(self):
        return f"""
{self.project_context}

Phase 2: 실시간 웹 대시보드 구현을 요청합니다.

요구사항:
- 듀얼 Y축 차트 (온도/습도)
- 환경지수 실시간 계산 (열지수, 이슬점, 불쾌지수)
- 3단계 알림 시스템 (Normal/Warning/Danger)
- 60초 롤링 버퍼
- WebSocket 실시간 통신

완료 기준:
□ Chart.js 듀얼축 그래프 구현
□ 환경지수 자동 계산 및 표시
□ 임계값 기반 색상 코딩
□ 모바일 반응형 디자인

실제 테스트 가능한 완전한 코드를 제공해주세요.
"""

# 사용법: python tools/ai_request_templates.py phase1
if __name__ == "__main__":
    import sys
    templates = DHT22AITemplates()
    
    if len(sys.argv) > 1:
        phase = sys.argv[1]
        if hasattr(templates, f"phase{phase}_request"):
            print(getattr(templates, f"phase{phase}_request")())
```

### 3. 코드 변환 자동화

#### `tools/ina219_to_dht22_converter.py`
```python
"""INA219 코드를 DHT22용으로 자동 변환"""

import re
from pathlib import Path

class CodeConverter:
    def __init__(self):
        self.variable_map = {
            'voltage': 'temperature',
            'current': 'humidity',
            'power': 'heat_index',
            'ina219': 'dht22',
            'INA219': 'DHT22',
            'PowerData': 'EnvironmentalData',
            'power_data': 'environmental_data'
        }
        
        self.unit_map = {
            'V': '°C',
            'A': '%RH',
            'W': 'HI',
            'voltage_threshold': 'temperature_threshold',
            'current_threshold': 'humidity_threshold'
        }
    
    def convert_file(self, file_path: Path):
        """단일 파일 변환"""
        if not file_path.exists():
            return
            
        content = file_path.read_text(encoding='utf-8')
        
        # 변수명 변환
        for old, new in self.variable_map.items():
            content = re.sub(rf'\b{old}\b', new, content)
        
        # 단위 변환
        for old, new in self.unit_map.items():
            content = content.replace(old, new)
        
        # DHT22 특화 수정
        content = self.apply_dht22_specifics(content)
        
        file_path.write_text(content, encoding='utf-8')
    
    def apply_dht22_specifics(self, content: str) -> str:
        """DHT22 센서 특화 수정사항 적용"""
        
        # 데이터 범위 수정
        content = re.sub(
            r'voltage_range.*=.*\[.*\]',
            'temperature_range = [-40, 80]',
            content
        )
        
        content = re.sub(
            r'current_range.*=.*\[.*\]',
            'humidity_range = [0, 100]',
            content
        )
        
        # 계산 공식 추가
        heat_index_calc = '''
def calculate_heat_index(temp_c, humidity):
    """열지수 계산"""
    temp_f = temp_c * 9/5 + 32
    if temp_f < 80:
        return temp_c
    
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return (hi - 32) * 5/9  # 섭씨로 변환
'''
        
        if 'def calculate_' not in content and 'class' in content:
            content = content.replace('class', heat_index_calc + '\n\nclass')
        
        return content
    
    def convert_project(self, project_path: Path):
        """전체 프로젝트 변환"""
        python_files = list(project_path.rglob("*.py"))
        
        for file_path in python_files:
            print(f"변환 중: {file_path}")
            self.convert_file(file_path)
        
        print(f"✅ {len(python_files)}개 파일 변환 완료")

if __name__ == "__main__":
    converter = CodeConverter()
    converter.convert_project(Path("04_P_dht22_monitoring"))
```

### 4. 테스트 자동화

#### `tools/auto_test_runner.py`
```python
"""Phase별 자동 테스트 실행기"""

import subprocess
import time
from pathlib import Path

class AutoTestRunner:
    def __init__(self):
        self.test_results = {}
    
    def run_phase_tests(self, phase_num: int):
        """특정 Phase 테스트 실행"""
        test_file = Path(f"tests/test_phase{phase_num}.py")
        
        if not test_file.exists():
            print(f"❌ Phase {phase_num} 테스트 파일 없음")
            return False
        
        print(f"🧪 Phase {phase_num} 테스트 실행 중...")
        
        result = subprocess.run([
            "python", "-m", "pytest", 
            str(test_file), 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        success = result.returncode == 0
        self.test_results[f"phase_{phase_num}"] = {
            "success": success,
            "output": result.stdout,
            "errors": result.stderr
        }
        
        if success:
            print(f"✅ Phase {phase_num} 테스트 통과")
        else:
            print(f"❌ Phase {phase_num} 테스트 실패")
            print(result.stderr)
        
        return success
    
    def run_all_quality_checks(self):
        """코드 품질 검사 일괄 실행"""
        checks = [
            ("Ruff 린트", ["uv", "run", "ruff", "check", "src/"]),
            ("Black 포맷", ["uv", "run", "black", "--check", "src/"]),
            ("MyPy 타입", ["uv", "run", "mypy", "src/"]),
            ("보안 스캔", ["python", "tools/security_scan.py"])
        ]
        
        results = {}
        for name, cmd in checks:
            print(f"🔍 {name} 실행 중...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            results[name] = result.returncode == 0
            
            if results[name]:
                print(f"✅ {name} 통과")
            else:
                print(f"❌ {name} 실패: {result.stderr}")
        
        return all(results.values())
    
    def continuous_monitoring(self, interval=30):
        """지속적 품질 모니터링"""
        print(f"🔄 {interval}초 간격으로 품질 모니터링 시작...")
        
        while True:
            try:
                if self.run_all_quality_checks():
                    print("✅ 모든 품질 검사 통과")
                else:
                    print("⚠️ 품질 이슈 발견, 수정 필요")
                
                time.sleep(interval)
            except KeyboardInterrupt:
                print("🛑 모니터링 중단")
                break

if __name__ == "__main__":
    runner = AutoTestRunner()
    
    # Phase별 테스트 실행
    for phase in range(1, 6):
        runner.run_phase_tests(phase)
    
    # 품질 검사 실행
    runner.run_all_quality_checks()
```

### 5. 문서 자동 생성

#### `tools/auto_documentation.py`
```python
"""API 문서 및 사용자 매뉴얼 자동 생성"""

from pathlib import Path
import json

class AutoDocGenerator:
    def __init__(self):
        self.project_root = Path("04_P_dht22_monitoring")
    
    def generate_api_docs(self):
        """FastAPI 문서 자동 생성"""
        api_template = """
# DHT22 모니터링 API 문서

## 개요
DHT22 센서 데이터 실시간 모니터링 API

## 엔드포인트

### 실시간 데이터
- `GET /api/environmental/current` - 현재 온습도 데이터
- `GET /api/environmental/history` - 히스토리 데이터
- `WebSocket /ws` - 실시간 데이터 스트림

### 분석 데이터
- `GET /api/analysis/moving_average` - 이동평균 데이터
- `GET /api/analysis/anomalies` - 이상치 탐지 결과

### 설정
- `GET /api/config/thresholds` - 임계값 설정 조회
- `POST /api/config/thresholds` - 임계값 설정 변경

## 자동 생성됨: 2025-08-14
"""
        
        docs_path = self.project_root / "docs" / "api_reference.md"
        docs_path.parent.mkdir(exist_ok=True)
        docs_path.write_text(api_template)
        
        print("✅ API 문서 생성 완료")
    
    def generate_user_manual(self):
        """사용자 매뉴얼 자동 생성"""
        manual_template = """
# DHT22 모니터링 시스템 사용 매뉴얼

## 빠른 시작 (3분)

1. **Docker로 실행**
   ```bash
   docker-compose up -d
   ```

2. **웹 대시보드 접속**
   - http://localhost:8000

3. **실시간 모니터링 확인**
   - 온도/습도 그래프 확인
   - 환경지수 모니터링
   - 알림 상태 확인

## 기능 설명

### 실시간 대시보드
- 듀얼 Y축 차트로 온도(°C)/습도(%RH) 동시 표시
- 열지수, 이슬점, 불쾌지수 실시간 계산
- 3단계 알림 시스템 (Normal/Warning/Danger)

### 데이터 내보내기
- CSV 형식으로 48시간 데이터 다운로드
- JSON API를 통한 프로그래밍 방식 접근

## 문제 해결

### 일반적인 문제
1. **연결 안됨**: 포트 8000 사용 중인지 확인
2. **데이터 없음**: DHT22 센서 연결 상태 확인
3. **느린 응답**: 브라우저 캐시 삭제 후 새로고침

자동 생성됨: 2025-08-14
"""
        
        manual_path = self.project_root / "docs" / "user_manual.md"
        manual_path.write_text(manual_template)
        
        print("✅ 사용자 매뉴얼 생성 완료")
    
    def generate_readme(self):
        """README.md 자동 생성"""
        readme_template = """
# DHT22 온습도 모니터링 웹 대시보드

실시간 DHT22 센서 데이터 모니터링 및 분석 시스템

## ⚡ 빠른 시작

```bash
# 1. Docker로 실행
docker-compose up -d

# 2. 웹 브라우저에서 접속
http://localhost:8000
```

## 🚀 주요 기능

- ✅ 실시간 온습도 모니터링
- ✅ 환경지수 자동 계산 (열지수, 이슬점, 불쾌지수)
- ✅ 3단계 알림 시스템
- ✅ 48시간 데이터 히스토리
- ✅ CSV 데이터 내보내기

## 📊 시스템 요구사항

- Docker & Docker Compose
- 최신 웹 브라우저
- DHT22 센서 + Arduino UNO R4 WiFi (선택사항)

## 📖 문서

- [사용자 매뉴얼](docs/user_manual.md)
- [API 문서](docs/api_reference.md)
- [개발자 가이드](docs/developer_guide.md)

## 🔧 개발 환경 설정

```bash
# 의존성 설치
uv pip install -r requirements-dev.txt

# 개발 서버 실행
python src/main.py
```

자동 생성됨: 2025-08-14
"""
        
        readme_path = self.project_root / "README.md"
        readme_path.write_text(readme_template)
        
        print("✅ README.md 생성 완료")

if __name__ == "__main__":
    doc_gen = AutoDocGenerator()
    doc_gen.generate_api_docs()
    doc_gen.generate_user_manual()
    doc_gen.generate_readme()
```

## 🔄 **자동화 워크플로우 실행 순서**

### 1일차: 프로젝트 초기화 (1시간)
```bash
# Step 1: 자동 셋업 (1분)
bash scripts/quick_setup.sh

# Step 2: AI 템플릿 준비 (5분)
python tools/ai_request_templates.py phase1 > phase1_request.txt

# Step 3: 코드 변환 실행 (2분)
python tools/ina219_to_dht22_converter.py

# Step 4: 품질 검사 (2분)
python tools/auto_test_runner.py
```

### 실제 개발 진행 (6시간)
```bash
# Phase 1: 시뮬레이터 (1.5시간)
# - AI에게 phase1_request.txt 내용 전달
# - 코드 구현 후 자동 테스트
python tools/auto_test_runner.py 1

# Phase 2: 대시보드 (2시간)  
# - AI에게 phase2 요청
# - 구현 후 품질 검사
python tools/auto_test_runner.py 2

# Phase 3: 데이터 저장 (1.5시간)
# Phase 4: 분석 기능 (1시간)
```

### 배포 및 문서화 (1시간)
```bash
# 자동 문서 생성
python tools/auto_documentation.py

# 최종 품질 검사
python tools/auto_test_runner.py

# Docker 빌드 및 테스트
docker-compose build
docker-compose up -d
```

## 🎯 **예상 시간 단축 효과**

| 작업 | 수동 시간 | 자동화 시간 | 단축율 |
|------|-----------|-------------|--------|
| 프로젝트 초기화 | 30분 | 3분 | **90%↓** |
| 코드 변환 | 2시간 | 10분 | **92%↓** |
| 품질 검사 | 1시간 | 5분 | **92%↓** |
| 문서 작성 | 2시간 | 15분 | **88%↓** |
| 테스트 실행 | 1시간 | 10분 | **83%↓** |
| **총계** | **14시간** | **7시간** | **50%↓** |

---

**📝 작성자**: Kiro (Claude Code AI Assistant)  
**📅 작성일**: 2025-08-14  
**🎯 목적**: DHT22 프로젝트 개발 시간 50% 단축을 위한 완전 자동화 계획