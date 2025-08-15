@echo off
REM DHT22 프로젝트 가상환경 활성화 배치 파일
REM PowerShell 실행 정책 문제 없이 가상환경을 활성화합니다

echo [INFO] DHT22 프로젝트 가상환경 활성화 중...

REM 현재 디렉토리가 프로젝트 루트인지 확인
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] 가상환경을 찾을 수 없습니다.
    echo [INFO] 현재 위치: %CD%
    echo [INFO] .venv 디렉토리가 있는 프로젝트 루트에서 실행해주세요.
    pause
    exit /b 1
)

REM 가상환경 활성화
call .venv\Scripts\activate.bat

REM 활성화 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python을 찾을 수 없습니다.
    pause
    exit /b 1
) else (
    echo [SUCCESS] 가상환경이 활성화되었습니다!
    echo [INFO] Python 버전:
    python --version
    echo [INFO] 설치된 패키지 목록:
    pip list --local
)

echo.
echo [TIP] 가상환경을 비활성화하려면 'deactivate' 명령을 입력하세요.
echo [TIP] 프로젝트 작업을 시작할 준비가 완료되었습니다!
