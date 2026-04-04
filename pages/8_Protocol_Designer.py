"""
Protocol Designer — Opus-powered experimental protocol generation.
"""

import json
import streamlit as st
from scientist import database as db
from scientist import drafter
from scientist.prompts import PROTOCOL_DESIGN_SYSTEM, SONNET_FORMAT_PROTOCOL_SYSTEM

st.set_page_config(page_title="Protocol Designer · Restinguo", page_icon="🔬", layout="wide")
st.title("🔬 Protocol Designer")
st.caption("AI-generated experimental protocols — powered by Claude Opus")

# ─────────────────────────────────────────────
# Load hypotheses for linking
# ─────────────────────────────────────────────
try:
    hypotheses = db.get_all_hypotheses()
    protocols = db.get_all_protocols()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# Design new protocol
# ─────────────────────────────────────────────
st.subheader("Design New Protocol")
st.info(
    "Describe your research question and Opus will generate a full experimental protocol "
    "including methodology, controls, readouts, statistics, and pitfall mitigations."
)

with st.form("design_protocol"):
    research_question = st.text_area(
        "Research question",
        placeholder="e.g., Does anifrolumab suppress the IFN signature in COPA patient PBMCs in a dose-dependent manner?",
        height=80,
    )

    hyp_options = {"None": None} | {h["title"]: h["id"] for h in hypotheses}
    linked_hyp_label = st.selectbox("Link to hypothesis (optional)", list(hyp_options.keys()))
    linked_hyp_id = hyp_options[linked_hyp_label]

    additional_context = st.text_area(
        "Additional context (optional)",
        placeholder="e.g., We have 6 COPA patient PBMC samples (n=6), healthy controls (n=6), "
                    "anifrolumab available at 10 μg/mL stock...",
        height=80,
    )

    st.caption("⚠️ Uses Claude Opus — this call may take 30-60 seconds.")
    submitted = st.form_submit_button("🧠 Generate Protocol", type="primary")

if submitted:
    if not research_question.strip():
        st.warning("Research question is required.")
    else:
        hyp_context = ""
        if linked_hyp_id:
            hyp = db.get_hypothesis(linked_hyp_id)
            if hyp:
                hyp_context = f"\n\nHYPOTHESIS BEING ADDRESSED: {hyp['statement']}"

        prompt = f"""Design a complete experimental protocol for Restinguo:

RESEARCH QUESTION: {research_question}
{hyp_context}
{f'ADDITIONAL CONTEXT: {additional_context}' if additional_context.strip() else ''}

Generate the full protocol as a JSON object per the specified format.
Be specific to COPA syndrome biology and Restinguo's resource constraints (startup, limited patient samples, no in-house animal facility, UCSF collaborator Anthony Shum).
Include realistic cost estimates and timeline for a lean early-stage biotech."""

        with st.spinner("Generating protocol with Opus... (30-60 seconds)"):
            try:
                protocol_data = drafter.opus_json(
                    prompt,
                    PROTOCOL_DESIGN_SYSTEM,
                    max_tokens=4096,
                    preprocess=False,
                )

                if "error" in protocol_data:
                    st.error(f"Failed to parse protocol: {protocol_data['error']}")
                    st.text_area("Raw response", protocol_data.get("raw", ""), height=300)
                else:
                    st.session_state["latest_protocol"] = {
                        "data": protocol_data,
                        "research_question": research_question,
                        "hypothesis_id": linked_hyp_id,
                    }
                    st.success("Protocol generated!")

            except Exception as e:
                st.error(f"Opus call failed: {e}")

