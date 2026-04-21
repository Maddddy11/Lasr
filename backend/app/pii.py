from __future__ import annotations

import re
from collections import defaultdict

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?\d{1,2}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "api_key": re.compile(r"\b(?:sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|AIza[A-Za-z0-9_-]{20,})\b"),
    "token": re.compile(r"\b(?:Bearer\s+[A-Za-z0-9._-]{12,}|ghp_[A-Za-z0-9]{20,})\b", re.IGNORECASE),
}


def redact_pii(text: str) -> tuple[str, dict[str, int], list[str]]:
    counts: dict[str, int] = defaultdict(int)
    redacted = text

    for pii_type, pattern in PII_PATTERNS.items():
        redacted, count = pattern.subn(f"[REDACTED_{pii_type.upper()}]", redacted)
        if count:
            counts[pii_type] += count

    pii_types = sorted(counts.keys())
    return redacted, dict(counts), pii_types
