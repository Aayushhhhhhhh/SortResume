"""
Signal 3: Substance Score (25% weight)
========================================
The moat. Measures whether keywords are PROVEN
with context, metrics, and outcomes.

Level 0: keyword present (just listed)
Level 1: keyword used in context (in a sentence)
Level 2: outcome stated (result described)
Level 3: quantified outcome (number, %, $, scale)

This is what separates "Python" in a skills list
from "Built Python ETL pipeline processing 2M
records/day, reducing costs by 35%".
"""

import re
from dataclasses import dataclass

from engine.parser.pdf_parser import ParsedResume, Section

# ── ACTION VERBS ─────────────────────────────────────────────────────────────
# Strong verbs that indicate real work — not filler

STRONG_ACTION_VERBS = {
    # Engineering
    "built", "developed", "designed", "architected", "implemented",
    "engineered", "created", "deployed", "automated", "optimised",
    "optimized", "refactored", "migrated", "integrated", "launched",
    "shipped", "scaled", "reduced", "improved", "increased",
    # Leadership
    "led", "managed", "mentored", "directed", "established",
    "spearheaded", "initiated", "drove", "coordinated", "collaborated",
    # Analysis
    "analysed", "analyzed", "researched", "investigated", "diagnosed",
    "identified", "evaluated", "assessed", "reviewed", "audited",
    # Delivery
    "delivered", "executed", "completed", "achieved", "accomplished",
    "produced", "generated", "streamlined", "simplified", "restructured",
}

WEAK_FILLER_VERBS = {
    "responsible for", "worked on", "involved in", "helped with",
    "assisted", "participated", "supported", "contributed to",
    "was part of", "duties included",
}

# ── METRIC PATTERNS ───────────────────────────────────────────────────────────

METRIC_PATTERNS = [
    r'\d+%',                          # Percentages
    r'\$[\d,]+[kmb]?',               # Dollar amounts
    r'£[\d,]+[kmb]?',                # Pound amounts
    r'₹[\d,]+[kmb]?',               # Rupee amounts
    r'\d+[kmb]\+?\s*(users?|records?|requests?|transactions?)',
    r'\d+x\s*(faster|improvement|increase|reduction)',
    r'(reduced|increased|improved|decreased|grew)\s+(by\s+)?\d+',
    r'\d+\s*(ms|milliseconds?|seconds?)\s*(latency|response)',
    r'\d+\+?\s*(team\s+members?|engineers?|developers?)',
    r'(million|billion|thousand)\s+(users?|records?|transactions?)',
]

COMPILED_METRICS = [re.compile(p, re.IGNORECASE) for p in METRIC_PATTERNS]

# ── OUTCOME SIGNALS ───────────────────────────────────────────────────────────

OUTCOME_SIGNALS = [
    "resulting in", "which resulted in", "leading to", "enabling",
    "saving", "reducing", "improving", "increasing", "achieving",
    "allowing", "which allowed", "that enabled", "contributing to",
]


@dataclass
class BulletScore:
    bullet: str
    level: int          # 0-3
    score: float        # 0.0-1.0
    has_action_verb: bool
    has_metric: bool
    has_outcome: bool
    has_context: bool
    flags: list[str]    # Explanation of scoring decisions


