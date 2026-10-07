@echo off
title SMSAPI Studio - Zdalny Dostep (ngrok Tunnel)
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Bezpieczny Tunel Zewnetrzny ngrok
echo ================================================================
echo.

:: 1. Sprawdz czy ngrok.exe istnieje
if not exist "ngrok.exe" (
    echo [INFO] Pobieranie oficjalnego programu ngrok dla Windows...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip'"
    if not exist "ngrok.exe" (
        echo [BLAD] Nie udalo sie automatycznie pobrac ngrok.exe.
        echo Pobierz plik recznie ze strony https://ngrok.com/download
        echo i umiesc plik 'ngrok.exe' w tym folderze.
        pause
        exit /b 1
    )
    echo [OK] Pobrano i rozpakowano ngrok.exe!
    echo.
)

:: 2. Sprawdz czy podano token w pliku ngrok_token.txt lub zapytaj
if exist "ngrok_token.txt" (
    set /p NGROK_TOKEN=<ngrok_token.txt
)

if "%NGROK_TOKEN%"=="" (
    echo [INFORMACJA] Wklej ponizej swoj authtoken ze strony ngrok.com:
    echo (Zarejestruj sie bezplatnie na https://dashboard.ngrok.com/signup i skopiuj Your Authtoken)
    echo.
    set /p NGROK_TOKEN="Wklej Authtoken: "
    if not "%NGROK_TOKEN%"=="" (
        echo %NGROK_TOKEN%>ngrok_token.txt
    )
)

if not "%NGROK_TOKEN%"=="" (
    ngrok.exe config add-authtoken %NGROK_TOKEN% >nul 2>&1
)

:: 3. Sprawdz czy jest stala domena w ngrok_domain.txt
set "DOMAIN_PARAM="
if exist "ngrok_domain.txt" (
    set /p NGROK_DOMAIN=<ngrok_domain.txt
    if not "%NGROK_DOMAIN%"=="" (
        set DOMAIN_PARAM=--domain=%NGROK_DOMAIN%
    )
)

echo.
echo [OK] Uruchamianie tunelu ngrok do portu 5000...
echo ================================================================
echo Szukaj w oknie linii 'Forwarding' z adresem HTTPS:
echo np. Forwarding   https://xxxx.ngrok-free.app -^> http://localhost:5000
echo ================================================================
echo.

if "%DOMAIN_PARAM%"=="" (
    ngrok.exe http 5000
) else (
    ngrok.exe http %DOMAIN_PARAM% 5000
)

pause
