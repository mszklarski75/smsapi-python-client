@echo off
title SMSAPI Studio - Deinstalator Autostartu Windows
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Usuwanie Automatycznego Startu
echo ================================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\SMSAPI_Studio_Autostart.lnk"

:: 1. Usun skrot z folderu Autostart
if exist "%SHORTCUT_PATH%" (
    del /f /q "%SHORTCUT_PATH%" >nul 2>&1
    echo [OK] Usunieto skrot z folderu Autostart.
) else (
    echo [INFO] Brak skrotu w folderze Autostart.
)

:: 2. Usun zadanie z Harmonogramu Zadan
schtasks /delete /tn "SMSAPI_Studio_Autostart" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Usunieto zadanie z Harmonogramu Zadan Windows.
) else (
    echo [INFO] Brak zarejestrowanego zadania w Harmonogramie Zadan.
)

echo.
echo [SUKCES] Autostart zostal calkowicie usuniety.
echo.
pause
