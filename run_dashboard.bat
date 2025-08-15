@echo off
REM DHT22 대시보드 실행 스크립트
echo ========================================
echo DHT22 환경 모니터링 대시보드 시작
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

REM 대시보드 실행
echo 대시보드 시작 중...
echo 브라우저에서 http://localhost:8050 을 열어주세요.
echo Ctrl+C 를 눌러 종료할 수 있습니다.
echo.

python src\python\dashboard\app.py
