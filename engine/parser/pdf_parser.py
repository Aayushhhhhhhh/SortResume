"""
Layer 1: PDF Parser — Fixed v2
================================
Added missing section patterns for non-standard resumes.
Handles hyphenated headers, ampersands, and Indian resume formats.
"""

import io
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import pdfplumber
import fitz

from loguru import logger


class Section(str, Enum):
    HEADER     = "header"
    SUMMARY    = "summary"
    EXPERIENCE = "experience"
    EDUCATION  = "education"
    SKILLS     = "skills"
    PROJECTS   = "projects"
    CERTS      = "certifications"
    AWARDS     = "awards"
    LEADERSHIP = "leadership"
    UNKNOWN    = "unknown"


SECTION_PATTERNS: dict[Section, list[str]] = {
    Section.SUMMARY: [
        r"^(professional\s+)?summary$",
        r"^(career\s+)?objective$",
        r"^profile$", r"^about\s*(me|myself)?$",
        r"^overview$", r"^executive\s+summary$",
        r"^personal\s+statement$",
    ],
    Section.EXPERIENCE: [
        r"^(work|professional|employment)\s+(experience|history)$",
        r"^experience$", r"^work\s+history$",
        r"^career\s+history$", r"^relevant\s+experience$",
        r"^positions?\s+held$", r"^employment$",
        # Indian resume formats
        r"^part[\s\-]*time\s*(&|and)\s*internship\s+(experience|history)?$",
        r"^internship\s+(experience|history)?$",
        r"^internships?$",
        r"^work\s*(&|and)\s*(internship|experience)$",
        r"^(professional\s+)?experience\s*(&|and)\s*internships?$",
    ],
    Section.EDUCATION: [
        r"^education(al)?\s*(background|qualifications?)?$",
        r"^academic\s+(background|qualifications?|history)$",
        r"^qualifications?$", r"^degrees?$", r"^schooling$",
    ],
    Section.SKILLS: [
        r"^(technical\s+)?skills?$",
        r"^(core\s+)?competenc(y|ies)$",
        r"^technologies?$", r"^tech(nical)?\s+stack$",
        r"^tools?\s*(and\s+technologies?)?$",
        r"^expertise$", r"^capabilities$",
        r"^languages?\s+and\s+tools?$",
        r"^personal\s*(&|and)?\s*hobbies$",
        r"^skills\s*(&|and)\s*(interests|hobbies)$",
    ],
    Section.PROJECTS: [
        r"^(personal\s+|key\s+|notable\s+)?projects?$",
        r"^portfolio$", r"^(personal\s+)?work$",
        r"^selected\s+projects?$", r"^open[\s\-]source$",
    ],
    Section.CERTS: [
        r"^certifications?$", r"^certificates?$",
        r"^licen[sc]es?\s*(and\s+certifications?)?$",
        r"^accreditations?$", r"^professional\s+development$",
        r"^courses?\s*(and\s+certifications?)?$",
    ],
    Section.AWARDS: [
        r"^awards?\s*(and\s+honors?)?$",
        r"^honors?\s*(and\s+awards?)?$",
        r"^achievements?$", r"^accomplishments?$",
        r"^recognition$",
    ],
    Section.LEADERSHIP: [
        r"^leadership\s*(&|and)?\s*(experience|activities|community)?(\s+service)?$",
        r"^(extra|co)[\s\-]?curricular\s*(activities)?$",
        r"^volunteer(ing)?\s*(experience|work)?$",
        r"^community\s+service$",
        r"^activities\s*(&|and)?\s*leadership$",
        r"^positions?\s+of\s+responsibility$",
    ],
}


@dataclass
class ResumeSection:
    section_type: Section
    raw_text: str
    bullets: list[str] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


@dataclass
class ParsedResume:
    raw_text: str
    sections: dict[Section, ResumeSection]
    parse_method: str
    page_count: int = 0
    char_count: int = 0
    parse_warnings: list[str] = field(default_factory=list)

    def get_section_text(self, section: Section) -> str:
        s = self.sections.get(section)
        return s.raw_text if s else ""

    def has_section(self, section: Section) -> bool:
        return section in self.sections

    @property
    def experience_text(self) -> str:
        return self.get_section_text(Section.EXPERIENCE)

    @property
    def skills_text(self) -> str:
        return self.get_section_text(Section.SKILLS)

    @property
    def all_bullets(self) -> list[str]:
        bullets = []
        for section in self.sections.values():
            bullets.extend(section.bullets)
        return bullets


