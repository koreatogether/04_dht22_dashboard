@echo off
REM DHT22 프로젝트 자동 테스트 실행 배치 스크립트
REM Windows용 테스트 실행 도구

echo ========================================
echo DHT22 프로젝트 자동 테스트 실행기
echo ========================================

cd /d "%~dp0..\.."

REM 가상환경 활성화 (존재하는 경우)
if exist ".venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
)

REM 인수에 따른 테스트 실행
if "%1"=="all" (
    echo 전체 테스트 실행 중...
    python tools\quality\auto_test_runner.py --all
) else if "%1"=="quality" (
    echo 품질 검사 실행 중...
    python tools\quality\auto_test_runner.py --quality
) else if "%1"=="functional" (
    echo 기능 테스트 실행 중...
    python tools\quality\auto_test_runner.py --functional
) else if "%1"=="security" (
    echo 보안 스캔 실행 중...
    python tools\quality\security_scan.py
) else if "%1"=="monitor" (
    echo 지속적 모니터링 시작...
    python tools\quality\auto_test_runner.py --monitor
) else (
    echo.
    echo 사용법: run_tests.bat [옵션]
    echo.
    echo 옵션:
    echo   all        - 전체 테스트 실행
    echo   quality    - 품질 검사만 실행
    echo   functional - 기능 테스트만 실행
    echo   security   - 보안 스캔만 실행
    echo   monitor    - 지속적 모니터링
    echo.
    echo 예시:
    echo   run_tests.bat all
    echo   run_tests.bat quality
    echo.
    pause
)

echo.
echo 테스트 완료!
pause