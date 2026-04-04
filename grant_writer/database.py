"""
Supabase (PostgreSQL) grant database — stores draft sections and versions.
"""

import os
import warnings
from datetime import datetime

from supabase import create_client, Client


def _cfg(key: str, default: str = "") -> str:
    """Read from st.secrets first (Streamlit Cloud), then os.environ (.env locally)."""
    try:
        import streamlit as st
        v = st.secrets.get(key)
        if v is not None:
            return str(v)
    except Exception:
        pass
    return os.getenv(key, default)


_client: Client | None = None


def _get_supabase() -> Client:
    global _client
    if _client is None:
        url = _cfg("SUPABASE_URL")
        key = _cfg("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .streamlit/secrets.toml or .env"
            )
        _client = create_client(url, key)
    return _client


def init_db() -> None:
    """Create all tables if they don't exist yet (requires DATABASE_URL + psycopg2)."""
    database_url = _cfg("DATABASE_URL")
    if not database_url:
        warnings.warn(
            "DATABASE_URL not set — skipping table creation. "
            "Tables must already exist in Supabase."
        )
        return

    try:
        import psycopg2
    except ImportError:
        warnings.warn("psycopg2-binary not installed — skipping table creation")
        return

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS grants (
            id         BIGSERIAL PRIMARY KEY,
            name       TEXT NOT NULL,
            foa        TEXT,
            notes      TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS drafts (
            id               BIGSERIAL PRIMARY KEY,
            grant_id         BIGINT NOT NULL REFERENCES grants(id) ON DELETE CASCADE,
            section          TEXT NOT NULL,
            version          INTEGER NOT NULL DEFAULT 1,
            content          TEXT NOT NULL,
            model            TEXT,
            additional_notes TEXT,
            created_at       TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id          BIGSERIAL PRIMARY KEY,
            title       TEXT NOT NULL,
            number      TEXT,
            url         TEXT,
            posted_date TEXT,
            close_date  TEXT,
            synopsis    TEXT,
            source      TEXT,
            fetched_at  TEXT NOT NULL,
            UNIQUE (number, source)
        )
    """)

    conn.commit()
    conn.close()


# ── Grant CRUD ──────────────────────────────────────────────────────────────

def create_grant(name: str, foa: str = "", notes: str = "") -> int:
    now = datetime.utcnow().isoformat()
    try:
        result = _get_supabase().table("grants").insert(
            {"name": name, "foa": foa, "notes": notes, "created_at": now, "updated_at": now}
        ).execute()
        return result.data[0]["id"]
    except Exception as e:
        warnings.warn(f"Supabase error (create_grant): {e}")
        raise


def list_grants() -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("grants")
            .select("*")
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (list_grants): {e}")
        return []


def get_grant(grant_id: int) -> dict | None:
    try:
        result = _get_supabase().table("grants").select("*").eq("id", grant_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        warnings.warn(f"Supabase error (get_grant): {e}")
        return None


def update_grant(grant_id: int, name: str, foa: str, notes: str) -> None:
    now = datetime.utcnow().isoformat()
    try:
        _get_supabase().table("grants").update(
            {"name": name, "foa": foa, "notes": notes, "updated_at": now}
        ).eq("id", grant_id).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (update_grant): {e}")


def delete_grant(grant_id: int) -> None:
    try:
        sb = _get_supabase()
        # Delete child drafts first (belt-and-suspenders alongside ON DELETE CASCADE)
        sb.table("drafts").delete().eq("grant_id", grant_id).execute()
        sb.table("grants").delete().eq("id", grant_id).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (delete_grant): {e}")


# ── Draft CRUD ──────────────────────────────────────────────────────────────

def save_draft(
    grant_id: int,
    section: str,
    content: str,
    model: str = "",
    additional_notes: str = "",
) -> int:
    now = datetime.utcnow().isoformat()
    try:
        sb = _get_supabase()
        # Get next version number for this grant+section
        ver_result = (
            sb.table("drafts")
            .select("version")
            .eq("grant_id", grant_id)
            .eq("section", section)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        version = (ver_result.data[0]["version"] if ver_result.data else 0) + 1

        result = sb.table("drafts").insert(
            {
                "grant_id":         grant_id,
                "section":          section,
                "version":          version,
                "content":          content,
                "model":            model,
                "additional_notes": additional_notes,
                "created_at":       now,
            }
        ).execute()

        # Update grant updated_at
        sb.table("grants").update({"updated_at": now}).eq("id", grant_id).execute()
        return result.data[0]["id"]
    except Exception as e:
        warnings.warn(f"Supabase error (save_draft): {e}")
        raise


def get_latest_draft(grant_id: int, section: str) -> dict | None:
    try:
        result = (
            _get_supabase()
            .table("drafts")
            .select("*")
            .eq("grant_id", grant_id)
            .eq("section", section)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        warnings.warn(f"Supabase error (get_latest_draft): {e}")
        return None


def list_drafts(grant_id: int) -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("drafts")
            .select("*")
            .eq("grant_id", grant_id)
            .order("section")
            .order("version", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (list_drafts): {e}")
        return []


def list_all_drafts_for_section(grant_id: int, section: str) -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("drafts")
            .select("*")
            .eq("grant_id", grant_id)
            .eq("section", section)
            .order("version", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (list_all_drafts_for_section): {e}")
        return []


# ── Opportunities ───────────────────────────────────────────────────────────

def upsert_opportunity(opp: dict) -> None:
    now = datetime.utcnow().isoformat()
    try:
        _get_supabase().table("opportunities").upsert(
            {
                "title":       opp.get("title"),
                "number":      opp.get("number"),
                "url":         opp.get("url"),
                "posted_date": opp.get("posted_date"),
                "close_date":  opp.get("close_date"),
                "synopsis":    opp.get("synopsis"),
                "source":      opp.get("source"),
                "fetched_at":  now,
            },
            on_conflict="number,source",
        ).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (upsert_opportunity): {e}")


def list_opportunities(limit: int = 50) -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("opportunities")
            .select("*")
            .order("fetched_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (list_opportunities): {e}")
        return []
