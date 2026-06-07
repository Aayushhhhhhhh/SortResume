"""Home / landing page."""
import streamlit as st

def render():
    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding: 48px 0 32px;">
        <div style="font-family:'DM Mono',monospace; font-size:11px;
                    letter-spacing:0.2em; color:rgba(0,229,255,0.7);
                    text-transform:uppercase; margin-bottom:16px;">
            Global B2B Resume Intelligence
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;
                    font-size:clamp(48px,7vw,88px); line-height:0.92;
                    letter-spacing:0.02em; margin-bottom:24px;">
            STOP EVALUATING<br>
            <span style="color:#00e5ff;">WHO HAS THE BEST</span><br>
            CHATGPT SKILLS
        </div>
        <div style="font-size:17px; color:rgba(255,255,255,0.6);
                    max-width:560px; line-height:1.6; margin-bottom:40px;">
            SortResume finds real candidates in a world of AI-generated noise.
            The only resume scoring tool that detects ChatGPT padding —
            not just keyword overlap.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STAT ROW ─────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Signals Used", "4", help="Semantic · Keyword · Substance · AI Noise")
    with col2:
        st.metric("AI Noise", "Detected", help="Only tool that catches ChatGPT resumes")
    with col3:
        st.metric("Bulk Upload", "100 PDFs", help="Score 100 resumes at once")
    with col4:
        st.metric("Competitors", "0", help="Nobody else detects AI noise in resumes")

    st.divider()

    # ── HOW IT WORKS ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif; font-size:2rem;
                letter-spacing:0.04em; margin-bottom:24px;">
        HOW IT WORKS
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    steps = [
        ("01", "Upload Resumes", "Drag and drop up to 100 PDF resumes at once. We handle multi-column, tables, and complex layouts."),
        ("02", "Paste Job Description", "Paste any JD from any job board — LinkedIn, Indeed, Naukri, your own ATS. We parse required vs preferred skills automatically."),
        ("03", "Get Ranked Results", "Every candidate ranked Top / Review / Skip with a full breakdown of why — semantic fit, keyword gaps, substance quality, and AI noise level."),
    ]
    for col, (num, title, desc) in zip([c1, c2, c3], steps):
        with col:
            st.markdown(f"""
            <div style="background:#13131f; border:1px solid rgba(255,255,255,0.06);
                        border-radius:12px; padding:24px; height:200px;">
                <div style="font-family:'Bebas Neue',sans-serif; font-size:2.5rem;
                            color:rgba(0,229,255,0.3); line-height:1;">{num}</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:1.2rem;
                            letter-spacing:0.04em; margin:8px 0;">{title}</div>
                <div style="font-size:13px; color:rgba(255,255,255,0.5);
                            line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── 4 SIGNALS ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif; font-size:2rem;
                letter-spacing:0.04em; margin-bottom:24px;">
        THE 4-SIGNAL SCORING ENGINE
    </div>
    """, unsafe_allow_html=True)

    signals = [
        ("🧠", "Semantic Match", "35%", "#00e5ff",
         "Understands meaning — 'ML Engineer' matches 'Machine Learning Developer'. "
         "Uses BAAI/bge-large-en-v1.5, the most accurate open-source embedding model."),
        ("🔑", "Keyword Match", "25%", "#7fff6b",
         "Section-aware TF-IDF. Skills in Experience section score higher than Skills list. "
         "Required JD keywords penalise harder when missing."),
        ("💪", "Substance Score", "25%", "#ffd166",
         "Measures if keywords are PROVEN with outcomes and metrics. "
         "'Built Python pipeline reducing costs by 40%' scores 4x over just 'Python'."),
        ("🤖", "AI Noise Detector", "15%", "#ff6b9d",
         "The feature nobody else has. Detects ChatGPT-generated resume padding "
         "using phrase analysis, sentence uniformity, and vocabulary diversity."),
    ]

    for emoji, name, weight, color, desc in signals:
        st.markdown(f"""
        <div style="background:#13131f; border:1px solid rgba(255,255,255,0.06);
                    border-left:3px solid {color}; border-radius:8px;
                    padding:16px 20px; margin-bottom:10px;
                    display:flex; gap:16px; align-items:flex-start;">
            <div style="font-size:1.5rem; flex-shrink:0;">{emoji}</div>
            <div style="flex:1;">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
                    <span style="font-family:'Bebas Neue',sans-serif; font-size:1.1rem;
                                 letter-spacing:0.04em;">{name}</span>
                    <span style="font-family:'DM Mono',monospace; font-size:10px;
                                 color:{color}; background:rgba(255,255,255,0.05);
                                 padding:2px 8px; border-radius:4px;">{weight}</span>
                </div>
                <div style="font-size:13px; color:rgba(255,255,255,0.5); line-height:1.5;">
                    {desc}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── CTA ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:32px 0;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2.5rem;
                    letter-spacing:0.04em; margin-bottom:8px;">
            READY TO FIND REAL TALENT?
        </div>
        <div style="font-size:14px; color:rgba(255,255,255,0.4);
                    font-family:'DM Mono',monospace; margin-bottom:24px;">
            Use the sidebar to go to Score Resumes →
        </div>
    </div>
    """, unsafe_allow_html=True)
