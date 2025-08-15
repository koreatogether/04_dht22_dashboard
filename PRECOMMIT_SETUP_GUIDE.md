# Pre-commit Windows 설정 가이드

## 문제 상황
Windows에서 pre-commit이 `/bin/bash`를 찾지 못하는 오류가 발생합니다.

## 해결 방법

### 방법 1: 자동 환경 설정 (권장)
```bash
# PowerShell에서 실행 (관리자 권한 필요)
.\setup_powershell_profile.ps1
```

### 방법 2: 배치 파일로 환경변수 설정
```bash
# 관리자 권한으로 실행
.\fix_precommit_bash.bat
```

### 방법 3: 수동 환경변수 설정
1. 시스템 환경변수에 다음 경로들을 PATH에 추가:
   - `C:\Program Files\Git\bin`
   - `C:\Users\h\AppData\Roaming\Python\Python313\Scripts`

2. 새 환경변수 생성:
   - 변수명: `PRE_COMMIT_BASH`
   - 값: `C:\Program Files\Git\bin\bash.exe`

### 방법 4: Pre-commit 우회 (임시 해결책)
```bash
# 안전한 커밋 (pre-commit 우회)
.\git_commit_safe.bat

# 또는 직접 명령어
git commit --no-verify -m "your message"
```

## 설정 확인

### PowerShell에서 확인:
```powershell
# 환경변수 확인
$env:PATH -split ';' | Where-Object { $_ -like '*Git*' }
$env:PRE_COMMIT_BASH

# bash 실행 가능 확인
bash --version

# pre-commit 실행 가능 확인
pre-commit --version
```

### 테스트 실행:
```bash
# 간단한 pre-commit 테스트
pre-commit run trailing-whitespace --all-files

# 전체 pre-commit 실행
pre-commit run --all-files
```

## 문제 해결

### 여전히 bash를 찾지 못하는 경우:
1. Git for Windows가 올바르게 설치되었는지 확인
2. PowerShell/CMD를 재시작
3. 시스템 재부팅

### Python 버전 문제:
- `.pre-commit-config.yaml`에서 `python3.9`를 현재 Python 버전으로 변경
- 현재 설정: `python3.13`

### 권한 문제:
- 관리자 권한으로 PowerShell 실행
- UAC 설정 확인

## 추천 워크플로우

1. **개발 중**: 코드 작성 후 `python tools/run_all_checks.py --all` 실행
2. **커밋 전**: `git_commit_safe.bat` 사용 또는 `git commit --no-verify`
3. **정기적으로**: `pre-commit run --all-files`로 전체 검사

## 참고사항

- Pre-commit hooks는 코드 품질을 보장하지만, 개발 속도를 늦출 수 있습니다
- 중요한 커밋의 경우 수동으로 품질 검사를 실행하는 것을 권장합니다
- CI/CD 파이프라인에서 최종 품질 검사를 수행하는 것이 좋습니다