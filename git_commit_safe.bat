@echo off
echo Safe Git Commit (bypasses pre-commit hooks)
echo ============================================

REM 현재 상태 확인
echo Current git status:
git status --short

echo.
echo Adding all changes...
git add .

echo.
set /p commit_msg="Enter commit message: "

echo.
echo Committing with message: "%commit_msg%"
git commit --no-verify -m "%commit_msg%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Commit successful!
    echo.
    echo You can run quality checks manually with:
    echo   python tools/run_all_checks.py --all
) else (
    echo.
    echo ❌ Commit failed!
)

pause