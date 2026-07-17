"""Optional structured enrichment tags."""

from __future__ import annotations

import re
from typing import Any

CATEGORY_PATTERNS = {
    "groceries": re.compile(r"\b(grocer(?:y|ies)|milk|eggs|snacks?)\b", re.I),
    "pet": re.compile(r"\b(pet|dog|puppy|litter)\b", re.I),
    "baby": re.compile(r"\b(baby|diaper|wipes|parent)\b", re.I),
    "personal_care": re.compile(r"\b(personal care|shampoo|skincare)\b", re.I),
    "household": re.compile(r"\b(household|cleaner|essentials)\b", re.I),
    "beverages": re.compile(r"\b(beverage|drinks?|juice)\b", re.I),
}

COMPETITOR_RE = re.compile(r"\b(zepto|instamart|swiggy|bigbasket|amazon fresh)\b", re.I)

KEYWORD_GROUPS = {
    "delivery": re.compile(r"\b(delivery|eta|late|10-?minute|fast)\b", re.I),
    "price": re.compile(r"\b(fee|fees|price|surge|discount|deal|expensive)\b", re.I),
    "support": re.compile(r"\b(support|refund|chat|unreachable)\b", re.I),
}


def enrich_text(text: str, engagement: dict[str, Any] | None = None) -> dict[str, Any]:
    cats = [name for name, pat in CATEGORY_PATTERNS.items() if pat.search(text)]
    if engagement and engagement.get("category"):
        cats.append(str(engagement["category"]).lower().replace(" ", "_"))
    competitors = COMPETITOR_RE.findall(text)
    keywords = [name for name, pat in KEYWORD_GROUPS.items() if pat.search(text)]
    return {
        "category_mentions": sorted(set(cats)),
        "competitor_mentions": sorted({c.lower() for c in competitors}),
        "keyword_tags": keywords,
    }
