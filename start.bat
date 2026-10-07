@echo off
title SMSAPI Studio
chcp 65001 > nul
cls

echo ================================================================
echo    SMSAPI Studio - Uruchamianie...
echo ================================================================
echo.

:: 1. Bezposrednia proba uruchomienia przez oficjalny launcher py (zawsze obecny w C:\Windows\py.exe)
if exist "C:\Windows\py.exe" (
    echo [OK] Znaleziono Python Launcher (py.exe)
    set "PY_CMD=C:\Windows\py.exe"
    goto :RUN
)

:: 2. Sprawdz py w sciezce
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Znaleziono polecenie py
    set "PY_CMD=py"
    goto :RUN
)

:: 3. Sprawdz python w sciezce
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Znaleziono polecenie python
    set "PY_CMD=python"
    goto :RUN
)

:: 4. Sprawdz standardowe foldery instalacyjne Python
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        echo [OK] Znaleziono Python w %%D
        set "PY_CMD=%%D\python.exe"
        goto :RUN
    )
)

for /d %%D in ("C:\Program Files\Python*") do (
    if exist "%%D\python.exe" (
        echo [OK] Znaleziono Python w %%D
        set "PY_CMD=%%D\python.exe"
        goto :RUN
    )
)

for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        echo [OK] Znaleziono Python w %%D
        set "PY_CMD=%%D\python.exe"
        goto :RUN
    )
)

echo [INFO] Proba uruchomienia bezposredniego...
start "" launcher.pyw 2>nul
if %errorlevel% equ 0 (
    echo [OK] Uruchomiono aplikacje!
    exit
)

echo.
echo [UWAGA] Windows nie odswiezyl jeszcze sciezki po instalacji Pythona.
echo.
echo Szybkie rozwiazanie (wybierz jedno):
echo 1. Kliknij dwukrotnie w plik 'launcher.pyw' w tym folderze.
echo 2. Lub zrestartuj komputer / zamknij i otworz ten folder ponownie.
echo.
pause
exit /b 1

:RUN
echo [1/2] Sprawdzanie bibliotek...
"%PY_CMD%" -m pip install -r requirements_app.txt --quiet --disable-pip-version-check 2>nul

echo [2/2] Otwieranie aplikacji w przegladarce...
start "" "%PY_CMD%" desktop_launcher.py

:: Krotkie odczekanie i zamkniecie okna
timeout /t 2 >nul
exit
