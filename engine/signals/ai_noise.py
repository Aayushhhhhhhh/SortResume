"""
Signal 4: AI Noise Detector (15% weight)
==========================================
The feature that makes SortResume globally unique.
No competitor has built this.

Detects ChatGPT-generated resume padding using:
1. Generic phrase detection (AI loves these phrases)
2. Sentence length variance (AI is suspiciously uniform)
3. Vocabulary diversity (AI repeats same words)
4. Metric inflation detection (AI invents or inflates numbers)
5. Structural uniformity (every bullet same pattern)

CRITICAL: Must not punish non-native English speakers.
Calibrated to minimise false positives.

Returns an AUTHENTICITY score (high = human, low = AI).
"""

import re
import math
from collections import Counter
from dataclasses import dataclass, field

# ── AI PHRASE LIBRARY ─────────────────────────────────────────────────────────
# Phrases that appear disproportionately in AI-generated resumes
# Based on r/recruitinghell analysis + GPT output research

AI_GENERIC_PHRASES = [
    # The classic ChatGPT resume openers
    "results-driven professional",
    "results-oriented",
    "dynamic professional",
    "passionate about",
    "highly motivated",
    "proven track record",
    "excellent communication skills",
    "strong work ethic",
    "team player",
    "fast-paced environment",
    "leverage cutting-edge",
    "leveraging cutting-edge",
    "drive business outcomes",
    "driving business value",
    "business outcomes",
    "cross-functional collaboration",
    "stakeholder management",        # Not inherently bad, but AI overuses it
    "go-getter",
    "synergy", "synergize",
    "bandwidth",
    "move the needle",
    "circle back",
    "take ownership",
    "wear many hats",
    "hit the ground running",
    "out-of-the-box thinking",
    "thought leader",
    "value-add",
    "core competencies include",
    "proficient in various",
    "extensive experience in",
    "significant experience",
    "seasoned professional",
    "demonstrated expertise",
    "exceptional interpersonal skills",
    "attention to detail",            # Overused even by humans, but AI doubles it
    "proactive approach",
    "innovative solutions",
    "spearheaded initiatives",        # "spearheaded" alone is fine, this phrase = AI
    "contributed to the success",
    "instrumental in",
    "cutting-edge technologies",
    "state-of-the-art",
    "best practices",                 # Fine once, AI puts it everywhere
    "deep understanding of",
    "robust understanding of",
    "comprehensive understanding of",
    "hands-on experience with",       # Fine once, AI repeats it
    "track record of success",
    "dedicated professional",
    "self-motivated individual",
    "strong analytical skills",
    "detail-oriented professional",
    "collaborative team environment",
    "passionate and driven",
]

# ── INFLATED METRIC PATTERNS ─────────────────────────────────────────────────
# AI tends to invent suspiciously large or precise numbers

INFLATED_METRIC_PATTERNS = [
    r'(improved|increased|reduced|decreased)\s+by\s+[89]\d%',  # 80-99% is suspicious
    r'(improved|increased|reduced|decreased)\s+by\s+100%',      # Exactly 100% = AI
    r'\d{4,}%',                                                   # 1000%+ is made up
    r'10[,\s]?000\+\s*(users|customers|clients)',                # Suspiciously round
    r'saved\s+\$\d+[mb]\+?\s*(annually|per year|yearly)',       # Often inflated
]

COMPILED_INFLATED = [re.compile(p, re.IGNORECASE) for p in INFLATED_METRIC_PATTERNS]


@dataclass
class NoiseAnalysis:
    authenticity_score: float          # 0-100, HIGH = human, LOW = AI noise
    noise_score: float                 # Inverse — for display
    generic_phrase_count: int
    generic_phrases_found: list[str]
    sentence_uniformity: float         # 0-1, high = AI
    vocabulary_diversity: float        # 0-1, high = human
    inflated_metrics_found: list[str]
    flags: list[str]                   # Explanation for UI
    is_likely_ai: bool                 # Simple threshold flag


