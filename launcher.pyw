#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
SMSAPI Studio - Silent Windowless Single-Instance Launcher (.pyw)
Ensures only 1 instance runs on fixed port 5000 and cleans up stale processes.
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


def ensure_dependencies():
    for pkg in ['xlrd', 'openpyxl']:
        try:
            __import__(pkg)
        except ImportError:
            try:
                subprocess.call([sys.executable, '-m', 'pip', 'install', pkg, '--quiet'], shell=(sys.platform == 'win32'))
            except Exception:
                pass


ensure_dependencies()

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
    """If port 5000 is occupied by a dead/frozen process on Windows, terminate it."""
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
    time.sleep(1.0)
    webbrowser.open(url)


def main():
    url = f"http://localhost:{FIXED_PORT}"

    # Always clean stale instance on launch to guarantee latest code
    if is_port_in_use(FIXED_PORT):
        free_port(FIXED_PORT)

    # Open browser on launch
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # Run Flask silently on fixed port 5000
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run(host='0.0.0.0', port=FIXED_PORT, debug=False, threaded=True)


if __name__ == '__main__':
    main()
