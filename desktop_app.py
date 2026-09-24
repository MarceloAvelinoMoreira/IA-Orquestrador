"""Desktop launcher for the IA Orquestrador local application."""

import threading
import time
import webbrowser

import uvicorn

from app.api import app


def _open_browser() -> None:
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
