"""Tests for the core arena module: Hero, Monster, scoring."""
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import arena


class FixedRng:
    """Random stub that returns predictable sequences."""
    def __init__(self, ints=None, floats=None):
        self.ints = list(ints or [])
        self.floats = list(floats or [])
        self.i = 0
        self.fi = 0

    def randint(self, a, b):
        if self.i >= len(self.ints):
            return a
        v = self.ints[self.i]
        self.i += 1
        return v

    def random(self):
        if self.fi >= len(self.floats):
            return 0.5
        v = self.floats[self.fi]
        self.fi += 1
        return v

    def choice(self, seq):
        return seq[0]


class TestHero(unittest.TestCase):
    def test_default_init(self):
        h = arena.Hero()
        self.assertEqual(h.level, 1)
        self.assertEqual(h.xp, 0)
        self.assertEqual(h.hp, h.max_hp)
        self.assertTrue(h.alive)

    def test_easy_more_hp(self):
        h_easy = arena.Hero(difficulty="easy")
        h_normal = arena.Hero(difficulty="normal")
        self.assertGreater(h_easy.max_hp, h_normal.max_hp)

    def test_hard_fewer_heals(self):
        h_hard = arena.Hero(difficulty="hard")
        h_normal = arena.Hero(difficulty="normal")
        self.assertLess(h_hard.heals_left, h_normal.heals_left)

    def test_attack_in_range(self):
        h = arena.Hero()
        for _ in range(20):
            dmg = h.attack_power()
            self.assertGreaterEqual(dmg, h.base_atk)
            self.assertLessEqual(dmg, int(h.base_atk * 1.5))

    def test_special_higher_than_attack(self):
        h = arena.Hero()
        rng = FixedRng(ints=[h.base_atk * 2, h.base_atk * 3])
        # Use deterministic rng for both
        atk = h.attack_power(FixedRng(ints=[h.base_atk]))
        spec = h.special_power(FixedRng(ints=[h.base_atk * 2]))
        self.assertGreater(spec, atk)

    def test_take_damage_reduces_by_def(self):
        h = arena.Hero()
        before = h.hp
        actual = h.take_damage(10)
        self.assertEqual(actual, max(0, 10 - h.base_def))
        self.assertEqual(h.hp, before - actual)

    def test_take_damage_defending_halves(self):
        h = arena.Hero()
        h.defending = True
        before = h.hp
        actual = h.take_damage(20)
        # 20 / 2 = 10, then -def(5) = 5
        self.assertEqual(actual, max(0, 10 - h.base_def))
        # defending consumed
        self.assertFalse(h.defending)

    def test_take_damage_min_zero(self):
        h = arena.Hero()
        actual = h.take_damage(1)  # less than def
        self.assertEqual(actual, 0)

    def test_heal_increases_hp(self):
        h = arena.Hero()
        h.hp = 50
        healed = h.heal()
        self.assertGreater(healed, 0)
        self.assertLessEqual(h.hp, h.max_hp)
        self.assertEqual(h.heals_left, arena.MAX_HEALS_PER_BATTLE - 1)

    def test_heal_when_no_charges(self):
        h = arena.Hero()
        h.heals_left = 0
        h.hp = 50
        healed = h.heal()
        self.assertEqual(healed, 0)

    def test_heal_capped_at_max(self):
        h = arena.Hero()
        h.hp = h.max_hp - 1
        h.heal()
        self.assertEqual(h.hp, h.max_hp)

    def test_special_self_damage(self):
        h = arena.Hero()
        before = h.hp
        dmg = h.special_self_damage()
        self.assertEqual(dmg, int(h.max_hp * arena.SPECIAL_DAMAGE_FRAC))
        self.assertEqual(h.hp, before - dmg)

    def test_xp_levels_up(self):
        h = arena.Hero()
        levels = h.add_xp(h.xp_to_next())
        self.assertEqual(levels, 1)
        self.assertEqual(h.level, 2)

    def test_xp_no_level(self):
        h = arena.Hero()
        levels = h.add_xp(h.xp_to_next() - 1)
        self.assertEqual(levels, 0)
        self.assertEqual(h.level, 1)

    def test_xp_double_level(self):
        h = arena.Hero()
        # Pass enough XP for two levels
        # Lv1->Lv2 needs 10. Lv2->Lv3 needs 20. Total 30.
        levels = h.add_xp(30)
        self.assertEqual(levels, 2)
        self.assertEqual(h.level, 3)

    def test_level_up_increases_stats(self):
        h = arena.Hero()
        atk0 = h.base_atk
        def0 = h.base_def
        max_hp0 = h.max_hp
        h.add_xp(h.xp_to_next())
        self.assertEqual(h.base_atk, atk0 + arena.ATK_PER_LEVEL)
        self.assertEqual(h.base_def, def0 + arena.DEF_PER_LEVEL)
        self.assertEqual(h.max_hp, max_hp0 + arena.HP_PER_LEVEL)

    def test_reset_battle(self):
        h = arena.Hero()
        h.heals_left = 0
        h.defending = True
        h.reset_battle()
        self.assertEqual(h.heals_left, arena.MAX_HEALS_PER_BATTLE)
        self.assertFalse(h.defending)

    def test_reset_battle_hard(self):
        h = arena.Hero(difficulty="hard")
        h.heals_left = 0
        h.reset_battle()
        self.assertEqual(h.heals_left, 1)

    def test_alive(self):
        h = arena.Hero()
        self.assertTrue(h.alive)
        h.hp = 0
        self.assertFalse(h.alive)


