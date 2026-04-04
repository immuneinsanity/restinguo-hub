"""
Two-tier AI drafting pipeline.
  Tier 1 — Mistral via Ollama: summarize docs, extract facts, generate rough outline
  Tier 2 — Claude API: final polished section draft
"""

import os
import httpx
import anthropic
from typing import Generator

from .prompts import (
    COMPANY_CONTEXT,
    MISTRAL_SUMMARIZE_DOCS,
    MISTRAL_EXTRACT_FACTS,
    MISTRAL_OUTLINE,
    SECTION_PROMPTS,
    SECTION_LABELS,
)


# ── Mistral / Ollama client ─────────────────────────────────────────────────

class MistralClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")

    def _generate(self, prompt: str, timeout: int = 60) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except httpx.ConnectError:
            return "[Ollama not available — skipping Mistral preprocessing]"
        except Exception as e:
            return f"[Mistral error: {e}]"

    def summarize(self, source_text: str) -> str:
        prompt = MISTRAL_SUMMARIZE_DOCS.format(source_text=source_text[:4000])
        return self._generate(prompt)

    def extract_facts(self, source_text: str) -> str:
        prompt = MISTRAL_EXTRACT_FACTS.format(source_text=source_text[:4000])
        return self._generate(prompt)

    def outline(self, section: str, additional_notes: str = "") -> str:
        prompt = MISTRAL_OUTLINE.format(
            section=SECTION_LABELS.get(section, section),
            company_context=COMPANY_CONTEXT,
            additional_notes=additional_notes or "None provided.",
        )
        return self._generate(prompt, timeout=90)

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


# ── Claude / Anthropic client ───────────────────────────────────────────────

class AnthropicClient:
    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        self.client = anthropic.Anthropic(api_key=key)
        self.model = "claude-sonnet-4-6"

    def draft_section(
        self,
        section: str,
        preprocessed: str,
        additional_notes: str = "",
        stream: bool = True,
    ) -> Generator[str, None, None] | str:
        template = SECTION_PROMPTS.get(section)
        if not template:
            raise ValueError(f"Unknown section: {section}")

        prompt = template.format(
            company_context=COMPANY_CONTEXT,
            preprocessed=preprocessed,
            additional_notes=additional_notes or "None provided.",
        )

        if stream:
            return self._stream(prompt)
        else:
            return self._complete(prompt)

    def _stream(self, prompt: str) -> Generator[str, None, None]:
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _complete(self, prompt: str) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text


# ── Pipeline orchestration ──────────────────────────────────────────────────

class DraftingPipeline:
    """
    Orchestrates the two-tier pipeline:
      1. Mistral preprocesses (outline + optional fact extraction from docs)
      2. Claude drafts the final section
    """

    def __init__(self):
        self.mistral = MistralClient()
        self._anthropic: AnthropicClient | None = None

    @property
    def anthropic(self) -> AnthropicClient:
        if self._anthropic is None:
            self._anthropic = AnthropicClient()
        return self._anthropic

    def preprocess(self, section: str, source_docs: str = "", additional_notes: str = "") -> str:
        """Run Mistral preprocessing. Returns combined preprocessed context."""
        parts = []

        outline = self.mistral.outline(section, additional_notes)
        parts.append(f"=== Rough Outline (Mistral) ===\n{outline}")

        if source_docs.strip():
            facts = self.mistral.extract_facts(source_docs)
            parts.append(f"=== Extracted Facts (Mistral) ===\n{facts}")

        return "\n\n".join(parts)

    def draft(
        self,
        section: str,
        source_docs: str = "",
        additional_notes: str = "",
        skip_mistral: bool = False,
    ) -> Generator[str, None, None]:
        """
        Full pipeline: preprocess with Mistral, then stream Claude final draft.
        Yields text chunks for Streamlit streaming display.
        """
        if skip_mistral or not self.mistral.is_available():
            preprocessed = (
                f"[Mistral unavailable — using direct context]\n\n"
                f"Section: {SECTION_LABELS.get(section, section)}\n"
                f"User notes: {additional_notes or 'None'}\n"
                f"Source docs provided: {'Yes' if source_docs.strip() else 'No'}"
            )
        else:
            preprocessed = self.preprocess(section, source_docs, additional_notes)

        yield from self.anthropic.draft_section(
            section=section,
            preprocessed=preprocessed,
            additional_notes=additional_notes,
            stream=True,
        )
