@echo off
REM 코드 품질 및 보안 검사 실행 스크립트
echo ========================================
echo DHT22 프로젝트 품질 및 보안 검사
echo ========================================

REM 가상환경 활성화
if exist ".venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
) else (
    echo 오류: 가상환경을 찾을 수 없습니다.
    echo uv venv 명령으로 가상환경을 먼저 생성하세요.
    pause
    exit /b 1
)

REM 인수에 따라 다른 검사 실행
if "%1"=="python" (
    echo Python 코드 품질 검사만 실행...
    python tools\quality\quality_check.py
) else if "%1"=="arduino" (
    echo Arduino 코드 검사만 실행...
    python tools\quality\arduino_check.py
) else if "%1"=="security" (
    echo 보안 검사만 실행...
    python tools\security\trufflehog_check.py
) else if "%1"=="all" (
    echo 모든 검사 실행...
    python tools\run_all_checks.py
) else (
    echo.
    echo 사용법: run_quality_check.bat [옵션]
    echo.
    echo 옵션:
    echo   python    - Python 코드 품질 검사만 실행
    echo   arduino   - Arduino 코드 검사만 실행
    echo   security  - 보안 검사만 실행
    echo   all       - 모든 검사 실행
    echo.
    echo 예시:
    echo   run_quality_check.bat python
    echo   run_quality_check.bat all
    echo.
    echo 기본값으로 모든 검사를 실행합니다...
    python tools\run_all_checks.py
)

echo.
echo 검사 완료!
pause
