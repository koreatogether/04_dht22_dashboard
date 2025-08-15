@echo off
echo ========================================
echo DHT22 프로젝트 메트릭스 및 커버리지 분석
echo ========================================

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..\..

cd /d "%PROJECT_ROOT%"

if "%1"=="python" goto python_only
if "%1"=="arduino" goto arduino_only
if "%1"=="integrated" goto integrated_only
if "%1"=="help" goto show_help

:all_metrics
echo.
echo 🚀 전체 메트릭스 분석 실행 중...
python "%SCRIPT_DIR%\integrated_metrics.py"
goto end

:python_only
echo.
echo 🐍 Python 메트릭스 분석 실행 중...
python "%SCRIPT_DIR%\python_coverage.py"
goto end

:arduino_only
echo.
echo 🔧 Arduino 메트릭스 분석 실행 중...
python "%SCRIPT_DIR%\arduino_metrics.py"
goto end

:integrated_only
echo.
echo 📊 통합 대시보드 생성 중...
python "%SCRIPT_DIR%\integrated_metrics.py"
goto end

:show_help
echo.
echo 사용법:
echo   run_metrics.bat [옵션]
echo.
echo 옵션:
echo   (없음)     - 전체 메트릭스 분석 실행
echo   python     - Python 코드만 분석
echo   arduino    - Arduino 코드만 분석
echo   integrated - 통합 대시보드만 생성
echo   help       - 이 도움말 표시
echo.
echo 예시:
echo   run_metrics.bat
echo   run_metrics.bat python
echo   run_metrics.bat arduino
goto end

:end
echo.
echo ✅ 메트릭스 분석 완료!
echo 📄 결과는 tools\metrics\reports\ 폴더에서 확인하세요.
pause