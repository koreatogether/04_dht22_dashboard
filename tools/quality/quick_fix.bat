@echo off
REM DHT22 프로젝트 빠른 자동 수정 도구
REM 이전 프로젝트에서 반복되는 오류 패턴을 자동으로 수정

echo.
echo ===============================================
echo 🚀 DHT22 프로젝트 빠른 자동 수정 도구
echo ===============================================
echo.
echo 💡 이전 프로젝트에서 학습한 패턴으로 자동 수정:
echo   - Ruff 린트 오류 자동 수정
echo   - MyPy 타입 힌트 자동 추가  
echo   - UTF-8 인코딩 문제 해결
echo   - 공통 코드 스타일 통일
echo.

REM UTF-8 콘솔 환경 설정
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1

REM 자동 수정 도구 실행
python tools\quality\auto_fix_common_issues.py

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ 자동 수정 완료!
    echo 📋 수정 결과를 확인하세요: tools\quality\results\
) else (
    echo.
    echo ❌ 자동 수정 중 오류 발생
    echo 💡 수동으로 확인이 필요합니다
)

echo.
pause