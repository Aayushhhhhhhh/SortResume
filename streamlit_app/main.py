"""
SortResume — Main Streamlit App
Entry point for Streamlit Cloud deployment.
"""

import sys
import os
import csv
import io as sio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="SortResume — Find Real Candidates",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=Lato:wght@300;400;500;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Lato', sans-serif !important;
    background: #0a0a0f !important;
    color: #e8edf2 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }
[data-testid="stSidebar"] {
    background: #0e0e1a !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #e8edf2 !important; }
h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 0.04em !important;
}
.stTextArea textarea, .stTextInput input {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e8edf2 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00e5ff 0%, #0051ff 100%) !important;
    color: #0a0a0f !important; border: none !important;
    border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important; letter-spacing: 0.08em !important;
    padding: 0.6rem 2rem !important; width: 100% !important;
}
[data-testid="stMetric"] {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important; padding: 16px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.2rem !important; color: #00e5ff !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)


# ── ALL PAGE FUNCTIONS DEFINED FIRST ─────────────────────────────────────────

def _render_home():
    st.markdown("""
    <div style="padding:48px 0 32px;">
        <div style="font-family:'DM Mono',monospace;font-size:11px;
                    letter-spacing:0.2em;color:rgba(0,229,255,0.7);margin-bottom:16px;">
            Global B2B Resume Intelligence
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;
                    font-size:clamp(48px,7vw,88px);line-height:0.92;
                    letter-spacing:0.02em;margin-bottom:24px;">
            STOP EVALUATING<br>
            <span style="color:#00e5ff;">WHO HAS THE BEST</span><br>
            CHATGPT SKILLS
        </div>
        <div style="font-size:17px;color:rgba(255,255,255,0.6);
                    max-width:560px;line-height:1.6;margin-bottom:40px;">
            SortResume finds real candidates in a world of AI-generated noise.
            The only resume scoring tool that detects ChatGPT padding —
            not just keyword overlap.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Signals", "4")
    with c2: st.metric("AI Noise", "Detected")
    with c3: st.metric("Bulk Upload", "100 PDFs")
    with c4: st.metric("Competitors", "0")

    st.divider()

    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                letter-spacing:0.04em;margin-bottom:24px;">
        THE 4-SIGNAL ENGINE
    </div>
    """, unsafe_allow_html=True)

    for emoji, name, weight, color, desc in [
        ("🧠", "Semantic Match", "35%", "#00e5ff",
         "Understands meaning — 'ML Engineer' matches 'Machine Learning Developer'. Section-weighted scoring."),
        ("🔑", "Keyword Match", "25%", "#7fff6b",
         "Section-aware TF-IDF. Skills in Experience score higher than a Skills list."),
        ("💪", "Substance Score", "25%", "#ffd166",
         "Measures if keywords are PROVEN with outcomes. 'Built Python pipeline saving 40%' scores 4x over just listing Python."),
        ("🤖", "AI Noise Detector", "15%", "#ff6b9d",
         "The feature nobody else has. Detects ChatGPT-generated padding using phrase analysis and linguistic signals."),
    ]:
        st.markdown(f"""
        <div style="background:#13131f;border:1px solid rgba(255,255,255,0.06);
                    border-left:3px solid {color};border-radius:8px;
                    padding:16px 20px;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
                <span style="font-size:1.3rem;">{emoji}</span>
                <span style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;
                             letter-spacing:0.04em;">{name}</span>
                <span style="font-family:'DM Mono',monospace;font-size:10px;
                             color:{color};background:rgba(255,255,255,0.05);
                             padding:2px 8px;border-radius:4px;">{weight}</span>
            </div>
            <div style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.5;">
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center;padding:32px 0;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;
                    letter-spacing:0.04em;margin-bottom:8px;">
            READY TO FIND REAL TALENT?
        </div>
        <div style="font-size:14px;color:rgba(255,255,255,0.4);
                    font-family:'DM Mono',monospace;">
            Use the sidebar → Score Resumes
        </div>
    </div>
    """, unsafe_allow_html=True)


def _make_pills(items, color):
    cfg = {
        "green": ("rgba(34,197,94,0.12)",  "#86efac", "rgba(34,197,94,0.3)"),
        "red":   ("rgba(239,68,68,0.12)",  "#fca5a5", "rgba(239,68,68,0.3)"),
        "amber": ("rgba(245,158,11,0.12)", "#fcd34d", "rgba(245,158,11,0.3)"),
    }
    bg, fg, bd = cfg.get(color, cfg["red"])
    return "".join(
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'border:1px solid {bd};border-radius:20px;'
        f'padding:3px 10px;margin:3px;font-size:12px;">{item}</span>'
        for item in items
    )


def _render_scorer():
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;
                letter-spacing:0.04em;margin-bottom:4px;">SCORE RESUMES</div>
    <div style="font-family:'DM Mono',monospace;font-size:11px;
                color:rgba(255,255,255,0.3);letter-spacing:0.1em;margin-bottom:32px;">
        UPLOAD RESUMES + PASTE JD → GET RANKED RESULTS
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace;font-size:10px;
                    letter-spacing:0.15em;color:rgba(0,229,255,0.7);margin-bottom:8px;">
            STEP 1 — UPLOAD RESUMES
        </div>""", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload PDFs", type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            st.success(f"✓ {len(uploaded_files)} resume{'s' if len(uploaded_files) > 1 else ''} uploaded")

    with col_right:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace;font-size:10px;
                    letter-spacing:0.15em;color:rgba(0,229,255,0.7);margin-bottom:8px;">
            STEP 2 — PASTE JOB DESCRIPTION
        </div>""", unsafe_allow_html=True)
        jd_text = st.text_area(
            "Job description", height=200,
            placeholder="Paste the full job description here...",
            label_visibility="collapsed",
        )
        if jd_text:
            wc = len(jd_text.split())
            st.caption(f"{wc} words {'✓' if wc >= 50 else '— add more for better accuracy'}")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    can_submit = bool(uploaded_files and jd_text and len(jd_text.split()) >= 30)

    if not can_submit and (uploaded_files or jd_text):
        if not uploaded_files:
            st.info("Upload at least one PDF resume to continue.")
        else:
            st.info("Paste a job description (at least 30 words) for accurate results.")

    submit = st.button(
        "💎 SCORE ALL RESUMES",
        disabled=not can_submit,
        use_container_width=True,
    )

    if submit and can_submit:
        st.divider()
        results = []
        progress = st.progress(0, text="Scoring resumes...")

        for i, file in enumerate(uploaded_files):
            progress.progress(
                (i + 1) / len(uploaded_files),
                text=f"Scoring {file.name} ({i+1}/{len(uploaded_files)})..."
            )
            try:
                from engine.parser.pdf_parser import parse_resume
                from engine.parser.jd_parser import parse_jd
                from engine.scorer.hybrid_scorer import score_resume

                parsed_resume = parse_resume(file.read())
                parsed_jd = parse_jd(jd_text)
                result = score_resume(parsed_resume, parsed_jd)
                results.append({"filename": file.name, "success": True, "result": result})
            except Exception as e:
                results.append({"filename": file.name, "success": False, "error": str(e)})

        progress.empty()

        successful = sorted(
            [r for r in results if r["success"]],
            key=lambda x: x["result"].final_score,
            reverse=True,
        )
        failed = [r for r in results if not r["success"]]

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Scored", len(successful))
        with m2: st.metric("Top", sum(1 for r in successful if r["result"].tier == "top"))
        with m3: st.metric("Review", sum(1 for r in successful if r["result"].tier == "review"))
        with m4: st.metric("Skip", sum(1 for r in successful if r["result"].tier == "skip"))

        if failed:
            with st.expander(f"⚠️ {len(failed)} file(s) failed"):
                for f in failed:
                    st.error(f"**{f['filename']}** — {f['error']}")

        st.divider()

        tier_colors = {"top": "#22c55e", "review": "#f59e0b", "skip": "#ef4444"}
        tier_labels = {"top": "TOP", "review": "REVIEW", "skip": "SKIP"}

        for rank, r in enumerate(successful, 1):
            res = r["result"]
            sc = tier_colors.get(res.tier, "#ef4444")

            with st.expander(
                f"#{rank}  {r['filename']}  —  {res.final_score}%  {tier_labels.get(res.tier,'')}",
                expanded=(rank <= 3),
            ):
                left, right = st.columns([1, 2])

                with left:
                    st.markdown(f"""
                    <div style="background:#13131f;border:1px solid rgba(255,255,255,0.08);
                                border-radius:12px;padding:20px;text-align:center;margin-bottom:12px;">
                        <div style="font-family:'Bebas Neue',sans-serif;
                                    font-size:3.5rem;line-height:1;color:{sc};">
                            {res.final_score}%
                        </div>
                        <div style="font-family:'DM Mono',monospace;font-size:10px;
                                    color:rgba(255,255,255,0.4);letter-spacing:0.1em;margin:6px 0;">
                            ATS MATCH SCORE
                        </div>
                        <span style="background:{sc}22;color:{sc};border:1px solid {sc}44;
                                     border-radius:4px;padding:2px 10px;
                                     font-family:'DM Mono',monospace;font-size:10px;">
                            {tier_labels.get(res.tier,'')} CANDIDATE
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    for label, val, color in [
                        ("🧠 Semantic",  res.semantic_score,  "#00e5ff"),
                        ("🔑 Keyword",   res.keyword_score,   "#7fff6b"),
                        ("💪 Substance", res.substance_score, "#ffd166"),
                        ("🤖 AI Noise",  res.ai_noise_score,  "#ff6b9d"),
                    ]:
                        st.markdown(f"""
                        <div style="margin-bottom:8px;">
                            <div style="display:flex;justify-content:space-between;
                                        font-size:12px;color:rgba(255,255,255,0.6);">
                                <span>{label}</span>
                                <span style="color:{color};font-family:'DM Mono',monospace;">
                                    {val}%
                                </span>
                            </div>
                            <div style="background:rgba(255,255,255,0.06);border-radius:4px;
                                        height:5px;margin-top:3px;">
                                <div style="width:{val}%;height:5px;border-radius:4px;
                                            background:{color};"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                with right:
                    if res.explanation:
                        st.markdown(f"""
                        <div style="background:#13131f;border:1px solid rgba(255,255,255,0.06);
                                    border-radius:8px;padding:16px;font-size:13px;
                                    color:rgba(255,255,255,0.7);line-height:1.6;margin-bottom:12px;">
                            {res.explanation}
                        </div>
                        """, unsafe_allow_html=True)

                    if res.is_likely_ai_generated:
                        st.warning("⚠️ **Likely AI-generated** — Verify this candidate's actual experience.")

                    if res.matched_keywords:
                        st.markdown("**✅ Matched**")
                        st.markdown(
                            f'<div style="margin:4px 0 12px">{_make_pills(res.matched_keywords[:10], "green")}</div>',
                            unsafe_allow_html=True
                        )

                    if res.missing_required:
                        st.markdown("**❌ Missing Required**")
                        st.markdown(
                            f'<div style="margin:4px 0 12px">{_make_pills(res.missing_required[:8], "red")}</div>',
                            unsafe_allow_html=True
                        )

                    if res.top_missing_keywords:
                        st.markdown("**🔍 Top Missing Keywords**")
                        st.markdown(
                            f'<div style="margin:4px 0 12px">{_make_pills(res.top_missing_keywords[:8], "amber")}</div>',
                            unsafe_allow_html=True
                        )

                    if res.ai_phrases_found:
                        with st.expander("🤖 AI Phrases Detected"):
                            for phrase in res.ai_phrases_found[:5]:
                                st.markdown(f"""
                                <div style="background:#13131f;border-left:3px solid #ff6b9d;
                                            padding:8px 12px;margin-bottom:6px;font-size:12px;
                                            border-radius:0 4px 4px 0;
                                            color:rgba(255,255,255,0.6);
                                            font-family:'DM Mono',monospace;">
                                    "{phrase}"
                                </div>
                                """, unsafe_allow_html=True)

        if successful:
            st.divider()
            out = sio.StringIO()
            w = csv.writer(out)
            w.writerow(["Rank", "File", "Score", "Tier", "Semantic",
                        "Keyword", "Substance", "AI Noise",
                        "Missing Required", "AI Generated"])
            for rank, r in enumerate(successful, 1):
                res = r["result"]
                w.writerow([
                    rank, r["filename"], res.final_score, res.tier_label,
                    res.semantic_score, res.keyword_score,
                    res.substance_score, res.ai_noise_score,
                    " | ".join(res.missing_required[:5]),
                    "Yes" if res.is_likely_ai_generated else "No",
                ])
            st.download_button(
                "⬇️ DOWNLOAD CSV REPORT",
                out.getvalue(),
                "sortresume_results.csv",
                "text/csv",
                use_container_width=True,
            )


def _render_about():
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;
                letter-spacing:0.04em;margin-bottom:4px;">ABOUT SORTRESUME</div>
    <div style="font-family:'DM Mono',monospace;font-size:11px;
                color:rgba(255,255,255,0.3);letter-spacing:0.1em;margin-bottom:32px;">
        THE ONLY TOOL THAT DETECTS AI RESUME NOISE
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    SortResume was built after analysing how recruiters actually screen resumes in 2026.
    The problem is no longer volume — it's **signal collapse**.

    Every resume looks perfect because AI tools make them perfect. And identical.

    **The old signals are dead:**
    - Clean formatting? AI does that automatically
    - Keywords matching the JD? AI handles that
    - Quantified achievements? AI makes those up
    - Strong action verbs? AI loves those

    SortResume introduces a new signal: **authenticity.**
    """)

    st.divider()

    for name, weight, desc in [
        ("Semantic Match", "35%",
         "BAAI/bge-large-en-v1.5 embeddings. Understands meaning, not just words. Section-weighted — Experience matters more than a Skills list."),
        ("Keyword Match", "25%",
         "TF-IDF with bigrams. Section-aware weighting. Required JD skills penalise harder when missing."),
        ("Substance Score", "25%",
         "Measures if keywords are proven with outcomes and metrics. Level 0 (just listed) to Level 3 (quantified outcome with scale)."),
        ("AI Noise Detector", "15%",
         "Detects ChatGPT-generated resume padding. Phrase analysis + sentence uniformity + vocabulary diversity. Won't penalise non-native speakers."),
    ]:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown(
                f'<div style="font-family:\'Bebas Neue\',sans-serif;'
                f'font-size:1.8rem;color:#00e5ff;text-align:center;">{weight}</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(f"**{name}** — {desc}")
        st.divider()

    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;
                color:rgba(255,255,255,0.2);text-align:center;margin-top:32px;">
        SORTRESUME · GLOBAL B2B SAAS · v0.1.0 BETA
    </div>
    """, unsafe_allow_html=True)


# ── SIDEBAR + ROUTING — RUNS LAST ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 24px;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                    letter-spacing:0.08em;color:#00e5ff;line-height:1;">
            SORT<br>RESUME
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;
                    color:rgba(255,255,255,0.3);letter-spacing:0.15em;margin-top:4px;">
            FIND REAL CANDIDATES
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Home", "💎 Score Resumes", "ℹ️ About"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;
                color:rgba(255,255,255,0.25);line-height:1.8;">
        4-SIGNAL SCORING<br>
        Semantic · Keyword<br>
        Substance · AI Noise<br><br>
        v0.1.0 — Beta
    </div>
    """, unsafe_allow_html=True)

if page == "🏠 Home":
    _render_home()
elif page == "💎 Score Resumes":
    _render_scorer()
else:
    _render_about()
