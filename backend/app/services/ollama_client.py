import httpx
import base64
from typing import List
from app.config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama_url
        self.timeout = httpx.Timeout(float(settings.ollama_timeout))
        
    async def generate(self, model: str, prompt: str, num_predict: int = 4096) -> str:
        """Basic text generation"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": num_predict,  # Max tokens to generate
                        "num_ctx": 8192,             # Context window size
                    }
                },
            )
            response.raise_for_status()
            return response.json()["response"]
    
    async def generate_with_image(self, model: str, prompt: str, image_path: str) -> str:
        """Vision model generation with image"""
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "images": [image_b64],
                    "options": {
                        "num_predict": 2048,
                        "num_ctx": 4096,
                    }
                },
            )
            response.raise_for_status()
            return response.json()["response"]

    async def chat(self, model: str, messages: List[dict]) -> str:
        """Chat completion"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 4096,
                        "num_ctx": 8192,
                    }
                },
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

ollama = OllamaClient()