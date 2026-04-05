"""
One-time setup page — enter credentials directly in the app.
Stores them in Streamlit session state for the current session.
For permanent storage, add them to Streamlit Cloud secrets.
"""
import streamlit as st

st.set_page_config(page_title="Setup — Restinguo Hub", page_icon="🧬")
st.title("🔧 Setup")
st.markdown("Enter your API credentials below. These will be saved to your browser session.")

with st.form("credentials"):
    supabase_url = st.text_input("Supabase URL", value=st.session_state.get("SUPABASE_URL", ""))
    supabase_key = st.text_input("Supabase Key", value=st.session_state.get("SUPABASE_KEY", ""), type="password")
    anthropic_key = st.text_input("Anthropic API Key", value=st.session_state.get("ANTHROPIC_API_KEY", ""), type="password")
    submitted = st.form_submit_button("Save")

if submitted:
    st.session_state["SUPABASE_URL"] = supabase_url
    st.session_state["SUPABASE_KEY"] = supabase_key
    st.session_state["ANTHROPIC_API_KEY"] = anthropic_key
    st.success("Credentials saved for this session!")

st.divider()
st.markdown("""
**For permanent setup** (so you don't have to re-enter every session):

Add these 3 lines to Streamlit Cloud → Settings → Secrets:
```
SUPABASE_URL = "https://xkpfoxnohewhkrtlizae.supabase.co"
SUPABASE_KEY = "sb_publishable_UmkbxDC9XUiTZaJYbdW0Xg_r4mww665"
ANTHROPIC_API_KEY = "your_key_here"
```
""")
