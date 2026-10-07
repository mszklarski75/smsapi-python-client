@echo off
title SMSAPI Studio - Instalacja zaleznosci
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================
echo    SMSAPI Studio - Instalacja bibliotek Python
echo ================================================================
echo.

set "PY_EXE="
if exist "%~dp0python\python.exe" (
    set "PY_EXE=%~dp0python\python.exe"
    goto :INSTALL
)
for /d %%D in ("%~dp0python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :INSTALL
    )
)
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_EXE=python"
    goto :INSTALL
)

echo [BLAD] Nie znaleziono interpretera Python.
pause
exit /b 1

:INSTALL
echo [OK] Uzywanie interpretera: "%PY_EXE%"
echo [1/2] Aktualizacja pip...
"%PY_EXE%" -m pip install --upgrade pip

echo.
echo [2/2] Instalowanie bibliotek z requirements_app.txt...
"%PY_EXE%" -m pip install -r requirements_app.txt

echo.
echo ================================================================
echo Gotowe! Mozesz teraz uruchomic start.bat
echo ================================================================
pause
