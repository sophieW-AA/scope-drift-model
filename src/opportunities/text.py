"""Title-token profiles and Jaccard overlap (paper-level home proxy)."""

from __future__ import annotations

import re
from collections import Counter

STOP = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "using",
    "based",
    "into",
    "onto",
    "over",
    "under",
    "via",
    "are",
    "was",
    "were",
    "been",
    "have",
    "has",
    "had",
    "not",
    "but",
    "its",
    "their",
    "new",
    "use",
    "used",
    "study",
    "analysis",
    "model",
    "models",
    "method",
    "methods",
    "approach",
    "system",
    "systems",
    "data",
    "review",
    "toward",
    "towards",
    "among",
    "between",
    "within",
    "frontiers",
}


def tokenize(text: str) -> list[str]:
    return [
        w
        for w in re.findall(r"[a-z]{3,}", (text or "").lower())
        if w not in STOP
    ]


def token_profile(titles: list[str], k: int = 40) -> set[str]:
    counts: Counter[str] = Counter()
    for t in titles:
        counts.update(tokenize(t))
    return {w for w, _ in counts.most_common(k)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def domain_hit_rate(titles: list[str], domain: set[str]) -> float:
    if not titles or not domain:
        return 0.0
    hits = 0
    for t in titles:
        toks = set(tokenize(t))
        if toks & domain:
            hits += 1
    return hits / len(titles)


def journal_domain_tokens(journal: str, extra: dict[str, set[str]] | None = None) -> set[str]:
    from . import config as C

    table = extra or C.JOURNAL_DOMAIN_TOKENS
    bare = re.sub(r"(?i)^frontiers\s+in\s+", "", journal or "").strip().lower()
    tokens = set(tokenize(bare))
    tokens |= table.get(bare, set())
    return tokens
