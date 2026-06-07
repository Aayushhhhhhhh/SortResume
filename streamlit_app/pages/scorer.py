"""
Score Resumes Page — Core product feature.
Upload PDFs + JD → get ranked results.
"""

import io
import time
import streamlit as st

# ── HELPERS ───────────────────────────────────────────────────────────────────

def _tier_badge(tier: str) -> str:
    colors = {
        "top":    ("#0a2a0a", "#22c55e", "TOP CANDIDATE"),
        "review": ("#2a1f0a", "#f59e0b", "WORTH REVIEWING"),
        "skip":   ("#2a0a0a", "#ef4444", "NOT A MATCH"),
    }
    bg, color, label = colors.get(tier, colors["skip"])
    return (f'<span style="background:{bg}; color:{color}; '
            f'border:1px solid {color}44; border-radius:4px; '
            f'padding:2px 10px; font-family:\'DM Mono\',monospace; '
            f'font-size:10px; letter-spacing:0.1em;">{label}</span>')


def _score_bar(score: float, color: str = "#00e5ff") -> str:
    return f"""
    <div style="background:rgba(255,255,255,0.06); border-radius:4px;
                height:6px; margin-top:4px; overflow:hidden;">
        <div style="width:{score}%; height:6px; border-radius:4px;
                    background:{color}; transition:width 0.5s;"></div>
    </div>"""


def _score_color(score: float) -> str:
    if score >= 75: return "#22c55e"
    if score >= 50: return "#f59e0b"
    return "#ef4444"


def _pill(text: str, color: str = "red") -> str:
    configs = {
        "red":   ("rgba(239,68,68,0.12)",  "#fca5a5", "rgba(239,68,68,0.3)"),
        "green": ("rgba(34,197,94,0.12)",  "#86efac", "rgba(34,197,94,0.3)"),
        "blue":  ("rgba(0,229,255,0.10)",  "#67e8f9", "rgba(0,229,255,0.3)"),
        "amber": ("rgba(245,158,11,0.12)", "#fcd34d", "rgba(245,158,11,0.3)"),
    }
    bg, fg, border = configs.get(color, configs["red"])
    return (f'<span style="display:inline-block; background:{bg}; color:{fg}; '
            f'border:1px solid {border}; border-radius:20px; '
            f'padding:3px 10px; margin:3px; font-size:12px;">{text}</span>')


def _run_scorer(resume_bytes: bytes, filename: str, jd_text: str) -> dict:
    """Runs the full scoring pipeline."""
    try:
        from engine.parser.pdf_parser import parse_resume
        from engine.parser.jd_parser import parse_jd
        from engine.scorer.hybrid_scorer import score_resume

        parsed_resume = parse_resume(resume_bytes)
        parsed_jd = parse_jd(jd_text)
        result = score_resume(parsed_resume, parsed_jd)

        return {
            "filename": filename,
            "success": True,
            "result": result,
        }
    except Exception as e:
        return {
            "filename": filename,
            "success": False,
            "error": str(e),
        }


# ── MAIN RENDER ───────────────────────────────────────────────────────────────

