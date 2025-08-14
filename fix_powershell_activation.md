# PowerShell 가상환경 활성화 문제 해결 가이드

## 🚫 **발생한 오류**
```powershell
& E:\project\04_P_dht22_monitoring\.venv_new\Scripts\Activate.ps1
& : 'E:\project\04_P_dht22_monitoring\.venv_new\Scripts\Activate.ps1' 용어가 cmdlet, 함수, 스크립트 파일 또는 실행할 수 있는 프로그램 이름으로 인식되지 않습니다.
```

## ✅ **해결 방법 (3가지 옵션)**

### **방법 1: 배치 파일 사용 (가장 간단)**
```cmd
# 프로젝트 루트에서 실행
activate_venv.bat
```

### **방법 2: PowerShell 스크립트 사용**
```powershell
# 프로젝트 루트에서 실행
.\activate_venv.ps1
```

### **방법 3: 직접 PowerShell 실행 정책 변경**
```powershell
# 1단계: 실행 정책 변경 (한 번만)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2단계: 가상환경 활성화 (올바른 경로)
.\.venv\Scripts\Activate.ps1
```

## 🔍 **문제 원인 분석**

1. **잘못된 경로**: `.venv_new` → `.venv` (실제 디렉토리는 .venv)
2. **PowerShell 실행 정책**: 기본값이 `Restricted`로 스크립트 실행 차단
3. **경로 인식 오류**: 절대 경로 대신 상대 경로 사용 필요

## 📋 **현재 환경 상태**
- ✅ **가상환경 디렉토리**: `.venv` (존재)
- ❌ **잘못 참조된 디렉토리**: `.venv_new` (존재하지 않음)
- ✅ **활성화 스크립트**: `.venv\Scripts\Activate.ps1` (존재)

## 💡 **권장 사용법**

### **Windows CMD/PowerShell에서**
```cmd
cd E:\project\04_P_dht22_monitoring
activate_venv.bat
```

### **편리한 단축키 설정**
프로젝트 루트에 바로가기 만들기:
- 대상: `cmd.exe /k "cd /d E:\project\04_P_dht22_monitoring && activate_venv.bat"`
- 이름: "DHT22 개발환경"

## 🛠️ **추가 도구**
- `activate_venv.bat`: Windows 배치 파일 (실행 정책 문제 없음)
- `activate_venv.ps1`: PowerShell 스크립트 (자동 실행 정책 처리)
- 자동 Python 버전 확인 및 패키지 목록 표시

## 🎯 **결과**
이제 PowerShell 오류 메시지 없이 깔끔하게 가상환경을 활성화할 수 있습니다!