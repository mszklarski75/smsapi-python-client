#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMSAPI Studio Desktop Launcher
Starts the local server on fixed port 5000 and automatically opens default web browser.
"""

import os
import sys
import time
import threading
import webbrowser
import socket
import urllib.request
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import app

FIXED_PORT = 5000


def is_port_in_use(port: int = FIXED_PORT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def is_app_already_running(port: int = FIXED_PORT) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/heartbeat", headers={'User-Agent': 'SMSAPI-Studio-Launcher'})
        with urllib.request.urlopen(req, timeout=1.0) as response:
            return response.status == 200
    except Exception:
        return False


def free_port(port: int = FIXED_PORT):
    if sys.platform == 'win32' and is_port_in_use(port):
        try:
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            pids = set()
            for line in output.strip().split('\n'):
                parts = line.strip().split()
                if len(parts) >= 5 and f':{port}' in parts[1]:
                    pids.add(parts[-1])
            for pid in pids:
                if pid and pid != '0':
                    subprocess.call(f'taskkill /F /PID {pid} >nul 2>&1', shell=True)
            time.sleep(0.8)
        except Exception:
            pass


def open_browser(url: str):
    time.sleep(1.2)
    print(f"Otwieranie przeglądarki: {url}")
    webbrowser.open(url)


def main():
    print("=" * 60)
    print("  📱 SMSAPI Studio - Panel Zarządzania SMS / MMS / VMS / 2FA")
    print("=" * 60)

    url = f"http://localhost:{FIXED_PORT}"

    # Single-instance check
    if is_app_already_running(FIXED_PORT):
        print(f"[INFO] Aplikacja już działa pod adresem {url}. Otwieranie przeglądarki...")
        webbrowser.open(url)
        sys.exit(0)

    if is_port_in_use(FIXED_PORT):
        print(f"[INFO] Zwalnianie portu {FIXED_PORT}...")
        free_port(FIXED_PORT)

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    print(f"\n[INFO] Serwer aplikacji działa pod adresem: {url}")
    print("[INFO] Zamykanie karty przeglądarki automatycznie zakończy działanie aplikacji.\n")

    try:
        app.run(host='0.0.0.0', port=FIXED_PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n[INFO] Zamykanie SMSAPI Studio. Do widzenia!")
        sys.exit(0)


if __name__ == '__main__':
    main()
