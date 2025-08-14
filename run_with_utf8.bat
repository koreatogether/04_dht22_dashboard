@echo off
REM UTF-8 환경에서 Python 도구 실행

REM UTF-8 강제 설정
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 가상환경 활성화
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 전달받은 인수로 Python 실행
if "%1"=="" (
    echo 사용법: run_with_utf8.bat ^<python_script^> [args]
    echo 예시: run_with_utf8.bat tools/quality/unified_code_fixer.py
    pause
    exit /b 1
)

echo [UTF-8 모드] %*
python %*