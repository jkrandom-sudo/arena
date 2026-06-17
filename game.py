"""Arena Combat — main menu, battle loop."""
import random
import sys
from typing import Optional

import arena
import score as score_mod
import settings as settings_mod
from i18n import t
from sound import Sound


class QuitGame(Exception):
    pass


def render_status(hero: arena.Hero, monster: arena.Monster,
                   lang: str, output) -> None:
    output.write(t(lang, "hero_status",
                    lvl=hero.level, hp=hero.hp, max_hp=hero.max_hp,
                    xp=hero.xp, next=hero.xp_to_next()) + "\n")
    output.write(t(lang, "monster_status",
                    name=monster.name, hp=monster.hp,
                    max_hp=monster.max_hp) + "\n")


def fight(hero: arena.Hero, monster: arena.Monster,
          input_func, output, lang: str, sound: Sound,
          rng=None) -> str:
    """Run a battle. Returns 'win', 'lose', or 'flee'."""
    if rng is None:
        rng = random.Random()
    hero.reset_battle()

    while hero.alive and monster.alive:
        output.write("\n")
        render_status(hero, monster, lang, output)
        output.write(t(lang, "battle_menu",
                        heals=hero.heals_left) + "\n")
        try:
            choice = input_func("> ").strip().lower()
        except EOFError:
            raise QuitGame()
        if choice == "q":
            raise QuitGame()
        if choice == "a":
            dmg = hero.attack_power(rng)
            actual = monster.take_damage(dmg)
            output.write(t(lang, "action_attack",
                            monster=monster.name, dmg=actual) + "\n")
            sound.correct()
        elif choice == "s":
            dmg = hero.special_power(rng)
            actual = monster.take_damage(dmg)
            self_dmg = hero.special_self_damage()
            output.write(t(lang, "action_special",
                            monster=monster.name, dmg=actual,
                            self_dmg=self_dmg) + "\n")
            sound.correct()
        elif choice == "h":
            healed = hero.heal()
            if healed <= 0:
                output.write(t(lang, "no_heals") + "\n")
                sound.incorrect()
                continue
            output.write(t(lang, "action_heal", healed=healed) + "\n")
            sound.correct()
        elif choice == "d":
            hero.defending = True
            output.write(t(lang, "action_defend") + "\n")
        elif choice == "f":
            if rng.random() < 0.5:
                output.write(t(lang, "action_flee_success") + "\n")
                return "flee"
            output.write(t(lang, "action_flee_fail") + "\n")
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")
            continue

        if not monster.alive:
            break

        # Monster turn
        action = arena.monster_decide(monster, hero, rng)
        if action == "attack":
            dmg = monster.attack_power(rng)
            actual = hero.take_damage(dmg)
            output.write(t(lang, "monster_attack",
                            monster=monster.name, dmg=actual) + "\n")
        elif action == "special":
            dmg = int(monster.attack_power(rng) * 1.5)
            actual = hero.take_damage(dmg)
            output.write(t(lang, "monster_special",
                            monster=monster.name, dmg=actual) + "\n")
        elif action == "defend":
            monster.defending = True
            output.write(t(lang, "monster_defend",
                            monster=monster.name) + "\n")

    if hero.alive:
        sound.win()
        return "win"
    sound.lose()
    return "lose"


