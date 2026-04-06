"""
Investor Tracker — CRM-style pipeline for Restinguo fundraising.
"""
import streamlit as st
from datetime import date
from fundraising import database as db

st.set_page_config(page_title="Investor Tracker · Restinguo", page_icon="💰", layout="wide")
st.title("💰 Investor Tracker")
st.caption("Fundraising pipeline for Restinguo")

STATUSES = ['Not Contacted', 'Researching', 'Reached Out', 'Meeting Scheduled',
            'In Diligence', 'Term Sheet', 'Pass', 'Invested']

STATUS_COLORS = {
    'Not Contacted': '⚪',
    'Researching': '🔵',
    'Reached Out': '🟡',
    'Meeting Scheduled': '🟠',
    'In Diligence': '🟣',
    'Term Sheet': '🟢',
    'Pass': '🔴',
    'Invested': '✅',
}

try:
    investors = db.get_all_investors()
    metrics = db.get_pipeline_metrics()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

# ── Metrics ────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total in Pipeline", len(investors))
col2.metric("Reached Out", metrics.get("Reached Out", 0))
col3.metric("Meetings Scheduled", metrics.get("Meeting Scheduled", 0))
col4.metric("In Diligence", metrics.get("In Diligence", 0))
col5.metric("Term Sheets", metrics.get("Term Sheet", 0))

st.divider()

# ── Pipeline view ──────────────────────────────────────────────────────────
filter_col1, filter_col2 = st.columns([2, 4])
with filter_col1:
    status_filter = st.selectbox("Filter by status", ["All"] + STATUSES)

filtered = investors if status_filter == "All" else [i for i in investors if i.get("status") == status_filter]

# Group by status
if status_filter == "All":
    for status in STATUSES:
        group = [i for i in investors if i.get("status") == status]
        if not group:
            continue
        st.subheader(f"{STATUS_COLORS.get(status, '•')} {status} ({len(group)})")
        for inv in group:
            _render_investor_card(inv)
else:
    for inv in filtered:
        _render_investor_card(inv)


def _render_investor_card(inv):
    with st.expander(f"**{inv['firm']}**" + (f" — {inv['name']}" if inv.get('name') else "")):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Focus:** {inv.get('fund_focus', '—')}")
            st.markdown(f"**Stage:** {inv.get('stage_focus', '—')}")
        with col2:
            st.markdown(f"**Check size:** {inv.get('typical_check_size', '—')}")
            st.markdown(f"**Priority:** {'⭐' * (4 - inv.get('priority', 3))}")
        with col3:
            new_status = st.selectbox("Status", STATUSES,
                                      index=STATUSES.index(inv.get("status", "Not Contacted")),
                                      key=f"status_{inv['id']}")
            if new_status != inv.get("status"):
                db.update_investor(inv["id"], {"status": new_status})
                st.rerun()

        if inv.get("notes"):
            st.info(inv["notes"])
        if inv.get("contact_name"):
            st.markdown(f"**Contact:** {inv['contact_name']}" +
                       (f" · {inv['contact_email']}" if inv.get('contact_email') else ""))

        # Interactions
        interactions = db.get_interactions(inv["id"])
        if interactions:
            st.markdown("**Interactions:**")
            for ix in interactions:
                st.markdown(f"- `{ix['date']}` **{ix['type']}** — {ix.get('notes', '')}" +
                           (f" → *Next: {ix['next_action']}*" if ix.get('next_action') else ""))

        # Log interaction
        with st.form(f"log_{inv['id']}"):
            st.markdown("**Log interaction:**")
            c1, c2 = st.columns(2)
            ix_date = c1.date_input("Date", value=date.today(), key=f"date_{inv['id']}")
            ix_type = c2.selectbox("Type", ["Email", "Call", "Meeting", "Intro", "Note", "Other"],
                                   key=f"type_{inv['id']}")
            ix_notes = st.text_area("Notes", key=f"notes_{inv['id']}", height=60)
            ix_next = st.text_input("Next action", key=f"next_{inv['id']}")
            ix_next_date = st.date_input("Next action date", value=None, key=f"nextdate_{inv['id']}")
            if st.form_submit_button("Log"):
                db.save_interaction({
                    "investor_id": inv["id"],
                    "date": str(ix_date),
                    "type": ix_type,
                    "notes": ix_notes,
                    "next_action": ix_next,
                    "next_action_date": str(ix_next_date) if ix_next_date else None,
                })
                st.success("Logged!")
                st.rerun()

st.divider()

# ── Add investor ───────────────────────────────────────────────────────────
with st.expander("➕ Add New Investor"):
    with st.form("add_investor"):
        c1, c2 = st.columns(2)
        firm = c1.text_input("Firm *")
        name = c2.text_input("Contact name")
        focus = c1.text_input("Fund focus")
        stage = c2.text_input("Stage focus")
        check = c1.text_input("Typical check size")
        status = c2.selectbox("Status", STATUSES)
        priority = st.slider("Priority (1=highest)", 1, 5, 3)
        notes = st.text_area("Notes")
        if st.form_submit_button("Add Investor"):
            if firm:
                db.save_investor({
                    "firm": firm, "name": name, "fund_focus": focus,
                    "stage_focus": stage, "typical_check_size": check,
                    "status": status, "priority": priority, "notes": notes,
                })
                st.success(f"Added {firm}!")
                st.rerun()
            else:
                st.warning("Firm name required.")
