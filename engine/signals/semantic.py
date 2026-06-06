"""
Signal 1: Semantic Match (35% weight)
=======================================
Uses BAAI/bge-large-en-v1.5 — beats MiniLM by 8%
on semantic similarity tasks.

Section-aware: weights Experience + Skills higher
than Education + Header.
"""

from functools import lru_cache
from loguru import logger

from engine.parser.pdf_parser import ParsedResume, Section
from engine.parser.jd_parser import ParsedJD

SECTION_WEIGHTS = {
    Section.EXPERIENCE: 1.5,
    Section.SKILLS:     1.2,
    Section.PROJECTS:   1.1,
    Section.SUMMARY:    0.9,
    Section.EDUCATION:  0.6,
    Section.CERTS:      0.7,
    Section.HEADER:     0.3,
    Section.UNKNOWN:    0.5,
}

MODEL_NAME = "BAAI/bge-large-en-v1.5"
FALLBACK_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model():
    """Load model once and cache. ~350MB for bge-large."""
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        return SentenceTransformer(MODEL_NAME)
    except Exception as e:
        logger.warning(f"Failed to load {MODEL_NAME}: {e}. Using fallback.")
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(FALLBACK_MODEL)


def calculate_semantic_score(resume: ParsedResume, jd: ParsedJD) -> dict:
    """
    Calculates section-weighted semantic similarity.

    Returns:
        score: float 0-100
        breakdown: per-section scores
        model_used: which model ran
    """
    try:
        from sentence_transformers import util
        import torch

        model = _load_model()
        model_name = getattr(model, '_name_or_path', MODEL_NAME)

        jd_text = jd.raw_text[:3000]  # Cap for performance
        section_scores = {}
        weighted_sum = 0.0
        weight_total = 0.0

        # Score each section independently
        for section_type, section_data in resume.sections.items():
            if not section_data.raw_text.strip():
                continue

            section_text = section_data.raw_text[:1500]
            weight = SECTION_WEIGHTS.get(section_type, 0.5)

            embeddings = model.encode(
                [section_text, jd_text],
                convert_to_tensor=True,
                show_progress_bar=False,
                normalize_embeddings=True,  # Required for BGE models
            )

            sim = util.cos_sim(embeddings[0], embeddings[1]).item()
            score = max(0.0, min(100.0, sim * 100))

            section_scores[section_type.value] = round(score, 1)
            weighted_sum += score * weight
            weight_total += weight

        if weight_total == 0:
            # Fallback: full text comparison
            embeddings = model.encode(
                [resume.raw_text[:2000], jd_text],
                convert_to_tensor=True,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            final_score = util.cos_sim(embeddings[0], embeddings[1]).item() * 100
        else:
            final_score = weighted_sum / weight_total

        return {
            "score": round(max(0.0, min(100.0, final_score)), 1),
            "section_scores": section_scores,
            "model_used": model_name,
            "method": "section_weighted",
        }

    except ImportError:
        return {
            "score": 0.0,
            "section_scores": {},
            "model_used": "unavailable",
            "method": "unavailable",
            "error": "sentence-transformers not installed",
        }
    except Exception as e:
        logger.error(f"Semantic scoring failed: {e}")
        return {
            "score": 0.0,
            "section_scores": {},
            "model_used": "error",
            "method": "error",
            "error": str(e),
        }
