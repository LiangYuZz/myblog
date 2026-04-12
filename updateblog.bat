@echo off
setlocal
cd /d "%~dp0"

set "HUGO_EXE=hugo"
where hugo >nul 2>nul
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Hugo.Hugo.Extended_Microsoft.Winget.Source_8wekyb3d8bbwe\hugo.exe" (
        set "HUGO_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Hugo.Hugo.Extended_Microsoft.Winget.Source_8wekyb3d8bbwe\hugo.exe"
    ) else (
        echo [ERROR] Hugo not found. Reopen PowerShell or add Hugo to PATH.
        exit /b 1
    )
)

"%HUGO_EXE%"
if errorlevel 1 exit /b %errorlevel%

git -c safe.directory="%CD%" add . -- :!run_hugo_manager.bat :!hugo_manager.py
if errorlevel 1 exit /b %errorlevel%

git -c safe.directory="%CD%" diff --cached --quiet
if not errorlevel 1 (
    echo [INFO] No staged changes.
    exit /b 0
)

git -c safe.directory="%CD%" commit -m "update %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%%time:~3,2%"
if errorlevel 1 exit /b %errorlevel%

git -c safe.directory="%CD%" pull --rebase --autostash origin main
if errorlevel 1 exit /b %errorlevel%

git -c safe.directory="%CD%" push origin main
