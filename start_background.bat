@echo off
chcp 65001 > nul
cd /d "%~dp0"

:: 1. Inteligentne wykrywanie interpretera Python / Pythonw
set "PY_EXE="
set "PYW_EXE="

if exist "%~dp0python\pythonw.exe" (
    set "PYW_EXE=%~dp0python\pythonw.exe"
    set "PY_EXE=%~dp0python\python.exe"
    goto :START_SERVICES
)

for /d %%D in ("%~dp0python*") do (
    if exist "%%D\pythonw.exe" (
        set "PYW_EXE=%%D\pythonw.exe"
        set "PY_EXE=%%D\python.exe"
        goto :START_SERVICES
    )
)

if exist "%~dp0venv\Scripts\pythonw.exe" (
    set "PYW_EXE=%~dp0venv\Scripts\pythonw.exe"
    set "PY_EXE=%~dp0venv\Scripts\python.exe"
    goto :START_SERVICES
)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    set "PYW_EXE=%~dp0.venv\Scripts\pythonw.exe"
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
    goto :START_SERVICES
)

for /d %%P in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%P\pythonw.exe" (
        set "PYW_EXE=%%P\pythonw.exe"
        set "PY_EXE=%%P\python.exe"
        goto :START_SERVICES
    )
)

if exist "C:\Python313\pythonw.exe" ( set "PYW_EXE=C:\Python313\pythonw.exe" & set "PY_EXE=C:\Python313\python.exe" & goto :START_SERVICES )
if exist "C:\Python312\pythonw.exe" ( set "PYW_EXE=C:\Python312\pythonw.exe" & set "PY_EXE=C:\Python312\python.exe" & goto :START_SERVICES )
if exist "C:\Python311\pythonw.exe" ( set "PYW_EXE=C:\Python311\pythonw.exe" & set "PY_EXE=C:\Python311\python.exe" & goto :START_SERVICES )
if exist "C:\Python310\pythonw.exe" ( set "PYW_EXE=C:\Python310\pythonw.exe" & set "PY_EXE=C:\Python310\python.exe" & goto :START_SERVICES )
if exist "C:\Program Files\Python313\pythonw.exe" ( set "PYW_EXE=C:\Program Files\Python313\pythonw.exe" & set "PY_EXE=C:\Program Files\Python313\python.exe" & goto :START_SERVICES )
if exist "C:\Program Files\Python312\pythonw.exe" ( set "PYW_EXE=C:\Program Files\Python312\pythonw.exe" & set "PY_EXE=C:\Program Files\Python312\python.exe" & goto :START_SERVICES )
if exist "C:\Program Files\Python311\pythonw.exe" ( set "PYW_EXE=C:\Program Files\Python311\pythonw.exe" & set "PY_EXE=C:\Program Files\Python311\python.exe" & goto :START_SERVICES )

pythonw --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYW_EXE=pythonw"
    set "PY_EXE=python"
    goto :START_SERVICES
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_EXE=python"
    set "PYW_EXE=python"
    goto :START_SERVICES
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_EXE=py"
    set "PYW_EXE=pyw"
    goto :START_SERVICES
)

:START_SERVICES
:: 2. Uruchom serwer Flask w tle
if not "%PYW_EXE%"=="" (
    start "" "%PYW_EXE%" "%~dp0launcher.pyw"
) else (
    start "" "%PY_EXE%" "%~dp0desktop_launcher.py"
)

:: 3. Odczekaj 2 sekundy na zainicjowanie portu 5000
timeout /t 2 /nobreak >nul 2>&1

:: 4. Sprawdz i uruchom tunel ngrok (jesli plik ngrok.exe istnieje)
if exist "%~dp0ngrok.exe" (
    set "DOMAIN_PARAM="
    if exist "%~dp0ngrok_domain.txt" (
        set /p NGROK_DOMAIN=<"%~dp0ngrok_domain.txt"
        if not "%NGROK_DOMAIN%"=="" (
            set DOMAIN_PARAM=--domain=%NGROK_DOMAIN%
        )
    )
    
    if "%DOMAIN_PARAM%"=="" (
        start "" /b "%~dp0ngrok.exe" http 5000 --log=stdout >nul 2>&1
    ) else (
        start "" /b "%~dp0ngrok.exe" http %DOMAIN_PARAM% 5000 --log=stdout >nul 2>&1
    )
)
