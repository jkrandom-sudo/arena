"""Tests for i18n, settings, score, sound."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import i18n
import settings as settings_mod
import score as score_mod
from sound import Sound


class TestI18n(unittest.TestCase):
    def test_keys_match(self):
        self.assertEqual(set(i18n.STRINGS["zh"].keys()),
                         set(i18n.STRINGS["en"].keys()))

    def test_t_basic(self):
        self.assertEqual(i18n.t("en", "title"), "Arena Combat")

    def test_t_kwargs(self):
        s = i18n.t("en", "round_intro", wave=3, monster="Slime")
        self.assertIn("3", s)
        self.assertIn("Slime", s)

    def test_t_missing_lang(self):
        self.assertEqual(i18n.t("xx", "title"), i18n.t("en", "title"))

    def test_t_missing_key(self):
        self.assertEqual(i18n.t("en", "no_such"), "no_such")

    def test_format_failure_returns_template(self):
        # missing kwargs is fine; returns template, no crash
        s = i18n.t("en", "round_intro")
        self.assertIsInstance(s, str)


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = Path(self.tmp) / "s.json"

    def test_defaults(self):
        s = settings_mod.load(self.path)
        self.assertEqual(s["lang"], "zh")
        self.assertTrue(s["sound"])
        self.assertEqual(s["volume"], 1)
        self.assertEqual(s["difficulty"], "normal")

    def test_round_trip(self):
        s = settings_mod.load(self.path)
        s["lang"] = "en"
        s["sound"] = False
        s["volume"] = 3
        s["difficulty"] = "hard"
        settings_mod.save(s, self.path)
        s2 = settings_mod.load(self.path)
        self.assertEqual(s2, s)

    def test_cycle_lang(self):
        s = {"lang": "zh"}
        settings_mod.cycle_lang(s)
        self.assertEqual(s["lang"], "en")

    def test_toggle_sound(self):
        s = {"sound": True}
        settings_mod.toggle_sound(s)
        self.assertFalse(s["sound"])

    def test_cycle_volume(self):
        s = {"volume": 1}
        for expected in (2, 3, 0, 1):
            settings_mod.cycle_volume(s)
            self.assertEqual(s["volume"], expected)

    def test_cycle_difficulty(self):
        s = {"difficulty": "easy"}
        for expected in ("normal", "hard", "easy"):
            settings_mod.cycle_difficulty(s)
            self.assertEqual(s["difficulty"], expected)

    def test_invalid_lang_resets(self):
        s = settings_mod.load(self.path)
        s["lang"] = "fr"
        settings_mod.save(s, self.path)
        s2 = settings_mod.load(self.path)
        self.assertEqual(s2["lang"], "zh")


class TestScore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = Path(self.tmp) / "sc.json"

    def test_empty(self):
        self.assertEqual(score_mod.load(self.path), [])

    def test_add(self):
        score_mod.add("Alice", 100, "normal", self.path)
        scores = score_mod.load(self.path)
        self.assertEqual(scores[0]["name"], "Alice")
        self.assertEqual(scores[0]["score"], 100)

    def test_sorted(self):
        score_mod.add("A", 50, "easy", self.path)
        score_mod.add("B", 200, "hard", self.path)
        score_mod.add("C", 100, "normal", self.path)
        scores = score_mod.load(self.path)
        self.assertEqual([s["name"] for s in scores], ["B", "C", "A"])

    def test_max_10(self):
        for i in range(15):
            score_mod.add(f"P{i}", i * 10, "normal", self.path)
        scores = score_mod.load(self.path)
        self.assertEqual(len(scores), 10)

    def test_empty_name(self):
        score_mod.add("", 50, "normal", self.path)
        scores = score_mod.load(self.path)
        self.assertEqual(scores[0]["name"], "anon")


class TestSound(unittest.TestCase):
    def _make(self, **kw):
        self.buf = []

        class Out:
            def write(_self, s): self.buf.append(s)
            def flush(_self): pass

        kw.setdefault("output", Out())
        kw.setdefault("volume", 1)
        kw.setdefault("enabled", True)
        return Sound(**kw)

    def test_correct(self):
        self._make().correct()
        self.assertEqual(self.buf, ["\a"])

    def test_incorrect(self):
        self._make().incorrect()
        self.assertEqual(self.buf, ["\a\a"])

    def test_win(self):
        self._make().win()
        self.assertEqual(self.buf, ["\a\a\a"])

    def test_lose(self):
        self._make().lose()
        self.assertEqual(self.buf, ["\a\a"])

    def test_disabled(self):
        self._make(enabled=False).correct()
        self.assertEqual(self.buf, [])

    def test_volume_zero(self):
        self._make(volume=0).correct()
        self.assertEqual(self.buf, [])

    def test_volume_multiplies(self):
        self._make(volume=3).correct()
        self.assertEqual(self.buf, ["\a\a\a"])


if __name__ == "__main__":
    unittest.main()
