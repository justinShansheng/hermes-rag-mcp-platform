import httpx

from app.config import settings


class LLMService:
    def __init__(self):
        self.ollama_base_url = settings.ollama_base_url
        self.openrouter_base_url = settings.openrouter_base_url
        self.openrouter_api_key = settings.openrouter_api_key

    async def generate(self, model: str, prompt: str) -> str:
        if model.startswith("openrouter/"):
            return await self._generate_via_openrouter(model=model.replace("openrouter/", ""), prompt=prompt)
        return await self._generate_via_ollama(model=model, prompt=prompt)

    async def _generate_via_ollama(self, model: str, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def _generate_via_openrouter(self, model: str, prompt: str) -> str:
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required when using cloud models.")

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
