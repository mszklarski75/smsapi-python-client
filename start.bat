@echo off
title SMSAPI Studio
chcp 65001 > nul

:: ==============================================================
:: Inteligentne wykrywanie Pythona w systemie Windows
:: ==============================================================
set "PY_CMD="

:: 1. Sprawdz zwykle polecenie python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :FOUND
)

:: 2. Sprawdz oficjalny launcher py.exe
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :FOUND
)

:: 3. Sprawdz python3
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python3"
    goto :FOUND
)

:: 4. Sprawdz w folderze biezacego uzytkownika (standardowy instalator AppData)
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%i\python.exe" (
        set "PY_CMD=%%i\python.exe"
        goto :FOUND
    )
)

:: 5. Sprawdz w Program Files
for /d %%i in ("%ProgramFiles%\Python3*") do (
    if exist "%%i\python.exe" (
        set "PY_CMD=%%i\python.exe"
        goto :FOUND
    )
)

:: 6. Sprawdz w Program Files (x86)
for /d %%i in ("%ProgramFiles(x86)%\Python3*") do (
    if exist "%%i\python.exe" (
        set "PY_CMD=%%i\python.exe"
        goto :FOUND
    )
)

:: 7. Sprawdz w WindowsApps (Microsoft Store)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto :FOUND
)

:: ==============================================================
:: Jezeli zupelnie nie znaleziono
:: ==============================================================
echo ================================================================
echo [BLAD] Python nie zostal wykryty w zmiennych srodowiskowych!
echo ================================================================
echo.
echo Aby to naprawic w 10 sekund:
echo 1. Uruchom ponownie instalator Pythona.
echo 2. Wybierz opcje "Modify" (Modyfikuj).
echo 3. Na dole pierwszego okna ZAZNACZ: [x] "Add Python to PATH".
echo.
pause
exit /b 1

:FOUND
:: Ustal katalog i wersje pythonw
set "PYW_CMD=%PY_CMD%"
if "%PY_CMD%"=="python" set "PYW_CMD=pythonw"
if "%PY_CMD%"=="py" set "PYW_CMD=pyw"

:: Instalacja brakujacych bibliotek w tle
echo [SMSAPI Studio] Weryfikacja bibliotek...
"%PY_CMD%" -m pip install -r requirements_app.txt --quiet --disable-pip-version-check >nul 2>&1

:: Uruchomienie aplikacji
echo [SMSAPI Studio] Uruchamianie aplikacji w przegladarce...
start "" "%PYW_CMD%" launcher.pyw 2>nul || start "" "%PY_CMD%" desktop_launcher.py

:: Zamknij okno konsoli
exit