class TestMonster(unittest.TestCase):
    def test_creation(self):
        m = arena.Monster(arena.MONSTERS[0], lang="en")
        self.assertEqual(m.name, "Slime")
        self.assertEqual(m.hp, m.max_hp)
        self.assertTrue(m.alive)

    def test_lang_zh(self):
        m = arena.Monster(arena.MONSTERS[0], lang="zh")
        self.assertEqual(m.name, "史莱姆")

    def test_easy_weakens(self):
        m_easy = arena.Monster(arena.MONSTERS[2], difficulty="easy")
        m_norm = arena.Monster(arena.MONSTERS[2], difficulty="normal")
        self.assertLessEqual(m_easy.max_hp, m_norm.max_hp)
        self.assertLessEqual(m_easy.atk, m_norm.atk)

    def test_hard_strengthens(self):
        m_hard = arena.Monster(arena.MONSTERS[2], difficulty="hard")
        m_norm = arena.Monster(arena.MONSTERS[2], difficulty="normal")
        self.assertGreater(m_hard.max_hp, m_norm.max_hp)
        self.assertGreater(m_hard.atk, m_norm.atk)

    def test_take_damage(self):
        m = arena.Monster(arena.MONSTERS[2])
        before = m.hp
        actual = m.take_damage(20)
        self.assertEqual(m.hp, before - actual)

    def test_take_damage_defending(self):
        m = arena.Monster(arena.MONSTERS[2])
        m.defending = True
        m.take_damage(20)
        self.assertFalse(m.defending)

    def test_attack_in_range(self):
        m = arena.Monster(arena.MONSTERS[2])
        for _ in range(20):
            dmg = m.attack_power()
            self.assertGreaterEqual(dmg, m.atk)
            self.assertLessEqual(dmg, int(m.atk * 1.3))


class TestPickMonster(unittest.TestCase):
    def test_wave_1_slime(self):
        m = arena.pick_monster(1, lang="en")
        self.assertEqual(m.name, "Slime")

    def test_boss_every_5(self):
        m = arena.pick_monster(5, lang="en")
        self.assertEqual(m.name, "Dragon")
        m = arena.pick_monster(10, lang="en")
        self.assertEqual(m.name, "Dragon")

    def test_later_waves_progress(self):
        # Wave 9 should be a non-boss tougher than wave 1
        m1 = arena.pick_monster(1, lang="en")
        m9 = arena.pick_monster(9, lang="en")
        # Dragon-only at wave 5/10 etc., wave 9 should be other
        self.assertNotEqual(m9.name, m1.name)

    def test_lang_passed(self):
        m = arena.pick_monster(1, lang="zh")
        self.assertEqual(m.name, "史莱姆")


class TestMonsterDecide(unittest.TestCase):
    def test_low_hp_more_defend(self):
        m = arena.Monster(arena.MONSTERS[2])
        m.hp = 1  # very low
        h = arena.Hero()
        rng = FixedRng(floats=[0.05])
        action = arena.monster_decide(m, h, rng)
        self.assertEqual(action, "defend")

    def test_default_attack(self):
        m = arena.Monster(arena.MONSTERS[2])
        h = arena.Hero()
        rng = FixedRng(floats=[0.5])  # > 0.10
        action = arena.monster_decide(m, h, rng)
        self.assertEqual(action, "attack")

    def test_special_chance(self):
        m = arena.Monster(arena.MONSTERS[2])
        h = arena.Hero()
        rng = FixedRng(floats=[0.05])
        action = arena.monster_decide(m, h, rng)
        self.assertEqual(action, "special")


class TestCalcScore(unittest.TestCase):
    def test_basic(self):
        s = arena.calc_score(50, 3, "normal")
        # (50 + 15) * 2 = 130
        self.assertEqual(s, 130)

    def test_difficulty_scales(self):
        s_easy = arena.calc_score(50, 3, "easy")
        s_hard = arena.calc_score(50, 3, "hard")
        self.assertGreater(s_hard, s_easy)

    def test_unknown_difficulty(self):
        s = arena.calc_score(10, 1, "weird")
        # bonus defaults to 1: (10 + 5) * 1 = 15
        self.assertEqual(s, 15)


if __name__ == "__main__":
    unittest.main()
