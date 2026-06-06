"""
Skill Normaliser
=================
Resolves aliases to canonical forms before any scoring.
Sorted longest-first so "gen ai" matches before "ai".
Global coverage — not India-specific.
"""

import re

SKILL_ALIASES: dict[str, str] = {
    # ── Languages ────────────────────────────────
    "py": "python", "python3": "python", "python 3": "python",
    "js": "javascript", "node": "nodejs", "node.js": "nodejs",
    "ts": "typescript", "c++": "cpp", "c plus plus": "cpp",
    "golang": "go", "rb": "ruby",

    # ── AI / ML ───────────────────────────────────
    "ml": "machine learning", "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "llm": "large language model", "llms": "large language model",
    "genai": "generative ai", "gen ai": "generative ai",
    "rl": "reinforcement learning",
    "rag": "retrieval augmented generation",

    # ── Web / Frontend ────────────────────────────
    "reactjs": "react", "react.js": "react",
    "vuejs": "vue", "vue.js": "vue",
    "angularjs": "angular",
    "nextjs": "next.js", "nuxtjs": "nuxt.js",

    # ── Cloud ─────────────────────────────────────
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "k8s": "kubernetes",
    "tf": "terraform",

    # ── Data ──────────────────────────────────────
    "postgres": "postgresql", "psql": "postgresql",
    "mongo": "mongodb",
    "mssql": "sql server",
    "powerbi": "power bi",
    "sk-learn": "scikit-learn", "sklearn": "scikit-learn",

    # ── DevOps ────────────────────────────────────
    "ci/cd": "ci cd", "cicd": "ci cd",

    # ── Common abbreviations ──────────────────────
    "oop": "object oriented programming",
    "api": "application programming interface",
    "swe": "software engineer",
    "sde": "software development engineer",
    "fe": "frontend", "be": "backend",
    "fs": "full stack", "fullstack": "full stack",

    # ── Testing ───────────────────────────────────
    "e2e": "end to end testing",
    "tdd": "test driven development",
    "bdd": "behavior driven development",
}


def normalize_text(text: str) -> str:
    """
    Lowercases and resolves skill aliases.
    Longest aliases matched first to prevent partial replacement.
    """
    text = text.lower()
    for alias, canonical in sorted(SKILL_ALIASES.items(), key=lambda x: -len(x[0])):
        pattern = r'\b' + re.escape(alias) + r'\b'
        text = re.sub(pattern, canonical, text)
    return text
