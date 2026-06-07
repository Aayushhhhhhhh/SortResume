"""About page."""
import streamlit as st

def render():
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif; font-size:2.5rem;
                letter-spacing:0.04em; margin-bottom:4px;">ABOUT SORTRESUME</div>
    <div style="font-family:'DM Mono',monospace; font-size:11px;
                color:rgba(255,255,255,0.3); letter-spacing:0.1em;
                margin-bottom:32px;">THE ONLY TOOL THAT DETECTS AI NOISE</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    SortResume was built after analysing how recruiters actually screen resumes in 2026.
    The problem is no longer volume — it's signal collapse. Every resume looks perfect
    because AI tools make them perfect. And identical.

    The old signals are dead:
    - Clean formatting? AI does that automatically
    - Keywords matching the JD? AI handles that
    - Quantified achievements? AI makes those up
    - Strong action verbs? AI loves those

    SortResume introduces a new signal: **authenticity**.
    """)

    st.divider()

    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif; font-size:1.8rem;
                letter-spacing:0.04em; margin-bottom:16px;">THE 4-SIGNAL ENGINE</div>
    """, unsafe_allow_html=True)

    data = [
        ("Semantic Match", "35%", "BAAI/bge-large-en-v1.5 embeddings. Understands meaning not just words. Section-weighted — Experience matters more than Skills list."),
        ("Keyword Match", "25%", "TF-IDF with bigrams. Section-aware weighting. Required JD skills penalise harder when missing."),
        ("Substance Score", "25%", "Measures if keywords are proven with outcomes and metrics. Level 0 (just listed) to Level 3 (quantified outcome)."),
        ("AI Noise Detector", "15%", "Detects ChatGPT-generated resume padding. Phrase analysis + sentence uniformity + vocabulary diversity. Won't penalise non-native speakers."),
    ]

    for name, weight, desc in data:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"""
            <div style="font-family:'Bebas Neue',sans-serif; font-size:1.8rem;
                        color:#00e5ff; text-align:center;">{weight}</div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{name}** — {desc}")
        st.divider()

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:11px;
                color:rgba(255,255,255,0.3); text-align:center; margin-top:32px;">
        SORTRESUME · GLOBAL B2B SAAS · v0.1.0 BETA
    </div>
    """, unsafe_allow_html=True)
