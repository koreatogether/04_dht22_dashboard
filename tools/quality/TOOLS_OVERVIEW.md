# 🛠️ Quality Tools Overview

DHT22 프로젝트의 코드 품질 관리 도구들입니다.

## 🎯 **메인 도구 (Primary Tools)**

### 🩺 **smart_code_doctor.py** ⭐ **[NEW]**
**종합 자동 진단 및 수정 도구**
```bash
python tools/quality/smart_code_doctor.py
```
- 가상환경 손상 탐지 및 시스템 Python 자동 사용
- 고급 구문 오류 패턴 자동 수정
- Black → Ruff → MyPy 통합 실행
- 상세한 JSON 보고서 생성

### 🔒 **pre_commit_checks.py**
**Pre-commit 훅용 빠른 품질 검사**
```bash
python tools/quality/pre_commit_checks.py
```
- Git commit 시 자동 실행
- Black, Ruff, MyPy 기본 검사
- src/, tools/ 폴더만 검사

## 🎯 **특화 도구 (Specialized Tools)**

### 📝 **fix_type_hints.py**
**타입 힌트 특화 수정**
- MyPy 오류 기반 타입 힌트 자동 추가
- Smart Code Doctor 보완용

### 🛡️ **find_security_issues.py**
**보안 취약점 스캔**
- 보안 패턴 검사
- 민감한 정보 누출 탐지

### ✅ **validate_tools.py**
**개발 도구 설치 검증**
- Black, Ruff, MyPy 등 설치 상태 확인
- 버전 호환성 검사

### 😀 **safe_emoji.py / test_emoji_compatibility.py**
**이모지 호환성 도구**
- Windows 터미널 이모지 호환성
- UTF-8 인코딩 테스트

## 📦 **폴더 구조**

```
tools/quality/
├── smart_code_doctor.py          # ⭐ 메인 자동 수정 도구
├── pre_commit_checks.py           # Pre-commit 훅
├── fix_type_hints.py             # 타입 힌트 특화
├── find_security_issues.py       # 보안 스캔
├── validate_tools.py             # 도구 검증
├── safe_emoji.py                 # 이모지 호환성
├── test_emoji_compatibility.py   # 이모지 테스트
├── myPy/                         # MyPy 관련 도구들
├── temp/                         # 실험적/백업 도구들
├── backups/                      # 자동 백업 파일들
└── results/                      # 실행 결과 보고서들
```

## 🚀 **권장 사용법**

### 일반적인 코드 수정
```bash
# 가장 포괄적인 자동 수정
python tools/quality/smart_code_doctor.py

# 더 적극적인 수정
python tools/quality/smart_code_doctor.py --aggressive

# 미리보기 (실제 수정 X)
python tools/quality/smart_code_doctor.py --dry-run
```

### 커밋 전 빠른 검사
```bash
python tools/quality/pre_commit_checks.py
```

### 특화된 문제 해결
```bash
# 타입 힌트만 집중 수정
python tools/quality/fix_type_hints.py

# 보안 취약점 스캔
python tools/quality/find_security_issues.py
```

## 📋 **비활성화된 도구들 (.bak)**

다음 도구들은 Smart Code Doctor와 기능이 중복되어 비활성화되었습니다:
- `unified_code_fixer.py.bak` - Ruff 기반 수정 (중복)
- `ai_coding_error_fixer.py.bak` - AI 오류 패턴 (중복)
- `auto_fix_common_issues.py.bak` - 일반 구문 오류 (중복)
- `fix_syntax_errors_with_autopep8_autoflake_pyupgrade.py.bak` - 구문+포맷 (중복)

필요시 `.bak` 확장자를 제거하여 재활성화할 수 있습니다.

---

**💡 팁**: 대부분의 경우 `smart_code_doctor.py` 하나만 사용하면 충분합니다!