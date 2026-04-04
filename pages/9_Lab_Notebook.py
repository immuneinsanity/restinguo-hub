"""
Virtual Lab Notebook — log experiments, Opus-powered result interpretation.
"""

import streamlit as st
from datetime import date
from scientist import database as db
from scientist import notebook as nb_logic
from scientist.notebook import STATUS_OPTIONS, STATUS_COLORS

st.set_page_config(page_title="Lab Notebook · Restinguo", page_icon="📓", layout="wide")
st.title("📓 Virtual Lab Notebook")
st.caption("Log experiments, interpret results with Opus, track what we've learned.")

# ─────────────────────────────────────────────
# Load
# ─────────────────────────────────────────────
try:
    experiments = db.get_all_experiments()
    hypotheses = db.get_all_hypotheses()
    protocols = db.get_all_protocols()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

hyp_map = {h["id"]: h for h in hypotheses}
protocol_map = {p["id"]: p for p in protocols}

# ─────────────────────────────────────────────
# Create new experiment
# ─────────────────────────────────────────────
with st.expander("➕ Log New Experiment", expanded=not experiments):
    with st.form("create_experiment"):
        exp_title = st.text_input(
            "Experiment title",
            placeholder="e.g., Anifrolumab dose-response in COPA PBMCs — ISG score",
        )
        exp_date = st.date_input("Date", value=date.today())

        hyp_options = {"None": None} | {h["title"]: h["id"] for h in hypotheses}
        linked_hyp = st.selectbox("Hypothesis being tested (optional)", list(hyp_options.keys()))
        linked_hyp_id = hyp_options[linked_hyp]

        prot_options = {"None": None} | {p["title"]: p["id"] for p in protocols}
        linked_prot = st.selectbox("Protocol used (optional)", list(prot_options.keys()))
        linked_prot_id = prot_options[linked_prot]

        submitted = st.form_submit_button("Create Experiment Entry")
        if submitted:
            if not exp_title.strip():
                st.warning("Title required.")
            else:
                try:
                    new_exp = db.create_experiment(
                        title=exp_title.strip(),
                        hypothesis_id=linked_hyp_id,
                        protocol_id=linked_prot_id,
                        experiment_date=exp_date,
                    )
                    st.success(f"Created: {new_exp['experiment_id']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

st.divider()

# ─────────────────────────────────────────────
# Experiment list
# ─────────────────────────────────────────────
if not experiments:
    st.info("No experiments logged yet.")
    st.stop()

# Filter/sort
filter_status = st.multiselect(
    "Filter by status",
    STATUS_OPTIONS,
    default=STATUS_OPTIONS,
)

filtered = [e for e in experiments if e.get("status") in filter_status]
st.caption(f"Showing {len(filtered)} of {len(experiments)} experiments")

st.divider()

for exp in filtered:
    status = exp.get("status", "Planned")
    color = STATUS_COLORS.get(status, "#9B9B9B")
    hyp = hyp_map.get(exp.get("hypothesis_id", ""))
    prot = protocol_map.get(exp.get("protocol_id", ""))

    status_icon = {"Planned": "🔵", "In Progress": "🟡", "Complete": "🟢", "Failed": "🔴"}.get(status, "⚪")

    with st.expander(
        f"{status_icon} **{exp['experiment_id']}** — {exp['title']} ({exp.get('date', '')})",
        expanded=status == "In Progress",
    ):
        # Metadata row
        meta_cols = st.columns(3)
        with meta_cols[0]:
            if hyp:
                st.caption(f"**Hypothesis:** {hyp['title']}")
            else:
                st.caption("No hypothesis linked")
        with meta_cols[1]:
            if prot:
                st.caption(f"**Protocol:** {prot['title']}")
            else:
                st.caption("No protocol linked")
        with meta_cols[2]:
            new_status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(status),
                key=f"status_{exp['id']}",
            )
            if new_status != status:
                try:
                    db.update_experiment(exp["id"], {"status": new_status})
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

        tab1, tab2, tab3 = st.tabs(["Results", "Interpretation", "Next Steps"])

        # ── Results tab ─────────────────────────────
        with tab1:
            current_results = exp.get("results", "") or ""
            new_results = st.text_area(
                "Log results (data, observations, numerical values)",
                value=current_results,
                height=150,
                key=f"results_{exp['id']}",
                placeholder="e.g., ISG score reduced from mean 3.2 to 0.8 (75% suppression) at 10 μg/mL anifrolumab. "
                            "n=4 COPA patients. p=0.02 by paired t-test. Isotype control: no change.",
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save results", key=f"save_results_{exp['id']}"):
                    try:
                        db.update_experiment(exp["id"], {"results": new_results})
                        st.success("Saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")
            with col2:
                if new_results.strip() and st.button(
                    "🧠 Interpret with Opus",
                    key=f"interpret_{exp['id']}",
                    type="primary",
                ):
                    with st.spinner("Running Opus interpretation..."):
                        try:
                            interpretation = nb_logic.interpret_results_with_opus(
                                experiment_title=exp["title"],
                                hypothesis_statement=hyp["statement"] if hyp else None,
                                protocol_summary=prot["research_question"] if prot else None,
                                results_text=new_results,
                            )
                            st.session_state[f"interp_{exp['id']}"] = interpretation
                            # Auto-save
                            db.update_experiment(exp["id"], {"interpretation": interpretation})
                        except Exception as e:
                            st.error(f"Opus failed: {e}")

        # ── Interpretation tab ───────────────────────
        with tab2:
            cached_interp = st.session_state.get(f"interp_{exp['id']}", exp.get("interpretation", "") or "")
            if cached_interp:
                st.markdown(cached_interp)
            else:
                st.info("No interpretation yet. Log results and click 'Interpret with Opus'.")

        # ── Next Steps tab ───────────────────────────
        with tab3:
            current_next = exp.get("next_steps", "") or ""
            new_next = st.text_area(
                "Next steps",
                value=current_next,
                height=100,
                key=f"next_{exp['id']}",
                placeholder="Experiments to run next based on these results...",
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save next steps", key=f"save_next_{exp['id']}"):
                    try:
                        db.update_experiment(exp["id"], {"next_steps": new_next})
                        st.success("Saved!")
                    except Exception as e:
                        st.error(f"Failed: {e}")
            with c2:
                if exp.get("results") and st.button(
                    "💡 Generate next steps (Opus)",
                    key=f"gen_next_{exp['id']}",
                ):
                    with st.spinner("Thinking..."):
                        try:
                            from scientist.prompts import RESULT_INTERPRETATION_SYSTEM
                            from scientist import drafter
                            prompt = f"""Based on these experimental results from {exp['title']}:

{exp['results']}

{'Hypothesis tested: ' + hyp['statement'] if hyp else ''}

Generate 3 concrete next experiments, ordered by priority, for Restinguo's program.
For each: state the question it answers, the experimental approach, and why it's the right next step."""
                            suggestion = drafter.opus(
                                prompt, RESULT_INTERPRETATION_SYSTEM, max_tokens=800
                            )
                            st.session_state[f"next_gen_{exp['id']}"] = suggestion
                        except Exception as e:
                            st.error(f"Failed: {e}")

            gen_next = st.session_state.get(f"next_gen_{exp['id']}")
            if gen_next:
                st.markdown("---")
                st.markdown("**Opus suggestions:**")
                st.markdown(gen_next)
                if st.button("Use these next steps", key=f"use_next_{exp['id']}"):
                    db.update_experiment(exp["id"], {"next_steps": gen_next})
                    st.success("Saved!")
                    st.rerun()
