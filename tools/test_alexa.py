import asyncio
import json
import sys
from integrations.alexa.handler import AlexaHandler
from app.engine import OrchestrationEngine

def payload(text: str) -> dict:
    return {"version":"1.0","session":{"sessionId":"local-test","user":{"userId":"local-user"}},"request":{"type":"IntentRequest","requestId":"local-request","intent":{"name":"AskAIIntent","slots":{"query":{"value":text}}}}}

async def main(text: str):
    handler = AlexaHandler(OrchestrationEngine())
    print("REQUEST -> Alexa Gateway")
    response = await handler.handle(payload(text))
    print("RESPONSE ->", json.dumps(response, ensure_ascii=False))
    print("SPEECH ->", response.get("response", {}).get("outputSpeech", {}).get("text", ""))

if __name__ == "__main__": asyncio.run(main(" ".join(sys.argv[1:]) or "Explique fibrilação atrial"))
