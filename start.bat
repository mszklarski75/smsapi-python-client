@echo off
title SMSAPI Studio - Panel Wysylki SMS
chcp 65001 > nul
cls

echo ================================================================
echo    SMSAPI Studio - Aplikacja do wysylki SMS / MMS / VMS / 2FA
echo ================================================================
echo.

:: Sprawdzenie czy Python jest zainstalowany
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Python nie zostal znaleziony w systemie!
    echo Zainstaluj Python ze strony https://www.python.org/ i zaznacz opcje "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [1/2] Sprawdzanie i instalacja wymaganych bibliotek...
pip install -r requirements_app.txt --quiet --disable-pip-version-check

echo [2/2] Uruchamianie aplikacji w przegladarce...
echo.
python desktop_launcher.py

pause
