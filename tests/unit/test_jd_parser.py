"""Unit tests for JD parser."""

import pytest
from engine.parser.jd_parser import JDParser, SeniorityLevel


@pytest.fixture
def parser():
    return JDParser()


class TestSeniorityDetection:

    def test_detects_senior(self, parser):
        jd = "We are looking for a Senior Software Engineer with 5+ years experience."
        result = parser.parse(jd)
        assert result.seniority == SeniorityLevel.SENIOR

    def test_detects_junior(self, parser):
        jd = "Entry-level position for a Junior Developer. 0-2 years experience."
        result = parser.parse(jd)
        assert result.seniority == SeniorityLevel.JUNIOR

    def test_detects_manager(self, parser):
        jd = "Engineering Manager role leading a team of 8 engineers."
        result = parser.parse(jd)
        assert result.seniority == SeniorityLevel.MANAGER


class TestYearsExperience:

    def test_extracts_years(self, parser):
        jd = "Minimum 5 years of professional experience required."
        result = parser.parse(jd)
        assert result.years_experience == 5

    def test_extracts_plus_years(self, parser):
        jd = "7+ years experience in backend development."
        result = parser.parse(jd)
        assert result.years_experience == 7


class TestSkillExtraction:

    def test_extracts_skills(self, parser):
        jd = "Must have experience with Python, PostgreSQL, and Docker."
        result = parser.parse(jd)
        skills_lower = [s.lower() for s in result.all_skills]
        assert "python" in skills_lower
        assert "docker" in skills_lower


class TestIndustryDetection:

    def test_detects_fintech(self, parser):
        jd = "Join our fintech startup building next-gen payment solutions."
        result = parser.parse(jd)
        assert "fintech" in result.industry_signals

    def test_detects_ai_ml(self, parser):
        jd = "We build machine learning models for enterprise clients."
        result = parser.parse(jd)
        assert "ai_ml" in result.industry_signals
