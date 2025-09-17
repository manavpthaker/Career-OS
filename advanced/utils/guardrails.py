# utils/guardrails.py
"""Content gates for quality control (claims, forbidden phrases, ATS format)."""

from typing import List, Dict, Iterable
import re

DEFAULT_REQUIRED: Iterable[str] = []       # keep empty by default; load from config if you like
DEFAULT_FORBIDDEN: Iterable[str] = [
    "AI-generated news", "mock news", "IPO-ready", "2 exits", "500K customers"
]

_TABLE_CHARS = ("│", "├", "─", "┌", "┬", "┼", "┐", "┘", "└")

def validate_claims(text: str, required: Iterable[str], forbidden: Iterable[str]) -> List[str]:
    """Validate that required claims are present and forbidden phrases are absent."""
    errs = []
    for claim in required or []:
        if claim not in (text or ""):
            errs.append(f"Missing required claim: {claim}")
    for phrase in forbidden or []:
        if phrase and phrase in (text or ""):
            errs.append(f"Forbidden phrase found: {phrase}")
    return errs

def validate_ats_format(text: str) -> List[str]:
    """Validate resume format for ATS compatibility."""
    errs = []
    # basic section checks (case-insensitive and handle variations)
    text_upper = (text or "").upper()
    section_checks = [
        ("EXPERIENCE", "Experience"),
        ("EDUCATION", "Education"),
        ("SKILL", "Skills")  # Check for SKILL to match both Skills and TECHNICAL SKILLS
    ]
    for check, display in section_checks:
        if check not in text_upper:
            errs.append(f"Missing section: {display}")
    # dates (MMM YYYY)
    if not re.search(r"\b[A-Z][a-z]{2}\s\d{4}\b", text or ""):
        errs.append("Use MMM YYYY date format (e.g., Jan 2023)")
    # no box-drawing tables
    if any(ch in (text or "") for ch in _TABLE_CHARS):
        errs.append("Remove table/box characters for ATS parsing")
    return errs

def validate_content(texts: Dict[str, str],
                     required: Iterable[str] = DEFAULT_REQUIRED,
                     forbidden: Iterable[str] = DEFAULT_FORBIDDEN) -> List[str]:
    """
    Validate a bundle of generated texts (e.g., cover letter & resume).
    
    Args:
        texts: Dictionary with 'cover_letter' and 'resume' keys
        required: Required claims/phrases
        forbidden: Forbidden phrases
        
    Returns:
        List of validation errors (empty if valid)
    """
    errs = []
    cover = texts.get("cover_letter", "")
    resume = texts.get("resume", "")
    # claims rules on cover letter by default
    errs += validate_claims(cover, required, forbidden)
    # ATS checks on resume (and optionally cover letter)
    errs += [f"resume: {e}" for e in validate_ats_format(resume)]
    return errs