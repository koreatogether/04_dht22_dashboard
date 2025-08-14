echo ========================================
echo DHT22 Pre-commit Hook 설정 도구
echo ========================================
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
@echo off
REM DHT22 Project Pre-commit Hook (Windows)
echo [SEARCH] DHT22 Pre-commit quality checks running...

python "e:\project\04_P_dht22_monitoring\tools\quality\pre_commit.py"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Pre-commit checks passed. Proceeding with commit.
) else (
    echo [ERROR] Pre-commit checks failed. Commit blocked.
)

exit /b %ERRORLEVEL%