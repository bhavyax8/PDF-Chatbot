# start.py
import os
import sys

port = int(os.environ.get("PORT", 10000))
print(f"=== START.PY RUNNING ===", flush=True)
print(f"=== PORT = {port} ===", flush=True)
print(f"=== Python = {sys.version} ===", flush=True)

import uvicorn
print(f"=== uvicorn imported successfully ===", flush=True)

uvicorn.run(
    "api.main:app",
    host="0.0.0.0",
    port=port,
    log_level="debug"
)