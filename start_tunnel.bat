@echo off
title SMSAPI Studio - Zdalny Dostep (Cloudflare Tunnel)
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Bezpieczny Tunel Zewnetrzny Cloudflare
echo ================================================================
echo.

:: Sprawdz czy cloudflared.exe istnieje, jesli nie - pobierz automatycznie
if not exist "cloudflared.exe" (
    echo [INFO] Pobieranie bezpiecznego programu cloudflared od Cloudflare...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', 'cloudflared.exe')"
    if %errorlevel% neq 0 (
        echo [BLAD] Nie udalo sie automatycznie pobrac cloudflared.exe.
        echo Pobierz plik recznie ze strony:
        echo https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
        echo i zapisz go jako 'cloudflared.exe' w tym folderze.
        pause
        exit /b 1
    )
    echo [OK] Pobrano cloudflared.exe pomyslnie!
    echo.
)

echo [1/2] Upewnij sie, ze SMSAPI Studio (start.bat) jest uruchomione w tle.
echo [2/2] Uruchamianie szyfrowanego tunelu HTTPS...
echo.
echo ================================================================
echo Po chwili ponizej pojawi sie Twoj prywatny adres HTTPS:
echo (Szukaj linii: https://xxxx-xxxx.trycloudflare.com)
echo Mozesz otworzyc ten adres w telefonie lub z dowolnego miejsca na swiecie!
echo ================================================================
echo.

cloudflared.exe tunnel --url http://127.0.0.1:5000

pause
