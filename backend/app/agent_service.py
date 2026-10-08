import httpx

from app.config import settings


class HermesAgentService:
    async def chat(self, model: str, prompt: str) -> str:
        if settings.hermes_api_url:
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        f"{settings.hermes_api_url}/api/chat",
                        json={"question": prompt, "model": model},
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        return payload.get("answer") or "No answer returned from Hermes."
            except Exception:
                pass

        return "Hermes is not available; returning a local fallback response."
