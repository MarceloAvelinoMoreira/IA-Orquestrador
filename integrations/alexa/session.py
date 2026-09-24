from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock

@dataclass
class SessionContext:
    session_id: str
    conversation_id: str
    last_request: str = ""
    last_response: str = ""
    timestamp: str = ""

class SessionStore:
    def __init__(self): self._items: dict[str, SessionContext] = {}; self._lock = Lock()
    def get(self, session_id: str):
        with self._lock: return self._items.get(session_id)
    def update(self, session_id: str, request: str, response: str):
        with self._lock:
            current = self._items.get(session_id)
            item = SessionContext(session_id, current.conversation_id if current else session_id, request, response, datetime.now(timezone.utc).isoformat())
            self._items[session_id] = item; return item
    def clear(self, session_id: str):
        with self._lock: self._items.pop(session_id, None)
