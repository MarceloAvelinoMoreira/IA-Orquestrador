import time
from collections import defaultdict, deque
from urllib.parse import urlparse
from fastapi import HTTPException, Request
from app.config import settings

class AlexaSecurity:
    def __init__(self): self._requests = defaultdict(deque)
    async def validate(self, request: Request, payload: dict) -> None:
        if not settings.alexa_require_verification: return
        skill_id = payload.get("session", {}).get("application", {}).get("applicationId", "")
        if settings.alexa_skill_id and skill_id != settings.alexa_skill_id: raise HTTPException(403, "invalid Alexa skill id")
        signature = request.headers.get("signaturechainurl"); cert = request.headers.get("signaturecertchainurl")
        if not signature or not cert: raise HTTPException(401, "Alexa verification headers are required")
        parsed = urlparse(cert)
        if parsed.scheme != "https" or parsed.hostname != "s3.amazonaws.com": raise HTTPException(401, "invalid Alexa certificate URL")
        timestamp = payload.get("request", {}).get("timestamp")
        if timestamp:
            try:
                if abs(time.time() - float(timestamp) / 1000) > 150: raise HTTPException(401, "stale Alexa request")
            except ValueError as exc: raise HTTPException(401, "invalid Alexa timestamp") from exc
    def rate_limit(self, key: str) -> None:
        now = time.time(); bucket = self._requests[key]
        while bucket and now - bucket[0] > 60: bucket.popleft()
        if len(bucket) >= settings.alexa_rate_limit_per_minute: raise HTTPException(429, "Alexa rate limit exceeded")
        bucket.append(now)
