from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.dedup import paper_identity_keys
from src.models import Digest, Paper


def load_recommendation_history(path: str | Path) -> set[str]:
    history_path = Path(path)
    if not history_path.exists():
        return set()
    try:
        payload = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    keys = payload.get("identity_keys", []) if isinstance(payload, dict) else []
    return {str(key) for key in keys if key}


def filter_previously_recommended(candidates: list[Paper], history_keys: set[str]) -> list[Paper]:
    if not history_keys:
        return candidates
    return [
        paper
        for paper in candidates
        if not paper_identity_keys(paper).intersection(history_keys)
    ]


def save_recommendation_history(path: str | Path, digest: Digest, existing_keys: set[str]) -> None:
    history_path = Path(path)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    all_keys = set(existing_keys)
    entries: list[dict[str, Any]] = []
    for paper in digest.new_papers + digest.classic_papers:
        keys = sorted(paper_identity_keys(paper))
        all_keys.update(keys)
        entries.append(
            {
                "title": paper.title,
                "doi": paper.doi,
                "year": paper.year,
                "category": paper.category,
                "identity_keys": keys,
            }
        )
    payload = {
        "identity_keys": sorted(all_keys),
        "last_recommendations": entries,
    }
    history_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
