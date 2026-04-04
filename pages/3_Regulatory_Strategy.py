"""
Restinguo Hub — Regulatory Strategy Agent
COPA Syndrome · IFNAR Blockade Program
"""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    for _k in ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_KEY",
               "DATABASE_URL", "OLLAMA_URL", "OLLAMA_MODEL"]:
        if _k in st.secrets and _k not in os.environ:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

from regulatory.database import (
    init_db,
    get_pathway_status, update_pathway_status,
    get_all_roadmap_items, update_roadmap_item,
    get_all_meetings, create_meeting, update_meeting,
    add_meeting_question, get_meeting_questions,
    save_document_metadata, get_all_documents,
    save_ai_output, get_ai_outputs,
)
from regulatory.pathways import (
    get_all_pathways, STATUS_COLORS, STATUS_ICONS,
)
from regulatory.roadmap import get_all_stages, get_stage, STAGES
from regulatory.meetings import (
    MEETING_TYPES, MEETING_STATUSES,
    get_pre_ind_agenda_template, get_meeting_request_template,
)
from regulatory.drafter import (
    check_ollama_available,
    run_pipeline_strategy_memo,
    run_pipeline_pre_ind_agenda,
    run_pipeline_odd_narrative,
    run_general_query,
)

init_db()

st.set_page_config(
    page_title="Restinguo Hub · Regulatory Strategy",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Regulatory Strategy")
    st.markdown("**COPA Syndrome · IFNAR Blockade**")
    st.divider()

    st.markdown("**Program Status**")
    odd_db = get_pathway_status("odd")
    current_stage_db = next(
        (s for s in get_all_roadmap_items() if s["status"] == "In Progress"), None
    )
    odd_status = odd_db["status"] if odd_db else "Not Started"
    current_stage_name = (
        get_stage(current_stage_db["stage_key"]).name
        if current_stage_db else "Target Validation"
    )
    st.markdown(f"Stage: **{current_stage_name}**")
    st.markdown(f"ODD: {STATUS_ICONS.get(odd_status, '⬜')} {odd_status}")
    st.divider()

    st.markdown("**⚡ Priority Action**")
    st.info("File Orphan Drug Designation (ODD) — no compound required, qualifies now.")

    st.divider()
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key and api_key != "your_anthropic_api_key_here":
        st.success("Claude API: Connected")
    else:
        st.warning("Claude API: Not configured")

    ollama_ok, ollama_msg = check_ollama_available()
    if ollama_ok:
        st.success("Ollama/Mistral: Connected")
    else:
        st.warning("Ollama/Mistral: Offline")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Dashboard",
    "🏷️ Pathways",
    "🗺️ Pre-IND Roadmap",
    "🤝 FDA Meetings",
    "🤖 AI Strategy",
    "📁 Document Library",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.header("Regulatory Strategy Dashboard")
    st.markdown("*Restinguo · COPA Syndrome · IFNAR Blockade Program*")

    col1, col2, col3, col4 = st.columns(4)
    all_pathways_db = {p.key: get_pathway_status(p.key) for p in get_all_pathways()}
    granted = sum(1 for v in all_pathways_db.values() if v and v["status"] == "Granted")
    roadmap_items_db = get_all_roadmap_items()
    complete_stages = sum(1 for s in roadmap_items_db if s["status"] == "Complete")
    total_stages = len(roadmap_items_db)
    meetings_db = get_all_meetings()
    active_meetings = sum(1 for m in meetings_db if m["status"] not in ("Completed", "Cancelled"))

    col1.metric("Designations Granted", f"{granted} / 4")
    col2.metric("Roadmap Progress", f"{complete_stages} / {total_stages} stages")
    col3.metric("Active FDA Meetings", active_meetings)
    col4.metric("AI Outputs Saved", len(get_ai_outputs()))

    st.divider()

    st.subheader("Designation Status")
    pathway_cols = st.columns(4)
    for i, pathway_def in enumerate(get_all_pathways()):
        db_row = all_pathways_db.get(pathway_def.key)
        status = db_row["status"] if db_row else "Not Started"
        with pathway_cols[i]:
            color = STATUS_COLORS.get(status, "#6b7280")
            icon = STATUS_ICONS.get(status, "⬜")
            st.markdown(f"""
                <div style='border:1px solid {color}; border-radius:8px; padding:12px; text-align:center;'>
                    <div style='font-size:24px'>{pathway_def.icon}</div>
                    <div style='font-weight:bold; font-size:14px'>{pathway_def.short_name}</div>
                    <div style='color:{color}; font-size:13px'>{icon} {status}</div>
                    <div style='font-size:11px; color:#9ca3af; margin-top:4px'>Priority: {pathway_def.priority}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Pre-IND Roadmap Progress")
    stage_status_map = {s["stage_key"]: s["status"] for s in roadmap_items_db}
    for stage_def in get_all_stages():
        status = stage_status_map.get(stage_def.key, "Pending")
        status_color = {
            "In Progress": "#f59e0b",
            "Complete": "#10b981",
            "Pending": "#6b7280",
            "Blocked": "#ef4444",
        }.get(status, "#6b7280")
        icon = {"In Progress": "🔄", "Complete": "✅", "Pending": "⬜", "Blocked": "🚫"}.get(status, "⬜")
        st.markdown(
            f"**{stage_def.order}. {stage_def.name}** — "
            f"<span style='color:{status_color}'>{icon} {status}</span> "
            f"<span style='color:#9ca3af; font-size:13px'>({stage_def.duration_estimate})</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("⚠️ Key Program Risks")
    risks = [
        ("Critical", "No validated animal model for COPA syndrome", "Must resolve before IND — discuss with FDA in Pre-IND meeting"),
        ("High", "ODD not yet filed", "Highest-priority near-term action — qualifies now, no compound required"),
        ("High", "No lead compound identified", "IP landscape analysis needed — anifrolumab FTO critical"),
        ("Medium", "Rare Pediatric PRV program subject to Congressional reauthorization", "Monitor legislative status"),
        ("Low", "IFN blockade immunosuppression risk", "Quantify in tox studies; precedent from anifrolumab is reassuring"),
    ]
    for severity, risk, mitigation in risks:
        severity_color = {"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#6b7280"}[severity]
        st.markdown(
            f"<span style='background:{severity_color}; color:white; border-radius:3px; padding:1px 6px; font-size:11px'>{severity}</span> "
            f"**{risk}** — *{mitigation}*",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: PATHWAYS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.header("FDA Regulatory Pathways")
    st.markdown(
        "Key designations relevant to the Restinguo COPA syndrome program. "
        "Update status as applications progress."
    )

    for pathway_def in get_all_pathways():
        db_row = get_pathway_status(pathway_def.key)
        status = db_row["status"] if db_row else "Not Started"
        notes_saved = db_row["notes"] if db_row else ""
        color = STATUS_COLORS.get(status, "#6b7280")
        icon = STATUS_ICONS.get(status, "⬜")

        with st.expander(
            f"{pathway_def.icon} {pathway_def.name} ({pathway_def.short_name}) — {icon} {status}",
            expanded=(pathway_def.priority <= 2),
        ):
            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.markdown(f"**What it is:** {pathway_def.what_it_is}")

                st.markdown("**Eligibility Checklist:**")
                for item in pathway_def.eligibility:
                    checkmark = "✅" if "qualifies" in item.lower() or "copa" in item.lower() else "☑️"
                    st.markdown(f"- {checkmark} {item}")

                st.markdown("**Benefits:**")
                for b in pathway_def.benefits:
                    st.markdown(f"- {b}")

                st.markdown(f"**Timing:** {pathway_def.timing}")
                st.markdown(f"**Strategic Value:** {pathway_def.strategic_value}")
                st.markdown(f"**Application Notes:** {pathway_def.application_notes}")
                st.markdown(f"**Timeline Estimate:** `{pathway_def.timeline_estimate}`")
                st.markdown(f"**FDA Office:** {pathway_def.fda_office}")

            with col_right:
                st.markdown("**Update Status**")
                new_status = st.selectbox(
                    "Status",
                    ["Not Started", "In Progress", "Submitted", "Granted"],
                    index=["Not Started", "In Progress", "Submitted", "Granted"].index(status),
                    key=f"status_{pathway_def.key}",
                )
                submitted_date = st.text_input(
                    "Submitted Date",
                    value=db_row.get("submitted_date") or "" if db_row else "",
                    placeholder="YYYY-MM-DD",
                    key=f"sub_{pathway_def.key}",
                )
                granted_date = st.text_input(
                    "Granted Date",
                    value=db_row.get("granted_date") or "" if db_row else "",
                    placeholder="YYYY-MM-DD",
                    key=f"grant_{pathway_def.key}",
                )
                notes_input = st.text_area(
                    "Notes",
                    value=notes_saved or "",
                    height=100,
                    key=f"notes_{pathway_def.key}",
                )
                if st.button("Save", key=f"save_{pathway_def.key}"):
                    update_pathway_status(
                        pathway_def.key,
                        new_status,
                        notes=notes_input or None,
                        submitted_date=submitted_date or None,
                        granted_date=granted_date or None,
                    )
                    st.success("Saved.")
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: PRE-IND ROADMAP
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.header("Pre-IND Roadmap")
    st.markdown(
        "Interactive checklist from target validation to IND filing. "
        "Update each stage as work progresses."
    )

    roadmap_items_db = {s["stage_key"]: s for s in get_all_roadmap_items()}

    for stage_def in get_all_stages():
        db_row = roadmap_items_db.get(stage_def.key, {})
        status = db_row.get("status", "Pending")
        notes_saved = db_row.get("notes") or ""

        status_color = {
            "In Progress": "#f59e0b",
            "Complete": "#10b981",
            "Pending": "#6b7280",
            "Blocked": "#ef4444",
        }.get(status, "#6b7280")
        status_icon = {
            "In Progress": "🔄",
            "Complete": "✅",
            "Pending": "⬜",
            "Blocked": "🚫",
        }.get(status, "⬜")

        is_current = status == "In Progress"
        with st.expander(
            f"**Stage {stage_def.order}: {stage_def.name}** — {status_icon} {status} · {stage_def.duration_estimate}",
            expanded=is_current,
        ):
            col_main, col_status = st.columns([3, 1])

            with col_main:
                st.markdown(f"**Phase:** {stage_def.phase}")
                st.markdown(stage_def.description)

                st.markdown("**Checklist:**")
                for item in stage_def.checklist:
                    st.markdown(f"- ☐ {item}")

                st.markdown("**Key Questions / Risks:**")
                for q in stage_def.key_questions:
                    st.markdown(f"- ❓ {q}")

                if stage_def.key_risks:
                    st.markdown("**Risks:**")
                    for r in stage_def.key_risks:
                        st.markdown(f"- ⚠️ {r}")

                st.markdown("**Deliverables:**")
                for d in stage_def.deliverables:
                    st.markdown(f"- 📄 {d}")

            with col_status:
                st.markdown("**Update Stage**")
                new_status = st.selectbox(
                    "Status",
                    ["Pending", "In Progress", "Blocked", "Complete"],
                    index=["Pending", "In Progress", "Blocked", "Complete"].index(
                        status if status in ["Pending", "In Progress", "Blocked", "Complete"] else "Pending"
                    ),
                    key=f"rs_{stage_def.key}",
                )
                started = st.text_input(
                    "Started",
                    value=db_row.get("started_date") or "",
                    placeholder="YYYY-MM-DD",
                    key=f"rstart_{stage_def.key}",
                )
                completed = st.text_input(
                    "Completed",
                    value=db_row.get("completed_date") or "",
                    placeholder="YYYY-MM-DD",
                    key=f"rcomplete_{stage_def.key}",
                )
                notes_input = st.text_area(
                    "Notes",
                    value=notes_saved,
                    height=100,
                    key=f"rnotes_{stage_def.key}",
                )
                if st.button("Save", key=f"rsave_{stage_def.key}"):
                    update_roadmap_item(
                        stage_def.key,
                        new_status,
                        notes=notes_input or None,
                        started_date=started or None,
                        completed_date=completed or None,
                    )
                    st.success("Saved.")
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: FDA MEETINGS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.header("FDA Meeting Tracker")

    with st.expander("FDA Meeting Types — Reference", expanded=False):
        for mtype, info in MEETING_TYPES.items():
            relevant = "✅ Relevant for Restinguo" if info["relevant_for_restinguo"] else "ℹ️ Less likely needed"
            st.markdown(f"### {mtype} Meeting")
            st.markdown(f"{info['description']}")
            st.markdown(f"**Timeline:** {info['timeline']}")
            st.markdown(f"**Use when:** {info['when_to_use']}")
            st.markdown(f"{relevant}")
            st.divider()

    st.subheader("Pre-IND Meeting Agenda Template")
    with st.expander("View / Copy Template", expanded=False):
        st.text_area(
            "Template",
            value=get_pre_ind_agenda_template(),
            height=400,
            key="agenda_template_display",
        )

    st.divider()

    st.subheader("Log a New Meeting")
    with st.form("new_meeting_form"):
        m_type = st.selectbox("Meeting Type", list(MEETING_TYPES.keys()))
        m_purpose = st.text_area("Purpose / Topic", height=80)
        m_status = st.selectbox("Status", MEETING_STATUSES)
        m_notes = st.text_area("Notes", height=80)
        submitted_form = st.form_submit_button("Add Meeting")
        if submitted_form and m_purpose:
            create_meeting(m_type, m_purpose, m_status, m_notes or None)
            st.success("Meeting added.")
            st.rerun()

    st.divider()

    st.subheader("Meeting Log")
    meetings_db = get_all_meetings()
    if not meetings_db:
        st.info("No meetings logged yet. Add your first meeting above.")
    else:
        for m in meetings_db:
            status_icon = {
                "Planning": "📝", "Request Drafted": "✏️", "Request Submitted": "📬",
                "Scheduled": "📅", "Completed": "✅", "Cancelled": "❌",
            }.get(m["status"], "📋")
            with st.expander(
                f"{status_icon} {m['meeting_type']} — {m['purpose'][:60]}... | {m['status']}",
                expanded=False,
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Purpose:** {m['purpose']}")
                    if m.get("fda_response"):
                        st.markdown(f"**FDA Response:** {m['fda_response']}")
                    if m.get("notes"):
                        st.markdown(f"**Notes:** {m['notes']}")

                    questions = get_meeting_questions(m["id"])
                    if questions:
                        st.markdown("**Questions for FDA:**")
                        for q in questions:
                            st.markdown(f"- Q{q['priority']}: {q['question']}")
                            if q.get("fda_response"):
                                st.markdown(f"  *FDA: {q['fda_response']}*")

                    new_q = st.text_input(
                        "Add question for FDA",
                        key=f"q_input_{m['id']}",
                        placeholder="E.g., Will FDA accept the SAVI mouse for IND-enabling tox?",
                    )
                    q_priority = st.number_input("Priority (1=high)", min_value=1, max_value=10, value=5, key=f"qp_{m['id']}")
                    if st.button("Add Question", key=f"addq_{m['id']}"):
                        if new_q:
                            add_meeting_question(m["id"], new_q, int(q_priority))
                            st.success("Question added.")
                            st.rerun()

                with col2:
                    st.markdown("**Update Meeting**")
                    new_m_status = st.selectbox(
                        "Status",
                        MEETING_STATUSES,
                        index=MEETING_STATUSES.index(m["status"]) if m["status"] in MEETING_STATUSES else 0,
                        key=f"mstatus_{m['id']}",
                    )
                    req_date = st.text_input("Requested Date", value=m.get("requested_date") or "", key=f"mreq_{m['id']}")
                    sched_date = st.text_input("Scheduled Date", value=m.get("scheduled_date") or "", key=f"msched_{m['id']}")
                    fda_resp = st.text_area("FDA Response", value=m.get("fda_response") or "", height=80, key=f"mfda_{m['id']}")
                    if st.button("Update", key=f"mupdate_{m['id']}"):
                        update_meeting(
                            m["id"],
                            status=new_m_status,
                            requested_date=req_date or None,
                            scheduled_date=sched_date or None,
                            fda_response=fda_resp or None,
                        )
                        st.success("Updated.")
                        st.rerun()

    st.divider()
    st.subheader("Meeting Request Letter Template")
    col_mtype, col_mpurpose = st.columns(2)
    tmpl_type = col_mtype.selectbox("Meeting type for template", list(MEETING_TYPES.keys()), key="tmpl_type")
    tmpl_purpose = col_mpurpose.text_input("Purpose", value="Pre-IND consultation on COPA syndrome IFNAR program", key="tmpl_purpose")
    st.text_area("Template", value=get_meeting_request_template(tmpl_type, tmpl_purpose), height=300, key="tmpl_output")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: AI STRATEGY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.header("AI Regulatory Strategy")
    st.markdown(
        "Two-tier AI pipeline: **Mistral** (Ollama) preprocesses guidance docs → "
        "**Claude** drafts final regulatory outputs. All prompts are pre-loaded with "
        "Restinguo / COPA syndrome context."
    )

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    claude_ready = api_key and api_key != "your_anthropic_api_key_here"

    col_s1, col_s2 = st.columns(2)
    col_s1.markdown(
        f"{'✅' if claude_ready else '❌'} **Claude API** (claude-sonnet-4-6) — "
        f"{'Ready' if claude_ready else 'Add ANTHROPIC_API_KEY to secrets'}"
    )
    col_s2.markdown(
        f"{'✅' if ollama_ok else '⚠️'} **Mistral / Ollama** — "
        f"{'Ready' if ollama_ok else 'Offline (Claude will run without Mistral preprocessing)'}"
    )

    st.divider()

    task = st.selectbox(
        "Select Task",
        [
            "Strategy Memo (from guidance doc)",
            "Draft Pre-IND Agenda",
            "Draft ODD Narrative (Prevalence/Medical Plausibility)",
            "General Regulatory Question",
        ],
    )

    result_text = ""

    if task == "Strategy Memo (from guidance doc)":
        st.markdown("Paste an FDA guidance document or regulatory text. Mistral will summarize it, then Claude will draft a strategy memo.")
        doc_text = st.text_area("Guidance Document / Regulatory Text", height=200, placeholder="Paste FDA guidance text here...")
        user_request = st.text_area(
            "Your Request / Question",
            height=80,
            placeholder="E.g., How should we apply this guidance to our Pre-IND meeting for COPA syndrome?",
        )
        title = st.text_input("Output Title (for saving)", value="Strategy Memo")

        if st.button("Generate Strategy Memo", type="primary"):
            if not doc_text or not user_request:
                st.warning("Provide both document text and your request.")
            elif not claude_ready:
                st.error("Claude API not configured. Add ANTHROPIC_API_KEY to secrets.")
            else:
                with st.spinner("Running two-tier pipeline..."):
                    result, err, mistral_summary = run_pipeline_strategy_memo(doc_text, user_request)
                if err:
                    st.error(err)
                else:
                    with st.expander("Mistral Summary (preprocessing)", expanded=False):
                        st.markdown(mistral_summary)
                    st.markdown("### Strategy Memo")
                    st.markdown(result)
                    if st.button("Save Output"):
                        save_ai_output("strategy_memo", title, result, "claude-sonnet-4-6")
                        st.success("Saved to Document Library → AI Outputs.")

    elif task == "Draft Pre-IND Agenda":
        st.markdown("Describe the focus areas for your Pre-IND meeting. Claude will draft a full agenda and question list.")
        focus = st.text_area(
            "Focus Areas / Key Questions",
            height=150,
            value="1. Animal model acceptability — Copa KI mouse vs SAVI mouse surrogate\n"
                  "2. Phase 1 design for ultra-rare population (combined Phase 1/2?)\n"
                  "3. PD biomarkers: IFN signature score as acceptable endpoint\n"
                  "4. CMC requirements for IND filing",
        )
        extra_ctx = st.text_area("Additional Context (optional)", height=80, placeholder="Any specific concerns or constraints...")
        title2 = st.text_input("Output Title", value="Pre-IND Meeting Agenda")

        if st.button("Draft Pre-IND Agenda", type="primary"):
            if not claude_ready:
                st.error("Claude API not configured.")
            else:
                with st.spinner("Drafting agenda with Claude..."):
                    result, err = run_pipeline_pre_ind_agenda(focus, extra_ctx)
                if err:
                    st.error(err)
                else:
                    st.markdown("### Pre-IND Meeting Agenda")
                    st.markdown(result)
                    if st.button("Save Output", key="save_agenda"):
                        save_ai_output("pre_ind_agenda", title2, result, "claude-sonnet-4-6")
                        st.success("Saved.")

    elif task == "Draft ODD Narrative (Prevalence/Medical Plausibility)":
        st.markdown(
            "Claude will draft the prevalence and medical plausibility narrative for the "
            "Orphan Drug Designation application for COPA syndrome."
        )
        user_notes = st.text_area(
            "Your Notes / Data Points (optional)",
            height=150,
            placeholder="E.g., References to specific papers, any new epidemiology data, notes on patient registry...",
        )
        title3 = st.text_input("Output Title", value="ODD Prevalence Narrative")

        if st.button("Draft ODD Narrative", type="primary"):
            if not claude_ready:
                st.error("Claude API not configured.")
            else:
                with st.spinner("Drafting ODD narrative with Claude..."):
                    result, err = run_pipeline_odd_narrative(user_notes or "Use published COPA syndrome literature.")
                if err:
                    st.error(err)
                else:
                    st.markdown("### ODD Prevalence & Medical Plausibility Narrative")
                    st.markdown(result)
                    if st.button("Save Output", key="save_odd"):
                        save_ai_output("odd_narrative", title3, result, "claude-sonnet-4-6")
                        st.success("Saved.")

    elif task == "General Regulatory Question":
        st.markdown("Ask any regulatory strategy question. Claude will answer with Restinguo context baked in.")
        question = st.text_area(
            "Question",
            height=100,
            placeholder="E.g., What are the requirements for a combined Phase 1/2 trial design in ultra-rare diseases?",
        )
        extra_ctx_q = st.text_area("Additional Context (optional)", height=80)
        title4 = st.text_input("Output Title", value="Regulatory Q&A")

        if st.button("Ask Claude", type="primary"):
            if not question:
                st.warning("Enter a question.")
            elif not claude_ready:
                st.error("Claude API not configured.")
            else:
                with st.spinner("Consulting Claude..."):
                    result, err = run_general_query(question, extra_ctx_q)
                if err:
                    st.error(err)
                else:
                    st.markdown("### Answer")
                    st.markdown(result)
                    if st.button("Save Output", key="save_qa"):
                        save_ai_output("regulatory_qa", title4, result, "claude-sonnet-4-6")
                        st.success("Saved.")

    st.divider()
    st.subheader("Saved AI Outputs")
    ai_outputs = get_ai_outputs()
    if not ai_outputs:
        st.info("No AI outputs saved yet.")
    else:
        for output in ai_outputs:
            with st.expander(
                f"📄 {output['title']} ({output['output_type']}) — {output['created_at'][:10]}",
                expanded=False,
            ):
                st.markdown(output["content"])
                st.caption(f"Model: {output['model_used']} | Created: {output['created_at']}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: DOCUMENT LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.header("Document Library")
    st.markdown("Store and organize regulatory documents, guidance, and supporting materials.")
    st.caption("Note: uploaded files are stored locally and will not persist in cloud deployments. Document metadata is saved in Supabase.")

    st.subheader("Add Document")
    with st.form("add_doc_form"):
        doc_title = st.text_input("Title", placeholder="FDA Orphan Drug Designation Guidance 2023")
        doc_type = st.selectbox(
            "Type",
            [
                "FDA Guidance",
                "Regulatory Precedent",
                "Nonclinical Data",
                "CMC",
                "Clinical Protocol",
                "Meeting Background Package",
                "Correspondence",
                "Internal Memo",
                "Other",
            ],
        )
        doc_description = st.text_area("Description", height=80)
        doc_tags = st.text_input("Tags (comma-separated)", placeholder="ODD, orphan, rare disease")
        uploaded_file = st.file_uploader("Upload File (optional)", type=["pdf", "docx", "txt", "xlsx"])
        add_doc_submitted = st.form_submit_button("Add Document")

        if add_doc_submitted and doc_title:
            filename = None
            if uploaded_file:
                try:
                    docs_dir = Path("data/documents")
                    docs_dir.mkdir(parents=True, exist_ok=True)
                    safe_name = uploaded_file.name.replace(" ", "_")
                    filepath = docs_dir / safe_name
                    with open(filepath, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    filename = safe_name
                except Exception as e:
                    st.warning(f"Could not save file locally: {e}. Metadata will still be saved.")
            save_document_metadata(doc_title, doc_type, filename, doc_description or None, doc_tags or None)
            st.success(f"Document '{doc_title}' added.")
            st.rerun()

    st.divider()

    st.subheader("Documents")
    all_docs = get_all_documents()
    if not all_docs:
        st.info("No documents added yet.")
    else:
        type_filter = st.selectbox(
            "Filter by type",
            ["All"] + list({d["doc_type"] for d in all_docs if d["doc_type"]}),
        )
        filtered = all_docs if type_filter == "All" else [d for d in all_docs if d["doc_type"] == type_filter]

        for doc in filtered:
            with st.expander(f"📄 {doc['title']} — {doc['doc_type']}"):
                if doc.get("description"):
                    st.markdown(f"**Description:** {doc['description']}")
                if doc.get("tags"):
                    st.markdown(f"**Tags:** `{doc['tags']}`")
                if doc.get("filename"):
                    filepath = Path("data/documents") / doc["filename"]
                    if filepath.exists():
                        with open(filepath, "rb") as f:
                            st.download_button(
                                f"Download {doc['filename']}",
                                data=f.read(),
                                file_name=doc["filename"],
                                key=f"dl_{doc['id']}",
                            )
                    else:
                        st.caption(f"File: {doc['filename']} (not on local disk)")
                st.caption(f"Added: {doc['uploaded_at'][:10]}")
