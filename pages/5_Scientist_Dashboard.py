"""
Restinguo Hub — Scientist Agent Dashboard
"""

import os
import streamlit as st
import plotly.graph_objects as go

try:
    for _k in ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]:
        if _k in st.secrets and _k not in os.environ:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

st.set_page_config(
    page_title="Restinguo Hub · Scientist",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from scientist import database as db
from scientist import roadmap as roadmap_logic
from scientist.hypotheses import STATUS_COLORS, PRIORITY_COLORS

with st.sidebar:
    st.markdown("## 🧬 Restinguo Hub")
    st.markdown("*COPA Syndrome · IFNAR Blockade*")
    st.divider()
    st.markdown("""
**Program:** IFNAR Blockade for COPA Syndrome
**Stage:** Target Validation
**Collaborator:** Anthony Shum, UCSF
**Target:** IND
    """)

st.title("🧬 Scientific Dashboard")
st.caption("COPA Syndrome · IFNAR Blockade Program · Target Validation Stage")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
try:
    stats = db.get_dashboard_stats()
    stage_progress = roadmap_logic.get_stage_progress()
    active_stage = roadmap_logic.current_stage(stage_progress)
    overall_pct = roadmap_logic.overall_progress(stage_progress)
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.info("Make sure SUPABASE_URL and SUPABASE_KEY are set in `.streamlit/secrets.toml`.")
    st.stop()

# ─────────────────────────────────────────────
# Top KPI row
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Hypotheses", stats["hypothesis_count"])

with col2:
    open_count = stats["hypothesis_status_counts"].get("Open", 0) + stats["hypothesis_status_counts"].get("Testing", 0)
    st.metric("Active Hypotheses", open_count)

with col3:
    st.metric("Roadmap Progress", f"{stats['roadmap_pct']:.0f}%",
              f"{stats['roadmap_done']}/{stats['roadmap_total']} tasks")

with col4:
    st.metric("Experiments Logged", stats["experiment_count"])

st.divider()

# ─────────────────────────────────────────────
# Two-column layout
# ─────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    # Hypothesis status board
    st.subheader("Hypothesis Status")
    hypotheses = db.get_all_hypotheses()
    if hypotheses:
        status_order = ["Open", "Testing", "Supported", "Refuted", "Uncertain"]
        for status in status_order:
            group = [h for h in hypotheses if h.get("status") == status]
            if not group:
                continue
            color = STATUS_COLORS.get(status, "#9B9B9B")
            st.markdown(f"**:{color.lstrip('#')}[{status}]** ({len(group)})")
            for h in group:
                priority = h.get("priority", "High")
                p_color = PRIORITY_COLORS.get(priority, "#9B9B9B")
                with st.container():
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(f"- **{h['title']}**")
                    with c2:
                        st.caption(priority)
    else:
        st.info("No hypotheses yet. Run the database migration and seed script.")

    st.divider()

    # Roadmap progress
    st.subheader("Experimental Roadmap")
    for stage_num in sorted(stage_progress.keys()):
        sp = stage_progress[stage_num]
        is_active = stage_num == active_stage
        label = f"{'▶ ' if is_active else ''}Stage {stage_num}: {sp['name']}"
        pct = sp["pct"] / 100

        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"**{label}**" if is_active else label)
            st.progress(pct)
        with cols[1]:
            st.metric("", f"{sp['done']}/{sp['total']}")

with right:
    # Open questions
    st.subheader("Open Questions (Critical/High)")
    from scientist.hypotheses import get_critical_open_hypotheses
    critical = get_critical_open_hypotheses()
    if critical:
        for h in critical:
            priority = h.get("priority", "High")
            color = PRIORITY_COLORS.get(priority, "#9B9B9B")
            st.markdown(
                f"""<div style="border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 8px;">
<strong>{h['title']}</strong><br>
<small>{h['statement'][:120]}...</small>
</div>""",
                unsafe_allow_html=True,
            )
    else:
        st.success("No critical open questions — all addressed!")

    st.divider()

    # Recent experiments
    st.subheader("Recent Experiments")
    recent = stats["recent_experiments"]
    if recent:
        for exp in recent:
            status = exp.get("status", "Planned")
            color = {
                "Planned": "🔵",
                "In Progress": "🟡",
                "Complete": "🟢",
                "Failed": "🔴",
            }.get(status, "⚪")
            st.markdown(f"{color} **{exp['experiment_id']}** — {exp['title']}")
            st.caption(f"  {exp.get('date', '')} · {status}")
    else:
        st.info("No experiments logged yet.")

    st.divider()

    # Hypothesis status donut
    st.subheader("Hypothesis Breakdown")
    status_counts = stats["hypothesis_status_counts"]
    if status_counts:
        fig = go.Figure(go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=0.5,
            marker_colors=[STATUS_COLORS.get(s, "#9B9B9B") for s in status_counts.keys()],
            textinfo="label+value",
        ))
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=200,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# Recent literature evaluations
# ─────────────────────────────────────────────
if stats["recent_lit_evals"]:
    st.divider()
    st.subheader("Recent Literature Evaluations")
    for ev in stats["recent_lit_evals"]:
        evdata = ev.get("evaluation", {})
        title = ev.get("paper_title") or "Untitled"
        score = evdata.get("relevance_score", "—")
        summary = evdata.get("paper_summary", "")
        created = ev.get("created_at", "")[:10]
        with st.expander(f"📄 {title} · Relevance: {score}/10 · {created}"):
            st.markdown(summary)
            takeaway = evdata.get("strategic_takeaway", "")
            if takeaway:
                st.info(f"**Strategic takeaway:** {takeaway}")
