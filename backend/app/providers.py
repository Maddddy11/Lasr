from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class ProviderResult:
    status: str
    latency_ms: int
    response: Any | None


class BaseProvider:
    name: str

    def invoke(self, model: str, prompt: str) -> ProviderResult:
        raise NotImplementedError


class LMStudioProvider(BaseProvider):
    name = "lmstudio"

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def invoke(self, model: str, prompt: str) -> ProviderResult:
        started = time.perf_counter()
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            status = "success"
        except Exception as exc:  # noqa: BLE001
            data = {"error": str(exc)}
            status = "provider_error"
        latency = int((time.perf_counter() - started) * 1000)
        return ProviderResult(status=status, latency_ms=latency, response=data)


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def invoke(self, model: str, prompt: str) -> ProviderResult:
        started = time.perf_counter()
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            status = "success"
        except Exception as exc:  # noqa: BLE001
            data = {"error": str(exc)}
            status = "provider_error"
        latency = int((time.perf_counter() - started) * 1000)
        return ProviderResult(status=status, latency_ms=latency, response=data)


class GroqProvider(BaseProvider):
    name = "groq"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def invoke(self, model: str, prompt: str) -> ProviderResult:
        started = time.perf_counter()
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            status = "success"
        except Exception as exc:  # noqa: BLE001
            data = {"error": str(exc)}
            status = "provider_error"
        latency = int((time.perf_counter() - started) * 1000)
        return ProviderResult(status=status, latency_ms=latency, response=data)
