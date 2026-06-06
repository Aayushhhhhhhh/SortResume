"""
Hybrid Scorer — Master Orchestrator
=====================================
Blends all 4 signals into one final score.
Every decision is explainable.

Formula:
  Final = (35% semantic) + (25% keyword) +
          (25% substance) + (15% ai_noise)

The weights are starting values — calibrate after
collecting 50+ human-rated resume+JD pairs.
"""

from dataclasses import dataclass, field
from loguru import logger

from engine.parser.pdf_parser import ParsedResume
from engine.parser.jd_parser import ParsedJD
from engine.signals.semantic import calculate_semantic_score
from engine.signals.keyword import calculate_keyword_score, extract_top_missing_keywords
from engine.signals.substance import calculate_substance_score
from engine.signals.ai_noise import calculate_ai_noise_score

# ── SIGNAL WEIGHTS ────────────────────────────────────────────────────────────
# Must sum to 1.0
WEIGHTS = {
    "semantic":  0.35,
    "keyword":   0.25,
    "substance": 0.25,
    "ai_noise":  0.15,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 0.001, "Weights must sum to 1.0"


def _tier(score: float) -> str:
    """Maps score to recruiter-facing tier."""
    if score >= 75: return "top"
    if score >= 50: return "review"
    return "skip"


def _tier_label(score: float) -> str:
    if score >= 75: return "Top Candidate"
    if score >= 50: return "Worth Reviewing"
    return "Not a Match"


@dataclass
class ScoringResult:
    """Complete scoring result — everything the UI needs."""

    # Core scores
    final_score: float
    tier: str               # "top", "review", "skip"
    tier_label: str

    # Signal breakdowns
    semantic_score: float
    keyword_score: float
    substance_score: float
    ai_noise_score: float   # Authenticity — HIGH is good

    # Explainability
    missing_required: list[str] = field(default_factory=list)
    missing_preferred: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    top_missing_keywords: list[str] = field(default_factory=list)
    weak_bullets: list[str] = field(default_factory=list)
    ai_phrases_found: list[str] = field(default_factory=list)
    is_likely_ai_generated: bool = False

    # Score explanation
    explanation: str = ""

    # Metadata
    parse_method: str = ""
    sections_detected: list[str] = field(default_factory=list)
    seniority_match: str = ""

    # Raw signal data (for debugging + calibration)
    raw_signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "final_score": self.final_score,
            "tier": self.tier,
            "tier_label": self.tier_label,
            "signals": {
                "semantic": self.semantic_score,
                "keyword": self.keyword_score,
                "substance": self.substance_score,
                "ai_noise": self.ai_noise_score,
            },
            "missing_required": self.missing_required,
            "missing_preferred": self.missing_preferred,
            "matched_keywords": self.matched_keywords,
            "top_missing_keywords": self.top_missing_keywords,
            "weak_bullets": self.weak_bullets,
            "ai_phrases_found": self.ai_phrases_found,
            "is_likely_ai_generated": self.is_likely_ai_generated,
            "explanation": self.explanation,
            "parse_method": self.parse_method,
            "sections_detected": self.sections_detected,
        }


