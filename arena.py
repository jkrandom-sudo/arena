"""Arena Combat — core combat logic.

Turn-based RPG battle: Hero fights monsters, gains XP, levels up.
"""
import random
from typing import Dict, List, Optional, Tuple


# ---------- Heroes ----------

HERO_BASE_HP = 100
HERO_BASE_ATK = 10
HERO_BASE_DEF = 5
HP_PER_LEVEL = 10
ATK_PER_LEVEL = 2
DEF_PER_LEVEL = 1
XP_PER_LEVEL_BASE = 10

HEAL_AMOUNT_FRAC = 0.30
MAX_HEALS_PER_BATTLE = 2
SPECIAL_DAMAGE_FRAC = 0.25  # self-damage as fraction of max_HP


class Hero:
    def __init__(self, difficulty: str = "normal"):
        self.level = 1
        self.xp = 0
        self.max_hp = HERO_BASE_HP
        self.base_atk = HERO_BASE_ATK
        self.base_def = HERO_BASE_DEF
        self.difficulty = difficulty
        if difficulty == "easy":
            self.max_hp = int(self.max_hp * 1.5)
        self.hp = self.max_hp
        self.heals_left = MAX_HEALS_PER_BATTLE
        if difficulty == "hard":
            self.heals_left = 1
        self.defending = False

    def attack_power(self, rng=None) -> int:
        if rng is None:
            rng = random.Random()
        return max(1, rng.randint(self.base_atk, int(self.base_atk * 1.5)))

    def special_power(self, rng=None) -> int:
        if rng is None:
            rng = random.Random()
        return max(1, rng.randint(self.base_atk * 2, self.base_atk * 3))

    def take_damage(self, dmg: int) -> int:
        if self.defending:
            dmg = max(1, dmg // 2)
        actual = max(0, dmg - self.base_def)
        self.hp = max(0, self.hp - actual)
        self.defending = False
        return actual

    def heal(self) -> int:
        if self.heals_left <= 0:
            return 0
        amount = int(self.max_hp * HEAL_AMOUNT_FRAC)
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        self.heals_left -= 1
        return self.hp - old

    def special_self_damage(self) -> int:
        amount = int(self.max_hp * SPECIAL_DAMAGE_FRAC)
        self.hp = max(0, self.hp - amount)
        return amount

    def xp_to_next(self) -> int:
        return XP_PER_LEVEL_BASE * self.level

    def add_xp(self, amount: int) -> int:
        """Add XP, return number of level-ups gained."""
        self.xp += amount
        levels_gained = 0
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level += 1
            self.max_hp += HP_PER_LEVEL
            self.hp = min(self.hp + HP_PER_LEVEL, self.max_hp)
            self.base_atk += ATK_PER_LEVEL
            self.base_def += DEF_PER_LEVEL
            levels_gained += 1
        return levels_gained

    def reset_battle(self):
        self.heals_left = (1 if self.difficulty == "hard"
                           else MAX_HEALS_PER_BATTLE)
        self.defending = False

    def heal_to_full(self):
        self.hp = self.max_hp

    @property
    def alive(self) -> bool:
        return self.hp > 0


# ---------- Monsters ----------

MONSTERS = [
    {"name_zh": "史莱姆", "name_en": "Slime",
     "hp": 20, "atk": 5, "def": 1, "xp": 5},
    {"name_zh": "哥布林", "name_en": "Goblin",
     "hp": 35, "atk": 8, "def": 2, "xp": 10},
    {"name_zh": "野狼",   "name_en": "Wolf",
     "hp": 40, "atk": 12, "def": 3, "xp": 15},
    {"name_zh": "骷髅",   "name_en": "Skeleton",
     "hp": 55, "atk": 15, "def": 5, "xp": 25},
    {"name_zh": "巨魔",   "name_en": "Troll",
     "hp": 80, "atk": 18, "def": 8, "xp": 40},
    {"name_zh": "巨龙",   "name_en": "Dragon",
     "hp": 150, "atk": 25, "def": 12, "xp": 100},
]


class Monster:
    def __init__(self, template: dict, difficulty: str = "normal",
                 lang: str = "en"):
        self.template = template
        self.name = template[f"name_{lang}"] if f"name_{lang}" in template \
                    else template.get("name_en", "Monster")
        self.max_hp = template["hp"]
        self.atk = template["atk"]
        self.defense = template["def"]
        self.xp_reward = template["xp"]
        if difficulty == "easy":
            self.max_hp = int(self.max_hp * 0.8)
            self.atk = max(1, int(self.atk * 0.8))
            self.defense = max(0, int(self.defense * 0.8))
        elif difficulty == "hard":
            self.max_hp = int(self.max_hp * 1.3)
            self.atk = int(self.atk * 1.3)
            self.defense = int(self.defense * 1.3)
        self.hp = self.max_hp
        self.defending = False

    def attack_power(self, rng=None) -> int:
        if rng is None:
            rng = random.Random()
        return max(1, rng.randint(self.atk, int(self.atk * 1.3)))

    def take_damage(self, dmg: int) -> int:
        if self.defending:
            dmg = max(1, dmg // 2)
        actual = max(0, dmg - self.defense)
        self.hp = max(0, self.hp - actual)
        self.defending = False
        return actual

    @property
    def alive(self) -> bool:
        return self.hp > 0


def pick_monster(wave: int, difficulty: str = "normal",
                 lang: str = "en") -> Monster:
    """Choose a monster from MONSTERS based on wave number."""
    # First waves: weaker monsters; later waves: include stronger ones
    available = MONSTERS[: min(len(MONSTERS), max(1, (wave + 1) // 2))]
    # Final boss every 5th wave
    if wave > 0 and wave % 5 == 0:
        template = MONSTERS[-1]
    else:
        idx = (wave - 1) % len(available)
        template = available[idx]
    return Monster(template, difficulty=difficulty, lang=lang)


def monster_decide(monster: Monster, hero: Hero, rng=None) -> str:
    if rng is None:
        rng = random.Random()
    r = rng.random()
    # If monster is weak, more likely to defend
    if monster.hp < monster.max_hp * 0.3 and r < 0.30:
        return "defend"
    if r < 0.10:
        return "special"
    return "attack"


# ---------- Score ----------

DIFFICULTY_BONUS = {"easy": 1, "normal": 2, "hard": 3}


def calc_score(total_xp: int, waves_cleared: int,
               difficulty: str = "normal") -> int:
    bonus = DIFFICULTY_BONUS.get(difficulty, 1)
    return (total_xp + waves_cleared * 5) * bonus
