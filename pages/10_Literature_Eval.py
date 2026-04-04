"""
Literature Evaluation — paste a paper abstract, Opus evaluates its impact on the Restinguo program.
"""

import streamlit as st
from scientist import database as db
from scientist import drafter
from scientist.prompts import LITERATURE_EVAL_SYSTEM

st.set_page_config(page_title="Literature Eval · Restinguo", page_icon="📚", layout="wide")
st.title("📚 Literature Evaluator")
st.caption("Paste a paper abstract → Opus evaluates strategic impact on the Restinguo program.")

# ─────────────────────────────────────────────
# Load
# ─────────────────────────────────────────────
try:
    hypotheses = db.get_all_hypotheses()
    recent_evals = db.get_recent_literature_evals(20)
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# Input form
# ─────────────────────────────────────────────
st.subheader("Evaluate New Paper")

with st.form("eval_paper"):
    paper_title = st.text_input(
        "Paper title (optional)",
        placeholder="e.g., Freuchet et al. 2021 — STING Golgi retention in COPA syndrome",
    )
    abstract_text = st.text_area(
        "Abstract / summary text",
        height=200,
        placeholder="Paste the abstract or a summary of the paper here...",
    )
    st.caption(
        "⚠️ Uses Claude Opus. Long abstracts will be pre-summarized by Mistral to save tokens. "
        "For very long texts, paste only the abstract."
    )
    submitted = st.form_submit_button("🧠 Evaluate with Opus", type="primary")

if submitted:
    if not abstract_text.strip():
        st.warning("Abstract text is required.")
    else:
        # Preprocess with Mistral if long
        preprocess = len(abstract_text) > 1500
        if preprocess:
            st.info("Pre-summarizing with Mistral before Opus evaluation...")

        prompt = f"""Evaluate this paper for strategic impact on Restinguo's COPA/IFNAR program:

{'PAPER: ' + paper_title if paper_title.strip() else ''}

ABSTRACT:
{abstract_text}

OPEN HYPOTHESES FOR CONTEXT:
{chr(10).join(f'- {h["title"]}: {h["statement"]}' for h in hypotheses[:5])}

Output the full evaluation as a JSON object per the specified format."""

        with st.spinner("Running Opus evaluation... (30-60 seconds)"):
            try:
                result = drafter.opus_json(
                    prompt,
                    LITERATURE_EVAL_SYSTEM,
                    max_tokens=3000,
                    preprocess=preprocess,
                )

                if "error" in result:
                    st.error(f"Parse failed: {result['error']}")
                    st.text_area("Raw Opus response", result.get("raw", ""), height=300)
                else:
                    # Save to DB
                    saved = db.save_literature_eval(
                        abstract_text=abstract_text,
                        evaluation=result,
                        paper_title=paper_title.strip(),
                    )
                    st.session_state["latest_eval"] = result
                    st.session_state["latest_eval_title"] = paper_title
                    st.success("Evaluation complete and saved!")

            except Exception as e:
                st.error(f"Opus call failed: {e}")

# ─────────────────────────────────────────────
# Helper render function
# ─────────────────────────────────────────────
def _render_evaluation(ev: dict, title: str = ""):
    st.subheader(f"📊 Evaluation: {title or 'Paper'}")

    # Summary + score
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**Summary:** {ev.get('paper_summary', '')}")
    with col2:
        score = ev.get("relevance_score", 0)
        color = "#7ED321" if score >= 7 else ("#F5A623" if score >= 4 else "#D0021B")
        st.markdown(
            f'<div style="text-align:center; font-size: 2em; color: {color}; font-weight: bold">{score}/10</div>'
            f'<div style="text-align:center; font-size: 0.75em; color: #888">Relevance</div>',
            unsafe_allow_html=True,
        )
    st.caption(ev.get("relevance_rationale", ""))

    st.divider()

    # Hypothesis impacts
    impacts = ev.get("hypothesis_impacts", [])
    if impacts:
        st.subheader("Impact on Hypotheses")
        impact_icons = {
            "strengthens": "✅",
            "weakens": "❌",
            "settles": "🏁",
            "neutral": "➖",
        }
        for imp in impacts:
            impact_type = imp.get("impact", "neutral").lower()
            icon = impact_icons.get(impact_type, "❓")
            with st.container():
                st.markdown(
                    f"{icon} **{imp.get('hypothesis', '')}** — _{impact_type.upper()}_"
                )
                st.caption(imp.get("reasoning", ""))

    st.divider()

    # Suggested experiments
    experiments = ev.get("suggested_experiments", [])
    if experiments:
        st.subheader("Suggested Experiments")
        from scientist.hypotheses import PRIORITY_COLORS
        for exp in experiments:
            priority = exp.get("priority", "Medium")
            color = PRIORITY_COLORS.get(priority, "#9B9B9B")
            st.markdown(
                f'<div style="border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 8px;">'
                f'<strong>{exp.get("experiment", "")}</strong><br>'
                f'<span style="font-size: 0.85em; color: #ccc">{exp.get("rationale", "")}</span><br>'
                f'<span style="color: {color}; font-size: 0.75em">{priority}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Competitive intelligence + strategic takeaway
    col1, col2 = st.columns(2)
    with col1:
        comp_intel = ev.get("competitive_intelligence", "")
        if comp_intel:
            st.subheader("Competitive Intelligence")
            st.markdown(comp_intel)
    with col2:
        takeaway = ev.get("strategic_takeaway", "")
        if takeaway:
            st.subheader("Strategic Takeaway")
            st.info(takeaway)


# ─────────────────────────────────────────────
# Display latest evaluation
# ─────────────────────────────────────────────
if "latest_eval" in st.session_state:
    ev = st.session_state["latest_eval"]
    title = st.session_state.get("latest_eval_title", "")
    st.divider()
    _render_evaluation(ev, title)

st.divider()

# ─────────────────────────────────────────────
# History
# ─────────────────────────────────────────────
st.subheader("Evaluation History")

if not recent_evals:
    st.info("No evaluations yet.")
else:
    for ev_row in recent_evals:
        ev = ev_row.get("evaluation", {})
        title = ev_row.get("paper_title", "") or "Untitled"
        score = ev.get("relevance_score", 0)
        created = ev_row.get("created_at", "")[:10]
        summary = ev.get("paper_summary", "")[:150]
        takeaway = ev.get("strategic_takeaway", "")

        with st.expander(f"📄 {title} — Relevance: {score}/10 · {created}"):
            st.caption(summary)
            if takeaway:
                st.info(f"**Strategic takeaway:** {takeaway}")

            impacts = ev.get("hypothesis_impacts", [])
            if impacts:
                impact_icons = {"strengthens": "✅", "weakens": "❌", "settles": "🏁", "neutral": "➖"}
                for imp in impacts:
                    icon = impact_icons.get(imp.get("impact", "neutral").lower(), "❓")
                    st.markdown(f"{icon} **{imp.get('hypothesis', '')}**: {imp.get('reasoning', '')[:100]}")

            experiments = ev.get("suggested_experiments", [])
            if experiments:
                st.markdown("**Suggested experiments:**")
                for exp in experiments[:2]:
                    st.markdown(f"- {exp.get('experiment', '')}")
