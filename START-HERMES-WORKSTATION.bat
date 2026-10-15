@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Hermes Work - One-Click Launcher

rem Keep PM's per-process PATH and Python selection active through Electron startup.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0workstation\scripts\oneclick_bootstrap.ps1"
set "HERMES_EXIT=%ERRORLEVEL%"
if "%HERMES_EXIT%"=="0" exit /b 0

echo.
echo [FAIL] Hermes Work could not finish startup (exit %HERMES_EXIT%).
echo Check the message above. First-run installation requires internet.
pause
exit /b %HERMES_EXIT%
