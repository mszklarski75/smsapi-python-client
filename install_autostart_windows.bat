@echo off
title SMSAPI Studio - Instalator Autostartu Windows
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Konfiguracja Automatycznego Startu
echo ================================================================
echo.
echo Ten skrypt skonfiguruje automatyczne uruchamianie aplikacji Flask
echo oraz tunelu ngrok w tle przy kazdym starcie/restarcie systemu Windows.
echo.

:: 1. Upewnij sie, ze pliki startowe istnieja
if not exist "start_all_silent.vbs" (
    echo [BLAD] Nie znaleziono pliku start_all_silent.vbs w tym folderze.
    pause
    exit /b 1
)

:: 2. Utworz skrot w folderze Autostart Windows (Startup)
echo [1/2] Tworzenie wpisu w folderze Autostart uzytkownika...
set "VBS_SCRIPT=%~dp0start_all_silent.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\SMSAPI_Studio_Autostart.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_SCRIPT%\"'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = 'shell32.dll,138'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo [OK] Skrot Autostartu zostal pomyslnie utworzony!
) else (
    echo [OSTRZEZENIE] Nie udalo sie utworzyc skrotu w folderze Autostart.
)

:: 3. Rejestracja w Harmonogramie Zadan Windows (Task Scheduler)
echo.
echo [2/2] Rejestracja w Harmonogramie Zadan Windows (Task Scheduler)...
schtasks /create /tn "SMSAPI_Studio_Autostart" /tr "wscript.exe \"%VBS_SCRIPT%\"" /sc onlogon /f >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Zadanie w Harmonogramie Zadan zostalo pomyslnie zarejestrowane!
) else (
    echo [INFO] Rejestracja z poziomu uzytkownika (autostart przez folder Startup jest aktywny).
)

echo.
echo ================================================================
echo    GRATULACJE! AUTOSTART ZOSTAL SKONFIGUROWANY!
echo ================================================================
echo.
echo Po kazdym restarcie komputera / serwera:
echo  1. Aplikacja SMSAPI Studio uruchomi sie automatycznie w tle.
echo  2. Tunel ngrok nawiaze polaczenie automatycznie (ukryty proces).
echo  3. Wszystkie webhooki i callbacki beda natychmiast aktywne!
echo.
echo Aby przetestowac natychmiast lub usunac autostart, uzyj pliku:
echo  - uninstall_autostart_windows.bat (do wylaczenia autostartu)
echo.
pause
