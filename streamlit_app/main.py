"""
SortResume — Main Streamlit App
================================
Entry point for Streamlit Cloud deployment.
"""

import streamlit as st

st.set_page_config(
    page_title="SortResume — Find Real Candidates",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=Lato:wght@300;400;500;700&display=swap');

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'Lato', sans-serif !important;
    background: #0a0a0f !important;
    color: #e8edf2 !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0e0e1a !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #e8edf2 !important; }

/* ── HEADINGS ── */
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 0.04em !important; }

/* ── INPUTS ── */
.stTextArea textarea, .stTextInput input {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e8edf2 !important;
    font-family: 'Lato', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(0,229,255,0.4) !important;
    box-shadow: 0 0 0 2px rgba(0,229,255,0.1) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #00e5ff 0%, #0051ff 100%) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #13131f !important;
    border: 1px dashed rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.2rem !important;
    color: #00e5ff !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
}

/* ── DIVIDER ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── ALERTS ── */
.stSuccess { background: rgba(34,197,94,0.1) !important; border: 1px solid rgba(34,197,94,0.3) !important; border-radius: 8px !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 8px !important; }
.stError   { background: rgba(239,68,68,0.1) !important;  border: 1px solid rgba(239,68,68,0.3) !important;  border-radius: 8px !important; }
.stInfo    { background: rgba(0,229,255,0.08) !important; border: 1px solid rgba(0,229,255,0.2) !important;  border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── ROUTING ───────────────────────────────────────────────────────────────────
from streamlit_app.pages import home, scorer, about

PAGES = {
    "🏠 Home":         home,
    "💎 Score Resumes": scorer,
    "ℹ️ About":         about,
}

with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 24px;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2rem;
                    letter-spacing:0.08em; color:#00e5ff; line-height:1;">
            SORT<br>RESUME
        </div>
        <div style="font-family:'DM Mono',monospace; font-size:10px;
                    color:rgba(255,255,255,0.3); letter-spacing:0.15em;
                    margin-top:4px;">
            FIND REAL CANDIDATES
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    selection = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:10px;
                color:rgba(255,255,255,0.25); line-height:1.8;">
        4-SIGNAL SCORING<br>
        Semantic · Keyword<br>
        Substance · AI Noise<br><br>
        GLOBAL B2B SAAS<br>
        v0.1.0 — Beta
    </div>
    """, unsafe_allow_html=True)

# ── RENDER SELECTED PAGE ──────────────────────────────────────────────────────
PAGES[selection].render()
