@echo off
title SMSAPI Studio
chcp 65001 > nul

:: Sprawdzenie czy Python jest zainstalowany
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Python nie zostal znaleziony w systemie!
    echo Zainstaluj Python ze strony https://www.python.org/ i zaznacz opcje "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Szybka weryfikacja bibliotek w tle
pip install -r requirements_app.txt --quiet --disable-pip-version-check >nul 2>&1

:: Uruchomienie aplikacji w tle bez wiszacego okna terminala
start "" pythonw launcher.pyw

:: Zamkniecie okna konsoli
exit
