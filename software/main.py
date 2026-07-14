# -------------------------
# Starting the backend and frontend
# -------------------------
import threading
import subprocess
from pathlib import Path
from backend.app import app

BASE_DIR = Path(__file__).resolve().parent

def start_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

threading.Thread(target=start_flask, daemon=True).start()

subprocess.run([
    "streamlit",
    "run",
    str(BASE_DIR / "frontend" / "dashboard.py")
])