@echo off
title SMSAPI Studio - Zamykanie Aplikacji
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Zamykanie Serwera i Tuneli
echo ================================================================
echo.

echo [1/3] Zamykanie tunelu ngrok...
taskkill /f /im ngrok.exe >nul 2>&1

echo [2/3] Zamykanie procesow tła Python (pythonw)...
taskkill /f /im pythonw.exe >nul 2>&1

echo [3/3] Zwalnianie portu 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo.
echo ================================================================
echo [OK] Wszystkie procesy aplikacji zostaly pomyslnie zamkniete!
echo ================================================================
echo.
timeout /t 2 /nobreak >nul 2>&1
exit /b 0
