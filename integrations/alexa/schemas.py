from typing import Any
from pydantic import BaseModel, Field


class AlexaRequest(BaseModel):
    version: str = "1.0"
    session: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    request: dict[str, Any]

    @property
    def request_type(self) -> str: return str(self.request.get("type", ""))
    @property
    def intent_name(self) -> str: return str(self.request.get("intent", {}).get("name", ""))
    @property
    def session_id(self) -> str: return str(self.session.get("sessionId", "anonymous"))
    @property
    def user_id(self) -> str: return str(self.session.get("user", {}).get("userId", ""))

    def slot_value(self, name: str) -> str:
        value = self.request.get("intent", {}).get("slots", {}).get(name, {})
        return str(value.get("value", "")).strip() if isinstance(value, dict) else ""
