import os
import time
from collections import defaultdict, deque
from itertools import cycle
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ROOT = Path(__file__).resolve().parent.parent
MODELS = {"groq": ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]}
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
groq_keys = [key.strip() for key in os.getenv("GROQ_API_KEYS", "").split(",") if key.strip()]
groq_key_cycle = cycle(groq_keys) if groq_keys else None
hits: dict[str, deque[float]] = defaultdict(deque)
app = FastAPI(title="AI Hub")


class ChatRequest(BaseModel):
    provider: str
    model: str
    prompt: str = Field(min_length=1, max_length=12000)


@app.get("/")
async def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/styles.css")
async def styles():
    return FileResponse(ROOT / "frontend" / "styles.css", media_type="text/css")


@app.get("/api/models")
async def models():
    return MODELS


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request):
    if body.provider not in MODELS or body.model not in MODELS[body.provider]:
        raise HTTPException(400, "Geçersiz sağlayıcı veya model.")

    # Reverse proxy kullanılıyorsa güvenilir proxy yapılandırmasını sunucuda yapın.
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = hits[ip]
    while bucket and now - bucket[0] >= 60:
        bucket.popleft()
    if len(bucket) >= 5:
        raise HTTPException(429, "Dakikada en fazla 5 istek gönderebilirsiniz.")
    bucket.append(now)

    key = next(groq_key_cycle) if groq_key_cycle is not None else os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise HTTPException(503, "Groq API anahtarı tanımlı değil.")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {key}"},
                json={"model": body.model, "messages": [{"role": "user", "content": body.prompt}]},
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            if not answer:
                raise ValueError("empty response")
            return {"provider": body.provider, "model": body.model, "answer": answer}
    except httpx.HTTPStatusError as exc:
        # Sağlayıcı gövdesini döndürmeyin: hata metni hassas bilgi içerebilir.
        if exc.response.status_code == 429:
            raise HTTPException(429, "Sağlayıcı kotası dolu veya istek sınırına ulaşıldı.") from exc
        if exc.response.status_code in (401, 403):
            raise HTTPException(502, "Sağlayıcı API anahtarını kabul etmedi veya model erişimine izin vermedi.") from exc
        raise HTTPException(502, f"Sağlayıcı isteği başarısız (HTTP {exc.response.status_code}).") from exc
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError) as exc:
        raise HTTPException(502, "Sağlayıcı yanıtı alınamadı veya çözümlenemedi.") from exc
