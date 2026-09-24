from typing import Any
import logging
import time
from uuid import uuid4
import httpx
from .config import settings


class OllamaError(RuntimeError):
    pass


class OllamaProvider:
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 180.0):
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout
        self.logger = logging.getLogger("ia_orquestrador.ollama")
        self.last_metrics: dict[str, Any] = {}

    def health(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.is_success
        except httpx.HTTPError:
            return False

    def chat(self, prompt: str, system: str | None = None, response_format: str | None = None) -> str:
        request_id = f"OLLAMA-{uuid4().hex[:10]}"
        started = time.perf_counter()
        messages: list[dict[str, str]] = []
        if system: messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            payload = {"model": self.model, "messages": messages, "stream": False, "think": False, "options": {"num_predict": 384}}
            if response_format: payload["format"] = response_format
            response = httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            message = data.get("message", {})
            content = message.get("content", "")
            raw_content = getattr(response, "content", b"")
            self.last_metrics = {"request_id": request_id, "operation": "chat", "model": self.model, "endpoint": "/api/chat", "duration": round(time.perf_counter() - started, 4), "http_status": getattr(response, "status_code", 200), "response_size": len(raw_content), "success": bool(content), **{key: data.get(key) for key in ("prompt_eval_count", "eval_count", "total_duration", "load_duration", "prompt_eval_duration", "eval_duration", "done_reason") if key in data}}
            self.logger.info("ollama_call %s", self.last_metrics)
            if not content: raise OllamaError(f"Ollama returned empty content: {self.last_metrics}")
            return content
        except (httpx.HTTPError, KeyError, TypeError) as exc:
            self.last_metrics = {"request_id": request_id, "operation": "chat", "model": self.model, "endpoint": "/api/chat", "duration": round(time.perf_counter() - started, 4), "success": False, "error_type": type(exc).__name__}
            self.logger.error("ollama_call %s", self.last_metrics)
            raise OllamaError(f"Ollama request failed: {exc}") from exc

    def structured(self, prompt: str, schema, system: str | None = None, retries: int = 1):
        from .structured import parse_model_output
        last = None
        for attempt in range(retries + 1):
            try:
                return parse_model_output(self.chat(prompt, system, response_format="json"), schema)
            except (ValueError, TypeError) as exc:
                last = exc
                if attempt < retries:
                    prompt += "\nReturn ONLY valid JSON matching the requested fields."
        raise OllamaError(f"Structured output validation failed: {last}") from last