class SectionDetector:

    def __init__(self):
        self._compiled: dict[Section, list[re.Pattern]] = {}
        for section, patterns in SECTION_PATTERNS.items():
            self._compiled[section] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def identify_section(self, line: str) -> Optional[Section]:
        cleaned = line.strip().rstrip(":.").strip()
        if not cleaned or len(cleaned) > 70:
            return None

        for section, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.fullmatch(cleaned):
                    return section

        # ALL CAPS heuristic
        if cleaned.isupper() and 3 <= len(cleaned) <= 60:
            result = self._match_caps_header(cleaned)
            if result:
                return result

        return None

    def _match_caps_header(self, text: str) -> Optional[Section]:
        text_lower = text.lower()
        for section, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.fullmatch(text_lower):
                    return section
        return None

    def detect_sections(self, lines: list[str]) -> dict[Section, ResumeSection]:
        sections: dict[Section, ResumeSection] = {}
        current_section = Section.HEADER
        current_lines: list[str] = []
        current_start = 0

        for i, line in enumerate(lines):
            detected = self.identify_section(line)
            if detected and detected != current_section:
                if current_lines:
                    section_text = "\n".join(current_lines).strip()
                    if section_text:
                        sections[current_section] = ResumeSection(
                            section_type=current_section,
                            raw_text=section_text,
                            bullets=self._extract_bullets(current_lines),
                            line_start=current_start,
                            line_end=i - 1,
                        )
                current_section = detected
                current_lines = []
                current_start = i
            else:
                current_lines.append(line)

        if current_lines:
            section_text = "\n".join(current_lines).strip()
            if section_text:
                sections[current_section] = ResumeSection(
                    section_type=current_section,
                    raw_text=section_text,
                    bullets=self._extract_bullets(current_lines),
                    line_start=current_start,
                    line_end=len(lines) - 1,
                )

        return sections

    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets = []
        current_bullet: list[str] = []
        bullet_markers = re.compile(r'^[\•\-\*\▪\→\–\—◦▸►▷▶]|\d+[\.\)]\s')

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_bullet:
                    bullets.append(" ".join(current_bullet))
                    current_bullet = []
                continue

            if bullet_markers.match(stripped):
                if current_bullet:
                    bullets.append(" ".join(current_bullet))
                clean = bullet_markers.sub("", stripped).strip()
                current_bullet = [clean]
            elif current_bullet:
                current_bullet.append(stripped)
            else:
                if len(stripped) > 20:
                    current_bullet = [stripped]

        if current_bullet:
            bullets.append(" ".join(current_bullet))

        return [b for b in bullets if len(b) > 10]


class PDFParser:
    MIN_CHARS = 200
    MIN_WORDS = 50

    def __init__(self):
        self.section_detector = SectionDetector()

    def parse(self, file_bytes: bytes) -> ParsedResume:
        try:
            result = self._parse_pdfplumber(file_bytes)
            if self._is_quality_extraction(result.raw_text):
                return result
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")

        try:
            result = self._parse_pymupdf(file_bytes)
            if self._is_quality_extraction(result.raw_text):
                return result
        except Exception as e:
            logger.error(f"pymupdf also failed: {e}")

        raise ValueError(
            "Could not extract text from this PDF. "
            "Make sure it is a text-based PDF, not a scanned image."
        )

    def _parse_pdfplumber(self, file_bytes: bytes) -> ParsedResume:
        warnings = []
        pages_text = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text(
                    x_tolerance=3, y_tolerance=3,
                    layout=True, x_density=7.25, y_density=13,
                )
                if text:
                    pages_text.append(text)
                else:
                    warnings.append(f"Page {i+1} returned no text")

        raw_text = self._clean_text("\n".join(pages_text))
        lines = raw_text.splitlines()
        sections = self.section_detector.detect_sections(lines)

        return ParsedResume(
            raw_text=raw_text, sections=sections,
            parse_method="pdfplumber", page_count=page_count,
            char_count=len(raw_text), parse_warnings=warnings,
        )

    def _parse_pymupdf(self, file_bytes: bytes) -> ParsedResume:
        warnings = []
        pages_text = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = doc.page_count

        for i, page in enumerate(doc):
            text = page.get_text("text", sort=True)
            if text.strip():
                pages_text.append(text)
            else:
                warnings.append(f"Page {i+1} returned no text")
        doc.close()

        raw_text = self._clean_text("\n".join(pages_text))
        lines = raw_text.splitlines()
        sections = self.section_detector.detect_sections(lines)

        return ParsedResume(
            raw_text=raw_text, sections=sections,
            parse_method="pymupdf", page_count=page_count,
            char_count=len(raw_text), parse_warnings=warnings,
        )

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        lines = [line.rstrip() for line in text.splitlines()]
        return '\n'.join(lines).strip()

    def _is_quality_extraction(self, text: str) -> bool:
        if not text or len(text) < self.MIN_CHARS:
            return False
        if len(text.split()) < self.MIN_WORDS:
            return False
        non_ascii = sum(1 for c in text if ord(c) > 127)
        if non_ascii / len(text) > 0.3:
            return False
        return True


_parser = PDFParser()

def parse_resume(file_bytes: bytes) -> ParsedResume:
    return _parser.parse(file_bytes)

def parse_resume_from_file(filepath: str) -> ParsedResume:
    with open(filepath, "rb") as f:
        return _parser.parse(f.read())
