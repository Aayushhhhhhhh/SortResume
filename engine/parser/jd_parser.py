"""
Layer 2: Job Description Parser — Fixed v2
============================================
Handles informal JDs with emoji bullets, casual language,
startup-style formatting (no formal "Requirements:" sections).
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SkillRequirement(str, Enum):
    REQUIRED  = "required"
    PREFERRED = "preferred"
    INFERRED  = "inferred"


class SeniorityLevel(str, Enum):
    INTERN   = "intern"
    JUNIOR   = "junior"
    MID      = "mid"
    SENIOR   = "senior"
    LEAD     = "lead"
    MANAGER  = "manager"
    DIRECTOR = "director"
    UNKNOWN  = "unknown"


@dataclass
class ExtractedSkill:
    skill: str
    requirement: SkillRequirement
    context: str = ""


@dataclass
class ParsedJD:
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

SENIORITY_SIGNALS: dict[SeniorityLevel, list[str]] = {
    SeniorityLevel.INTERN:   ["intern", "internship", "trainee", "graduate program", "fresher"],
    SeniorityLevel.JUNIOR:   ["junior", "entry.level", "entry level", "0-2 years", "1-2 years", "associate"],
    SeniorityLevel.MID:      ["mid.level", "mid level", "intermediate", "2-4 years", "3-5 years", "2-5 years"],
    SeniorityLevel.SENIOR:   ["senior", "sr.", "sr ", "5+ years", "5-7 years", "6+ years", "experienced"],
    SeniorityLevel.LEAD:     ["lead", "tech lead", "technical lead", "principal", "staff engineer", "8+ years"],
    SeniorityLevel.MANAGER:  ["manager", "engineering manager", "team lead", "people manager", "head of"],
    SeniorityLevel.DIRECTOR: ["director", "chief", "cto", "cpo"],
}

INDUSTRY_SIGNALS = {
    "fintech":    ["fintech", "banking", "financial", "payments", "lending", "insurance"],
    "healthtech": ["health", "medical", "clinical", "hospital", "pharma", "biotech"],
    "ecommerce":  ["ecommerce", "e-commerce", "marketplace", "retail", "d2c", "logistics"],
    "saas":       ["saas", "b2b", "enterprise software", "platform", "multi-tenant"],
    "ai_ml":      ["ai", "machine learning", "deep learning", "llm", "generative ai"],
    "media":      ["film", "movie", "production", "studio", "media", "entertainment", "storytelling"],
}

# ── BROAD SKILL EXTRACTION ────────────────────────────────────────────────────
# Covers both tech AND non-tech skills for broader JD compatibility

SKILL_PATTERNS = re.compile(
    r'\b('
    # Tech skills
    r'python|javascript|typescript|java|golang|rust|ruby|php|swift|kotlin|'
    r'react|angular|vue|nextjs|nodejs|django|fastapi|flask|spring|'
    r'aws|gcp|azure|kubernetes|docker|terraform|ansible|jenkins|'
    r'postgresql|mysql|mongodb|redis|elasticsearch|kafka|'
    r'machine learning|deep learning|nlp|computer vision|'
    r'sql|nosql|rest api|graphql|grpc|'
    r'git|github|gitlab|ci\/cd|devops|agile|scrum|'
    r'html|css|sass|webpack|figma|sketch|'
    r'pandas|numpy|pytorch|tensorflow|scikit.learn|'
    r'linux|bash|powershell|'
    # HR / Business skills
    r'recruitment|talent acquisition|sourcing|screening|'
    r'linkedin|naukri|indeed|job boards|'
    r'interview coordination|candidate management|'
    r'employer branding|hiring funnel|onboarding|'
    r'hris|applicant tracking|ats|'
    r'communication|negotiation|stakeholder management|'
    r'microsoft office|excel|powerpoint|word|'
    r'data handling|documentation|reporting|'
    r'project management|jira|trello|notion|'
    r'canva|adobe|photoshop|'
    r'generative ai|chatgpt|ai tools|'
    # Soft skills that appear in JDs
    r'organized|responsive|ownership|remote work|'
    r'startup|fast.paced|high.ownership'
    r')\b',
    re.IGNORECASE
)

# Words to EXCLUDE from missing keywords (company names, locations, filler)
NOISE_WORDS = {
    "storyvord", "hong", "kong", "india", "uk", "france", "netherlands",
    "singapore", "iit", "bombay", "aicte", "unicef", "global", "high",
    "help", "just", "already", "also", "using", "work", "team", "year",
    "people", "access", "part", "film", "films", "movie", "production",
    "technology", "startup", "company", "office", "world", "future",
    "real", "rare", "mix", "truly", "unique", "frontier", "right",
    "learn", "more", "back", "backed", "leading", "giving",
}


class JDParser:

    def parse(self, jd_text: str) -> ParsedJD:
        """Main entry point — handles both formal and informal JDs."""
        text = jd_text.strip()
        # Strip emoji and special unicode chars before processing
        clean_text = self._strip_emoji(text)
        lines = clean_text.splitlines()

        all_skills = self._extract_all_skills(clean_text)
        required = self._extract_required_skills(clean_text, all_skills)
        preferred = self._extract_preferred_skills(clean_text, all_skills)

        # If no formal required/preferred found, infer from bullet structure
        if not required and not preferred:
            required, preferred = self._infer_from_bullets(lines, all_skills)

        return ParsedJD(
            raw_text=text,
            required_skills=required,
            preferred_skills=preferred,
            all_skills=all_skills,
            seniority=self._detect_seniority(clean_text),
            years_experience=self._extract_years_experience(clean_text),
            role_title=self._extract_role_title(lines),
            industry_signals=self._detect_industry(clean_text),
            responsibilities=self._extract_bullets_after(lines, [
                "what you'll do", "responsibilities", "role", "you will",
                "what you will", "duties",
            ]),
            qualifications=self._extract_bullets_after(lines, [
                "who you are", "qualifications", "requirements",
                "what we're looking for", "you bring", "you have",
                "who we", "looking for",
            ]),
        )

    def _strip_emoji(self, text: str) -> str:
        """Removes emoji and special unicode characters."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "✅✔☑🔍💡⭐🎯🚀💎🔑"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(" ", text)

    def _extract_all_skills(self, text: str) -> list[str]:
        """Extracts all skill-like terms from JD text."""
        found = list(set(
            m.group().lower()
            for m in SKILL_PATTERNS.finditer(text)
        ))
        # Filter noise words
        return [s for s in found if s.lower() not in NOISE_WORDS and len(s) > 2]

    def _extract_required_skills(self, text: str, all_skills: list[str]) -> list[ExtractedSkill]:
        skills = []
        text_lower = text.lower()
        for signal in REQUIRED_SIGNALS:
            if signal not in text_lower:
                continue
            # Find sentences containing this signal
            for sent in re.split(r'[.\n]', text_lower):
                if signal in sent:
                    for skill in all_skills:
                        if skill in sent:
                            skills.append(ExtractedSkill(
                                skill=skill,
                                requirement=SkillRequirement.REQUIRED,
                                context=sent.strip(),
                            ))
        # Dedup
        seen, unique = set(), []
        for s in skills:
            if s.skill not in seen:
                seen.add(s.skill)
                unique.append(s)
        return unique

    def _extract_preferred_skills(self, text: str, all_skills: list[str]) -> list[ExtractedSkill]:
        skills = []
        text_lower = text.lower()
        for signal in PREFERRED_SIGNALS:
            if signal not in text_lower:
                continue
            for sent in re.split(r'[.\n]', text_lower):
                if signal in sent:
                    for skill in all_skills:
                        if skill in sent:
                            skills.append(ExtractedSkill(
                                skill=skill,
                                requirement=SkillRequirement.PREFERRED,
                                context=sent.strip(),
                            ))
        seen, unique = set(), []
        for s in skills:
            if s.skill not in seen:
                seen.add(s.skill)
                unique.append(s)
        return unique

    def _infer_from_bullets(self, lines: list[str],
                             all_skills: list[str]) -> tuple:
        """
        For informal JDs with no formal required/preferred sections,
        treat all extracted skills as inferred required.
        """
        required = [
            ExtractedSkill(skill=s, requirement=SkillRequirement.INFERRED)
            for s in all_skills
        ]
        return required, []

    def _extract_bullets_after(self, lines: list[str],
                                 triggers: list[str]) -> list[str]:
        """Extracts bullet lines after a section header matching any trigger."""
        bullets = []
        capturing = False
        bullet_re = re.compile(r'^[\•\-\*\▪✅✔🔍💡⭐]|\d+[\.\)]\s')

        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            if any(t in line_lower for t in triggers):
                capturing = True
                continue

            if capturing:
                # Stop at next section header (short line ending in : or all caps)
                if (re.match(r'^[A-Z][A-Z\s]{3,}:?\s*$', line_clean) or
                        (len(line_clean) < 60 and line_clean.endswith(':'))):
                    if bullets:  # Only stop if we captured something
                        capturing = False
                        continue

                if bullet_re.match(line_clean) or (len(line_clean) > 15 and capturing):
                    clean = bullet_re.sub("", line_clean).strip()
                    if len(clean) > 10:
                        bullets.append(clean)

        return bullets[:20]

    def _detect_seniority(self, text: str) -> SeniorityLevel:
        text_lower = text.lower()
        for level, signals in SENIORITY_SIGNALS.items():
            for signal in signals:
                if signal in text_lower:
                    return level
        return SeniorityLevel.UNKNOWN

    def _extract_years_experience(self, text: str) -> Optional[int]:
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
        for line in lines[:5]:
            line_clean = line.strip()
            if 3 < len(line_clean) < 80:
                title_re = re.compile(
                    r'(senior|junior|lead|principal|intern|hr|human resources|'
                    r'software|data|ml|ai|backend|frontend|fullstack|'
                    r'devops|cloud|mobile|product|marketing|sales|'
                    r'recruitment|talent|operations|finance)\s*'
                    r'(engineer|developer|manager|intern|analyst|'
                    r'specialist|coordinator|associate|officer|executive)?',
                    re.IGNORECASE
                )
                if title_re.search(line_clean):
                    return line_clean
        return lines[0].strip() if lines else ""

    def _detect_industry(self, text: str) -> list[str]:
        text_lower = text.lower()
        return [
            industry for industry, signals in INDUSTRY_SIGNALS.items()
            if any(signal in text_lower for signal in signals)
        ]


_jd_parser = JDParser()

def parse_jd(jd_text: str) -> ParsedJD:
    return _jd_parser.parse(jd_text)