# ─────────────────────────────────────────────
# Display generated protocol
# ─────────────────────────────────────────────
if "latest_protocol" in st.session_state:
    latest = st.session_state["latest_protocol"]
    protocol = latest["data"]
    st.divider()
    st.subheader(f"📋 {protocol.get('title', 'Generated Protocol')}")

    # Save button
    save_col, _ = st.columns([2, 6])
    with save_col:
        if st.button("💾 Save to Library", type="primary"):
            try:
                saved = db.save_protocol(
                    title=protocol.get("title", "Untitled Protocol"),
                    research_question=latest["research_question"],
                    content=protocol,
                    hypothesis_id=latest.get("hypothesis_id"),
                )
                st.success(f"Saved! Protocol ID: {saved['id'][:8]}...")
                del st.session_state["latest_protocol"]
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save: {e}")

    # Render protocol
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"**Objective:** {protocol.get('objective', '')}")
        st.markdown(f"**Experimental System:** {protocol.get('experimental_system', '')}")
        st.markdown(f"**Timeline:** {protocol.get('timeline_weeks', '?')} weeks")
        st.markdown(f"**Estimated Cost:** {protocol.get('cost_estimate', 'TBD')}")

        if protocol.get("copa_specific_considerations"):
            st.info(f"**COPA-specific:** {protocol['copa_specific_considerations']}")

        st.markdown("#### Methodology")
        steps = protocol.get("methodology", [])
        for i, step in enumerate(steps, 1):
            st.markdown(f"{i}. {step}")

        st.markdown("#### Controls")
        controls = protocol.get("controls", {})
        for k, v in controls.items():
            if v:
                st.markdown(f"- **{k.title()}:** {v}")

    with col2:
        st.markdown("#### Readouts")
        for r in protocol.get("readouts", []):
            st.markdown(
                f"- **{r.get('assay', '')}** — {r.get('timepoint', '')} ({r.get('platform', '')})"
            )

        st.markdown("#### Statistics")
        st.markdown(protocol.get("statistics", ""))
        if protocol.get("power_calculation"):
            st.caption(f"Power: {protocol['power_calculation']}")

        st.markdown("#### Reagents")
        for reagent in protocol.get("reagents", []):
            st.markdown(
                f"- **{reagent.get('name', '')}** — {reagent.get('source', '')} "
                f"{'('+reagent.get('catalog','')+')' if reagent.get('catalog') else ''}"
            )
            if reagent.get("notes"):
                st.caption(f"  ↳ {reagent['notes']}")

        st.markdown("#### Pitfalls & Mitigations")
        for p in protocol.get("pitfalls", []):
            st.warning(
                f"**Risk:** {p.get('risk', '')}  \n**Mitigation:** {p.get('mitigation', '')}"
            )

    st.markdown("#### Interpretation Guide")
    guide = protocol.get("interpretation_guide", {})
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success(f"**Supports hypothesis:** {guide.get('supports_hypothesis', '')}")
    with c2:
        st.error(f"**Refutes hypothesis:** {guide.get('refutes_hypothesis', '')}")
    with c3:
        st.warning(f"**Ambiguous:** {guide.get('ambiguous', '')}")

    st.markdown("#### Expected Results")
    st.markdown(protocol.get("expected_results", ""))

st.divider()

# ─────────────────────────────────────────────
# Protocol library
# ─────────────────────────────────────────────
st.subheader("Protocol Library")

if not protocols:
    st.info("No protocols saved yet. Generate and save one above.")
else:
    for p in protocols:
        content = p.get("content", {})
        created = p.get("created_at", "")[:10]
        with st.expander(f"📋 {p['title']} — {created}"):
            st.caption(f"**Research question:** {p['research_question']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**System:** {content.get('experimental_system', '—')[:60]}")
            with col2:
                st.markdown(f"**Timeline:** {content.get('timeline_weeks', '?')} weeks")
            with col3:
                st.markdown(f"**Cost:** {content.get('cost_estimate', '?')}")

            with st.expander("View full protocol"):
                st.json(content)

            if st.button("🗑 Delete", key=f"del_protocol_{p['id']}"):
                try:
                    db.delete_protocol(p["id"])
                    st.success("Deleted")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")
