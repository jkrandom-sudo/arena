"""Tests for the game flow."""
import io
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import arena
import game
import score as score_mod
import settings as settings_mod


class StackedInput:
    def __init__(self, lines):
        self.lines = list(lines)
        self.idx = 0

    def __call__(self, prompt=""):
        if self.idx >= len(self.lines):
            raise EOFError()
        v = self.lines[self.idx]
        self.idx += 1
        return v


def _stub(**overrides):
    s = {"lang": "en", "sound": False, "volume": 0,
         "difficulty": "normal"}
    s.update(overrides)
    return s


class TestRenderStatus(unittest.TestCase):
    def test_renders(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        out = io.StringIO()
        game.render_status(h, m, "en", out)
        text = out.getvalue()
        self.assertIn("Hero", text)
        self.assertIn("Slime", text)


class TestFight(unittest.TestCase):
    def test_attack_until_win(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")  # Slime, 20 hp
        m.hp = 1  # one-shot it
        sound = mock.MagicMock()
        out = io.StringIO()
        result = game.fight(h, m, StackedInput(["a"]), out, "en",
                              sound, rng=random.Random(0))
        self.assertEqual(result, "win")
        sound.win.assert_called()

    def test_quit_raises(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        sound = mock.MagicMock()
        out = io.StringIO()
        with self.assertRaises(game.QuitGame):
            game.fight(h, m, StackedInput(["q"]), out, "en",
                         sound, rng=random.Random(0))

    def test_eof_raises(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        sound = mock.MagicMock()
        out = io.StringIO()
        with self.assertRaises(game.QuitGame):
            game.fight(h, m, StackedInput([]), out, "en",
                         sound, rng=random.Random(0))

    def test_lose(self):
        h = arena.Hero()
        h.hp = 1
        m = arena.Monster(arena.MONSTERS[5], lang="en")  # Dragon
        sound = mock.MagicMock()
        out = io.StringIO()
        # Force monster attack to deal full damage by mocking decide
        with mock.patch("arena.monster_decide", return_value="attack"):
            result = game.fight(h, m, StackedInput(["d"] * 50), out, "en",
                                  sound, rng=random.Random(42))
        self.assertEqual(result, "lose")
        sound.lose.assert_called()

    def test_flee_success(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[5], lang="en")
        sound = mock.MagicMock()
        out = io.StringIO()
        # rng.random() returns < 0.5 → flee succeeds
        rng = mock.MagicMock()
        rng.random.return_value = 0.1
        rng.randint = lambda a, b: a
        result = game.fight(h, m, StackedInput(["f"]), out, "en",
                              sound, rng=rng)
        self.assertEqual(result, "flee")

    def test_flee_fail_continues(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        m.hp = 1
        sound = mock.MagicMock()
        out = io.StringIO()
        rng = mock.MagicMock()
        # First call (.random()): 0.9 → fail. Then attack lands.
        rng.random.return_value = 0.9
        rng.randint = lambda a, b: b
        # Patch monster_decide to defend (no damage done)
        with mock.patch("arena.monster_decide", return_value="defend"):
            result = game.fight(h, m, StackedInput(["f", "a"]), out, "en",
                                  sound, rng=rng)
        self.assertEqual(result, "win")

    def test_heal(self):
        h = arena.Hero()
        h.hp = 50
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        sound = mock.MagicMock()
        out = io.StringIO()
        # heal then attack to win
        m.hp = 1
        with mock.patch("arena.monster_decide", return_value="defend"):
            game.fight(h, m, StackedInput(["h", "a"]), out, "en",
                         sound, rng=random.Random(0))
        # HP should have increased from 50
        self.assertGreater(h.hp, 50)

    def test_no_heals(self):
        h = arena.Hero()
        h.hp = 50
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        m.hp = 1
        sound = mock.MagicMock()
        out = io.StringIO()
        h.heals_left = 0
        # Need reset_battle to not refill them — we set difficulty to hard
        # Actually reset_battle sets to MAX (or 1 if hard). Let's just
        # test the message appears mid-fight after exhaustion.
        with mock.patch("arena.monster_decide", return_value="defend"):
            # heal twice (uses charges), then again (no charges)
            game.fight(h, m, StackedInput(["h", "h", "h", "a"]), out,
                         "en", sound, rng=random.Random(0))
        self.assertIn("No heals", out.getvalue())

    def test_special_attack(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        m.hp = 100  # tough enough to absorb special
        sound = mock.MagicMock()
        out = io.StringIO()
        # Special then attack to win
        m.hp = 1
        with mock.patch("arena.monster_decide", return_value="defend"):
            game.fight(h, m, StackedInput(["s"]), out, "en",
                         sound, rng=random.Random(0))
        # Should have applied self-damage
        self.assertLess(h.hp, h.max_hp)

    def test_defend_action(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        m.hp = 1
        sound = mock.MagicMock()
        out = io.StringIO()
        with mock.patch("arena.monster_decide", return_value="defend"):
            game.fight(h, m, StackedInput(["d", "a"]), out, "en",
                         sound, rng=random.Random(0))
        self.assertIn("defensive", out.getvalue())

    def test_unknown_action(self):
        h = arena.Hero()
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        m.hp = 1
        sound = mock.MagicMock()
        out = io.StringIO()
        with mock.patch("arena.monster_decide", return_value="defend"):
            game.fight(h, m, StackedInput(["xyz", "a"]), out, "en",
                         sound, rng=random.Random(0))
        self.assertIn("Unknown", out.getvalue())


class TestPlayArena(unittest.TestCase):
    def test_flee_returns_result(self):
        s = _stub()
        sound = mock.MagicMock()
        out = io.StringIO()
        rng = mock.MagicMock()
        rng.random.return_value = 0.1  # flee succeeds
        rng.randint = lambda a, b: a
        result = game.play_arena(s, sound, StackedInput(["f"]), out, rng=rng)
        self.assertIsNotNone(result)
        self.assertEqual(result["result"], "flee")

    def test_quit_propagates(self):
        s = _stub()
        sound = mock.MagicMock()
        out = io.StringIO()
        with self.assertRaises(game.QuitGame):
            game.play_arena(s, sound, StackedInput(["q"]), out,
                              rng=random.Random(0))


class TestShowHelp(unittest.TestCase):
    def test_help(self):
        out = io.StringIO()
        game.show_help(_stub(), StackedInput([""]), out)
        self.assertIn("Help", out.getvalue())


class TestShowScores(unittest.TestCase):
    def test_empty(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(score_mod, "DEFAULT_PATH",
                                     Path(tmp) / "sc.json"):
                game.show_scores(_stub(), StackedInput([""]), out)
        self.assertIn("No scores", out.getvalue())

    def test_with_entries(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(score_mod, "DEFAULT_PATH",
                                     Path(tmp) / "sc.json"):
                score_mod.add("Alice", 100, "normal")
                game.show_scores(_stub(), StackedInput([""]), out)
        self.assertIn("Alice", out.getvalue())


class TestSettingsMenu(unittest.TestCase):
    def test_back(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(settings_mod, "DEFAULT_PATH",
                                     Path(tmp) / "s.json"):
                game.settings_menu(_stub(), StackedInput(["b"]), out)

    def test_cycle_lang(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(settings_mod, "DEFAULT_PATH",
                                     Path(tmp) / "s.json"):
                s = _stub(lang="zh")
                game.settings_menu(s, StackedInput(["1", "b"]), out)
        self.assertEqual(s["lang"], "en")

    def test_unknown(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(settings_mod, "DEFAULT_PATH",
                                     Path(tmp) / "s.json"):
                s = _stub()
                game.settings_menu(s, StackedInput(["xyz", "b"]), out)
        self.assertIn("Unknown", out.getvalue())


class TestMainMenu(unittest.TestCase):
    def _ctx(self, tmp):
        return (mock.patch.object(settings_mod, "DEFAULT_PATH",
                                    Path(tmp) / "s.json"),
                mock.patch.object(score_mod, "DEFAULT_PATH",
                                    Path(tmp) / "sc.json"))

    def test_quit(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput(["q"]), out)
        self.assertIn("Bye", out.getvalue())

    def test_help(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput(["h", "", "q"]), out)
        self.assertIn("Help", out.getvalue())

    def test_play_saves_score(self):
        fake = {"result": "win", "score": 100, "waves": 3,
                "xp": 50, "difficulty": "normal", "level": 2}
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                with mock.patch.object(game, "play_arena",
                                         return_value=fake):
                    game.main_menu(StackedInput(["p", "Bob", "q"]), out)
                scores = score_mod.load()
        self.assertEqual(scores[0]["name"], "Bob")

    def test_play_no_name(self):
        fake = {"result": "win", "score": 100, "waves": 3,
                "xp": 50, "difficulty": "normal", "level": 2}
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                with mock.patch.object(game, "play_arena",
                                         return_value=fake):
                    game.main_menu(StackedInput(["p", "", "q"]), out)
                scores = score_mod.load()
        self.assertEqual(scores, [])

    def test_play_quit_during(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                with mock.patch.object(game, "play_arena",
                                         side_effect=game.QuitGame()):
                    game.main_menu(StackedInput(["p"]), out)
        self.assertIn("Bye", out.getvalue())

    def test_unknown(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput(["x", "q"]), out)
        self.assertIn("Unknown", out.getvalue())

    def test_eof(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput([]), out)
        self.assertIn("Bye", out.getvalue())


if __name__ == "__main__":
    unittest.main()