def play_arena(s: dict, sound: Sound, input_func, output,
                rng=None) -> Optional[dict]:
    if rng is None:
        rng = random.Random()
    lang = s.get("lang", "zh")
    difficulty = s.get("difficulty", "normal")

    hero = arena.Hero(difficulty=difficulty)
    total_xp = 0
    wave = 0

    while True:
        wave += 1
        monster = arena.pick_monster(wave, difficulty=difficulty,
                                       lang=lang)
        output.write("\n--- " + t(lang, "round_intro",
                                    wave=wave, monster=monster.name)
                     + " ---\n")

        result = fight(hero, monster, input_func, output, lang,
                        sound, rng)

        if result == "win":
            output.write(t(lang, "battle_win",
                            monster=monster.name) + "\n")
            xp = monster.xp_reward
            total_xp += xp
            output.write(t(lang, "xp_gained", xp=xp) + "\n")
            levels = hero.add_xp(xp)
            for _ in range(levels):
                output.write(t(lang, "level_up", lvl=hero.level) + "\n")
        elif result == "flee":
            break
        else:
            output.write(t(lang, "battle_lose",
                            monster=monster.name) + "\n")
            break

    waves_cleared = wave - 1 if (not hero.alive or result == "flee") else wave
    if result == "win":
        waves_cleared = wave
    elif result == "flee":
        waves_cleared = wave - 1
    else:
        waves_cleared = wave - 1
    score = arena.calc_score(total_xp, waves_cleared, difficulty)
    output.write("\n" + t(lang, "score_earned", score=score) + "\n")
    return {"result": result, "score": score, "waves": waves_cleared,
            "xp": total_xp, "difficulty": difficulty,
            "level": hero.level}


def show_help(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    output.write("\n=== " + t(lang, "help_title") + " ===\n")
    output.write(t(lang, "help_body",
                    heals=arena.MAX_HEALS_PER_BATTLE) + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def show_scores(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    scores = score_mod.load()
    output.write("\n=== " + t(lang, "scores_title") + " ===\n")
    if not scores:
        output.write(t(lang, "scores_empty") + "\n")
    else:
        for i, e in enumerate(scores, 1):
            output.write(t(
                lang, "scores_row",
                rank=i, name=e.get("name", "")[:12],
                score=e.get("score", 0),
                difficulty=t(lang, f"diff_{e.get('difficulty', 'normal')}"),
            ) + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def settings_menu(s: dict, input_func, output) -> dict:
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "settings_title") + " ===\n")
        output.write(t(lang, "settings_lang",
                       value=t(lang, f"lang_{lang}")) + "\n")
        output.write(t(lang, "settings_sound",
                       value=t(lang, "on" if s.get("sound") else "off"))
                     + "\n")
        output.write(t(lang, "settings_volume",
                       value=s.get("volume", 1)) + "\n")
        output.write(t(lang, "settings_difficulty",
                       value=t(lang,
                               f"diff_{s.get('difficulty', 'normal')}"))
                     + "\n")
        output.write(t(lang, "settings_back") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            break
        if choice == "1":
            settings_mod.cycle_lang(s)
        elif choice == "2":
            settings_mod.toggle_sound(s)
        elif choice == "3":
            settings_mod.cycle_volume(s)
        elif choice == "4":
            settings_mod.cycle_difficulty(s)
        elif choice == "b":
            break
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")
    settings_mod.save(s)
    return s


def main_menu(input_func=None, output=None, rng=None) -> None:
    if input_func is None:
        input_func = input
    if output is None:
        output = sys.stdout
    if rng is None:
        rng = random.Random()
    s = settings_mod.load()
    settings_mod.save(s)
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "title") + " ===\n")
        output.write(t(lang, "menu_play") + "\n")
        output.write(t(lang, "menu_help") + "\n")
        output.write(t(lang, "menu_scores") + "\n")
        output.write(t(lang, "menu_settings") + "\n")
        output.write(t(lang, "menu_quit") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "q":
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "p":
            sound = Sound(enabled=bool(s.get("sound", True)),
                          volume=int(s.get("volume", 1)),
                          output=output)
            try:
                result = play_arena(s, sound, input_func, output, rng=rng)
            except QuitGame:
                output.write(t(lang, "bye") + "\n")
                return
            if result is None:
                continue
            try:
                name = input_func(t(lang, "name_prompt")).strip()
            except EOFError:
                name = ""
            if name and result["score"] > 0:
                score_mod.add(name, result["score"], result["difficulty"])
        elif choice == "h":
            show_help(s, input_func, output)
        elif choice == "l":
            show_scores(s, input_func, output)
        elif choice == "s":
            settings_menu(s, input_func, output)
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
