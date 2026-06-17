# Arena Combat / 竞技场战斗

A turn-based RPG console battler. Play as a hero, fight wave after wave of monsters, gain XP, level up, and survive as long as you can.

## Features

- **Turn-based combat** with five action types: attack, special attack, heal, defend, flee
- **Six monster types** ranging from Slime to Dragon, with bosses every 5 waves
- **Leveling system** — hero gains HP, attack, and defense each level-up
- **Three difficulty levels** affecting hero stats, monster strength, and score multiplier
- **Bilingual UI** (Chinese / English)
- **Persistent leaderboard** (top 10)
- **Terminal bell sound effects** (configurable on/off, volume 0-3)
- **Pure Python standard library** — no extra packages

## Quick Start

```bash
python3 game.py
```

## Combat Actions

| Key | Action  | Effect                                                   |
|-----|---------|----------------------------------------------------------|
| `a` | Attack  | Deal 1.0×–1.5× base attack damage                        |
| `s` | Special | Deal 2×–3× attack damage, but take 25% self-damage       |
| `h` | Heal    | Restore 30% of max HP (limited charges per battle)       |
| `d` | Defend  | Halve incoming damage on the monster's next turn         |
| `f` | Flee    | 50% chance to escape and end the run                     |
| `q` | Quit    | Abandon and return to menu                               |

## Difficulty

| Level   | Hero HP | Heals | Monster stats | Score multiplier |
|---------|---------|-------|---------------|------------------|
| easy    | 1.5×    | 2     | 0.8×          | ×1               |
| normal  | 1.0×    | 2     | 1.0×          | ×2               |
| hard    | 1.0×    | 1     | 1.3×          | ×3               |

## Score Formula

```
score = (total_xp + waves_cleared × 5) × difficulty_bonus
```

## Project Structure

```
arena/
├── game.py        # Main menu, battle loop
├── arena.py       # Hero, Monster, combat math, scoring
├── i18n.py        # Bilingual strings
├── settings.py    # Persistent settings
├── score.py       # Persistent leaderboard
├── sound.py       # Terminal bell sound effects
└── tests/
    ├── test_arena.py
    ├── test_modules.py
    └── test_game.py
```

## Running Tests

```bash
python3 tests/run_tests.py
```
