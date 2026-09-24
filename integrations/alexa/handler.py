import logging
from typing import Any
from fastapi import HTTPException
from app.engine import OrchestrationEngine
from .schemas import AlexaRequest
from .security import AlexaSecurity
from .service import AlexaService

log = logging.getLogger("alexa.gateway")
class AlexaHandler:
    def __init__(self, engine: OrchestrationEngine): self.service = AlexaService(engine); self.security = AlexaSecurity()
    async def handle(self, payload: dict[str, Any]):
        request = AlexaRequest.model_validate(payload); self.security.rate_limit(request.user_id or request.session_id)
        intent = request.intent_name
        if request.request_type == "LaunchRequest": return self._response("Marcelo IA conectado. O que deseja?", True)
        if request.request_type == "SessionEndedRequest": self.service.sessions.clear(request.session_id); return {"version": "1.0", "response": {}}
        if intent in {"StopIntent", "CancelIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"}: return self._response("Até logo.", False)
        if intent in {"HelpIntent", "AMAZON.HelpIntent"}: return self._response("Você pode pedir para eu explicar um assunto, verificar o sistema ou consultar uma tarefa.", True)
        if intent in {"FallbackIntent", "AMAZON.FallbackIntent"}: return self._response("Não entendi. Diga, por exemplo: explique fibrilação atrial.", True)
        if intent == "SystemStatusIntent": return self._response("O IA Orquestrador está disponível localmente.", True)
        if intent == "TaskStatusIntent": return self._response("As tarefas são acompanhadas pelo IA Orquestrador. Consulte o painel local para detalhes.", True)
        if intent == "LastResultIntent": return self._response("O último resultado fica disponível no painel do IA Orquestrador.", True)
        if intent != "AskAIIntent": raise HTTPException(400, "unsupported Alexa intent")
        query = request.slot_value("query")
        if not query or len(query) > 12000: raise HTTPException(422, "query is required and must be limited")
        try:
            answer, latency = await self.service.ask(query, request.session_id)
            log.info("alexa request_id=%s session_id=%s intent=%s latency=%.3f status=ok", request.request.get("requestId"), request.session_id, intent, latency)
            return self._response(answer, True)
        except TimeoutError: return self._response("A solicitação demorou mais que o limite de voz. Tente novamente em alguns instantes.", False)
        except Exception:
            log.exception("Alexa orchestration failed"); return self._response("Não consegui consultar o IA Orquestrador agora.", False)
    @staticmethod
    def _response(text: str, reprompt: bool):
        response = {"outputSpeech": {"type": "PlainText", "text": text}, "shouldEndSession": not reprompt}
        if reprompt: response["reprompt"] = {"outputSpeech": {"type": "PlainText", "text": "Como posso ajudar?"}}
        return {"version": "1.0", "response": response}
