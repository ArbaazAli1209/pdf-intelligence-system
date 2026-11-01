"""Configurable LLM provider interface. Providers: gemini, openai_compatible (Groq, OpenRouter, ...)."""
import httpx

from app.core.config import settings


class LLMError(Exception):
    """Safe-to-display error (quota, auth, network, malformed response)."""


def _post(url: str, headers: dict, payload: dict) -> dict:
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=60)
    except httpx.HTTPError as exc:
        raise LLMError(f"Could not reach the LLM provider: {exc.__class__.__name__}") from exc
    if r.status_code == 429:
        raise LLMError("LLM rate limit or free-tier quota reached. Try again later or use extractive mode.")
    if r.status_code in (401, 403):
        raise LLMError("LLM API key was rejected. Check LLM_API_KEY.")
    if r.status_code == 404:
        raise LLMError("LLM model or endpoint not found. Check LLM_MODEL / LLM_BASE_URL.")
    if r.status_code >= 400:
        raise LLMError(f"LLM provider error (HTTP {r.status_code}).")
    try:
        return r.json()
    except ValueError as exc:
        raise LLMError("LLM provider returned an invalid response.") from exc


def _gemini(system: str, user: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.llm_model}:generateContent"
    data = _post(
        url,
        {"x-goog-api-key": settings.llm_api_key, "Content-Type": "application/json"},
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0.2},
        },
    )
    try:
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("The model returned no answer (it may have been blocked).") from exc


def _openai_compatible(system: str, user: str) -> str:
    if not settings.llm_base_url:
        raise LLMError("LLM_BASE_URL is required for the openai_compatible provider.")
    data = _post(
        f"{settings.llm_base_url}/chat/completions",
        {"Authorization": f"Bearer {settings.llm_api_key}"},
        {
            "model": settings.llm_model,
            "temperature": 0.2,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        },
    )
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise LLMError("The model returned no answer.") from exc


def generate(system: str, user: str) -> str:
    if not settings.llm_configured:
        raise LLMError("No LLM is configured (set LLM_PROVIDER and LLM_API_KEY).")
    if settings.llm_provider == "gemini":
        return _gemini(system, user)
    if settings.llm_provider == "openai_compatible":
        return _openai_compatible(system, user)
    raise LLMError(f"Unknown LLM_PROVIDER '{settings.llm_provider}'.")
