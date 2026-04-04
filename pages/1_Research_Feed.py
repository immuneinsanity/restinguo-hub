"""
Restinguo Hub — Research Feed
The research agent runs as a local CLI tool and publishes briefings as markdown files.
This page provides an overview and launch instructions.
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
    page_title="Restinguo Hub · Research Feed",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("## 🔬 Research Feed")
    st.markdown("*Anifrolumab · COPA Syndrome*")
    st.divider()
    st.caption("Research agent: CLI-only")

st.markdown("## 🔬 Research Feed")
st.markdown("*Anifrolumab · COPA Syndrome · IFNAR Blockade*")

st.info(
    "The research agent is a **CLI-only tool** that runs on a local schedule. "
    "It pulls papers from PubMed/arXiv, scores them, and saves daily briefings as markdown files. "
    "In cloud mode, live briefings are not available here."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("What the Research Agent Does")
    st.markdown("""
- Fetches papers from **PubMed** and **bioRxiv** daily at 07:00
- Keywords: anifrolumab, COPA syndrome, IFNAR, type I interferon, STING, interferonopathy
- Scores papers as `HIGH / MEDIUM / LOW` priority
- Generates a markdown briefing saved to `research-agent/data/briefings/`
- Tracks papers in a local SQLite database (`research-agent/data/research.db`)
    """)

with col2:
    st.subheader("How to Run Locally")
    st.code("""# From the workspace root:
cd research-agent
python main.py

# Or via cron (scheduled daily at 07:00):
# Managed via Claude Code cron jobs""", language="bash")

st.divider()

st.subheader("Latest Agent Board Metrics")
st.markdown(
    "Connect the research agent's local DB to view live metrics. "
    "The Agent Board (home page) will show research stats when running locally."
)

st.markdown("""
| Metric | Source | Availability |
|--------|--------|-------------|
| Papers today | research.db (local) | Local only |
| High-priority papers | research.db (local) | Local only |
| Latest briefing | briefings/*.md (local) | Local only |
| Grant drafts | Supabase | ✅ Cloud |
| Regulatory pathways | Supabase | ✅ Cloud |
""")

st.divider()

st.subheader("Key Research Topics")
topics = [
    ("Anifrolumab", "Anti-IFNAR1 mAb approved for SLE — primary regulatory analog for COPA program"),
    ("COPA Syndrome", "Autosomal dominant interferonopathy caused by COPA gene mutations"),
    ("IFNAR Blockade", "Type I IFN receptor blockade — Restinguo's therapeutic approach"),
    ("STING Pathway", "Constitutive STING activation drives IFN signaling in COPA syndrome"),
    ("JAK Inhibitors", "Current off-label standard of care — baricitinib, ruxolitinib"),
    ("Interferonopathies", "Broader class of diseases with constitutive type I IFN signaling"),
]
for topic, desc in topics:
    with st.expander(f"**{topic}**"):
        st.write(desc)
