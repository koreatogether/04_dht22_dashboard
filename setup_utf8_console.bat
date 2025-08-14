@echo off
REM UTF-8 콘솔 환경 설정 배치 파일
echo Setting up UTF-8 console environment...

REM 콘솔 코드페이지를 UTF-8로 변경
chcp 65001 >nul

REM Python UTF-8 환경변수 설정
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1

REM 콘솔 폰트 설정 (이모지 지원)
powershell -Command "& {[Console]::OutputEncoding = [System.Text.Encoding]::UTF8}"

echo ✅ UTF-8 console environment configured!
echo 🚀 You can now use emojis and Unicode characters
echo.
echo Test emojis: 🎉 🔧 📊 💡 ⚡ 🎯
echo.