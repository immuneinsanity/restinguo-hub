"""
Restinguo Hub — Hypothesis Tracker
Evidence management, status updates, Opus evaluation.
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
    page_title="Restinguo Hub · Hypotheses",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from scientist import database as db
from scientist import hypotheses as hyp_logic
from scientist.hypotheses import STATUS_OPTIONS, PRIORITY_OPTIONS, STATUS_COLORS, PRIORITY_COLORS

with st.sidebar:
    st.markdown("## 🧬 Restinguo Hub")
    st.markdown("*COPA Syndrome · IFNAR Blockade*")

st.title("🧪 Hypothesis Tracker")
st.caption("Track all scientific hypotheses for the COPA/IFNAR program.")

# ─────────────────────────────────────────────
# Load
# ─────────────────────────────────────────────
try:
    hypotheses = db.get_all_hypotheses()
except Exception as e:
    st.error(f"Failed to load hypotheses: {e}")
    st.stop()

# ─────────────────────────────────────────────
# Kanban view
# ─────────────────────────────────────────────
st.subheader("Status Board")

cols = st.columns(len(STATUS_OPTIONS))
grouped = hyp_logic.get_hypotheses_by_status()

for i, status in enumerate(STATUS_OPTIONS):
    with cols[i]:
        color = STATUS_COLORS.get(status, "#9B9B9B")
        count = len(grouped.get(status, []))
        st.markdown(
            f'<div style="background:{color}22; border-top: 3px solid {color}; '
            f'padding: 8px; border-radius: 4px; margin-bottom: 8px;">'
            f'<strong style="color:{color}">{status}</strong> <span style="color:#888">({count})</span></div>',
            unsafe_allow_html=True,
        )
        for h in grouped.get(status, []):
            with st.container():
                p_color = PRIORITY_COLORS.get(h.get("priority", "High"), "#9B9B9B")
                st.markdown(
                    f'<div style="border: 1px solid #333; border-left: 3px solid {p_color}; '
                    f'padding: 8px; border-radius: 4px; margin-bottom: 6px; font-size: 0.85em;">'
                    f'<strong>{h["title"]}</strong><br>'
                    f'<span style="color:{p_color}; font-size:0.75em">{h.get("priority","")}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

st.divider()

# ─────────────────────────────────────────────
# Add new hypothesis
# ─────────────────────────────────────────────
with st.expander("➕ Add New Hypothesis"):
    with st.form("add_hypothesis"):
        title = st.text_input("Short title (e.g. 'IFNAR Blockade PD Biomarker')")
        statement = st.text_area("Full hypothesis statement")
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("Initial status", STATUS_OPTIONS, index=0)
        with col2:
            priority = st.selectbox("Priority", PRIORITY_OPTIONS, index=1)
        key_exp = st.text_area("Key settling experiment (optional)")
        submitted = st.form_submit_button("Add Hypothesis")
        if submitted:
            if not title or not statement:
                st.warning("Title and statement are required.")
            else:
                try:
                    db.create_hypothesis(title, statement, status, priority, key_exp)
                    st.success(f"Added: {title}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

st.divider()

# ─────────────────────────────────────────────
# Detail view — select a hypothesis
# ─────────────────────────────────────────────
st.subheader("Hypothesis Detail")

if not hypotheses:
    st.info("No hypotheses loaded. Run the database migration.")
    st.stop()

hyp_options = {f"{h['title']} [{h['status']}]": h["id"] for h in hypotheses}
selected_label = st.selectbox("Select hypothesis", list(hyp_options.keys()))
selected_id = hyp_options[selected_label]
h = db.get_hypothesis(selected_id)

if not h:
    st.warning("Hypothesis not found.")
    st.stop()

p_color = PRIORITY_COLORS.get(h.get("priority", "High"), "#9B9B9B")
s_color = STATUS_COLORS.get(h.get("status", "Open"), "#4A90D9")

st.markdown(
    f"### {h['title']} "
    f'<span style="background:{s_color}33; color:{s_color}; padding: 2px 8px; border-radius: 12px; font-size:0.8em">{h["status"]}</span> '
    f'<span style="background:{p_color}33; color:{p_color}; padding: 2px 8px; border-radius: 12px; font-size:0.8em">{h["priority"]}</span>',
    unsafe_allow_html=True,
)
st.markdown(f"**{h['statement']}**")
if h.get("key_experiment"):
    st.info(f"**Key settling experiment:** {h['key_experiment']}")

detail_tab, evidence_tab, edit_tab, eval_tab = st.tabs(
    ["Overview", "Evidence", "Edit", "Opus Evaluation"]
)

# ── Overview ──────────────────────────────────
with detail_tab:
    evidence_for = h.get("evidence_for") or []
    evidence_against = h.get("evidence_against") or []

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Evidence For ({len(evidence_for)})**")
        if evidence_for:
            for e in evidence_for:
                st.markdown(f"✅ {e}")
        else:
            st.caption("None recorded")
    with col2:
        st.markdown(f"**Evidence Against ({len(evidence_against)})**")
        if evidence_against:
            for e in evidence_against:
                st.markdown(f"❌ {e}")
        else:
            st.caption("None recorded")

# ── Evidence management ───────────────────────
with evidence_tab:
    ev_col1, ev_col2 = st.columns(2)

    with ev_col1:
        st.markdown("**Add Evidence For**")
        with st.form("add_evidence_for"):
            new_for = st.text_area(
                "Evidence statement (cite paper, experiment, or observation)",
                key="for_text",
                height=80,
            )
            submitted_for = st.form_submit_button("Add")
            if submitted_for and new_for.strip():
                try:
                    db.add_evidence(selected_id, new_for.strip(), "for")
                    st.success("Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

        evidence_for = h.get("evidence_for") or []
        if evidence_for:
            st.markdown("**Current evidence for:**")
            for idx, e in enumerate(evidence_for):
                c1, c2 = st.columns([8, 1])
                with c1:
                    st.markdown(f"✅ {e}")
                with c2:
                    if st.button("🗑", key=f"del_for_{idx}"):
                        db.remove_evidence(selected_id, idx, "for")
                        st.rerun()

    with ev_col2:
        st.markdown("**Add Evidence Against**")
        with st.form("add_evidence_against"):
            new_against = st.text_area(
                "Evidence statement",
                key="against_text",
                height=80,
            )
            submitted_against = st.form_submit_button("Add")
            if submitted_against and new_against.strip():
                try:
                    db.add_evidence(selected_id, new_against.strip(), "against")
                    st.success("Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

        evidence_against = h.get("evidence_against") or []
        if evidence_against:
            st.markdown("**Current evidence against:**")
            for idx, e in enumerate(evidence_against):
                c1, c2 = st.columns([8, 1])
                with c1:
                    st.markdown(f"❌ {e}")
                with c2:
                    if st.button("🗑", key=f"del_against_{idx}"):
                        db.remove_evidence(selected_id, idx, "against")
                        st.rerun()

# ── Edit ─────────────────────────────────────
with edit_tab:
    with st.form("edit_hypothesis"):
        new_title = st.text_input("Title", value=h["title"])
        new_statement = st.text_area("Hypothesis statement", value=h["statement"])
        c1, c2 = st.columns(2)
        with c1:
            new_status = st.selectbox(
                "Status", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(h.get("status", "Open"))
            )
        with c2:
            new_priority = st.selectbox(
                "Priority", PRIORITY_OPTIONS,
                index=PRIORITY_OPTIONS.index(h.get("priority", "High"))
            )
        new_key_exp = st.text_area("Key settling experiment", value=h.get("key_experiment", ""))
        save = st.form_submit_button("Save Changes")
        if save:
            try:
                db.update_hypothesis(selected_id, {
                    "title": new_title,
                    "statement": new_statement,
                    "status": new_status,
                    "priority": new_priority,
                    "key_experiment": new_key_exp,
                })
                st.success("Saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")

    st.divider()
    if st.button("🗑 Delete this hypothesis", type="secondary"):
        if st.session_state.get("confirm_delete_hyp"):
            db.delete_hypothesis(selected_id)
            st.success("Deleted")
            st.session_state["confirm_delete_hyp"] = False
            st.rerun()
        else:
            st.session_state["confirm_delete_hyp"] = True
            st.warning("Click again to confirm deletion.")

# ── Opus Evaluation ───────────────────────────
with eval_tab:
    st.markdown("**Ask Opus to evaluate this hypothesis** — synthesizes evidence, estimates confidence, recommends next experiment.")
    st.caption("⚠️ Uses Claude Opus — significant cost per call. Use judiciously.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Run Opus Evaluation", type="primary"):
            with st.spinner("Running Opus evaluation..."):
                try:
                    result = hyp_logic.evaluate_hypothesis_with_opus(h)
                    st.session_state[f"eval_result_{selected_id}"] = result
                except Exception as e:
                    st.error(f"Opus call failed: {e}")

    with col2:
        if st.button("💡 Suggest Key Experiment"):
            with st.spinner("Thinking..."):
                try:
                    suggestion = hyp_logic.suggest_key_experiment(h["statement"])
                    st.session_state[f"key_exp_suggestion_{selected_id}"] = suggestion
                except Exception as e:
                    st.error(f"Failed: {e}")

    cached_eval = st.session_state.get(f"eval_result_{selected_id}")
    if cached_eval:
        st.markdown("---")
        st.markdown("#### Opus Evaluation")
        st.markdown(cached_eval)
        if st.button("Save evaluation as evidence note"):
            try:
                summary = f"[Opus evaluation {__import__('datetime').date.today()}] " + cached_eval[:300] + "..."
                db.add_evidence(selected_id, summary, "for")
                st.success("Saved as evidence!")
            except Exception as e:
                st.error(f"Failed: {e}")

    cached_suggestion = st.session_state.get(f"key_exp_suggestion_{selected_id}")
    if cached_suggestion:
        st.markdown("---")
        st.markdown("#### Suggested Key Experiment")
        st.markdown(cached_suggestion)
        if st.button("Save as key experiment"):
            try:
                db.update_hypothesis(selected_id, {"key_experiment": cached_suggestion})
                st.success("Saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")
