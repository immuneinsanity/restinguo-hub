"""
Funding Landscape — recent deals, comparables, and strategy for Restinguo.
"""
import streamlit as st
from fundraising import database as db

st.set_page_config(page_title="Funding Landscape · Restinguo", page_icon="📊", layout="wide")
st.title("📊 Funding Landscape")
st.caption("Rare disease biotech funding intelligence")

try:
    events = db.get_funding_events()
    comps = db.get_comparables()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Recent Deals", "Comparable Companies", "Funding Strategy"])

# ── Recent Deals ───────────────────────────────────────────────────────────
with tab1:
    st.subheader("Recent Funding Events — Rare Disease / IFN Pathway")
    if events:
        for ev in events:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
                c1.markdown(f"**{ev['company']}**")
                c2.markdown(f"💰 {ev.get('amount', '—')}")
                c3.markdown(f"📅 {ev.get('date', '—')[:7] if ev.get('date') else '—'}")
                c4.markdown(f"🏷️ {ev.get('disease_area', '—')}")
                if ev.get('notes'):
                    st.caption(ev['notes'])
                st.divider()
    else:
        st.info("No funding events yet.")

    with st.expander("➕ Add Funding Event"):
        with st.form("add_event"):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company *")
            amount = c2.text_input("Amount (e.g. $15M)")
            stage = c1.text_input("Round (Seed, Series A, etc.)")
            ev_date = c2.date_input("Date")
            investors = c1.text_input("Investors")
            disease = c2.text_input("Disease area")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add"):
                if company:
                    db.save_funding_event({
                        "company": company, "amount": amount, "stage": stage,
                        "date": str(ev_date), "investors": investors,
                        "disease_area": disease, "notes": notes,
                    })
                    st.success("Added!")
                    st.rerun()

# ── Comparables ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Comparable Companies — Similar Stage & Profile")
    st.caption("Companies that raised at similar stages: rare disease, early mechanism validation, pre-IND")
    if comps:
        for c in comps:
            with st.expander(f"**{c['company']}** — {c.get('raised_amount', '?')} ({c.get('year', '?')})"):
                st.markdown(c.get('description', ''))
                col1, col2 = st.columns(2)
                col1.markdown(f"**Stage at raise:** {c.get('stage_at_raise', '—')}")
                col2.markdown(f"**Amount:** {c.get('raised_amount', '—')}")
                if c.get('notes'):
                    st.info(c['notes'])
    else:
        st.info("No comparables yet.")

    with st.expander("➕ Add Comparable"):
        with st.form("add_comp"):
            c1, c2 = st.columns(2)
            comp_company = c1.text_input("Company *")
            comp_amount = c2.text_input("Amount raised")
            comp_stage = c1.text_input("Stage at raise")
            comp_year = c2.number_input("Year", min_value=2010, max_value=2030, value=2023)
            comp_desc = st.text_area("Description")
            comp_notes = st.text_area("Notes / relevance to Restinguo")
            if st.form_submit_button("Add"):
                if comp_company:
                    db.save_comparable({
                        "company": comp_company, "raised_amount": comp_amount,
                        "stage_at_raise": comp_stage, "year": int(comp_year),
                        "description": comp_desc, "notes": comp_notes,
                    })
                    st.success("Added!")
                    st.rerun()

# ── Funding Strategy ───────────────────────────────────────────────────────
with tab3:
    st.subheader("Funding Strategy for Restinguo")
    st.markdown("""
### Where Restinguo Sits Today
- **Stage:** Target validation (pre-IND, pre-lead compound)
- **Data:** No published efficacy data yet; COPA syndrome mechanism well-characterized in literature
- **Narrative:** Ultra-rare disease (ODD qualifies), validated target (anifrolumab precedent), large unmet need

---

### Recommended Funding Path

#### Phase 1: Non-dilutive First (Now → 12 months)
**NIH SBIR Phase I (R43)** — $300K, 6 months
- Apply to NIAMS study section
- Specific Aims: validate IFNAR blockade in COPA patient PBMCs (Experiment 1 already designed)
- Strengthens IP position and investor story
- **Timeline:** Apply by April 2025 deadline (next: September 2025)

**Rare Pediatric Disease designation** — free, apply now via FDA
- COPA affects children → qualifies
- Grants Priority Review Voucher (PRV) worth $100-150M at approval
- This alone dramatically changes investor calculus

#### Phase 2: Angel / Seed (12-18 months)
- Target: $1-3M seed
- Milestone: PBMC proof-of-concept data in hand
- Use to: fund iPSC disease model + establish UCSF collaboration formally
- Investor profile: rare disease angels, family offices, patient advocacy-connected capital

#### Phase 3: Series A (24-36 months)  
- Target: $15-30M
- Milestone: iPSC efficacy data, ODD granted, pre-IND meeting completed
- Investor profile: RA Capital, Atlas, Vida, Third Rock (see Investor Tracker)

---

### SBIR vs VC: Key Considerations

| | SBIR Phase I | Angel/Seed | Series A VC |
|---|---|---|---|
| **Amount** | ~$300K | $500K-3M | $15-50M |
| **Dilution** | None | 15-25% | 20-30% |
| **Timeline to close** | 6-9 months | 3-6 months | 6-12 months |
| **Best for** | Generating data | Bridge to Series A | Full program build |
| **Restinguo timing** | Now | After PBMC data | After iPSC data |

---

### The Investor Pitch — Core Narrative
1. **Unmet need:** COPA syndrome — kids dying of lung disease, no approved therapy
2. **Validated target:** Anifrolumab approved for lupus (same IFNAR target) — de-risks MOA
3. **Regulatory tailwind:** ODD, RPDD (PRV), potential Fast Track
4. **Clear path:** PBMC POC → iPSC model → IND → Phase 1 (small N, rare disease)
5. **Defensible:** COPA-specific IP around IFNAR blockade in this disease
    """)
