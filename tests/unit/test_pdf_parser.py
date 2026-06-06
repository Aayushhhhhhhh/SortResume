"""
Unit tests for PDF parser and section detector.
Target: > 90% section detection accuracy on diverse PDFs.
"""

import pytest
from engine.parser.pdf_parser import SectionDetector, Section


@pytest.fixture
def detector():
    return SectionDetector()


class TestSectionDetector:

    def test_detects_experience_variants(self, detector):
        headers = [
            "Work Experience", "WORK EXPERIENCE",
            "Professional Experience", "Employment History",
            "Career History", "Experience",
        ]
        for h in headers:
            result = detector.identify_section(h)
            assert result == Section.EXPERIENCE, f"Failed for: '{h}'"

    def test_detects_education_variants(self, detector):
        headers = [
            "Education", "EDUCATION",
            "Academic Background", "Qualifications",
            "Educational Background",
        ]
        for h in headers:
            result = detector.identify_section(h)
            assert result == Section.EDUCATION, f"Failed for: '{h}'"

    def test_detects_skills_variants(self, detector):
        headers = [
            "Skills", "Technical Skills", "SKILLS",
            "Core Competencies", "Tech Stack",
            "Tools and Technologies", "Expertise",
        ]
        for h in headers:
            result = detector.identify_section(h)
            assert result == Section.SKILLS, f"Failed for: '{h}'"

    def test_detects_projects_variants(self, detector):
        headers = [
            "Projects", "Personal Projects",
            "Key Projects", "Portfolio",
            "Open Source",
        ]
        for h in headers:
            result = detector.identify_section(h)
            assert result == Section.PROJECTS, f"Failed for: '{h}'"

    def test_ignores_long_lines(self, detector):
        long_line = "This is a long line that is definitely not a section header " * 2
        result = detector.identify_section(long_line)
        assert result is None

    def test_ignores_empty_lines(self, detector):
        assert detector.identify_section("") is None
        assert detector.identify_section("   ") is None

    def test_bullet_extraction(self, detector):
        lines = [
            "• Built a REST API using FastAPI",
            "- Reduced latency by 40%",
            "* Managed a team of 5 engineers",
            "1. Deployed to AWS using Terraform",
        ]
        bullets = detector._extract_bullets(lines)
        assert len(bullets) == 4
        assert "Built a REST API using FastAPI" in bullets[0]

    def test_full_section_detection(self, detector):
        resume_lines = [
            "John Smith",
            "john@example.com",
            "",
            "Summary",
            "Experienced software engineer with 5 years in backend development.",
            "",
            "Work Experience",
            "• Built microservices at Acme Corp",
            "• Reduced API latency by 35%",
            "",
            "Technical Skills",
            "• Python, FastAPI, PostgreSQL, Docker",
            "",
            "Education",
            "B.Sc Computer Science, MIT, 2019",
        ]
        sections = detector.detect_sections(resume_lines)
        assert Section.EXPERIENCE in sections
        assert Section.SKILLS in sections
        assert Section.EDUCATION in sections


class TestSubstanceScorer:
    """Tests for bullet-level substance detection."""

    def test_level_3_bullet(self):
        from engine.signals.substance import SubstanceScorer
        scorer = SubstanceScorer()
        bullet = "Built Python ETL pipeline processing 2M records/day, reducing data latency by 40%"
        result = scorer.score_bullet(bullet)
        assert result.level == 3
        assert result.has_metric is True
        assert result.has_outcome is True

    def test_level_0_bullet(self):
        from engine.signals.substance import SubstanceScorer
        scorer = SubstanceScorer()
        bullet = "Python, JavaScript, SQL"
        result = scorer.score_bullet(bullet)
        assert result.level == 0
        assert result.score < 0.3

    def test_level_1_bullet(self):
        from engine.signals.substance import SubstanceScorer
        scorer = SubstanceScorer()
        bullet = "Developed REST APIs using FastAPI for internal tooling"
        result = scorer.score_bullet(bullet)
        assert result.level >= 1
        assert result.has_action_verb is True


class TestAINoiseDetector:
    """Tests for AI noise detection — critical for false positive rate."""

    def test_detects_ai_phrases(self):
        from engine.signals.ai_noise import AINoiseDetector
        detector = AINoiseDetector()
        ai_resume = """
        Results-driven professional with a proven track record of success.
        Passionate about leveraging cutting-edge technologies to drive business outcomes.
        Excellent communication skills and strong work ethic in fast-paced environments.
        Dynamic team player with exceptional interpersonal skills.
        Highly motivated self-starter with deep understanding of best practices.
        """
        analysis = detector.analyse(ai_resume, [])
        assert analysis.generic_phrase_count >= 4
        assert analysis.authenticity_score < 60

    def test_clean_resume_not_flagged(self):
        from engine.signals.ai_noise import AINoiseDetector
        detector = AINoiseDetector()
        human_resume = """
        Built a distributed caching system that reduced p99 latency from 800ms to 45ms.
        Led migration of 3 legacy services to Kubernetes, cutting infrastructure costs by $120k/year.
        Wrote a custom Postgres query optimiser that improved reporting queries by 8x.
        Mentored 2 junior engineers who were promoted within 18 months.
        """
        analysis = detector.analyse(human_resume, [])
        assert analysis.authenticity_score > 70
        assert analysis.is_likely_ai is False

    def test_non_native_speaker_not_penalised(self):
        """Critical test — must not punish non-native English speakers."""
        from engine.signals.ai_noise import AINoiseDetector
        detector = AINoiseDetector()
        non_native_resume = """
        I am develop software for 4 year. I make web application using React and Node.
        I build database with PostgreSQL. My project save company 30% cost.
        I work in team of 6 people and we deliver product on time.
        """
        analysis = detector.analyse(non_native_resume, [])
        # Should NOT flag this as AI — grammar errors are a human signal
        assert analysis.is_likely_ai is False
