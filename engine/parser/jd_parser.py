"""
Layer 2: Job Description Parser
================================
Nobody parses JDs properly. They treat them as blobs.
We extract structured data — required vs preferred,
seniority signals, role type, industry context.

This structured extraction is what enables accurate
section-weighted scoring.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SkillRequirement(str, Enum):
    REQUIRED  = "required"   # Must have — "required", "must have", "essential"
    PREFERRED = "preferred"  # Nice to have — "preferred", "nice to have", "bonus"
    INFERRED  = "inferred"   # Not explicitly labelled — we infer from context


class SeniorityLevel(str, Enum):
    INTERN     = "intern"
    JUNIOR     = "junior"      # 0-2 years
    MID        = "mid"         # 2-5 years
    SENIOR     = "senior"      # 5-8 years
    LEAD       = "lead"        # 8+ or leadership title
    MANAGER    = "manager"     # People manager
    DIRECTOR   = "director"
    UNKNOWN    = "unknown"


@dataclass
class ExtractedSkill:
    skill: str
    requirement: SkillRequirement
    context: str = ""          # The sentence it appeared in


@dataclass
class ParsedJD:
    """Structured JD — ready for comparison against parsed resume."""
    raw_text: str
    required_skills: list[ExtractedSkill] = field(default_factory=list)
    preferred_skills: list[ExtractedSkill] = field(default_factory=list)
    all_skills: list[str] = field(default_factory=list)
    seniority: SeniorityLevel = SeniorityLevel.UNKNOWN
    years_experience: Optional[int] = None
    role_title: str = ""
    industry_signals: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    qualifications: list[str] = field(default_factory=list)

    @property
    def required_skill_names(self) -> list[str]:
        return [s.skill for s in self.required_skills]

    @property
    def preferred_skill_names(self) -> list[str]:
        return [s.skill for s in self.preferred_skills]


# ── REQUIREMENT SIGNALS ───────────────────────────────────────────────────────

REQUIRED_SIGNALS = [
    "required", "must have", "must-have", "essential",
    "mandatory", "necessary", "you will need", "you must",
    "we require", "minimum requirement", "key requirement",
    "non-negotiable", "critical", "strong", "proficient in",
    "experience with", "expertise in",
]

PREFERRED_SIGNALS = [
    "preferred", "nice to have", "nice-to-have", "bonus",
    "desirable", "advantageous", "ideally", "a plus",
    "an advantage", "good to have", "beneficial",
    "would be great", "welcome", "optional",
    "familiar with", "exposure to", "knowledge of",
]

# ── SENIORITY SIGNALS ─────────────────────────────────────────────────────────

SENIORITY_SIGNALS: dict[SeniorityLevel, list[str]] = {
    SeniorityLevel.INTERN:   ["intern", "internship", "trainee", "graduate program"],
    SeniorityLevel.JUNIOR:   ["junior", "entry.level", "entry level", "0-2 years",
                              "1-2 years", "fresher", "new grad", "associate"],
    SeniorityLevel.MID:      ["mid.level", "mid level", "intermediate", "2-4 years",
                              "3-5 years", "2-5 years"],
    SeniorityLevel.SENIOR:   ["senior", "sr.", "sr ", "5+ years", "5-7 years",
                              "6+ years", "7+ years", "experienced"],
    SeniorityLevel.LEAD:     ["lead", "tech lead", "technical lead", "principal",
                              "staff engineer", "8+ years", "10+ years"],
    SeniorityLevel.MANAGER:  ["manager", "engineering manager", "team lead",
                              "people manager", "head of", "vp of", "vp,"],
    SeniorityLevel.DIRECTOR: ["director", "chief", "cto", "cpo", "vp"],
}

# ── INDUSTRY SIGNALS ──────────────────────────────────────────────────────────

INDUSTRY_SIGNALS = {
    "fintech":    ["fintech", "banking", "financial", "payments", "lending",
                   "insurance", "wealth", "trading", "blockchain", "crypto"],
    "healthtech": ["health", "medical", "clinical", "hospital", "pharma",
                   "biotech", "telemedicine", "ehr", "fhir"],
    "ecommerce":  ["ecommerce", "e-commerce", "marketplace", "retail",
                   "d2c", "supply chain", "logistics", "fulfilment"],
    "saas":       ["saas", "b2b", "enterprise software", "platform",
                   "multi-tenant", "subscription"],
    "ai_ml":      ["ai", "machine learning", "deep learning", "llm",
                   "generative ai", "computer vision", "nlp"],
}


class JDParser:
    """
    Parses job descriptions into structured data.
    Uses regex + heuristics (LLM extraction in Phase 2).
    """

    def parse(self, jd_text: str) -> ParsedJD:
        """Main entry point."""
        text = jd_text.strip()
        lines = text.splitlines()

        return ParsedJD(
            raw_text=text,
            required_skills=self._extract_required_skills(text),
            preferred_skills=self._extract_preferred_skills(text),
            all_skills=self._extract_all_skills(text),
            seniority=self._detect_seniority(text),
            years_experience=self._extract_years_experience(text),
            role_title=self._extract_role_title(lines),
            industry_signals=self._detect_industry(text),
            responsibilities=self._extract_responsibilities(lines),
            qualifications=self._extract_qualifications(lines),
        )

    def _extract_required_skills(self, text: str) -> list[ExtractedSkill]:
        """Finds skills marked as required."""
        skills = []
        text_lower = text.lower()

        for signal in REQUIRED_SIGNALS:
            # Find sentences containing this signal
            pattern = rf'[^.]*{re.escape(signal)}[^.]*\.'
            for match in re.finditer(pattern, text_lower):
                sentence = match.group()
                extracted = self._extract_skills_from_sentence(sentence)
                for skill in extracted:
                    skills.append(ExtractedSkill(
                        skill=skill,
                        requirement=SkillRequirement.REQUIRED,
                        context=sentence,
                    ))

        # Deduplicate
        seen = set()
        unique = []
        for s in skills:
            if s.skill not in seen:
                seen.add(s.skill)
                unique.append(s)
        return unique

    def _extract_preferred_skills(self, text: str) -> list[ExtractedSkill]:
        """Finds skills marked as preferred/nice-to-have."""
        skills = []
        text_lower = text.lower()

        for signal in PREFERRED_SIGNALS:
            pattern = rf'[^.]*{re.escape(signal)}[^.]*\.'
            for match in re.finditer(pattern, text_lower):
                sentence = match.group()
                extracted = self._extract_skills_from_sentence(sentence)
                for skill in extracted:
                    skills.append(ExtractedSkill(
                        skill=skill,
                        requirement=SkillRequirement.PREFERRED,
                        context=sentence,
                    ))

        seen = set()
        unique = []
        for s in skills:
            if s.skill not in seen:
                seen.add(s.skill)
                unique.append(s)
        return unique

    def _extract_all_skills(self, text: str) -> list[str]:
        """
        Extracts all skill-like tokens from the JD.
        Uses a combination of known tech terms + pattern matching.
        For Phase 2: replace with LLM extraction.
        """
        # Common tech skill patterns
        tech_pattern = re.compile(
            r'\b('
            r'python|javascript|typescript|java|golang|rust|ruby|php|swift|kotlin|scala|'
            r'react|angular|vue|nextjs|nodejs|django|fastapi|flask|spring|'
            r'aws|gcp|azure|kubernetes|docker|terraform|ansible|jenkins|'
            r'postgresql|mysql|mongodb|redis|elasticsearch|kafka|'
            r'machine learning|deep learning|nlp|computer vision|'
            r'sql|nosql|rest api|graphql|grpc|'
            r'git|github|gitlab|ci/cd|devops|agile|scrum|'
            r'html|css|sass|webpack|vite|'
            r'pandas|numpy|pytorch|tensorflow|scikit.learn|'
            r'linux|bash|powershell|'
            r'figma|sketch|adobe xd'
            r')\b',
            re.IGNORECASE
        )

        skills = list(set(
            match.group().lower()
            for match in tech_pattern.finditer(text)
        ))
        return skills

    def _extract_skills_from_sentence(self, sentence: str) -> list[str]:
        """Extracts skill names from a sentence."""
        # Simple: return tech terms found in sentence
        tech_pattern = re.compile(
            r'\b(python|javascript|typescript|java|golang|react|angular|vue|'
            r'nodejs|aws|gcp|azure|kubernetes|docker|postgresql|mongodb|redis|'
            r'machine learning|deep learning|sql|git|agile|scrum|rest|graphql)\b',
            re.IGNORECASE
        )
        return [m.group().lower() for m in tech_pattern.finditer(sentence)]

    def _detect_seniority(self, text: str) -> SeniorityLevel:
        """Detects seniority level from JD text."""
        text_lower = text.lower()
        for level, signals in SENIORITY_SIGNALS.items():
            for signal in signals:
                if signal in text_lower:
                    return level
        return SeniorityLevel.UNKNOWN

    def _extract_years_experience(self, text: str) -> Optional[int]:
        """Extracts minimum years of experience required."""
        patterns = [
            r'(\d+)\+?\s*years?\s+of\s+(professional\s+)?experience',
            r'(\d+)\+?\s*years?\s+experience',
            r'minimum\s+(\d+)\s+years?',
            r'at\s+least\s+(\d+)\s+years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_role_title(self, lines: list[str]) -> str:
        """
        Attempts to extract the job title.
        Usually in the first 5 lines of a JD.
        """
        title_patterns = [
            r'(senior|junior|lead|principal|staff)?\s*'
            r'(software|data|ml|ai|backend|frontend|fullstack|full.stack|'
            r'devops|cloud|mobile|ios|android|platform|infrastructure)\s*'
            r'(engineer|developer|architect|scientist|analyst|manager)',
            r'(product|engineering|technical)\s+manager',
            r'(cto|cpo|vp\s+of\s+engineering)',
        ]
        for line in lines[:5]:
            for pattern in title_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group().strip()
        return ""

    def _detect_industry(self, text: str) -> list[str]:
        """Detects industry context from JD."""
        text_lower = text.lower()
        found = []
        for industry, signals in INDUSTRY_SIGNALS.items():
            if any(signal in text_lower for signal in signals):
                found.append(industry)
        return found

    def _extract_responsibilities(self, lines: list[str]) -> list[str]:
        """Extracts responsibility bullets from JD."""
        responsibilities = []
        in_responsibilities = False
        resp_pattern = re.compile(
            r'(responsibilities|what you.ll do|role overview|'
            r'key responsibilities|your role|duties)',
            re.IGNORECASE
        )
        bullet_pattern = re.compile(r'^[\•\-\*\▪]|\d+\.\s')

        for line in lines:
            if resp_pattern.search(line):
                in_responsibilities = True
                continue
            if in_responsibilities:
                if re.match(r'^[A-Z][A-Z\s]+:?\s*$', line.strip()):
                    in_responsibilities = False
                    continue
                if bullet_pattern.match(line.strip()):
                    clean = bullet_pattern.sub("", line.strip()).strip()
                    if len(clean) > 10:
                        responsibilities.append(clean)

        return responsibilities[:20]  # Cap at 20

    def _extract_qualifications(self, lines: list[str]) -> list[str]:
        """Extracts qualification bullets from JD."""
        qualifications = []
        in_quals = False
        qual_pattern = re.compile(
            r'(qualifications?|requirements?|what we.re looking for|'
            r'what you.ll bring|you have|you bring|must have)',
            re.IGNORECASE
        )
        bullet_pattern = re.compile(r'^[\•\-\*\▪]|\d+\.\s')

        for line in lines:
            if qual_pattern.search(line):
                in_quals = True
                continue
            if in_quals:
                if re.match(r'^[A-Z][A-Z\s]+:?\s*$', line.strip()):
                    in_quals = False
                    continue
                if bullet_pattern.match(line.strip()):
                    clean = bullet_pattern.sub("", line.strip()).strip()
                    if len(clean) > 10:
                        qualifications.append(clean)

        return qualifications[:20]


# ── PUBLIC API ────────────────────────────────────────────────────────────────

_jd_parser = JDParser()

def parse_jd(jd_text: str) -> ParsedJD:
    """Main entry point for JD parsing."""
    return _jd_parser.parse(jd_text)
