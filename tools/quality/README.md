# DHT22 프로젝트 자동 테스트 및 품질 관리 도구

automation_workflow_plan.md의 **4. 테스트 자동화 계획**에 따라 구현된 DHT22 프로젝트 전용 자동 테스트 및 품질 관리 도구입니다.

## 📁 파일 구조

```
tools/quality/
├── auto_test_runner.py    # 메인 자동 테스트 실행기
├── security_scan.py       # 보안 스캔 도구
├── run_tests.bat         # Windows 배치 스크립트
├── results/              # 테스트 결과 저장 디렉토리
└── README.md            # 이 파일
```

## 🚀 주요 기능

### 1. 자동 테스트 실행기 (auto_test_runner.py)
- **Phase별 테스트**: Phase 1-5 개별 테스트 실행
- **품질 검사**: Ruff, Black, MyPy, 보안 스캔, 의존성 검사
- **기능 테스트**: DHT22 시뮬레이터, 환경 계산, WebSocket, API 테스트
- **지속적 모니터링**: 30초 간격 자동 품질 검사
- **테스트 리포트**: 상세한 테스트 결과 리포트 생성

### 2. 보안 스캔 도구 (security_scan.py)
- **하드코딩된 비밀정보 검사**: 패스워드, API 키, 토큰 등
- **SQL 인젝션 취약점 검사**: 동적 쿼리, 문자열 연결 등
- **명령어 인젝션 검사**: os.system, subprocess 등
- **파일 권한 검사**: 민감한 파일의 권한 확인
- **의존성 보안 검사**: 알려진 취약한 패키지 검사

## 📋 사용법

### 🖥️ Windows 사용자 (권장)

```batch
# 전체 테스트 실행
run_tests.bat all

# 품질 검사만 실행
run_tests.bat quality

# 기능 테스트만 실행
run_tests.bat functional

# 보안 스캔만 실행
run_tests.bat security

# 지속적 모니터링
run_tests.bat monitor
```

### 🐍 Python 직접 실행

```bash
# 전체 테스트 실행
python tools/quality/auto_test_runner.py --all

# 특정 Phase 테스트
python tools/quality/auto_test_runner.py --phase 1

# 품질 검사만
python tools/quality/auto_test_runner.py --quality

# 기능 테스트만
python tools/quality/auto_test_runner.py --functional

# 지속적 모니터링
python tools/quality/auto_test_runner.py --monitor

# 테스트 리포트 생성
python tools/quality/auto_test_runner.py --report

# 보안 스캔
python tools/quality/security_scan.py
```

## 📊 테스트 결과 해석

### ✅ 성공 사례
```
🚀 DHT22 자동 테스트 실행기 초기화 완료
🧪 Phase 1 테스트 실행 중...
✅ Phase 1 테스트 통과
🔍 코드 품질 검사 시작...
  ✅ Ruff 린트 검사 통과
  ✅ Black 포맷 검사 통과
✅ 모든 품질 검사 통과
```

### ❌ 실패 사례
```
❌ Phase 2 테스트 실패
   오류: AssertionError: DHT22 시뮬레이터 데이터 검증 실패
❌ Ruff 린트 검사 실패
   오류: src/main.py:45:1: E302 expected 2 blank lines
⚠️ 일부 품질 검사 실패
```

## 📈 테스트 리포트

테스트 실행 후 `tools/quality/results/` 디렉토리에 다음 파일들이 생성됩니다:

- `test_report_YYYYMMDD_HHMMSS.md` - 전체 테스트 리포트
- `quality_results_YYYYMMDD_HHMMSS.json` - 품질 검사 결과
- `security_scan_YYYYMMDD_HHMMSS.json` - 보안 스캔 결과
- `phaseN_results.json` - Phase별 테스트 결과

### 📄 리포트 예시
```markdown
# DHT22 프로젝트 테스트 리포트

## 📊 테스트 개요
- **실행 시간**: 2025-08-14 15:30:00
- **총 테스트 수**: 8
- **통과한 테스트**: 7
- **실패한 테스트**: 1
- **성공률**: 87.5%

## 🔍 품질 검사 결과
- **총 검사 수**: 5
- **통과한 검사**: 4
- **실패한 검사**: 1
- **품질 점수**: 80.0%
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 테스트 파일이 없음
```
❌ Phase 1 테스트 파일 없음: tests/test_phase1.py
📝 샘플 테스트 파일 생성: tests/test_phase1.py
```
**해결**: 자동으로 샘플 테스트 파일이 생성됩니다.

#### 2. 의존성 누락
```
⚠️ MyPy 타입 검사 도구를 찾을 수 없음
```
**해결**: 
```bash
pip install mypy
# 또는
pip install -r requirements-dev.txt
```

#### 3. 권한 문제 (Linux/Mac)
```
❌ 파일 권한 검사 실패: config.py - Permission denied
```
**해결**:
```bash
chmod 600 config.py  # 민감한 파일
chmod 755 tools/quality/  # 실행 디렉토리
```

### 보안 스캔 결과 해석

#### 🔴 HIGH (즉시 수정 필요)
- 하드코딩된 패스워드/API 키
- SQL 인젝션 취약점
- 명령어 인젝션 취약점

#### 🟡 MEDIUM (수정 권장)
- 부적절한 파일 권한
- 취약한 의존성 패키지
- SSL 인증서 검증 비활성화

#### 🔵 LOW/INFO (참고사항)
- 파일 쓰기 작업
- HTTP 사용 (HTTPS 권장)
- 일반적인 정보

## 🎯 권장 워크플로우

### 개발 중
```bash
# 1. 코드 작성 후 품질 검사
run_tests.bat quality

# 2. 기능 테스트 실행
run_tests.bat functional

# 3. 보안 스캔
run_tests.bat security
```

### 배포 전
```bash
# 전체 테스트 실행
run_tests.bat all

# 리포트 확인
# tools/quality/results/ 디렉토리 확인
```

### 지속적 통합 (CI)
```bash
# 자동화된 품질 모니터링
python tools/quality/auto_test_runner.py --monitor
```

## 📚 추가 정보

### 커스터마이징

테스트 설정을 변경하려면 `auto_test_runner.py`의 다음 부분을 수정하세요:

```python
# 모니터링 간격 변경 (기본: 30초)
runner.continuous_monitoring(interval=60)

# 최대 모니터링 횟수 변경 (기본: 10회)
runner.continuous_monitoring(max_iterations=20)
```

### 새로운 테스트 추가

1. `tests/` 디렉토리에 `test_phaseN.py` 파일 생성
2. pytest 형식으로 테스트 작성
3. `auto_test_runner.py` 실행

### 보안 패턴 추가

`security_scan.py`의 `security_patterns` 딕셔너리에 새로운 패턴 추가:

```python
"custom_category": [
    (r'your_pattern_here', "설명"),
]
```

---

**📅 작성일**: 2025-08-14  
**👨‍💻 작성자**: Kiro AI Assistant  
**🎯 목적**: DHT22 프로젝트 품질 관리 자동화  
**📋 기반**: automation_workflow_plan.md의 4. 테스트 자동화 계획