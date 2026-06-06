"""
Signal 2: Keyword Match (25% weight)
======================================
Section-aware TF-IDF with bigrams.
Skills in Experience section > Skills list.
Required JD skills penalise harder when missing.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from engine.parser.pdf_parser import ParsedResume, Section
from engine.parser.jd_parser import ParsedJD
from engine.signals.normaliser import normalize_text

# Weight per section — keywords in Experience mean more
SECTION_TFIDF_WEIGHTS = {
    Section.EXPERIENCE: 2.0,
    Section.SKILLS:     1.5,
    Section.PROJECTS:   1.3,
    Section.SUMMARY:    1.0,
    Section.CERTS:      0.8,
    Section.EDUCATION:  0.6,
    Section.HEADER:     0.2,
    Section.UNKNOWN:    0.5,
}


def calculate_keyword_score(resume: ParsedResume, jd: ParsedJD) -> dict:
    """
    Section-weighted TF-IDF keyword match score.

    Returns:
        score: float 0-100
        missing_required: required JD skills missing from resume
        missing_preferred: preferred JD skills missing from resume
        matched_keywords: keywords present in both
    """
    norm_jd = normalize_text(jd.raw_text)

    # Build a weighted resume text — sections with higher importance
    # are repeated proportionally to their weight
    weighted_resume_parts = []
    for section_type, section_data in resume.sections.items():
        weight = SECTION_TFIDF_WEIGHTS.get(section_type, 0.5)
        norm_section = normalize_text(section_data.raw_text)
        # Repeat section text proportional to weight (integer repetitions)
        repetitions = max(1, round(weight))
        weighted_resume_parts.extend([norm_section] * repetitions)

    weighted_resume = " ".join(weighted_resume_parts)

    if not weighted_resume.strip():
        weighted_resume = normalize_text(resume.raw_text)

    # TF-IDF with bigrams
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
            max_features=5000,
        )
        matrix = vectorizer.fit_transform([weighted_resume, norm_jd])
        base_score = cosine_similarity(matrix)[0][1] * 100
    except Exception:
        base_score = 0.0

    # Penalty for missing required skills
    norm_resume_full = normalize_text(resume.raw_text)
    missing_required = [
        skill for skill in jd.required_skill_names
        if normalize_text(skill) not in norm_resume_full
    ]
    missing_preferred = [
        skill for skill in jd.preferred_skill_names
        if normalize_text(skill) not in norm_resume_full
    ]
    matched = [
        skill for skill in jd.all_skills
        if normalize_text(skill) in norm_resume_full
    ]

    # Apply penalty: each missing required skill costs 3 points (capped at 25)
    required_penalty = min(25.0, len(missing_required) * 3.0)
    final_score = max(0.0, base_score - required_penalty)

    return {
        "score": round(min(100.0, final_score), 1),
        "base_score": round(base_score, 1),
        "required_penalty": round(required_penalty, 1),
        "missing_required": missing_required[:15],
        "missing_preferred": missing_preferred[:10],
        "matched_keywords": matched[:20],
        "method": "section_weighted_tfidf",
    }


def extract_top_missing_keywords(resume: ParsedResume, jd: ParsedJD,
                                  top_n: int = 15) -> list[str]:
    """
    Returns top missing keywords ranked by TF-IDF importance in JD.
    Used for the 'Missing Keywords' display in UI.
    """
    norm_resume = normalize_text(resume.raw_text)
    norm_jd = normalize_text(jd.raw_text)

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english', ngram_range=(1, 2), min_df=1,
        )
        vectorizer.fit([norm_jd])
        feature_names = vectorizer.get_feature_names_out()
        jd_vector = vectorizer.transform([norm_jd]).toarray()[0]
        top_indices = jd_vector.argsort()[::-1][:top_n * 3]
        jd_keywords = [
            feature_names[i] for i in top_indices
            if jd_vector[i] > 0 and len(feature_names[i]) > 2
        ]
        return [kw for kw in jd_keywords if kw not in norm_resume][:top_n]
    except Exception:
        return []
