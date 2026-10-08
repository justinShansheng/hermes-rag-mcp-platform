import logging
from typing import Literal
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class LLMRouter:
    """Route requests to local Ollama or cloud OpenRouter"""

    def __init__(self):
        self.ollama_url = settings.ollama_base_url
        self.openrouter_url = settings.openrouter_base_url
        self.openrouter_key = settings.openrouter_api_key

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using the appropriate model"""
        if model.startswith("openrouter/"):
            return await self._call_openrouter(
                model=model.replace("openrouter/", ""),
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        return await self._call_ollama(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def _call_ollama(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call local Ollama instance"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "top_p": 0.9,
                            "num_predict": max_tokens,
                        },
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return "Error: Ollama failed to generate response."
        except httpx.TimeoutException:
            return "Error: Ollama request timed out."
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error: {str(e)}"

    async def _call_openrouter(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call OpenRouter cloud API"""
        if not self.openrouter_key:
            return "Error: OPENROUTER_API_KEY not configured."

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://hermes-rag.local",
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.openrouter_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenRouter error: {response.status_code} {response.text}")
                    return "Error: OpenRouter API failed."
        except httpx.TimeoutException:
            return "Error: OpenRouter request timed out."
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return f"Error: {str(e)}"

    async def stream_generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
    ):
        """Stream generation (yields chunks)"""
        if model.startswith("openrouter/"):
            yield "Streaming not yet supported for cloud models."
        else:
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream(
                        "POST",
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": model,
                            "prompt": prompt,
                            "stream": True,
                            "options": {"temperature": temperature},
                        },
                    ) as response:
                        async for line in response.aiter_lines():
                            if line:
                                import json

                                chunk = json.loads(line)
                                yield chunk.get("response", "")
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"Error: {str(e)}"
