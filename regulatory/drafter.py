"""
AI drafting pipeline: Mistral (Ollama) for preprocessing + Claude for final output.
"""

import os
import httpx
import anthropic
from dotenv import load_dotenv

from .prompts import (
    SYSTEM_REGULATORY_STRATEGIST,
    MISTRAL_SUMMARIZE_PROMPT,
    CLAUDE_STRATEGY_MEMO_PROMPT,
    CLAUDE_PRE_IND_AGENDA_PROMPT,
    CLAUDE_ODD_NARRATIVE_PROMPT,
    CLAUDE_GENERAL_QUERY_PROMPT,
)

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
CLAUDE_MODEL = "claude-sonnet-4-6"


# --- Mistral via Ollama ---

def mistral_summarize(text: str, timeout: int = 60) -> tuple[str, str | None]:
    """
    Summarize text using Mistral via Ollama.
    Returns (summary, error_message). If error, summary is empty string.
    """
    prompt = MISTRAL_SUMMARIZE_PROMPT.format(text=text[:8000])  # cap input
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", ""), None
    except httpx.ConnectError:
        return "", f"Ollama not running at {OLLAMA_URL}. Start Ollama and pull the {OLLAMA_MODEL} model."
    except httpx.TimeoutException:
        return "", "Mistral request timed out. Try a shorter document."
    except Exception as e:
        return "", f"Mistral error: {str(e)}"


def check_ollama_available() -> tuple[bool, str]:
    """Check if Ollama is running and the model is available."""
    try:
        response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = [m["name"] for m in response.json().get("models", [])]
        model_available = any(OLLAMA_MODEL in m for m in models)
        if not model_available:
            return False, f"Ollama is running but model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}"
        return True, "Ollama available"
    except Exception:
        return False, f"Ollama not reachable at {OLLAMA_URL}"


# --- Claude via Anthropic SDK ---

def _get_claude_client() -> anthropic.Anthropic | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_anthropic_api_key_here":
        return None
    return anthropic.Anthropic(api_key=api_key)


def claude_draft(prompt: str, stream_callback=None) -> tuple[str, str | None]:
    """
    Draft content using Claude.
    If stream_callback is provided, streams chunks to it.
    Returns (full_text, error_message).
    """
    client = _get_claude_client()
    if client is None:
        return "", "ANTHROPIC_API_KEY not configured. Add it to your .env file."

    try:
        if stream_callback:
            full_text = ""
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                system=SYSTEM_REGULATORY_STRATEGIST,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text_chunk in stream.text_stream:
                    full_text += text_chunk
                    stream_callback(text_chunk)
            return full_text, None
        else:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                system=SYSTEM_REGULATORY_STRATEGIST,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text, None
    except anthropic.AuthenticationError:
        return "", "Invalid ANTHROPIC_API_KEY. Check your .env file."
    except anthropic.APIError as e:
        return "", f"Claude API error: {str(e)}"
    except Exception as e:
        return "", f"Unexpected error: {str(e)}"


# --- Two-tier pipeline ---

def run_pipeline_strategy_memo(
    document_text: str,
    user_request: str,
    stream_callback=None,
) -> tuple[str, str | None, str]:
    """
    Two-tier pipeline: Mistral summarizes document -> Claude drafts strategy memo.
    Returns (result, error, mistral_summary).
    """
    # Tier 1: Mistral
    mistral_summary, err = mistral_summarize(document_text)
    if err:
        mistral_summary = f"[Mistral unavailable — {err}]\n\nRaw document excerpt:\n{document_text[:1500]}"

    # Tier 2: Claude
    claude_prompt = CLAUDE_STRATEGY_MEMO_PROMPT.format(
        mistral_summary=mistral_summary,
        user_request=user_request,
    )
    result, claude_err = claude_draft(claude_prompt, stream_callback=stream_callback)
    return result, claude_err, mistral_summary


def run_pipeline_pre_ind_agenda(
    focus_areas: str,
    additional_context: str = "",
    stream_callback=None,
) -> tuple[str, str | None]:
    """Draft a Pre-IND meeting agenda via Claude."""
    prompt = CLAUDE_PRE_IND_AGENDA_PROMPT.format(
        focus_areas=focus_areas,
        additional_context=additional_context,
    )
    return claude_draft(prompt, stream_callback=stream_callback)


def run_pipeline_odd_narrative(
    user_notes: str,
    stream_callback=None,
) -> tuple[str, str | None]:
    """Draft an ODD prevalence/medical plausibility narrative via Claude."""
    prompt = CLAUDE_ODD_NARRATIVE_PROMPT.format(user_notes=user_notes)
    return claude_draft(prompt, stream_callback=stream_callback)


def run_general_query(
    question: str,
    context: str = "",
    stream_callback=None,
) -> tuple[str, str | None]:
    """Answer a general regulatory strategy question via Claude."""
    prompt = CLAUDE_GENERAL_QUERY_PROMPT.format(
        question=question,
        context=context if context else "No additional context provided.",
    )
    return claude_draft(prompt, stream_callback=stream_callback)