def render():
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif; font-size:2.5rem;
                letter-spacing:0.04em; margin-bottom:4px;">
        SCORE RESUMES
    </div>
    <div style="font-family:'DM Mono',monospace; font-size:11px;
                color:rgba(255,255,255,0.3); letter-spacing:0.1em;
                margin-bottom:32px;">
        UPLOAD RESUMES + PASTE JD → GET RANKED RESULTS
    </div>
    """, unsafe_allow_html=True)

    # ── INPUT COLUMNS ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace; font-size:10px;
                    letter-spacing:0.15em; color:rgba(0,229,255,0.7);
                    margin-bottom:8px;">STEP 1 — UPLOAD RESUMES</div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload PDF resumes",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload up to 100 PDF resumes at once",
            label_visibility="collapsed",
        )

        if uploaded_files:
            st.markdown(f"""
            <div style="font-family:'DM Mono',monospace; font-size:11px;
                        color:#22c55e; margin-top:8px;">
                ✓ {len(uploaded_files)} resume{'s' if len(uploaded_files) > 1 else ''} uploaded
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace; font-size:10px;
                    letter-spacing:0.15em; color:rgba(0,229,255,0.7);
                    margin-bottom:8px;">STEP 2 — PASTE JOB DESCRIPTION</div>
        """, unsafe_allow_html=True)

        jd_text = st.text_area(
            "Job description",
            height=200,
            placeholder="Paste the full job description here...\n\nWorks with any job board — LinkedIn, Indeed, Naukri, your own ATS.",
            label_visibility="collapsed",
        )

        if jd_text:
            word_count = len(jd_text.split())
            color = "#22c55e" if word_count >= 50 else "#f59e0b"
            st.markdown(f"""
            <div style="font-family:'DM Mono',monospace; font-size:11px;
                        color:{color}; margin-top:4px;">
                {word_count} words {'✓' if word_count >= 50 else '— add more for better accuracy'}
            </div>
            """, unsafe_allow_html=True)

    # ── VALIDATE + SUBMIT ─────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    can_submit = bool(uploaded_files and jd_text and len(jd_text.split()) >= 30)

    if not can_submit and (uploaded_files or jd_text):
        if not uploaded_files:
            st.info("Upload at least one PDF resume to continue.")
        elif not jd_text or len(jd_text.split()) < 30:
            st.info("Paste a job description (at least 30 words) for accurate results.")

    submit = st.button(
        "💎 SCORE ALL RESUMES",
        disabled=not can_submit,
        use_container_width=True,
    )

    # ── RESULTS ───────────────────────────────────────────────────────────────
    if submit and can_submit:
        st.divider()
        st.markdown("""
        <div style="font-family:'Bebas Neue',sans-serif; font-size:1.8rem;
                    letter-spacing:0.04em; margin-bottom:16px;">
            RESULTS
        </div>
        """, unsafe_allow_html=True)

        results = []
        progress = st.progress(0, text="Scoring resumes...")

        for i, file in enumerate(uploaded_files):
            progress.progress(
                (i + 1) / len(uploaded_files),
                text=f"Scoring {file.name} ({i+1}/{len(uploaded_files)})..."
            )
            result = _run_scorer(file.read(), file.name, jd_text)
            results.append(result)

        progress.empty()

        # ── SORT BY SCORE ─────────────────────────────────────────────────────
        successful = [r for r in results if r["success"]]
        failed     = [r for r in results if not r["success"]]

        successful.sort(
            key=lambda x: x["result"].final_score,
            reverse=True
        )

        # ── SUMMARY STRIP ─────────────────────────────────────────────────────
        top_count    = sum(1 for r in successful if r["result"].tier == "top")
        review_count = sum(1 for r in successful if r["result"].tier == "review")
        skip_count   = sum(1 for r in successful if r["result"].tier == "skip")

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Scored", len(successful))
        with m2: st.metric("Top Candidates", top_count)
        with m3: st.metric("Worth Reviewing", review_count)
        with m4: st.metric("Skip", skip_count)

        if failed:
            with st.expander(f"⚠️ {len(failed)} files failed to parse"):
                for f in failed:
                    st.error(f"**{f['filename']}** — {f['error']}")

        st.divider()

        # ── CANDIDATE CARDS ───────────────────────────────────────────────────
        for rank, r in enumerate(successful, 1):
            res = r["result"]
            score_color = _score_color(res.final_score)

            with st.expander(
                f"#{rank}  {r['filename']}  —  {res.final_score}%  {res.tier_label}",
                expanded=(rank <= 3),
            ):
                # Top row — score + tier
                top_left, top_right = st.columns([1, 2])

                with top_left:
                    st.markdown(f"""
                    <div style="background:#13131f; border:1px solid rgba(255,255,255,0.08);
                                border-radius:12px; padding:20px; text-align:center;">
                        <div style="font-family:'Bebas Neue',sans-serif;
                                    font-size:3.5rem; line-height:1;
                                    color:{score_color};">{res.final_score}%</div>
                        <div style="font-family:'DM Mono',monospace; font-size:10px;
                                    color:rgba(255,255,255,0.4); letter-spacing:0.1em;
                                    margin:6px 0;">ATS MATCH SCORE</div>
                        {_tier_badge(res.tier)}
                    </div>
                    """, unsafe_allow_html=True)

                    # Signal bars
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                    for label, val, color in [
                        ("🧠 Semantic",  res.semantic_score,  "#00e5ff"),
                        ("🔑 Keyword",   res.keyword_score,   "#7fff6b"),
                        ("💪 Substance", res.substance_score, "#ffd166"),
                        ("🤖 AI Noise",  res.ai_noise_score,  "#ff6b9d"),
                    ]:
                        st.markdown(f"""
                        <div style="margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between;
                                        font-size:12px; color:rgba(255,255,255,0.6);">
                                <span>{label}</span>
                                <span style="color:{color}; font-family:'DM Mono',monospace;">
                                    {val}%
                                </span>
                            </div>
                            {_score_bar(val, color)}
                        </div>
                        """, unsafe_allow_html=True)

                with top_right:
                    # Explanation
                    if res.explanation:
                        st.markdown(f"""
                        <div style="background:#13131f;
                                    border:1px solid rgba(255,255,255,0.06);
                                    border-radius:8px; padding:16px;
                                    font-size:13px; color:rgba(255,255,255,0.7);
                                    line-height:1.6; margin-bottom:12px;">
                            {res.explanation}
                        </div>
                        """, unsafe_allow_html=True)

                    # AI Warning
                    if res.is_likely_ai_generated:
                        st.warning(
                            "⚠️ **Likely AI-generated resume** — "
                            "This resume shows strong ChatGPT signals. "
                            "Verify the candidate's actual experience before proceeding."
                        )

                    # Matched keywords
                    if res.matched_keywords:
                        st.markdown("**✅ Matched Keywords**")
                        pills_html = "".join(
                            _pill(kw, "green") for kw in res.matched_keywords[:12]
                        )
                        st.markdown(
                            f'<div style="margin:4px 0 12px">{pills_html}</div>',
                            unsafe_allow_html=True
                        )

                    # Missing required
                    if res.missing_required:
                        st.markdown("**❌ Missing Required Skills**")
                        pills_html = "".join(
                            _pill(kw, "red") for kw in res.missing_required[:10]
                        )
                        st.markdown(
                            f'<div style="margin:4px 0 12px">{pills_html}</div>',
                            unsafe_allow_html=True
                        )

                    # Top missing keywords
                    if res.top_missing_keywords:
                        st.markdown("**🔍 Top Missing Keywords**")
                        pills_html = "".join(
                            _pill(kw, "amber") for kw in res.top_missing_keywords[:10]
                        )
                        st.markdown(
                            f'<div style="margin:4px 0 12px">{pills_html}</div>',
                            unsafe_allow_html=True
                        )

                # Weak bullets + AI phrases
                detail_left, detail_right = st.columns(2)

                with detail_left:
                    if res.weak_bullets:
                        with st.expander("💪 Bullets to Improve"):
                            for b in res.weak_bullets[:3]:
                                st.markdown(f"""
                                <div style="background:#13131f;
                                            border-left:3px solid #f59e0b;
                                            padding:8px 12px; margin-bottom:6px;
                                            font-size:12px; border-radius:0 4px 4px 0;
                                            color:rgba(255,255,255,0.6);">
                                    {b}
                                </div>
                                """, unsafe_allow_html=True)

                with detail_right:
                    if res.ai_phrases_found:
                        with st.expander("🤖 AI Phrases Detected"):
                            for phrase in res.ai_phrases_found[:5]:
                                st.markdown(f"""
                                <div style="background:#13131f;
                                            border-left:3px solid #ff6b9d;
                                            padding:8px 12px; margin-bottom:6px;
                                            font-size:12px; border-radius:0 4px 4px 0;
                                            color:rgba(255,255,255,0.6);
                                            font-family:'DM Mono',monospace;">
                                    "{phrase}"
                                </div>
                                """, unsafe_allow_html=True)

                # Parse metadata
                st.markdown(f"""
                <div style="font-family:'DM Mono',monospace; font-size:10px;
                            color:rgba(255,255,255,0.2); margin-top:8px;">
                    Parsed via {res.parse_method} ·
                    Sections: {', '.join(res.sections_detected)}
                </div>
                """, unsafe_allow_html=True)

        # ── CSV EXPORT ────────────────────────────────────────────────────────
        if successful:
            st.divider()
            st.markdown("""
            <div style="font-family:'Bebas Neue',sans-serif; font-size:1.4rem;
                        letter-spacing:0.04em; margin-bottom:12px;">
                EXPORT RESULTS
            </div>
            """, unsafe_allow_html=True)

            import csv, io as io_module
            output = io_module.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "Rank", "Filename", "Final Score", "Tier",
                "Semantic", "Keyword", "Substance", "AI Noise",
                "Missing Required", "AI Generated", "Explanation"
            ])
            for rank, r in enumerate(successful, 1):
                res = r["result"]
                writer.writerow([
                    rank,
                    r["filename"],
                    res.final_score,
                    res.tier_label,
                    res.semantic_score,
                    res.keyword_score,
                    res.substance_score,
                    res.ai_noise_score,
                    " | ".join(res.missing_required[:5]),
                    "Yes" if res.is_likely_ai_generated else "No",
                    res.explanation,
                ])

            st.download_button(
                label="⬇️ DOWNLOAD CSV REPORT",
                data=output.getvalue(),
                file_name="sortresume_results.csv",
                mime="text/csv",
                use_container_width=True,
            )
