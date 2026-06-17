"""Persistent leaderboard."""
import json
import time
from pathlib import Path
from typing import List, Optional


DEFAULT_PATH = Path.home() / ".arena_scores.json"
MAX_ENTRIES = 10


def load(path: Optional[Path] = None) -> List[dict]:
    if path is None:
        path = DEFAULT_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return []


def save(scores: List[dict], path: Optional[Path] = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def add(name: str, score: int, difficulty: str,
        path: Optional[Path] = None) -> List[dict]:
    scores = load(path)
    scores.append({
        "name": name[:12] if name else "anon",
        "score": int(score),
        "difficulty": difficulty,
        "time": int(time.time()),
    })
    scores.sort(key=lambda e: (-int(e.get("score", 0)),
                                int(e.get("time", 0))))
    scores = scores[:MAX_ENTRIES]
    save(scores, path)
    return scores