class HybridScorer:

    def score(self, resume: ParsedResume, jd: ParsedJD) -> ScoringResult:
        """
        Runs all 4 signals and blends into final score.
        All signals run independently — one failure doesn't kill the rest.
        """
        logger.info(f"Scoring resume ({resume.char_count} chars) "
                   f"against JD ({len(jd.raw_text)} chars)")

        # ── RUN ALL 4 SIGNALS ─────────────────────────────────────────────────

        semantic_result = self._safe_run("semantic", calculate_semantic_score,
                                          resume, jd)
        keyword_result  = self._safe_run("keyword",  calculate_keyword_score,
                                          resume, jd)
        substance_result= self._safe_run("substance",calculate_substance_score,
                                          resume, jd)
        noise_result    = self._safe_run("ai_noise", calculate_ai_noise_score,
                                          resume)

        # ── EXTRACT SCORES ────────────────────────────────────────────────────

        semantic_score  = semantic_result.get("score", 0.0)
        keyword_score   = keyword_result.get("score", 0.0)
        substance_score = substance_result.get("score", 0.0)
        ai_noise_score  = noise_result.get("score", 50.0)  # Default neutral

        # ── WEIGHTED BLEND ────────────────────────────────────────────────────

        final_score = (
            WEIGHTS["semantic"]  * semantic_score  +
            WEIGHTS["keyword"]   * keyword_score   +
            WEIGHTS["substance"] * substance_score +
            WEIGHTS["ai_noise"]  * ai_noise_score
        )
        final_score = round(max(0.0, min(100.0, final_score)), 1)

        # ── MISSING KEYWORDS ──────────────────────────────────────────────────

        top_missing = extract_top_missing_keywords(resume, jd, top_n=15)

        # ── EXPLANATION ───────────────────────────────────────────────────────

        explanation = self._generate_explanation(
            final_score, semantic_score, keyword_score,
            substance_score, ai_noise_score,
            keyword_result.get("missing_required", []),
            substance_result.get("level_distribution", {}),
            noise_result.get("is_likely_ai", False),
        )

        return ScoringResult(
            final_score=final_score,
            tier=_tier(final_score),
            tier_label=_tier_label(final_score),
            semantic_score=round(semantic_score, 1),
            keyword_score=round(keyword_score, 1),
            substance_score=round(substance_score, 1),
            ai_noise_score=round(ai_noise_score, 1),
            missing_required=keyword_result.get("missing_required", [])[:10],
            missing_preferred=keyword_result.get("missing_preferred", [])[:8],
            matched_keywords=keyword_result.get("matched_keywords", [])[:15],
            top_missing_keywords=top_missing,
            weak_bullets=substance_result.get("weak_bullets", [])[:5],
            ai_phrases_found=noise_result.get("generic_phrases_found", [])[:5],
            is_likely_ai_generated=noise_result.get("is_likely_ai", False),
            explanation=explanation,
            parse_method=resume.parse_method,
            sections_detected=[s.value for s in resume.sections.keys()],
            raw_signals={
                "semantic": semantic_result,
                "keyword": keyword_result,
                "substance": substance_result,
                "ai_noise": noise_result,
            },
        )

    def _safe_run(self, signal_name: str, fn, *args) -> dict:
        """Runs a signal function safely — never crashes the scorer."""
        try:
            return fn(*args) or {}
        except Exception as e:
            logger.error(f"Signal '{signal_name}' failed: {e}")
            return {"score": 0.0, "error": str(e)}

    def _generate_explanation(
        self,
        final: float,
        semantic: float,
        keyword: float,
        substance: float,
        noise: float,
        missing_required: list,
        level_dist: dict,
        is_ai: bool,
    ) -> str:
        """
        Generates a human-readable explanation of the score.
        This is what makes the product trustworthy globally.
        """
        parts = []

        # Overall verdict
        if final >= 75:
            parts.append(f"Strong match at {final}%.")
        elif final >= 50:
            parts.append(f"Moderate match at {final}%.")
        else:
            parts.append(f"Low match at {final}%.")

        # What's driving it up
        strengths = []
        if semantic >= 70: strengths.append("experience closely aligns with the role")
        if keyword >= 70:  strengths.append("strong keyword coverage")
        if substance >= 70: strengths.append("bullets show clear outcomes and metrics")
        if noise >= 80:    strengths.append("resume reads as authentic")
        if strengths:
            parts.append("Strengths: " + ", ".join(strengths) + ".")

        # What's pulling it down
        weaknesses = []
        if missing_required:
            weaknesses.append(
                f"missing {len(missing_required)} required skills "
                f"({', '.join(missing_required[:3])})"
            )
        if substance < 50:
            level_0 = level_dist.get("level_0", 0)
            if level_0 > 3:
                weaknesses.append(
                    f"{level_0} bullets list skills without showing outcomes"
                )
        if noise < 50:
            weaknesses.append("resume contains AI-generated phrases")
        if weaknesses:
            parts.append("Areas to improve: " + ", ".join(weaknesses) + ".")

        # AI warning
        if is_ai:
            parts.append(
                "⚠️ Resume shows strong AI-generation signals — "
                "verify candidate's actual experience."
            )

        return " ".join(parts)


# ── PUBLIC API ────────────────────────────────────────────────────────────────

_scorer = HybridScorer()

def score_resume(resume: ParsedResume, jd: ParsedJD) -> ScoringResult:
    """Main entry point for scoring."""
    return _scorer.score(resume, jd)
