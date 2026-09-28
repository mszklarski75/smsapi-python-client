#!/usr/bin/env bash
# SMSAPI Studio Launcher for Linux / macOS

echo "================================================================"
echo "   SMSAPI Studio - Aplikacja do wysyłki SMS / MMS / VMS / 2FA"
echo "================================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[BŁĄD] Python3 nie został znaleziony!"
    exit 1
fi

echo "[1/2] Sprawdzanie bibliotek..."
python3 -m pip install -r requirements_app.txt --quiet --disable-pip-version-check 2>/dev/null || true

echo "[2/2] Uruchamianie aplikacji..."
echo ""
python3 desktop_launcher.py
