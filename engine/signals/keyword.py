"""
Signal 2: Keyword Match (25% weight)
Section-aware TF-IDF with bigrams.
Fixed: proper stop words, skill-focused extraction.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from engine.parser.pdf_parser import ParsedResume, Section
from engine.parser.jd_parser import ParsedJD
from engine.signals.normaliser import normalize_text

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

# Words that appear in JDs but are NOT skills — must be ignored
JD_NOISE_WORDS = {
    # Company/product names
    "storyvord", "google", "microsoft", "amazon", "apple", "meta",
    "netflix", "spotify", "uber", "airbnb", "stripe",
    # Locations
    "hong", "kong", "london", "india", "uk", "usa", "singapore",
    "new", "delhi", "mumbai", "bangalore", "hyderabad",
    # Generic JD filler
    "help", "high", "just", "work", "team", "will", "you",
    "we", "our", "the", "and", "for", "with", "that", "this",
    "are", "have", "your", "from", "been", "they", "their",
    "global", "world", "real", "fast", "best", "great", "good",
    "role", "join", "looking", "offer", "unique", "rare",
    "opportunity", "environment", "exposure", "access",
    "initiative", "ecosystem", "network", "impact", "frontier",
    # Film/media (context words, not skills for generic roles)
    "film", "filming", "movie", "production", "script", "screen",
    "filmmaking", "producer", "studio", "storytelling",
    # Generic action words (not skills)
    "ensure", "shape", "build", "create", "manage", "support",
    "assist", "help", "work", "make", "get", "use", "learn",
}

# Actual skill/competency words to prioritise
SKILL_SIGNALS = [
    "communication", "recruitment", "sourcing", "screening",
    "interviewing", "scheduling", "coordination", "linkedin",
    "database", "tracking", "branding", "outreach", "hiring",
    "talent", "acquisition", "shortlisting", "onboarding",
    "organised", "organized", "responsive", "ownership",
    "remote", "startup", "candidates", "job description",
    "hiring funnel", "employer branding", "candidate experience",
]


def _clean_jd_for_keywords(jd_text: str) -> str:
    """
    Removes noise words from JD before TF-IDF.
    Keeps skill-relevant content only.
    """
    # Remove URLs
    text = re.sub(r'https?://\S+', '', jd_text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # Remove special characters except spaces and basic punctuation
    text = re.sub(r'[^\w\s\-]', ' ', text)
    # Normalise
    text = normalize_text(text)
    # Remove noise words
    words = text.split()
    filtered = [w for w in words if w.lower() not in JD_NOISE_WORDS and len(w) > 2]
    return ' '.join(filtered)


def calculate_keyword_score(resume: ParsedResume, jd: ParsedJD) -> dict:
    """Section-weighted TF-IDF keyword match score."""

    clean_jd = _clean_jd_for_keywords(jd.raw_text)

    # Build weighted resume text
    weighted_resume_parts = []
    for section_type, section_data in resume.sections.items():
        weight = SECTION_TFIDF_WEIGHTS.get(section_type, 0.5)
        norm_section = normalize_text(section_data.raw_text)
        repetitions = max(1, round(weight))
        weighted_resume_parts.extend([norm_section] * repetitions)

    weighted_resume = " ".join(weighted_resume_parts)
    if not weighted_resume.strip():
        weighted_resume = normalize_text(resume.raw_text)

    # TF-IDF
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
            max_features=3000,
        )
        matrix = vectorizer.fit_transform([weighted_resume, clean_jd])
        base_score = cosine_similarity(matrix)[0][1] * 100
    except Exception:
        base_score = 0.0

    # Check for actual skill keywords
    norm_resume_full = normalize_text(resume.raw_text)

    # Skills present in resume from the skill signals list
    matched = [s for s in SKILL_SIGNALS if s in norm_resume_full]

    # Skills from skill signals missing in resume
    jd_lower = jd.raw_text.lower()
    missing_required = [
        s for s in SKILL_SIGNALS
        if s in jd_lower and s not in norm_resume_full
    ]

    # Also check JD parsed required skills
    for skill in jd.required_skill_names:
        norm_skill = normalize_text(skill)
        if norm_skill not in norm_resume_full and norm_skill not in JD_NOISE_WORDS:
            if skill not in missing_required:
                missing_required.append(skill)

    missing_preferred = [
        skill for skill in jd.preferred_skill_names
        if normalize_text(skill) not in norm_resume_full
        and normalize_text(skill) not in JD_NOISE_WORDS
    ]

    # Penalty for missing required skills
    required_penalty = min(20.0, len(missing_required) * 2.5)
    final_score = max(0.0, base_score - required_penalty)

    # Boost if strong skill overlap found
    skill_overlap_boost = min(15.0, len(matched) * 2.5)
    final_score = min(100.0, final_score + skill_overlap_boost)

    return {
        "score": round(final_score, 1),
        "base_score": round(base_score, 1),
        "required_penalty": round(required_penalty, 1),
        "missing_required": missing_required[:15],
        "missing_preferred": missing_preferred[:10],
        "matched_keywords": matched[:20],
        "method": "section_weighted_tfidf_v2",
    }


def extract_top_missing_keywords(resume: ParsedResume, jd: ParsedJD,
                                  top_n: int = 15) -> list[str]:
    """
    Returns top missing keywords — skill-focused, noise filtered.
    """
    norm_resume = normalize_text(resume.raw_text)
    clean_jd = _clean_jd_for_keywords(jd.raw_text)

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
        )
        vectorizer.fit([clean_jd])
        feature_names = vectorizer.get_feature_names_out()
        jd_vector = vectorizer.transform([clean_jd]).toarray()[0]
        top_indices = jd_vector.argsort()[::-1][:top_n * 3]

        missing = []
        for i in top_indices:
            kw = feature_names[i]
            if (jd_vector[i] > 0
                    and kw not in norm_resume
                    and len(kw) > 2
                    and kw not in JD_NOISE_WORDS
                    and not kw.isdigit()):
                missing.append(kw)

        return missing[:top_n]
    except Exception:
        return []


# ── NOISE WORD FILTER ─────────────────────────────────────────────────────────
# Words that appear in JDs but are NOT skills — filtered from missing keywords

KEYWORD_NOISE_WORDS = {
    # Company/brand names
    "storyvord", "naukri", "linkedin", "google", "microsoft", "apple",
    # Locations
    "hong", "kong", "india", "uk", "usa", "france", "netherlands",
    "singapore", "global", "worldwide", "international",
    # Generic filler
    "high", "help", "just", "also", "using", "work", "team", "year",
    "people", "access", "part", "right", "real", "new", "good",
    "learn", "more", "back", "leading", "giving", "looking",
    "build", "shape", "join", "offer", "looking", "like",
    # Film/media specific (not HR skills)
    "film", "films", "movie", "production", "studio", "screen",
    "script", "storytelling", "filmmaking", "filming",
}


def _filter_noise(keywords: list[str]) -> list[str]:
    """Removes noise words from keyword lists."""
    return [
        kw for kw in keywords
        if kw.lower() not in KEYWORD_NOISE_WORDS
        and len(kw) > 2
        and not kw.isdigit()
    ]
