"""
Restinguo Hub — Grant Writer
NIH SBIR/STTR Phase I · COPA Syndrome · IFNAR Blockade
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    for _k in ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_KEY",
               "DATABASE_URL", "OLLAMA_URL", "OLLAMA_MODEL"]:
        if _k in st.secrets and _k not in os.environ:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

from grant_writer.database import (
    init_db, create_grant, list_grants, get_grant, update_grant, delete_grant,
    save_draft, get_latest_draft, list_drafts, list_all_drafts_for_section,
)
from grant_writer.drafter import DraftingPipeline
from grant_writer.opportunities import refresh_opportunities, get_opportunities, RELEVANT_FOAS
from grant_writer.prompts import SECTION_LABELS

init_db()

st.set_page_config(
    page_title="Restinguo Hub · Grant Writer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 Grant Writer")
    st.markdown("**NIH SBIR/STTR Phase I**")
    st.markdown("COPA syndrome · IFNAR blockade")
    st.divider()

    grants = list_grants()
    grant_options = {g["name"]: g["id"] for g in grants}

    st.markdown("### Active Grant")
    if grants:
        selected_name = st.selectbox(
            "Select grant",
            options=list(grant_options.keys()),
            label_visibility="collapsed",
        )
        active_grant_id = grant_options[selected_name]
        active_grant = get_grant(active_grant_id)
    else:
        st.info("No grants yet. Create one in Dashboard.")
        active_grant_id = None
        active_grant = None

    st.divider()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    st.markdown("### Status")
    if api_key and api_key != "your_key_here":
        st.success("Claude API ✓")
    else:
        st.error("Claude API key missing")

    if "mistral_status" not in st.session_state:
        try:
            from grant_writer.drafter import MistralClient
            st.session_state.mistral_status = MistralClient().is_available()
        except Exception:
            st.session_state.mistral_status = False

    if st.session_state.mistral_status:
        st.success("Ollama/Mistral ✓")
    else:
        st.warning("Ollama offline (Claude-only mode)")

    if st.button("Recheck Ollama"):
        try:
            from grant_writer.drafter import MistralClient
            st.session_state.mistral_status = MistralClient().is_available()
        except Exception:
            st.session_state.mistral_status = False
        st.rerun()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_dash, tab_draft, tab_history, tab_opps = st.tabs([
    "Dashboard", "Draft Sections", "History", "Opportunities"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ══════════════════════════════════════════════════════════════════
with tab_dash:
    st.header("Dashboard")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Create New Grant")
        with st.form("new_grant"):
            g_name = st.text_input("Grant name", placeholder="SBIR Phase I — COPA IFNAR Validation")
            g_foa = st.text_input("FOA number", value="PA-24-185")
            g_notes = st.text_area("Notes", placeholder="Target IC: NIAMS or NIAID\nSubmission date: ...", height=80)
            if st.form_submit_button("Create Grant", type="primary"):
                if g_name.strip():
                    create_grant(g_name.strip(), g_foa.strip(), g_notes.strip())
                    st.success(f"Created grant: {g_name}")
                    st.rerun()
                else:
                    st.error("Grant name required.")

    with col2:
        st.subheader("Active Grant Details")
        if active_grant:
            with st.form("edit_grant"):
                e_name = st.text_input("Name", value=active_grant["name"])
                e_foa = st.text_input("FOA", value=active_grant.get("foa", ""))
                e_notes = st.text_area("Notes", value=active_grant.get("notes", ""), height=80)
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("Save"):
                        update_grant(active_grant_id, e_name, e_foa, e_notes)
                        st.success("Saved.")
                        st.rerun()
                with c2:
                    if st.form_submit_button("Delete", type="secondary"):
                        delete_grant(active_grant_id)
                        st.warning("Grant deleted.")
                        st.rerun()
        else:
            st.info("No active grant selected.")

    st.divider()
    st.subheader("All Grants")
    if grants:
        for g in grants:
            drafts = list_drafts(g["id"])
            sections_done = len({d["section"] for d in drafts})
            st.markdown(
                f"**{g['name']}** · FOA: `{g.get('foa','—')}` · "
                f"{sections_done}/5 sections drafted · "
                f"Updated: {g['updated_at'][:10]}"
            )
    else:
        st.info("No grants yet.")

    st.divider()
    st.subheader("Key FOAs for Restinguo")
    for foa in RELEVANT_FOAS:
        with st.expander(f"{foa['number']} — {foa['title']}"):
            st.markdown(foa["synopsis"])
            if foa.get("close_date"):
                st.markdown(f"**Close date:** {foa['close_date']}")
            if foa.get("url"):
                st.markdown(f"[View FOA]({foa['url']})")


# ══════════════════════════════════════════════════════════════════
# TAB 2: DRAFT SECTIONS
# ══════════════════════════════════════════════════════════════════
with tab_draft:
    st.header("Draft Sections")

    if not active_grant:
        st.warning("Create and select a grant first (Dashboard tab).")
        st.stop()

    st.markdown(f"**Grant:** {active_grant['name']} · FOA: `{active_grant.get('foa', '—')}`")

    section_key = st.selectbox(
        "Section to draft",
        options=list(SECTION_LABELS.keys()),
        format_func=lambda k: SECTION_LABELS[k],
    )

    existing = get_latest_draft(active_grant_id, section_key)
    if existing:
        st.info(f"Latest draft: version {existing['version']} · {existing['created_at'][:16]}")

    with st.expander("Source documents / background (optional)", expanded=False):
        source_docs = st.text_area(
            "Paste any papers, notes, or data you want Mistral to preprocess",
            height=150,
            placeholder="Paste abstracts, key findings, or notes here...",
            key="source_docs",
        )

    additional_notes = st.text_area(
        "Additional notes / instructions for this section",
        height=80,
        placeholder="e.g., 'Emphasize COPA lung disease data', 'Aim 1 should focus on patient iPSC model'",
        key="additional_notes",
    )

    skip_mistral = not st.session_state.get("mistral_status", False)
    if not skip_mistral:
        skip_mistral = st.checkbox("Skip Mistral preprocessing (use Claude directly)", value=False)

    col_draft, col_save = st.columns([2, 1])
    draft_clicked = col_draft.button("Draft with Claude", type="primary", use_container_width=True)

    if draft_clicked:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key == "your_key_here":
            st.error("Set ANTHROPIC_API_KEY in .streamlit/secrets.toml first.")
        else:
            pipeline = DraftingPipeline()
            section_label = SECTION_LABELS[section_key]

            st.markdown(f"### {section_label}")

            if not skip_mistral and st.session_state.get("mistral_status"):
                with st.status("Step 1: Mistral preprocessing...", expanded=False) as mistral_status:
                    preprocessed = pipeline.preprocess(section_key, source_docs or "", additional_notes or "")
                    st.code(preprocessed[:800] + ("..." if len(preprocessed) > 800 else ""), language=None)
                    mistral_status.update(label="Mistral preprocessing complete", state="complete")
                st.session_state["last_preprocessed"] = preprocessed
            else:
                st.session_state["last_preprocessed"] = None

            with st.status("Step 2: Claude drafting final section...", expanded=True):
                output_container = st.empty()
                full_text = ""
                for chunk in pipeline.draft(
                    section=section_key,
                    source_docs=source_docs or "",
                    additional_notes=additional_notes or "",
                    skip_mistral=skip_mistral,
                ):
                    full_text += chunk
                    output_container.markdown(full_text + "▌")
                output_container.markdown(full_text)

            st.session_state["last_draft_text"] = full_text
            st.session_state["last_draft_section"] = section_key
            st.success("Draft complete.")

    if st.session_state.get("last_draft_text") and st.session_state.get("last_draft_section") == section_key:
        st.divider()
        st.markdown("**Editable draft** — make changes before saving:")
        edited = st.text_area(
            "Edit draft",
            value=st.session_state["last_draft_text"],
            height=400,
            key="editable_draft",
            label_visibility="collapsed",
        )

        if st.button("Save Draft to Database", type="primary"):
            save_draft(
                grant_id=active_grant_id,
                section=section_key,
                content=edited,
                model="claude-sonnet-4-6",
                additional_notes=additional_notes or "",
            )
            st.success(f"Saved {SECTION_LABELS[section_key]} draft.")
            st.session_state.pop("last_draft_text", None)
            st.rerun()

    if existing and not st.session_state.get("last_draft_text"):
        st.divider()
        st.markdown(f"#### Current Draft (v{existing['version']})")
        st.markdown(existing["content"])


# ══════════════════════════════════════════════════════════════════
# TAB 3: HISTORY
# ══════════════════════════════════════════════════════════════════
with tab_history:
    st.header("Draft History")

    if not active_grant:
        st.warning("Select a grant to view history.")
        st.stop()

    st.markdown(f"**Grant:** {active_grant['name']}")

    all_drafts = list_drafts(active_grant_id)
    if not all_drafts:
        st.info("No drafts saved yet.")
    else:
        by_section: dict[str, list] = {}
        for d in all_drafts:
            by_section.setdefault(d["section"], []).append(d)

        for section_k, drafts in by_section.items():
            label = SECTION_LABELS.get(section_k, section_k)
            st.subheader(label)

            version_opts = {f"v{d['version']} — {d['created_at'][:16]}": d for d in drafts}
            selected_ver = st.selectbox(
                "Version",
                options=list(version_opts.keys()),
                key=f"ver_{section_k}",
            )
            selected_draft = version_opts[selected_ver]

            if selected_draft.get("additional_notes"):
                st.caption(f"Notes: {selected_draft['additional_notes']}")

            with st.expander("View draft text", expanded=False):
                st.markdown(selected_draft["content"])
                st.download_button(
                    label="Download as .txt",
                    data=selected_draft["content"],
                    file_name=f"{section_k}_v{selected_draft['version']}.txt",
                    mime="text/plain",
                    key=f"dl_{section_k}_{selected_draft['version']}",
                )

        st.divider()
        st.subheader("Export Full Grant Package")
        sections_order = ["specific_aims", "significance", "innovation", "approach", "facilities"]
        export_parts = [f"# {active_grant['name']}\nFOA: {active_grant.get('foa','')}\n\n"]
        for sk in sections_order:
            latest = get_latest_draft(active_grant_id, sk)
            if latest:
                export_parts.append(f"## {SECTION_LABELS[sk]}\n\n{latest['content']}\n\n")
            else:
                export_parts.append(f"## {SECTION_LABELS[sk]}\n\n[Not yet drafted]\n\n")

        full_export = "".join(export_parts)
        st.download_button(
            label="Download Full Grant (.txt)",
            data=full_export,
            file_name=f"{active_grant['name'].replace(' ', '_')}_grant.txt",
            mime="text/plain",
        )


# ══════════════════════════════════════════════════════════════════
# TAB 4: OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════
with tab_opps:
    st.header("NIH Opportunities Tracker")

    col_refresh, col_info = st.columns([1, 3])
    with col_refresh:
        if st.button("Refresh from NIH", type="primary"):
            with st.spinner("Fetching from NIH Guide RSS and REPORTER..."):
                count, msg = refresh_opportunities()
            st.success(msg)

    with col_info:
        st.caption("Pulls from NIH Guide RSS (R43 activity code) and NIH REPORTER API. Results cached in Supabase.")

    st.divider()

    st.subheader("Recommended FOAs for Restinguo")
    for foa in RELEVANT_FOAS:
        with st.expander(f"{foa['number']} — {foa['title']}", expanded=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(foa["synopsis"])
                if foa.get("url"):
                    st.markdown(f"[View FOA]({foa['url']})")
            with cols[1]:
                if foa.get("close_date"):
                    st.metric("Close Date", foa["close_date"])
                if foa.get("posted_date"):
                    st.caption(f"Posted: {foa['posted_date']}")

    st.divider()
    st.subheader("Live Fetched Opportunities")
    opps = get_opportunities(50)
    if not opps:
        st.info("No fetched opportunities yet. Click 'Refresh from NIH' above.")
    else:
        for opp in opps:
            with st.expander(f"{opp.get('number', '—')} · {opp['title'][:80]}"):
                st.markdown(opp.get("synopsis", "") or "_No synopsis available._")
                meta_cols = st.columns(3)
                meta_cols[0].caption(f"Source: {opp.get('source','—')}")
                meta_cols[1].caption(f"Posted: {opp.get('posted_date','—')}")
                meta_cols[2].caption(f"Close: {opp.get('close_date','—')}")
                if opp.get("url"):
                    st.markdown(f"[Open link]({opp['url']})")
