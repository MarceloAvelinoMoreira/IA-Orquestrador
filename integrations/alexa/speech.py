import html
import re
from xml.etree import ElementTree


class SpeechFormatter:
    def __init__(self, max_length: int = 7500): self.max_length = max(1, max_length)

    def format(self, value: str | None) -> str:
        text = str(value or "").strip()
        text = re.sub(r"```[\s\S]*?```", " trecho de código omitido. ", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[*_`#>~-]+", "", text)
        text = re.sub(r"\|", ", ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= self.max_length: return text or "Não recebi uma resposta útil."
        cut = text[: self.max_length]; boundary = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
        return (cut[: boundary + 1] if boundary > self.max_length // 2 else cut.rstrip() + "...")

    def ssml(self, value: str) -> str:
        raw = re.sub(r"https?://\S+", "", str(value or "")).strip()
        candidate = f"<speak>{html.escape(raw, quote=False)}</speak>"
        ElementTree.fromstring(candidate)
        return candidate
