from fastapi import APIRouter, HTTPException, Request
from app.config import settings
from app.engine import OrchestrationEngine
from .handler import AlexaHandler

router = APIRouter(tags=["Alexa"]); _handler = AlexaHandler(OrchestrationEngine())
@router.post("/integrations/alexa")
async def alexa_webhook(request: Request):
    if not settings.alexa_enabled: raise HTTPException(404, "Alexa integration disabled")
    try: payload = await request.json()
    except Exception as exc: raise HTTPException(400, "invalid JSON") from exc
    await _handler.security.validate(request, payload)
    return await _handler.handle(payload)
