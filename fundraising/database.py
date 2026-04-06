"""
Supabase CRUD for fundraising tables: investors, interactions, funding events, comparables.
"""

import os
from datetime import datetime
from supabase import create_client, Client
import streamlit as st


def _cfg(key: str, default: str = "") -> str:
    try:
        v = st.secrets.get(key)
        if v is not None:
            return str(v)
    except Exception:
        pass
    try:
        v = st.session_state.get(key)
        if v:
            return str(v)
    except Exception:
        pass
    return os.getenv(key, default)


_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = _cfg("SUPABASE_URL")
        key = _cfg("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required.")
        _client = create_client(url, key)
    return _client


# ── Investors ──────────────────────────────────────────────────────────────

def get_all_investors(status: str = None) -> list[dict]:
    db = get_client()
    q = db.table("investors").select("*").order("priority", desc=False).order("firm")
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


def get_investor(investor_id: str) -> dict | None:
    db = get_client()
    res = db.table("investors").select("*").eq("id", investor_id).execute()
    return res.data[0] if res.data else None


def save_investor(data: dict) -> dict:
    db = get_client()
    data["updated_at"] = datetime.utcnow().isoformat()
    res = db.table("investors").insert(data).execute()
    return res.data[0]


def update_investor(investor_id: str, updates: dict) -> dict:
    db = get_client()
    updates["updated_at"] = datetime.utcnow().isoformat()
    res = db.table("investors").update(updates).eq("id", investor_id).execute()
    return res.data[0]


def delete_investor(investor_id: str):
    db = get_client()
    db.table("investor_interactions").delete().eq("investor_id", investor_id).execute()
    db.table("investors").delete().eq("id", investor_id).execute()


# ── Interactions ───────────────────────────────────────────────────────────

def get_interactions(investor_id: str) -> list[dict]:
    db = get_client()
    return db.table("investor_interactions").select("*").eq("investor_id", investor_id).order("date", desc=True).execute().data or []


def save_interaction(data: dict) -> dict:
    db = get_client()
    res = db.table("investor_interactions").insert(data).execute()
    return res.data[0]


def delete_interaction(interaction_id: str):
    db = get_client()
    db.table("investor_interactions").delete().eq("id", interaction_id).execute()


# ── Funding Events ─────────────────────────────────────────────────────────

def get_funding_events() -> list[dict]:
    db = get_client()
    return db.table("funding_events").select("*").order("date", desc=True).execute().data or []


def save_funding_event(data: dict) -> dict:
    db = get_client()
    res = db.table("funding_events").insert(data).execute()
    return res.data[0]


# ── Comparables ────────────────────────────────────────────────────────────

def get_comparables() -> list[dict]:
    db = get_client()
    return db.table("comparables").select("*").order("year", desc=True).execute().data or []


def save_comparable(data: dict) -> dict:
    db = get_client()
    res = db.table("comparables").insert(data).execute()
    return res.data[0]


# ── Pipeline metrics ───────────────────────────────────────────────────────

def get_pipeline_metrics() -> dict:
    db = get_client()
    investors = db.table("investors").select("status").execute().data or []
    counts = {}
    for inv in investors:
        s = inv.get("status", "Unknown")
        counts[s] = counts.get(s, 0) + 1
    return counts
