@echo off
title SMSAPI Studio
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Uruchamianie serwera...
echo ================================================================
echo.

:: 1. Jesli jest lokalny folder python (wersja Portable na Windows Server)
if exist "python\python.exe" (
    echo [OK] Uruchamianie z lokalnego folderu Python...
    python\python.exe desktop_launcher.py
    goto :END
)

:: 2. Jesli jest zainstalowany python w systemie
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Uruchamianie przez systemowy Python...
    python desktop_launcher.py
    goto :END
)

:: 3. Jesli jest launcher py
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Uruchamianie przez py launcher...
    py desktop_launcher.py
    goto :END
)

echo ================================================================
echo [BLAD] Nie znaleziono Pythona!
echo Upewnij sie, ze folder 'python' znajduje sie w tym samym katalogu.
echo ================================================================
pause

:END
