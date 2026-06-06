"""Unit tests for skill normaliser."""

import pytest
from engine.signals.normaliser import normalize_text


@pytest.mark.parametrize("raw,expected", [
    ("ReactJS developer", "react developer"),
    ("ML engineer", "machine learning engineer"),
    ("k8s deployment", "kubernetes deployment"),
    ("gen ai experience", "generative ai experience"),
    ("Python3 and JS", "python and javascript"),
    ("CI/CD pipeline", "ci cd pipeline"),
    ("LLMs and RAG", "large language model and retrieval augmented generation"),
    ("full stack developer", "full stack developer"),  # Already canonical
])
def test_normalization(raw, expected):
    assert normalize_text(raw) == expected


def test_longest_alias_matches_first():
    """gen ai should match before ai."""
    result = normalize_text("gen ai tools")
    assert "generative ai" in result
    assert result.count("generative ai") == 1
