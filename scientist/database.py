"""
Supabase CRUD for all tables.
All DB interaction goes through this module.
"""

import os
from datetime import date, datetime
from typing import Any
import streamlit as st
from supabase import create_client, Client


# ─────────────────────────────────────────────
# Client
# ─────────────────────────────────────────────

def _get_config(key: str, default: str = "") -> str:
    try:
        v = st.secrets.get(key)
        if v:
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


@st.cache_resource
def get_client() -> Client:
    url = _get_config("SUPABASE_URL")
    key = _get_config("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)


# ─────────────────────────────────────────────
# Hypotheses
# ─────────────────────────────────────────────

def get_all_hypotheses() -> list[dict]:
    db = get_client()
    res = db.table("hypotheses").select("*").order("created_at").execute()
    return res.data or []


def get_hypothesis(hypothesis_id: str) -> dict | None:
    db = get_client()
    res = db.table("hypotheses").select("*").eq("id", hypothesis_id).single().execute()
    return res.data


def create_hypothesis(
    title: str,
    statement: str,
    status: str,
    priority: str,
    key_experiment: str = "",
    evidence_for: list[str] | None = None,
    evidence_against: list[str] | None = None,
) -> dict:
    db = get_client()
    res = db.table("hypotheses").insert({
        "title": title,
        "statement": statement,
        "status": status,
        "priority": priority,
        "key_experiment": key_experiment,
        "evidence_for": evidence_for or [],
        "evidence_against": evidence_against or [],
    }).execute()
    return res.data[0]


def update_hypothesis(hypothesis_id: str, updates: dict) -> dict:
    db = get_client()
    res = db.table("hypotheses").update(updates).eq("id", hypothesis_id).execute()
    return res.data[0]


def delete_hypothesis(hypothesis_id: str) -> None:
    db = get_client()
    db.table("hypotheses").delete().eq("id", hypothesis_id).execute()


def add_evidence(hypothesis_id: str, text: str, direction: str) -> dict:
    """direction: 'for' or 'against'"""
    hyp = get_hypothesis(hypothesis_id)
    if not hyp:
        raise ValueError(f"Hypothesis {hypothesis_id} not found")
    field = "evidence_for" if direction == "for" else "evidence_against"
    current = hyp.get(field, []) or []
    current.append(text)
    return update_hypothesis(hypothesis_id, {field: current})


def remove_evidence(hypothesis_id: str, index: int, direction: str) -> dict:
    hyp = get_hypothesis(hypothesis_id)
    field = "evidence_for" if direction == "for" else "evidence_against"
    current = hyp.get(field, []) or []
    if 0 <= index < len(current):
        current.pop(index)
    return update_hypothesis(hypothesis_id, {field: current})


# ─────────────────────────────────────────────
# Roadmap
# ─────────────────────────────────────────────

def get_roadmap_items() -> list[dict]:
    db = get_client()
    res = (
        db.table("roadmap_items")
        .select("*")
        .order("stage")
        .order("created_at")
        .execute()
    )
    return res.data or []


def get_roadmap_by_stage() -> dict[int, list[dict]]:
    items = get_roadmap_items()
    stages: dict[int, list[dict]] = {}
    for item in items:
        s = item["stage"]
        stages.setdefault(s, []).append(item)
    return stages


def toggle_roadmap_item(item_id: str, completed: bool) -> dict:
    db = get_client()
    updates: dict[str, Any] = {"completed": completed}
    if completed:
        updates["completed_at"] = datetime.utcnow().isoformat()
    else:
        updates["completed_at"] = None
    res = db.table("roadmap_items").update(updates).eq("id", item_id).execute()
    return res.data[0]


def update_roadmap_notes(item_id: str, notes: str) -> dict:
    db = get_client()
    res = db.table("roadmap_items").update({"notes": notes}).eq("id", item_id).execute()
    return res.data[0]


def add_roadmap_item(stage: int, stage_name: str, description: str) -> dict:
    db = get_client()
    res = db.table("roadmap_items").insert({
        "stage": stage,
        "stage_name": stage_name,
        "description": description,
    }).execute()
    return res.data[0]


# ─────────────────────────────────────────────
# Protocols
# ─────────────────────────────────────────────

def save_protocol(
    title: str,
    research_question: str,
    content: dict,
    hypothesis_id: str | None = None,
) -> dict:
    db = get_client()
    res = db.table("protocols").insert({
        "title": title,
        "research_question": research_question,
        "content": content,
        "hypothesis_id": hypothesis_id,
    }).execute()
    return res.data[0]


def get_all_protocols() -> list[dict]:
    db = get_client()
    res = db.table("protocols").select("*").order("created_at", desc=True).execute()
    return res.data or []


def get_protocol(protocol_id: str) -> dict | None:
    db = get_client()
    res = db.table("protocols").select("*").eq("id", protocol_id).single().execute()
    return res.data


def delete_protocol(protocol_id: str) -> None:
    db = get_client()
    db.table("protocols").delete().eq("id", protocol_id).execute()


# ─────────────────────────────────────────────
# Lab Notebook
# ─────────────────────────────────────────────

def _next_experiment_id() -> str:
    db = get_client()
    res = db.table("lab_notebook").select("experiment_id").order("created_at", desc=True).limit(1).execute()
    if not res.data:
        return "EXP-001"
    last = res.data[0]["experiment_id"]
    num = int(last.split("-")[-1]) + 1
    return f"EXP-{num:03d}"


def create_experiment(
    title: str,
    hypothesis_id: str | None = None,
    protocol_id: str | None = None,
    experiment_date: date | None = None,
) -> dict:
    db = get_client()
    exp_id = _next_experiment_id()
    res = db.table("lab_notebook").insert({
        "experiment_id": exp_id,
        "title": title,
        "hypothesis_id": hypothesis_id,
        "protocol_id": protocol_id,
        "date": (experiment_date or date.today()).isoformat(),
        "status": "Planned",
    }).execute()
    return res.data[0]


def get_all_experiments() -> list[dict]:
    db = get_client()
    res = (
        db.table("lab_notebook")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def get_experiment(experiment_id: str) -> dict | None:
    db = get_client()
    res = (
        db.table("lab_notebook")
        .select("*")
        .eq("id", experiment_id)
        .single()
        .execute()
    )
    return res.data


def update_experiment(experiment_id: str, updates: dict) -> dict:
    db = get_client()
    res = db.table("lab_notebook").update(updates).eq("id", experiment_id).execute()
    return res.data[0]


def log_results(
    experiment_id: str,
    results: str,
    interpretation: str,
    next_steps: str,
    status: str = "Complete",
) -> dict:
    return update_experiment(experiment_id, {
        "results": results,
        "interpretation": interpretation,
        "next_steps": next_steps,
        "status": status,
    })


# ─────────────────────────────────────────────
# Literature Evaluations
# ─────────────────────────────────────────────

def save_literature_eval(
    abstract_text: str,
    evaluation: dict,
    paper_title: str = "",
) -> dict:
    db = get_client()
    res = db.table("literature_evaluations").insert({
        "abstract_text": abstract_text,
        "evaluation": evaluation,
        "paper_title": paper_title,
    }).execute()
    return res.data[0]


def get_recent_literature_evals(limit: int = 20) -> list[dict]:
    db = get_client()
    res = (
        db.table("literature_evaluations")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


def get_literature_eval(eval_id: str) -> dict | None:
    db = get_client()
    res = (
        db.table("literature_evaluations")
        .select("*")
        .eq("id", eval_id)
        .single()
        .execute()
    )
    return res.data


# ─────────────────────────────────────────────
# Dashboard stats
# ─────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    hypotheses = get_all_hypotheses()
    roadmap = get_roadmap_items()
    experiments = get_all_experiments()
    lit_evals = get_recent_literature_evals(5)

    status_counts: dict[str, int] = {}
    for h in hypotheses:
        s = h.get("status", "Open")
        status_counts[s] = status_counts.get(s, 0) + 1

    roadmap_total = len(roadmap)
    roadmap_done = sum(1 for r in roadmap if r.get("completed"))

    recent_experiments = sorted(
        experiments,
        key=lambda e: e.get("created_at", ""),
        reverse=True,
    )[:5]

    return {
        "hypothesis_count": len(hypotheses),
        "hypothesis_status_counts": status_counts,
        "roadmap_total": roadmap_total,
        "roadmap_done": roadmap_done,
        "roadmap_pct": (roadmap_done / roadmap_total * 100) if roadmap_total else 0,
        "experiment_count": len(experiments),
        "recent_experiments": recent_experiments,
        "recent_lit_evals": lit_evals,
    }
