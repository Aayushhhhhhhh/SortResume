"""
Shared test fixtures.
Add real resume + JD pairs to tests/fixtures/ for accuracy testing.
"""
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_jd_python_senior():
    return """
    Senior Python Engineer — Remote Global

    We are looking for a Senior Python Engineer with 5+ years of experience
    building scalable backend systems.

    Requirements (Must Have):
    - Python (5+ years)
    - FastAPI or Django
    - PostgreSQL or MySQL
    - Docker and Kubernetes
    - CI/CD experience (GitHub Actions or Jenkins)

    Nice to Have:
    - Experience with AWS or GCP
    - Machine learning background
    - Redis or Kafka experience

    Responsibilities:
    - Design and build high-performance REST APIs
    - Lead technical architecture decisions
    - Mentor junior engineers
    - Work in an agile team of 8 engineers
    """


@pytest.fixture
def sample_resume_strong():
    return """
    JANE SMITH | jane@example.com | github.com/janesmith

    SUMMARY
    Backend engineer with 6 years building distributed systems in Python.
    Led teams of 3-5 engineers delivering high-availability APIs.

    WORK EXPERIENCE
    Senior Software Engineer — TechCorp (2021–Present)
    • Built FastAPI microservices handling 50M requests/day, achieving 99.99% uptime
    • Led migration from Django monolith to microservices, reducing deployment time by 70%
    • Designed PostgreSQL schema optimisations that cut query time from 2s to 45ms
    • Mentored 3 junior engineers, 2 of whom were promoted within 12 months

    Software Engineer — StartupXYZ (2018–2021)
    • Developed REST APIs serving 500K daily active users using Python and Flask
    • Implemented Docker + Kubernetes deployment pipeline, reducing infra costs by $80K/year
    • Built CI/CD pipeline with GitHub Actions, reducing release cycle from 2 weeks to 2 days

    TECHNICAL SKILLS
    Python, FastAPI, Django, PostgreSQL, MySQL, Docker, Kubernetes,
    GitHub Actions, AWS, Redis, SQLAlchemy, pytest

    EDUCATION
    B.Sc Computer Science — University of Edinburgh, 2018
    """


@pytest.fixture
def sample_resume_weak():
    return """
    JOHN DOE | john@example.com

    SUMMARY
    Results-driven professional passionate about leveraging cutting-edge technologies
    to drive business outcomes. Excellent communication skills and proven track record.
    Highly motivated team player with strong work ethic.

    WORK EXPERIENCE
    Software Developer — Some Company (2022–Present)
    • Responsible for developing software applications
    • Worked on various Python projects
    • Involved in database work
    • Participated in agile ceremonies
    • Helped with deployment tasks

    SKILLS
    Python, JavaScript, SQL, Docker, Kubernetes, AWS, FastAPI,
    Machine Learning, Deep Learning, React, Node.js
    """
