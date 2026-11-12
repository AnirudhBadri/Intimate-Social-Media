"""Task Script: launch_den_server.py
Launches The Den small social media server on port 8090.
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import uvicorn
from den_prototype.app import create_app

app = create_app()

if __name__ == "__main__":
    print("[*] Starting The Den Server on http://127.0.0.1:8090 ...")
    uvicorn.run(app, host="127.0.0.1", port=8090, log_level="info")
