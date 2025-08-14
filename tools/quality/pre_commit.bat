@echo off
REM DHT22 프로젝트 Pre-commit Hook 설정 (Windows)
REM 자동 품질 검사를 위한 Git hook 설정

echo ========================================
echo DHT22 Pre-commit Hook 설정 도구
echo ========================================

cd /d "%~dp0..\.."

REM 가상환경 활성화 (존재하는 경우)
if exist ".venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
)

REM Pre-commit hook 설정 스크립트 실행
echo Pre-commit hook 설정 중...
python tools\quality\setup_precommit.py

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 이제 'git commit' 실행 시 자동으로 품질 검사가 실행됩니다.
echo.
echo 사용법:
echo   git add .
echo   git commit -m "feat: 새 기능 추가"
echo.
echo Hook 비활성화:
echo   git commit --no-verify -m "메시지"
echo.
pause