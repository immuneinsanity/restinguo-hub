"""
Supabase (PostgreSQL) database layer for the regulatory agent.
Stores pathway status, meeting records, document metadata, and AI outputs.
"""

import os
import warnings
from datetime import datetime

from supabase import create_client, Client


DOCS_PATH_LOCAL = "data/documents"


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
    """Create all tables and seed defaults (requires DATABASE_URL + psycopg2)."""
    database_url = _cfg("DATABASE_URL")
    if not database_url:
        warnings.warn(
            "DATABASE_URL not set â€” skipping table creation. "
            "Tables must already exist in Supabase."
        )
        # Still try to seed defaults via supabase-py in case tables exist
        try:
            _seed_defaults_supabase()
        except Exception:
            pass
        return

    try:
        import psycopg2
    except ImportError:
        warnings.warn("psycopg2-binary not installed â€” skipping table creation")
        return

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pathway_status (
            id           BIGSERIAL PRIMARY KEY,
            pathway_key  TEXT UNIQUE NOT NULL,
            status       TEXT NOT NULL DEFAULT 'Not Started',
            notes        TEXT,
            submitted_date TEXT,
            granted_date TEXT,
            updated_at   TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_items (
            id             BIGSERIAL PRIMARY KEY,
            stage_key      TEXT UNIQUE NOT NULL,
            status         TEXT NOT NULL DEFAULT 'Pending',
            started_date   TEXT,
            completed_date TEXT,
            notes          TEXT,
            updated_at     TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fda_meetings (
            id             BIGSERIAL PRIMARY KEY,
            meeting_type   TEXT NOT NULL,
            purpose        TEXT,
            status         TEXT NOT NULL DEFAULT 'Planning',
            requested_date TEXT,
            scheduled_date TEXT,
            completed_date TEXT,
            fda_response   TEXT,
            notes          TEXT,
            created_at     TEXT NOT NULL,
            updated_at     TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_questions (
            id           BIGSERIAL PRIMARY KEY,
            meeting_id   BIGINT NOT NULL REFERENCES fda_meetings(id) ON DELETE CASCADE,
            question     TEXT NOT NULL,
            fda_response TEXT,
            priority     INTEGER DEFAULT 5
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id          BIGSERIAL PRIMARY KEY,
            title       TEXT NOT NULL,
            doc_type    TEXT,
            filename    TEXT,
            description TEXT,
            tags        TEXT,
            uploaded_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_outputs (
            id         BIGSERIAL PRIMARY KEY,
            output_type TEXT NOT NULL,
            title       TEXT,
            content     TEXT NOT NULL,
            model_used  TEXT,
            created_at  TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    _seed_defaults_supabase()


def _seed_defaults_supabase() -> None:
    """Insert default pathway and roadmap rows (ignore if already present)."""
    now = datetime.now().isoformat()
    sb = _get_supabase()

    pathway_defaults = [
        ("odd",  "Not Started", "Highest priority action. COPA syndrome qualifies â€” <500 patients worldwide, well below the 200K US threshold."),
        ("rpdd", "Not Started", "COPA syndrome affects children. Rare Pediatric Disease Designation would provide Priority Review Voucher on approval."),
        ("btd",  "Not Started", "Too early â€” need clinical evidence. Revisit after IND-enabling studies show strong PD signal."),
        ("ftd",  "Not Started", "Criteria: serious condition + preliminary evidence of advantage. Apply alongside or after IND submission."),
    ]
    for key, status, notes in pathway_defaults:
        sb.table("pathway_status").insert(
            {"pathway_key": key, "status": status, "notes": notes, "updated_at": now},
            ignore_duplicates=True,
        ).execute()

    roadmap_defaults = [
        ("target_validation",  "In Progress", "Current stage. Confirm IFNAR is the right target for COPA syndrome. Key: IFN signature data and mechanistic rationale."),
        ("lead_identification", "Pending",    None),
        ("in_vitro_poc",        "Pending",    None),
        ("in_vivo_models",      "Pending",    "Key risk: no validated animal model for COPA syndrome. Will need to develop Copa KI mouse or use surrogate interferonopathy model."),
        ("ind_enabling",        "Pending",    None),
        ("pre_ind_meeting",     "Pending",    None),
        ("ind_submission",      "Pending",    None),
    ]
    for key, status, notes in roadmap_defaults:
        sb.table("roadmap_items").insert(
            {"stage_key": key, "status": status, "notes": notes, "updated_at": now},
            ignore_duplicates=True,
        ).execute()


# --- Pathway CRUD ---

def get_pathway_status(pathway_key: str) -> dict | None:
    try:
        result = (
            _get_supabase()
            .table("pathway_status")
            .select("*")
            .eq("pathway_key", pathway_key)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        warnings.warn(f"Supabase error (get_pathway_status): {e}")
        return None


def update_pathway_status(
    pathway_key: str,
    status: str,
    notes: str = None,
    submitted_date: str = None,
    granted_date: str = None,
) -> None:
    try:
        now = datetime.now().isoformat()
        _get_supabase().table("pathway_status").update(
            {
                "status":         status,
                "notes":          notes,
                "submitted_date": submitted_date,
                "granted_date":   granted_date,
                "updated_at":     now,
            }
        ).eq("pathway_key", pathway_key).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (update_pathway_status): {e}")


# --- Roadmap CRUD ---

def get_all_roadmap_items() -> list[dict]:
    try:
        result = _get_supabase().table("roadmap_items").select("*").order("id").execute()
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (get_all_roadmap_items): {e}")
        return []


def update_roadmap_item(
    stage_key: str,
    status: str,
    notes: str = None,
    started_date: str = None,
    completed_date: str = None,
) -> None:
    try:
        now = datetime.now().isoformat()
        _get_supabase().table("roadmap_items").update(
            {
                "status":         status,
                "notes":          notes,
                "started_date":   started_date,
                "completed_date": completed_date,
                "updated_at":     now,
            }
        ).eq("stage_key", stage_key).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (update_roadmap_item): {e}")


# --- FDA Meeting CRUD ---

def get_all_meetings() -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("fda_meetings")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (get_all_meetings): {e}")
        return []


def create_meeting(
    meeting_type: str,
    purpose: str,
    status: str = "Planning",
    notes: str = None,
) -> int:
    try:
        now = datetime.now().isoformat()
        result = _get_supabase().table("fda_meetings").insert(
            {
                "meeting_type": meeting_type,
                "purpose":      purpose,
                "status":       status,
                "notes":        notes,
                "created_at":   now,
                "updated_at":   now,
            }
        ).execute()
        return result.data[0]["id"]
    except Exception as e:
        warnings.warn(f"Supabase error (create_meeting): {e}")
        raise


def update_meeting(meeting_id: int, **kwargs) -> None:
    try:
        now = datetime.now().isoformat()
        kwargs["updated_at"] = now
        _get_supabase().table("fda_meetings").update(kwargs).eq("id", meeting_id).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (update_meeting): {e}")


def add_meeting_question(meeting_id: int, question: str, priority: int = 5) -> None:
    try:
        _get_supabase().table("meeting_questions").insert(
            {"meeting_id": meeting_id, "question": question, "priority": priority}
        ).execute()
    except Exception as e:
        warnings.warn(f"Supabase error (add_meeting_question): {e}")


def get_meeting_questions(meeting_id: int) -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("meeting_questions")
            .select("*")
            .eq("meeting_id", meeting_id)
            .order("priority")
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (get_meeting_questions): {e}")
        return []


# --- Document CRUD ---

def save_document_metadata(
    title: str,
    doc_type: str,
    filename: str,
    description: str = None,
    tags: str = None,
) -> int:
    try:
        now = datetime.now().isoformat()
        result = _get_supabase().table("documents").insert(
            {
                "title":       title,
                "doc_type":    doc_type,
                "filename":    filename,
                "description": description,
                "tags":        tags,
                "uploaded_at": now,
            }
        ).execute()
        return result.data[0]["id"]
    except Exception as e:
        warnings.warn(f"Supabase error (save_document_metadata): {e}")
        raise


def get_all_documents() -> list[dict]:
    try:
        result = (
            _get_supabase()
            .table("documents")
            .select("*")
            .order("uploaded_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (get_all_documents): {e}")
        return []


# --- AI Output CRUD ---

def save_ai_output(output_type: str, title: str, content: str, model_used: str) -> int:
    try:
        now = datetime.now().isoformat()
        result = _get_supabase().table("ai_outputs").insert(
            {
                "output_type": output_type,
                "title":       title,
                "content":     content,
                "model_used":  model_used,
                "created_at":  now,
            }
        ).execute()
        return result.data[0]["id"]
    except Exception as e:
        warnings.warn(f"Supabase error (save_ai_output): {e}")
        raise


def get_ai_outputs(output_type: str = None) -> list[dict]:
    try:
        q = _get_supabase().table("ai_outputs").select("*")
        if output_type:
            q = q.eq("output_type", output_type)
        result = q.order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        warnings.warn(f"Supabase error (get_ai_outputs): {e}")
        return []

