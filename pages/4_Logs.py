"""
Restinguo Hub — Agent Logs
Shows activity logs from Supabase-backed agents.
Research agent (CLI-only) and cron logs are not available in cloud mode.
"""

import os
import streamlit as st

try:
    for _k in ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]:
        if _k in st.secrets and _k not in os.environ:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

st.set_page_config(
    page_title="Restinguo Hub · Logs",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("## 📋 Agent Logs")
    st.markdown("*Activity across all agents*")
    st.divider()
    st.caption("Research and cron logs require local access.")

st.markdown("## 📋 Agent Logs")

col_h, col_r = st.columns([8, 1])
with col_r:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ── Research Agent logs ───────────────────────────────────────────────────────
with st.expander("🔬 Research Agent — logs", expanded=False):
    st.info(
        "The research agent writes to a local SQLite database (`research-agent/data/research.db`). "
        "Logs are not available in cloud mode. Run the research agent locally and use the "
        "local agent-board app to view paper counts and briefing history."
    )

# ── Grant Writer logs ─────────────────────────────────────────────────────────
with st.expander("📝 Grant Writer — recent drafts (last 20)", expanded=True):
    try:
        from grant_writer.database import list_grants, list_drafts
        grants = list_grants()
        if not grants:
            st.info("No grants in database yet.")
        else:
            all_drafts = []
            grant_map = {g["id"]: g["name"] for g in grants}
            for g in grants:
                for d in list_drafts(g["id"]):
                    d["grant_name"] = g["name"]
                    all_drafts.append(d)
            all_drafts.sort(key=lambda d: d["created_at"], reverse=True)
            recent = all_drafts[:20]
            if recent:
                cols = st.columns([3, 2, 1, 2])
                for h, c in zip(["Grant", "Section", "Version", "Created"], cols):
                    c.markdown(f"**{h}**")
                for d in recent:
                    cs = st.columns([3, 2, 1, 2])
                    cs[0].write(d.get("grant_name", "—"))
                    cs[1].write(d.get("section", "—"))
                    cs[2].write(f"v{d.get('version', '—')}")
                    cs[3].write(d.get("created_at", "—")[:16])
            else:
                st.info("No drafts saved yet.")
    except Exception as e:
        st.error(f"Could not load grant data: {e}")

# ── Regulatory Agent logs ─────────────────────────────────────────────────────
with st.expander("⚖️ Regulatory Agent — pathway status", expanded=True):
    try:
        from regulatory.database import get_all_roadmap_items
        from regulatory.pathways import get_all_pathways, STATUS_ICONS
        from regulatory.database import get_pathway_status

        st.markdown("**Designation Status:**")
        pathways = get_all_pathways()
        pathway_cols = st.columns(4)
        for i, p in enumerate(pathways):
            row = get_pathway_status(p.key)
            status = row["status"] if row else "Not Started"
            icon = STATUS_ICONS.get(status, "⬜")
            pathway_cols[i % 4].markdown(f"**{p.short_name}**: {icon} {status}")

        st.markdown("**Roadmap:**")
        items = get_all_roadmap_items()
        if items:
            for item in items:
                from regulatory.roadmap import get_stage
                stage = get_stage(item["stage_key"])
                name = stage.name if stage else item["stage_key"]
                status_icon = {"In Progress": "🔄", "Complete": "✅", "Pending": "⬜", "Blocked": "🚫"}.get(item["status"], "⬜")
                st.write(f"  • {name}: {status_icon} {item['status']}")
        else:
            st.info("No roadmap data yet. Open Regulatory Strategy to initialise.")
    except Exception as e:
        st.error(f"Could not load regulatory data: {e}")

# ── AI Outputs log ────────────────────────────────────────────────────────────
with st.expander("🤖 AI Outputs — recent (last 10)", expanded=False):
    try:
        from regulatory.database import get_ai_outputs
        outputs = get_ai_outputs()[:10]
        if not outputs:
            st.info("No AI outputs saved yet.")
        else:
            for o in outputs:
                st.write(
                    f"**{o.get('title', '—')}** ({o.get('output_type', '—')}) — "
                    f"Model: {o.get('model_used', '—')} — {o.get('created_at', '—')[:16]}"
                )
    except Exception as e:
        st.error(f"Could not load AI outputs: {e}")

# ── Cron logs ─────────────────────────────────────────────────────────────────
with st.expander("⏰ Cron — anifrolumab-ferment", expanded=False):
    st.info(
        "Cron job logs are managed by the local Claude Code cron system and are not "
        "available in cloud mode. To view cron history, run the local agent-board app "
        "or inspect `C:/Users/Leviw/.openclaw/cron/` directly."
    )
