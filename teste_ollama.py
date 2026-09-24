import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "system",
            "content": (
                "Você está sendo executado localmente em um computador Windows "
                "através do Ollama. Você é o modelo local do projeto IA Orquestrador. "
                "Responda em português."
            ),
        },
        {
            "role": "user",
            "content": "Quem é você, onde está sendo executado e qual será sua função?"
        },
    ],
    "stream": False,
}

print("Conectando ao Ollama...")

response = httpx.post(
    OLLAMA_URL,
    json=payload,
    timeout=120.0,
)

response.raise_for_status()

data = response.json()

print("\n=== RESPOSTA DO MODELO ===\n")
print(data["message"]["content"])