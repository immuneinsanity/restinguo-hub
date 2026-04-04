"""
Restinguo Hub — central dashboard for all Restinguo AI agents.
Home page: Agent Board overview.
"""

import os
import streamlit as st
from datetime import datetime

# ── Secrets injection ─────────────────────────────────────────────────────────
try:
    for _k in ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]:
        if _k in st.secrets and _k not in os.environ:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

st.set_page_config(
    page_title="Restinguo Hub",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 Restinguo Hub")
    st.markdown("*COPA Syndrome · IFNAR Blockade*")
    st.divider()
    st.caption("Use the navigation above to switch between agents.")

# ── Helpers ───────────────────────────────────────────────────────────────────

PATHWAY_LABELS = {"odd": "ODD", "rpdd": "RPDD", "btd": "BTD", "ftd": "FTD"}

def status_dot(color: str) -> str:
    colors = {"green": "#22c55e", "yellow": "#eab308", "red": "#ef4444", "gray": "#9ca3af"}
    hex_color = colors.get(color, "#9ca3af")
    return f'<span style="color:{hex_color};font-size:1.1em;">●</span>'


@st.cache_data(ttl=60)
def load_grant_stats() -> dict:
    out = {"grant_count": 0, "draft_count": 0, "last_edited": None, "opp_count": 0, "error": None}
    try:
        from grant_writer.database import list_grants, list_drafts, list_opportunities as _list_opps
        grants = list_grants()
        out["grant_count"] = len(grants)
        total_drafts = 0
        last_edited = None
        for g in grants:
            drafts = list_drafts(g["id"])
            total_drafts += len(drafts)
            for d in drafts:
                if last_edited is None or d["created_at"] > last_edited:
                    last_edited = d["created_at"]
        out["draft_count"] = total_drafts
        out["last_edited"] = last_edited
        out["opp_count"] = len(_list_opps(50))
    except Exception as e:
        out["error"] = str(e)
    return out


@st.cache_data(ttl=60)
def load_regulatory_stats() -> dict:
    out = {"pathways": {}, "roadmap": [], "meetings": [], "error": None}
    try:
        from regulatory.database import get_all_roadmap_items, get_all_meetings, get_pathway_status
        from regulatory.pathways import get_all_pathways

        for pathway in get_all_pathways():
            try:
                row = get_pathway_status(pathway.key)
                if row:
                    out["pathways"][pathway.key] = {"status": row["status"]}
            except Exception:
                pass

        out["roadmap"] = get_all_roadmap_items()
        out["meetings"] = get_all_meetings()
    except Exception as e:
        out["error"] = str(e)
    return out


# ── Dashboard ─────────────────────────────────────────────────────────────────

col_title, col_refresh = st.columns([9, 1])
with col_title:
    st.markdown("## 🧬 Restinguo Agent Board")
    st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col_refresh:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

grant = load_grant_stats()
reg   = load_regulatory_stats()

col1, col2 = st.columns(2)

# ── Research Agent card ──────────────────────────────────────────────────────
with col1:
    with st.container(border=True):
        st.markdown(
            f"### 🔬 Research Agent &nbsp; {status_dot('gray')}",
            unsafe_allow_html=True,
        )
        st.info("CLI-only agent — not available in cloud mode.")
        st.caption("Runs `python main.py` in the research-agent directory. Briefings stored locally.")
        st.caption("Navigate to **Research Feed** for a placeholder view.")

# ── Grant Writer card ────────────────────────────────────────────────────────
with col2:
    g_status = "red" if grant["error"] else ("green" if grant["grant_count"] > 0 else "gray")
    with st.container(border=True):
        st.markdown(
            f"### 📝 Grant Writer &nbsp; {status_dot(g_status)}",
            unsafe_allow_html=True,
        )
        if grant["error"]:
            st.error(grant["error"])
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Grants", grant["grant_count"])
            m2.metric("Draft sections", grant["draft_count"])
            m3.metric("Opportunities", grant["opp_count"])
            if grant["last_edited"]:
                st.caption(f"Last edited: {grant['last_edited'][:16]}")

col3, col4 = st.columns(2)

# ── Regulatory Agent card ────────────────────────────────────────────────────
with col3:
    r2_status = "red" if reg["error"] else ("green" if reg["pathways"] else "gray")
    with st.container(border=True):
        st.markdown(
            f"### ⚖️ Regulatory Agent &nbsp; {status_dot(r2_status)}",
            unsafe_allow_html=True,
        )
        if reg["error"]:
            st.warning(reg["error"])
        elif reg["pathways"]:
            pathway_cols = st.columns(4)
            for i, (key, label) in enumerate(PATHWAY_LABELS.items()):
                pdata = reg["pathways"].get(key, {})
                pstatus = pdata.get("status", "—")
                dot_color = "green" if pstatus not in ("Not Started", "—") else "gray"
                pathway_cols[i].markdown(
                    f"**{label}**<br>{status_dot(dot_color)} {pstatus}",
                    unsafe_allow_html=True,
                )
            in_progress = [r for r in reg["roadmap"] if r.get("status") == "In Progress"]
            if in_progress:
                from regulatory.roadmap import get_stage
                stage = get_stage(in_progress[0]["stage_key"])
                st.caption(f"Current stage: **{stage.name if stage else in_progress[0]['stage_key']}**")
        else:
            st.info("No regulatory data yet — open Regulatory Strategy to initialise.")

# ── Cron card ────────────────────────────────────────────────────────────────
with col4:
    with st.container(border=True):
        st.markdown(
            f"### ⏰ Cron Jobs &nbsp; {status_dot('gray')}",
            unsafe_allow_html=True,
        )
        st.info("Cron job management is not available in cloud mode.")
        st.caption(
            "Scheduled tasks run via the local Claude Code cron system. "
            "To manage cron jobs, use the Claude Code CLI or the local agent-board app."
        )

st.divider()

# ── Quick links ───────────────────────────────────────────────────────────────
st.markdown("### Quick Links")
ql_cols = st.columns(3)
ql_cols[0].page_link("pages/2_Grant_Writer.py", label="📝 Open Grant Writer", use_container_width=True)
ql_cols[1].page_link("pages/3_Regulatory_Strategy.py", label="⚖️ Open Regulatory Strategy", use_container_width=True)
ql_cols[2].page_link("pages/1_Research_Feed.py", label="🔬 Research Feed", use_container_width=True)
