import time
import pytest
from fastapi.testclient import TestClient
from app.api import app
from integrations.alexa.handler import AlexaHandler
from integrations.alexa.speech import SpeechFormatter
from app.config import settings

client = TestClient(app)

def base(request_type="LaunchRequest", intent=None):
    body = {"version":"1.0","session":{"sessionId":"s1","user":{"userId":"u1"}},"request":{"type":request_type,"requestId":"r1"}}
    if intent: body["request"]["intent"] = intent
    return body

def test_launch():
    response = client.post('/integrations/alexa', json=base())
    assert response.status_code == 200
    assert "Marcelo IA conectado" in response.json()["response"]["outputSpeech"]["text"]

@pytest.mark.anyio
async def test_ask_ai_session_and_context(monkeypatch):
    handler = AlexaHandler.__new__(AlexaHandler)
    from integrations.alexa.security import AlexaSecurity
    from integrations.alexa.service import AlexaService
    handler.security = AlexaSecurity(); handler.service = AlexaService(object())
    calls = []
    async def ask(text, session): calls.append(text); return ("Resposta com markdown", 0.01)
    monkeypatch.setattr(handler.service, 'ask', ask)
    first = await handler.handle(base('IntentRequest', {'name':'AskAIIntent','slots':{'query':{'value':'quem foi Alan Turing'}}}))
    second = await handler.handle({**base('IntentRequest', {'name':'AskAIIntent','slots':{'query':{'value':'quando ele nasceu'}}}), 'request': {**base('IntentRequest', {'name':'AskAIIntent','slots':{'query':{'value':'quando ele nasceu'}}})['request']}})
    assert first['response']['shouldEndSession'] is False
    assert len(calls) == 2

def test_standard_intents():
    for name in ('AMAZON.HelpIntent','AMAZON.StopIntent','AMAZON.FallbackIntent','SystemStatusIntent','TaskStatusIntent','LastResultIntent'):
        response = client.post('/integrations/alexa', json=base('IntentRequest', {'name':name,'slots':{}}))
        assert response.status_code == 200

def test_invalid_request():
    assert client.post('/integrations/alexa', json={'request': {}}).status_code == 400
    assert client.post('/integrations/alexa', data='not-json').status_code == 400

def test_speech_formatter():
    formatter = SpeechFormatter(30)
    assert 'http' not in formatter.format('**Olá** https://example.com')
    assert formatter.ssml('<teste>') == '<speak>&lt;teste&gt;</speak>'
    assert len(formatter.format('a' * 100)) <= 33

def test_security_verification(monkeypatch):
    monkeypatch.setattr(settings, 'alexa_require_verification', True)
    try:
        assert client.post('/integrations/alexa', json=base()).status_code == 401
    finally:
        monkeypatch.setattr(settings, 'alexa_require_verification', False)
