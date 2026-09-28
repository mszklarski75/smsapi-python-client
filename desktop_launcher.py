#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMSAPI Studio Desktop Launcher
Starts the local server and automatically opens the application in your default web browser.
"""

import os
import sys
import time
import threading
import webbrowser
import socket

# Ensure local smsapi package is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import app


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def find_free_port(start_port: int = 5000) -> int:
    port = start_port
    while is_port_in_use(port) and port < 5100:
        port += 1
    return port


def open_browser(url: str):
    time.sleep(1.2)
    print(f"Otwieranie przeglądarki: {url}")
    webbrowser.open(url)


def main():
    print("=" * 60)
    print("  📱 SMSAPI Studio - Panel Zarządzania SMS / MMS / VMS / 2FA")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', find_free_port(5000)))
    url = f"http://localhost:{port}"

    # Start browser in separate thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    print(f"\n[INFO] Serwer aplikacji działa pod adresem: {url}")
    print("[INFO] Aby zakończyć działanie aplikacji, naciśnij Ctrl+C w tym oknie.\n")

    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n[INFO] Zamykanie SMSAPI Studio. Do widzenia!")
        sys.exit(0)


if __name__ == '__main__':
    main()
