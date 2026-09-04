import httpx
from .config import settings

async def optional_ollama_summary(prompt: str):
    if not settings.enable_ollama:
        return None
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(f"{settings.ollama_base_url}/api/generate", json={"model":settings.ollama_model,"prompt":prompt,"stream":False})
        response.raise_for_status()
        return response.json().get("response")
