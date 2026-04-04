"""
Restinguo Hub — Experimental Roadmap
Track progress from current stage to IND.
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
    page_title="Restinguo Hub · Roadmap",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from scientist import database as db
from scientist import roadmap as roadmap_logic

with st.sidebar:
    st.markdown("## 🧬 Restinguo Hub")
    st.markdown("*COPA Syndrome · IFNAR Blockade*")

st.title("🗺️ Experimental Roadmap")
st.caption("Target Validation → Disease Model → Efficacy PoC → IND-Enabling Prep")

# ─────────────────────────────────────────────
# Load
# ─────────────────────────────────────────────
try:
    stage_progress = roadmap_logic.get_stage_progress()
    active_stage = roadmap_logic.current_stage(stage_progress)
    overall_pct = roadmap_logic.overall_progress(stage_progress)
except Exception as e:
    st.error(f"Failed to load roadmap: {e}")
    st.stop()

# ─────────────────────────────────────────────
# Overall progress bar
# ─────────────────────────────────────────────
st.metric("Overall Program Progress", f"{overall_pct:.0f}%")
st.progress(overall_pct / 100)
st.caption(f"Currently in **Stage {active_stage}: {roadmap_logic.STAGE_NAMES.get(active_stage, '')}**")
st.divider()

# ─────────────────────────────────────────────
# Stage progress chart
# ─────────────────────────────────────────────
stage_names = [f"S{n}: {roadmap_logic.STAGE_NAMES[n]}" for n in sorted(stage_progress.keys())]
stage_pcts = [stage_progress[n]["pct"] for n in sorted(stage_progress.keys())]
colors = []
for n in sorted(stage_progress.keys()):
    if n < active_stage:
        colors.append("#7ED321")  # complete
    elif n == active_stage:
        colors.append("#F5A623")  # active
    else:
        colors.append("#333333")  # future

fig = go.Figure(go.Bar(
    x=stage_names,
    y=stage_pcts,
    marker_color=colors,
    text=[f"{p:.0f}%" for p in stage_pcts],
    textposition="outside",
))
fig.update_layout(
    yaxis=dict(range=[0, 110], title="Completion %"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=280,
    margin=dict(t=20, b=20),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ─────────────────────────────────────────────
# Stage detail cards
# ─────────────────────────────────────────────
for stage_num in sorted(stage_progress.keys()):
    sp = stage_progress[stage_num]
    is_active = stage_num == active_stage
    is_complete = sp["complete"]

    icon = "✅" if is_complete else ("▶️" if is_active else "⏳")

    with st.expander(
        f"{icon} Stage {stage_num}: {sp['name']} — {sp['done']}/{sp['total']} tasks",
        expanded=is_active,
    ):
        st.caption(sp["description"])
        st.markdown(f"**Milestone:** _{sp['milestone']}_")
        st.progress(sp["pct"] / 100)
        st.markdown("---")

        for item in sp["items"]:
            item_id = item["id"]
            completed = item.get("completed", False)

            col1, col2 = st.columns([8, 2])
            with col1:
                checked = st.checkbox(
                    item["description"],
                    value=completed,
                    key=f"roadmap_{item_id}",
                )
                if checked != completed:
                    try:
                        db.toggle_roadmap_item(item_id, checked)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update: {e}")

            with col2:
                if item.get("completed_at"):
                    st.caption(f"Done: {item['completed_at'][:10]}")

            notes_key = f"notes_{item_id}"
            current_notes = item.get("notes", "") or ""
            with st.expander("Add notes", expanded=bool(current_notes)):
                new_notes = st.text_area(
                    "Notes",
                    value=current_notes,
                    key=notes_key,
                    height=60,
                    label_visibility="collapsed",
                )
                if new_notes != current_notes:
                    if st.button("Save notes", key=f"save_notes_{item_id}"):
                        try:
                            db.update_roadmap_notes(item_id, new_notes)
                            st.success("Saved!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

st.divider()

# ─────────────────────────────────────────────
# Add custom roadmap item
# ─────────────────────────────────────────────
with st.expander("➕ Add Custom Roadmap Item"):
    with st.form("add_roadmap_item"):
        stage_options = {f"Stage {n}: {roadmap_logic.STAGE_NAMES[n]}": n for n in sorted(stage_progress.keys())}
        selected_stage_label = st.selectbox("Stage", list(stage_options.keys()))
        selected_stage_num = stage_options[selected_stage_label]
        item_desc = st.text_input("Task description")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not item_desc.strip():
                st.warning("Description required.")
            else:
                try:
                    db.add_roadmap_item(
                        selected_stage_num,
                        roadmap_logic.STAGE_NAMES[selected_stage_num],
                        item_desc.strip(),
                    )
                    st.success("Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")
