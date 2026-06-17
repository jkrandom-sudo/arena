"""Persistent settings."""
import json
from pathlib import Path
from typing import Optional


DEFAULT_PATH = Path.home() / ".arena_settings.json"

DEFAULTS = {
    "lang": "zh",
    "sound": True,
    "volume": 1,
    "difficulty": "normal",
}

VALID_LANGS = ("zh", "en")
VALID_DIFFICULTIES = ("easy", "normal", "hard")


def load(path: Optional[Path] = None) -> dict:
    if path is None:
        path = DEFAULT_PATH
    s = dict(DEFAULTS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                if k in s:
                    s[k] = v
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    if s.get("lang") not in VALID_LANGS:
        s["lang"] = DEFAULTS["lang"]
    if not isinstance(s.get("sound"), bool):
        s["sound"] = DEFAULTS["sound"]
    if (not isinstance(s.get("volume"), int)
            or s["volume"] < 0 or s["volume"] > 3):
        s["volume"] = DEFAULTS["volume"]
    if s.get("difficulty") not in VALID_DIFFICULTIES:
        s["difficulty"] = DEFAULTS["difficulty"]
    return s


def save(s: dict, path: Optional[Path] = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def cycle_lang(s: dict) -> dict:
    s["lang"] = "en" if s.get("lang") == "zh" else "zh"
    return s


def toggle_sound(s: dict) -> dict:
    s["sound"] = not bool(s.get("sound", True))
    return s


def cycle_volume(s: dict) -> dict:
    s["volume"] = (s.get("volume", 1) + 1) % 4
    return s


def cycle_difficulty(s: dict) -> dict:
    cur = s.get("difficulty", "normal")
    idx = VALID_DIFFICULTIES.index(cur) if cur in VALID_DIFFICULTIES else 1
    s["difficulty"] = VALID_DIFFICULTIES[(idx + 1) % len(VALID_DIFFICULTIES)]
    return s