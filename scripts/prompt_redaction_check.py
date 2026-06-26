from __future__ import annotations

import re

SENSITIVE_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?:\+?98|0)?9\d{9}"),
    "national_id": re.compile(r"\b\d{10}\b"),
    "iban": re.compile(r"\bIR\d{24}\b", re.IGNORECASE),
    "bank_card": re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),
}


def detected_sensitive_fields(text: str) -> tuple[str, ...]:
    return tuple(name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(text))


def prompt_requires_redaction(text: str) -> bool:
    return bool(detected_sensitive_fields(text))


def redact_prompt(text: str, replacement: str = "[REDACTED]") -> str:
    redacted = text
    for pattern in SENSITIVE_PATTERNS.values():
        redacted = pattern.sub(replacement, redacted)
    return redacted
