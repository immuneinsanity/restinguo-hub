"""
Three-tier AI routing:
  Mistral (Ollama, localhost:11434) → preprocess/summarize raw input
  Claude Sonnet (claude-sonnet-4-6) → UI text, formatting, summaries
  Claude Opus (claude-opus-4-5) → all core scientific reasoning
"""

import json
import os
import httpx
import streamlit as st
import anthropic
from scientist.prompts import MISTRAL_PREPROCESS_PROMPT, MISTRAL_CHUNK_PROMPT

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

OPUS_MODEL = "claude-opus-4-5"
SONNET_MODEL = "claude-sonnet-4-6"

def _get_config(key: str, default: str = "") -> str:
    """Read from Streamlit secrets, then env, then default."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


def _anthropic_client() -> anthropic.Anthropic:
    api_key = _get_config("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in secrets or environment")
    return anthropic.Anthropic(api_key=api_key)


def _ollama_url() -> str:
    return _get_config("OLLAMA_URL", "http://localhost:11434")


def _ollama_model() -> str:
    return _get_config("OLLAMA_MODEL", "mistral")


# ─────────────────────────────────────────────
# Tier 1 — Mistral (Ollama): preprocess raw text
# ─────────────────────────────────────────────

def preprocess_with_mistral(text: str, mode: str = "summarize") -> str:
    """
    Use local Mistral to condense/preprocess raw text before sending to Opus.
    Falls back to the original text if Ollama is unavailable.
    mode: 'summarize' | 'chunk'
    """
    if not text or not text.strip():
        return text

    prompt = (
        MISTRAL_PREPROCESS_PROMPT.format(text=text)
        if mode == "summarize"
        else MISTRAL_CHUNK_PROMPT.format(text=text)
    )

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{_ollama_url()}/api/generate",
                json={
                    "model": _ollama_model(),
                    "prompt": prompt,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return resp.json().get("response", text)
    except Exception:
        # Ollama unavailable — pass text through unmodified
        return text


def mistral_available() -> bool:
    """Check if local Ollama/Mistral is reachable."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{_ollama_url()}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────
# Tier 2 — Claude Sonnet: formatting + summaries
# ─────────────────────────────────────────────

def sonnet(
    user_prompt: str,
    system_prompt: str,
    max_tokens: int = 1024,
) -> str:
    """Call Claude Sonnet for UI text, formatting, routine summaries."""
    client = _anthropic_client()
    msg = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return msg.content[0].text


# ─────────────────────────────────────────────
# Tier 3 — Claude Opus: core scientific reasoning
# ─────────────────────────────────────────────

def opus(
    user_prompt: str,
    system_prompt: str,
    max_tokens: int = 4096,
    preprocess: bool = False,
) -> str:
    """
    Call Claude Opus for scientific reasoning.
    If preprocess=True, run user_prompt through Mistral first to reduce tokens.
    """
    if preprocess:
        user_prompt = preprocess_with_mistral(user_prompt)

    client = _anthropic_client()
    msg = client.messages.create(
        model=OPUS_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return msg.content[0].text


def opus_json(
    user_prompt: str,
    system_prompt: str,
    max_tokens: int = 4096,
    preprocess: bool = False,
) -> dict:
    """
    Call Opus and parse the response as JSON.
    Returns the parsed dict, or {'error': ..., 'raw': ...} on parse failure.
    """
    raw = opus(user_prompt, system_prompt, max_tokens, preprocess)

    # Strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove opening fence (```json or ```)
        lines = lines[1:]
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON object from the text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
        return {"error": "Failed to parse JSON response", "raw": raw}


# ─────────────────────────────────────────────
# Streaming variants for long Opus calls
# ─────────────────────────────────────────────

def opus_stream(
    user_prompt: str,
    system_prompt: str,
    max_tokens: int = 4096,
    preprocess: bool = False,
):
    """
    Stream Opus response. Yields text chunks.
    Usage: for chunk in opus_stream(...): print(chunk, end='')
    """
    if preprocess:
        user_prompt = preprocess_with_mistral(user_prompt)

    client = _anthropic_client()
    with client.messages.stream(
        model=OPUS_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def sonnet_stream(
    user_prompt: str,
    system_prompt: str,
    max_tokens: int = 2048,
):
    """Stream Sonnet response."""
    client = _anthropic_client()
    with client.messages.stream(
        model=SONNET_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
