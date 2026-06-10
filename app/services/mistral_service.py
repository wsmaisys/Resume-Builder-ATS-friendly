import json
import re
from typing import Any

import httpx

from app.config import get_settings


class MistralService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def complete_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any] | None:
        if not self.settings.mistral_api_key:
            return None

        payload = {
            "model": self.settings.mistral_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt or (
                        "You are a precise resume intelligence agent. "
                        "Return only valid JSON. Do not wrap JSON in markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.mistral_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_json(content)
        except Exception:
            return None

    def _parse_json(self, content: str) -> dict[str, Any] | None:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.S)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
