#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMSAPI Studio - PyInstaller Exe Builder
Creates a standalone executable (.exe for Windows or binary for Linux/Mac)
that includes all dependencies, templates, and libraries.
"""

import os
import sys
import subprocess
import shutil

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("=" * 60)
    print(" 🛠️  Budowanie pliku wykonywalnego SMSAPI Studio...")
    print("=" * 60)

    # PyInstaller arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SMSAPI_Studio",
        "--onedir",  # or --onefile
        "--windowed", # on Windows, avoids showing black console window, or remove if console is desired
        f"--add-data={os.path.join(CURRENT_DIR, 'templates')}:templates",
        f"--add-data={os.path.join(CURRENT_DIR, 'smsapi')}:smsapi",
        "--hidden-import=smsapi",
        "--hidden-import=requests",
        "--hidden-import=flask",
        "--hidden-import=jinja2",
        "--hidden-import=openpyxl",
        "--hidden-import=sqlite3",
        os.path.join(CURRENT_DIR, "desktop_launcher.py")
    ]

    # Adjust separator for Windows if building on Windows
    if os.name == 'nt':
        cmd[4] = f"--add-data={os.path.join(CURRENT_DIR, 'templates')};templates"
        cmd[5] = f"--add-data={os.path.join(CURRENT_DIR, 'smsapi')};smsapi"

    print("Uruchamianie polecenia:\n", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print(" ✅ SUKCES! Aplikacja została zbudowana w katalogu 'dist/SMSAPI_Studio'")
        print(" Możesz uruchomić plik 'SMSAPI_Studio' (lub 'SMSAPI_Studio.exe' na Windows).")
        print("=" * 60)
    else:
        print("\n❌ Błąd podczas budowania pliku wykonywalnego.", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    build()