class AINoiseDetector:
    """
    Detects AI-generated resume content.
    Designed to minimise false positives on non-native speakers.
    """

    # Thresholds — calibrated conservatively to avoid false positives
    GENERIC_PHRASE_THRESHOLD = 4      # > 4 generic phrases = flag
    UNIFORMITY_THRESHOLD = 0.85       # > 85% uniform = flag
    DIVERSITY_THRESHOLD = 0.35        # < 35% diversity = flag

    def analyse(self, text: str, bullets: list[str]) -> NoiseAnalysis:
        """Main analysis entry point."""
        text_lower = text.lower()
        flags = []

        # 1. Generic phrase detection
        found_phrases = [
            phrase for phrase in AI_GENERIC_PHRASES
            if phrase in text_lower
        ]
        phrase_score = min(1.0, len(found_phrases) / 8)  # Normalise to 0-1

        if len(found_phrases) >= self.GENERIC_PHRASE_THRESHOLD:
            flags.append(f"high_generic_phrase_count:{len(found_phrases)}")

        # 2. Sentence length uniformity (AI writes very uniform sentences)
        uniformity = self._calculate_uniformity(bullets)
        if uniformity > self.UNIFORMITY_THRESHOLD:
            flags.append(f"high_sentence_uniformity:{uniformity:.2f}")

        # 3. Vocabulary diversity (type-token ratio)
        diversity = self._calculate_vocabulary_diversity(text)
        if diversity < self.DIVERSITY_THRESHOLD:
            flags.append(f"low_vocabulary_diversity:{diversity:.2f}")

        # 4. Inflated metrics
        inflated = [
            pattern.pattern for pattern in COMPILED_INFLATED
            if pattern.search(text)
        ]
        if inflated:
            flags.append(f"inflated_metrics:{len(inflated)}")

        # ── CALCULATE AUTHENTICITY SCORE ─────────────────────────────────────
        # Weighted combination — phrase detection is strongest signal

        noise_components = {
            "phrases":     phrase_score * 0.45,
            "uniformity":  (uniformity if uniformity > 0.6 else 0) * 0.25,
            "diversity":   (1 - diversity) * 0.20,
            "metrics":     min(1.0, len(inflated) / 3) * 0.10,
        }
        total_noise = sum(noise_components.values())
        total_noise = max(0.0, min(1.0, total_noise))

        # Authenticity is inverse of noise
        authenticity_score = round((1 - total_noise) * 100, 1)
        noise_score = round(total_noise * 100, 1)

        # Only flag as likely AI if multiple strong signals present
        is_likely_ai = (
            len(found_phrases) >= self.GENERIC_PHRASE_THRESHOLD and
            (uniformity > self.UNIFORMITY_THRESHOLD or
             diversity < self.DIVERSITY_THRESHOLD)
        )

        return NoiseAnalysis(
            authenticity_score=authenticity_score,
            noise_score=noise_score,
            generic_phrase_count=len(found_phrases),
            generic_phrases_found=found_phrases[:5],  # Show top 5
            sentence_uniformity=round(uniformity, 3),
            vocabulary_diversity=round(diversity, 3),
            inflated_metrics_found=inflated[:3],
            flags=flags,
            is_likely_ai=is_likely_ai,
        )

    def _calculate_uniformity(self, bullets: list[str]) -> float:
        """
        Measures how uniform bullet lengths are.
        AI tends to write bullets of very similar length.
        Returns 0-1, high = uniform = AI signal.
        """
        if len(bullets) < 5:
            return 0.5  # Not enough data — neutral

        lengths = [len(b.split()) for b in bullets]
        if not lengths:
            return 0.5

        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)

        # Coefficient of variation — normalised variance
        cv = std_dev / mean_len if mean_len > 0 else 0

        # Low CV = high uniformity
        # Humans: CV typically 0.3-0.6
        # AI: CV typically 0.05-0.20
        uniformity = max(0.0, 1.0 - (cv / 0.5))
        return min(1.0, uniformity)

    def _calculate_vocabulary_diversity(self, text: str) -> float:
        """
        Type-Token Ratio (TTR) — unique words / total words.
        Low TTR = repetitive = AI signal.
        Adjusted for text length (longer text naturally has lower TTR).
        """
        words = re.findall(r'\b[a-z]+\b', text.lower())
        if len(words) < 50:
            return 0.7  # Not enough data — assume human

        # Use moving TTR window for length-normalised score
        window = 50
        ttrs = []
        for i in range(0, len(words) - window, 10):
            window_words = words[i:i + window]
            ttr = len(set(window_words)) / len(window_words)
            ttrs.append(ttr)

        return sum(ttrs) / len(ttrs) if ttrs else 0.5


def calculate_ai_noise_score(resume, jd=None) -> dict:
    """
    Main entry point for AI noise scoring.
    Returns authenticity score (100 = very human, 0 = very AI).
    """
    detector = AINoiseDetector()
    all_bullets = resume.all_bullets if hasattr(resume, 'all_bullets') else []
    analysis = detector.analyse(resume.raw_text, all_bullets)

    return {
        "score": analysis.authenticity_score,     # HIGH = good (human)
        "noise_score": analysis.noise_score,      # LOW = good
        "is_likely_ai": analysis.is_likely_ai,
        "generic_phrase_count": analysis.generic_phrase_count,
        "generic_phrases_found": analysis.generic_phrases_found,
        "flags": analysis.flags,
        "vocabulary_diversity": analysis.vocabulary_diversity,
        "sentence_uniformity": analysis.sentence_uniformity,
        "method": "multi_signal_noise_detection",
    }