class SubstanceScorer:

    def score_bullet(self, bullet: str) -> BulletScore:
        """Scores a single resume bullet 0.0-1.0."""
        bullet_lower = bullet.lower().strip()
        flags = []
        score = 0.0

        # Check action verb at START (not just present anywhere)
        has_action_verb = self._starts_with_action_verb(bullet_lower)
        if has_action_verb:
            score += 0.20
            flags.append("strong_action_verb")
        elif self._has_weak_verb(bullet_lower):
            score -= 0.10
            flags.append("weak_filler_verb")

        # Check for quantifiable metrics
        has_metric = self._has_metric(bullet)
        if has_metric:
            score += 0.35
            flags.append("quantified_metric")

        # Check for outcome/result
        has_outcome = self._has_outcome(bullet_lower)
        if has_outcome:
            score += 0.25
            flags.append("outcome_stated")

        # Check for tool/technology used in context (not just named)
        has_context = self._has_contextual_usage(bullet_lower)
        if has_context:
            score += 0.20
            flags.append("tool_in_context")

        # Determine level
        if has_metric and has_outcome:
            level = 3
        elif has_outcome or has_metric:
            level = 2
        elif has_context or has_action_verb:
            level = 1
        else:
            level = 0

        # Penalty for very short bullets (< 8 words) — likely just a skill name
        word_count = len(bullet.split())
        if word_count < 8:
            score *= 0.5
            flags.append("too_short")

        return BulletScore(
            bullet=bullet,
            level=level,
            score=max(0.0, min(1.0, score)),
            has_action_verb=has_action_verb,
            has_metric=has_metric,
            has_outcome=has_outcome,
            has_context=has_context,
            flags=flags,
        )

    def _starts_with_action_verb(self, text: str) -> bool:
        first_word = text.split()[0] if text.split() else ""
        return first_word in STRONG_ACTION_VERBS

    def _has_weak_verb(self, text: str) -> bool:
        return any(phrase in text for phrase in WEAK_FILLER_VERBS)

    def _has_metric(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in COMPILED_METRICS)

    def _has_outcome(self, text: str) -> bool:
        return any(signal in text for signal in OUTCOME_SIGNALS)

    def _has_contextual_usage(self, text: str) -> bool:
        """Checks if a tool is used in context vs just named."""
        context_patterns = [
            r'using\s+\w+', r'with\s+\w+', r'via\s+\w+',
            r'built\s+\w+\s+(with|using|in)',
            r'leveraged\s+\w+', r'developed\s+\w+\s+using',
        ]
        return any(
            re.search(p, text, re.IGNORECASE)
            for p in context_patterns
        )


def calculate_substance_score(resume: ParsedResume, jd: ParsedJD) -> dict:
    """
    Scores the overall substance of resume bullets.
    Weights Experience bullets 2x vs other sections.
    """
    scorer = SubstanceScorer()
    all_bullet_scores: list[BulletScore] = []
    section_breakdowns = {}

    for section_type, section_data in resume.sections.items():
        if not section_data.bullets:
            continue

        section_bullet_scores = [
            scorer.score_bullet(b) for b in section_data.bullets
        ]

        # Experience bullets count double
        weight = 2.0 if section_type == Section.EXPERIENCE else 1.0
        avg = (sum(b.score for b in section_bullet_scores) /
               len(section_bullet_scores)) if section_bullet_scores else 0.0

        section_breakdowns[section_type.value] = {
            "avg_score": round(avg * 100, 1),
            "bullet_count": len(section_bullet_scores),
            "level_3_count": sum(1 for b in section_bullet_scores if b.level == 3),
            "level_0_count": sum(1 for b in section_bullet_scores if b.level == 0),
        }

        # Add weighted bullets to global list
        for bs in section_bullet_scores:
            bs_copy = BulletScore(
                bullet=bs.bullet,
                level=bs.level,
                score=bs.score * weight,
                has_action_verb=bs.has_action_verb,
                has_metric=bs.has_metric,
                has_outcome=bs.has_outcome,
                has_context=bs.has_context,
                flags=bs.flags,
            )
            all_bullet_scores.append(bs_copy)

    if not all_bullet_scores:
        return {"score": 0.0, "breakdown": {}, "total_bullets": 0}

    # Normalise back to 0-100
    avg_score = (
        sum(b.score for b in all_bullet_scores) /
        len(all_bullet_scores)
    ) * 100

    # Find weakest bullets for UI feedback
    weak_bullets = sorted(
        [b for b in all_bullet_scores if b.level <= 1],
        key=lambda x: x.score
    )[:5]

    return {
        "score": round(min(100.0, avg_score), 1),
        "section_breakdown": section_breakdowns,
        "total_bullets": len(all_bullet_scores),
        "level_distribution": {
            "level_3": sum(1 for b in all_bullet_scores if b.level == 3),
            "level_2": sum(1 for b in all_bullet_scores if b.level == 2),
            "level_1": sum(1 for b in all_bullet_scores if b.level == 1),
            "level_0": sum(1 for b in all_bullet_scores if b.level == 0),
        },
        "weak_bullets": [b.bullet[:100] for b in weak_bullets],
        "method": "section_weighted_bullets",
    }
