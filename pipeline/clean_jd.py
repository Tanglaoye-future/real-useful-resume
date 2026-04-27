"""JD text cleaning.

Why this module exists:
SmartShanghai / yingjiesheng / shixiseng JD strings come back loaded with:
  - HTML entities (&rsquo; &ndash; &nbsp; &amp; ...)
  - HTML fragments (<a href=...>, <div class="...">, <img src=...>)
  - Site footer boilerplate ("SmartShanghai is the longest-running... NAVIGATE...")
  - "Read More" placeholders separating sections
  - Excessive whitespace and stray newlines

If we feed this raw into an embedding model, semantic similarity gets
contaminated by site chrome (e.g. every SmartShanghai job looks similar
because they share footers). So we strip aggressively, but we keep
the actual responsibilities + requirements text.

The cleaning is intentionally rule-based (no ML): cheap, deterministic,
and easy to audit when a recommendation looks wrong.
"""
from __future__ import annotations

import html
import re
from typing import Iterable

# --- known site-footer / boilerplate patterns to strip ----------------------
# Order matters: longest / most specific first.
_BOILERPLATE_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"SmartShanghai\.com is the longest-running.*?(?=$|\n\n|\Z)",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        r"NAVIGATE\s*(About Us|Contact Us|Advertise|FAQ|Privacy)[\s\S]*?(?=\Z|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"GET LISTED[\s\S]*?(?=\Z|$)",
        re.IGNORECASE,
    ),
    re.compile(r"\bRead More\b", re.IGNORECASE),
    re.compile(r"\bApply Now\b", re.IGNORECASE),
    re.compile(r"Posted By:\s*$", re.IGNORECASE | re.MULTILINE),
]

# --- HTML stripping ---------------------------------------------------------
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# unicode garbage often left from copy-pasted JDs
_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\ufeff]")
# 3+ consecutive newlines -> 2
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
# leading whitespace on each line (kept single space between tokens)
_LINE_LEADING_WS_RE = re.compile(r"^[ \t]+", re.MULTILINE)
# trailing whitespace on each line
_LINE_TRAILING_WS_RE = re.compile(r"[ \t]+$", re.MULTILINE)


def strip_html(text: str) -> str:
    """Remove tags, decode entities, drop zero-width chars."""
    if not text:
        return ""
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _ZERO_WIDTH_RE.sub("", text)
    return text


def strip_boilerplate(text: str) -> str:
    """Remove known site footer / 'Read More' / 'Apply Now' chrome."""
    if not text:
        return ""
    for pat in _BOILERPLATE_PATTERNS:
        text = pat.sub("", text)
    return text


def normalize_whitespace(text: str) -> str:
    """Tidy line endings, drop empty trailing whitespace, collapse blank lines."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _LINE_LEADING_WS_RE.sub("", text)
    text = _LINE_TRAILING_WS_RE.sub("", text)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def clean_jd(text: str) -> str:
    """Full pipeline: HTML -> boilerplate -> whitespace.

    Idempotent: clean_jd(clean_jd(x)) == clean_jd(x).
    """
    if not text:
        return ""
    text = strip_html(text)
    text = strip_boilerplate(text)
    text = normalize_whitespace(text)
    return text


def join_sections(parts: Iterable[str], sep: str = "\n\n") -> str:
    """Join multiple JD sub-fields (description + requirements) into one block.

    Empty parts are dropped. Used by adapters that expose JD as multiple
    fields (e.g. shixiseng has job_description + job_requirement).
    """
    return sep.join(p.strip() for p in parts if p and p.strip())
