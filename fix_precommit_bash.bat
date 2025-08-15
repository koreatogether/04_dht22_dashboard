@echo off
echo Setting up pre-commit bash environment for Windows...

REM Add Git bin to PATH permanently
setx PATH "%PATH%;C:\Program Files\Git\bin" /M

REM Add Python Scripts to PATH permanently
setx PATH "%PATH%;C:\Users\h\AppData\Roaming\Python\Python313\Scripts" /M

REM Set bash executable for pre-commit
setx PRE_COMMIT_BASH "C:\Program Files\Git\bin\bash.exe" /M

echo Environment variables set successfully!
echo Please restart your terminal or IDE for changes to take effect.
pause
