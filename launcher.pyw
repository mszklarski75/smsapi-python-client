#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
SMSAPI Studio - Silent Windowless Launcher (.pyw)
Runs with pythonw (no black terminal window on Windows).
"""

import os
import sys
import time
import threading
import webbrowser
import socket

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
    time.sleep(1.0)
    webbrowser.open(url)


def main():
    port = int(os.environ.get('PORT', find_free_port(5000)))
    url = f"http://localhost:{port}"

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # Run silently
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
