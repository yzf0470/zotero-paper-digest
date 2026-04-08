from __future__ import annotations

import html
import re


def clean_text(value: object, *, max_whitespace: bool = True) -> str:
    text = "" if value is None else str(value)
    for _ in range(2):
        text = html.unescape(text)
    text = re.sub(r"<\s*/?\s*(jats:)?(title|sec|p|italic|bold|sub|sup|break|br)[^>]*>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+([,.;:)])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    text = text.replace("\u2010", "-").replace("\u2011", "-").replace("\u2012", "-")
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    if max_whitespace:
        text = " ".join(text.split())
    return text.strip()


def clean_abstract(value: object) -> str:
    text = clean_text(value)
    text = re.sub(r"^(abstract|summary)\s*[:.-]?\s*", "", text, flags=re.IGNORECASE)
    if not has_useful_abstract(text):
        return ""
    return text


def has_useful_abstract(text: str) -> bool:
    compact = clean_text(text)
    if len(compact) < 40:
        return False
    if re.fullmatch(r"\d+\.?", compact):
        return False
    words = re.findall(r"[A-Za-z]{3,}", compact)
    return len(words) >= 8
