@echo off
REM 한글 인코딩 문제 해결 스크립트

echo [INFO] 한글 인코딩 환경 설정 중...

REM UTF-8 환경변수 설정
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 현재 세션에서 적용
echo [STEP 1] 환경변수 설정 완료
echo   PYTHONIOENCODING=utf-8
echo   PYTHONUTF8=1

REM Python 인코딩 테스트
echo.
echo [STEP 2] Python 인코딩 테스트...
python -c "import sys; print(f'출력 인코딩: {sys.stdout.encoding}'); print('한글 테스트: 안녕하세요 🎉')"

REM 도구 실행 테스트  
echo.
echo [STEP 3] 도구 실행 테스트...
python tools\quality\validate_tools.py

echo.
echo [SUCCESS] 인코딩 설정이 완료되었습니다!
echo 앞으로 이 배치 파일을 실행한 후 Python 도구들을 사용하세요.

pause