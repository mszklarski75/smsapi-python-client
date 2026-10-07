@echo off
title SMSAPI Studio - Panel Zarzadzania
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Aplikacja do wysylki SMS / MMS / VMS / 2FA
echo ================================================================
echo.

set "PY_EXE="

:: 1. Sprawdz bezposredni folder python\python.exe
if exist "%~dp0python\python.exe" (
    set "PY_EXE=%~dp0python\python.exe"
    goto :FOUND
)

:: 2. Sprawdz ewentualny zagniezdzony folder python-* (np. python-3.11.9-embed-amd64)
for /d %%D in ("%~dp0python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :FOUND
    )
)

:: 3. Sprawdz wirtualne srodowisko (venv / .venv / env)
if exist "%~dp0venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0venv\Scripts\python.exe"
    goto :FOUND
)
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
    goto :FOUND
)

:: 4. Sprawdz domyslne sciezki instalacji w Windows AppData
for /d %%P in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%P\python.exe" (
        set "PY_EXE=%%P\python.exe"
        goto :FOUND
    )
)

:: 5. Sprawdz glowne katalogi na dysku C:\
if exist "C:\Python312\python.exe" ( set "PY_EXE=C:\Python312\python.exe" & goto :FOUND )
if exist "C:\Python311\python.exe" ( set "PY_EXE=C:\Python311\python.exe" & goto :FOUND )
if exist "C:\Python310\python.exe" ( set "PY_EXE=C:\Python310\python.exe" & goto :FOUND )
if exist "C:\Program Files\Python312\python.exe" ( set "PY_EXE=C:\Program Files\Python312\python.exe" & goto :FOUND )
if exist "C:\Program Files\Python311\python.exe" ( set "PY_EXE=C:\Program Files\Python311\python.exe" & goto :FOUND )
if exist "C:\Program Files\Python310\python.exe" ( set "PY_EXE=C:\Program Files\Python310\python.exe" & goto :FOUND )

:: 6. Sprawdz zmienna srodowiskowa PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_EXE=python"
    goto :FOUND
)

:: 7. Sprawdz py launcher
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -0 >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_EXE=py"
        goto :FOUND
    )
)

:NOT_FOUND
echo ================================================================
echo [BLAD] Nie znaleziono interpretera Python!
echo ================================================================
echo.
echo Biezacy katalog aplikacji: "%~dp0"
echo.
echo Aby rozwiazac ten problem, wybierz jedna z dwoch opcji:
echo.
echo   OPCJA A (Zalecana - wersja bez instalowania):
echo     Wypakuj przenosnego Pythona bezposrednio do folderu 'python':
echo     "%~dp0python\python.exe"
echo.
echo   OPCJA B (Standardowa instalacja):
echo     Pobierz instalator ze strony: https://www.python.org/downloads/
echo     Podczas instalacji ZAZNACZ ptaszek: "Add Python to PATH".
echo.
echo ================================================================
pause
exit /b 1

:FOUND
echo [OK] Znaleziono Python: "%PY_EXE%"
echo [OK] Uruchamianie aplikacji SMSAPI Studio...
echo.

"%PY_EXE%" desktop_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo ================================================================
    echo [INFORMACJA] Aplikacja zostala zamknieta lub wystapil blad.
    echo Jesli brakuje bibliotek, uruchom w folderze z pythonem:
    echo pip install -r requirements_app.txt
    echo ================================================================
    pause
)
