import httpx
import pytest
from app.providers import OllamaError, OllamaProvider


def test_provider_parses_chat(monkeypatch):
    class Response:
        def raise_for_status(self): pass
        def json(self): return {"message": {"content": "resposta"}}
    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: Response())
    assert OllamaProvider().chat("oi") == "resposta"


def test_provider_errors_are_wrapped(monkeypatch):
    def fail(*args, **kwargs): raise httpx.ConnectError("offline")
    monkeypatch.setattr(httpx.Client, "post", fail)
    with pytest.raises(OllamaError): OllamaProvider().chat("oi")
