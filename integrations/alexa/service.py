import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from app.config import settings
from app.engine import OrchestrationEngine
from app.schemas import OrchestrationRequest
from .session import SessionStore
from .speech import SpeechFormatter

class AlexaService:
    def __init__(self, engine: OrchestrationEngine):
        self.engine = engine; self.sessions = SessionStore(); self.speech = SpeechFormatter(settings.alexa_max_response_length)
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="alexa")
    async def ask(self, text: str, session_id: str):
        previous = self.sessions.get(session_id); prompt = text
        if previous and previous.last_request: prompt = f"Contexto anterior: {previous.last_request}\nResposta anterior: {previous.last_response}\nNova pergunta: {text}"
        started = time.perf_counter(); loop = asyncio.get_running_loop()
        request = OrchestrationRequest(request=prompt, execution_mode="local")
        result = await asyncio.wait_for(loop.run_in_executor(self.executor, lambda: self.engine.execute(request, use_ollama=True)), settings.alexa_request_timeout)
        answer = result.get("final_report", {}).get("final_response") or result.get("answer") or result.get("final_response")
        if not answer: raise RuntimeError("empty orchestrator response")
        speech = self.speech.format(answer); self.sessions.update(session_id, text, speech)
        return speech, round(time.perf_counter() - started, 3)
