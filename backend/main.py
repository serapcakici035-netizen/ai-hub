import os
import time
from collections import defaultdict, deque
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ROOT = Path(__file__).resolve().parent.parent
MODELS = {
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
    "huggingface": ["Qwen/Qwen3-4B-Thinking-2507"],
    "gemini": ["gemini-2.5-flash", "gemini-2.5-flash-lite"],
}
URLS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "huggingface": "https://router.huggingface.co/v1/chat/completions",
}
ENV_KEYS = {"groq": "GROQ_API_KEY", "huggingface": "HF_TOKEN", "gemini": "GEMINI_API_KEY"}
hits: dict[str, deque[float]] = defaultdict(deque)
app = FastAPI(title="AI Hub")


class ChatRequest(BaseModel):
    provider: str
    model: str
    prompt: str = Field(min_length=1, max_length=12000)


@app.get("/")
async def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/api/models")
async def models():
    return MODELS


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request, x_api_key: str | None = Header(default=None)):
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

    key = (x_api_key or "").strip() or os.getenv(ENV_KEYS[body.provider], "").strip()
    if not key:
        raise HTTPException(503, "Bu sağlayıcı için API anahtarı tanımlı değil.")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            if body.provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{body.model}:generateContent"
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": key},
                    json={"contents": [{"parts": [{"text": body.prompt}]}]},
                )
            else:
                response = await client.post(
                    URLS[body.provider],
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": body.model, "messages": [{"role": "user", "content": body.prompt}]},
                )
            response.raise_for_status()
            data = response.json()
            if body.provider == "gemini":
                parts = data["candidates"][0]["content"]["parts"]
                answer = "".join(part.get("text", "") for part in parts)
            else:
                answer = data["choices"][0]["message"]["content"]
            if not answer:
                raise ValueError("empty response")
            return {"provider": body.provider, "model": body.model, "answer": answer}
    except httpx.HTTPStatusError as exc:
        # Sağlayıcı gövdesini döndürmeyin: hata metni hassas bilgi içerebilir.
        raise HTTPException(502, f"Sağlayıcı isteği başarısız (HTTP {exc.response.status_code}).") from exc
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError) as exc:
        raise HTTPException(502, "Sağlayıcı yanıtı alınamadı veya çözümlenemedi.") from exc
