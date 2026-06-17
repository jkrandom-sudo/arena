"""Bilingual strings."""

STRINGS = {
    "zh": {
        "title": "竞技场 / Arena Combat",
        "menu_play": "p) 进入竞技场",
        "menu_help": "h) 帮助",
        "menu_scores": "l) 排行榜",
        "menu_settings": "s) 设置",
        "menu_quit": "q) 退出",
        "menu_choice": "请选择 > ",
        "bye": "再见!",
        "unknown": "未知选项: {choice}",
        "help_title": "帮助",
        "help_body": (
            "竞技场战斗: 你扮演英雄, 与各种怪物战斗。\n"
            "每场战斗你的行动:\n"
            "  a = 普通攻击 (造成 1x-1.5x 攻击力的伤害)\n"
            "  s = 重击 (造成 2x-3x 攻击力的伤害, 但自伤 25% 血量)\n"
            "  h = 治疗 (恢复 30% 血量, 每场限 {heals} 次)\n"
            "  d = 防御 (本回合伤害减半)\n"
            "  f = 逃跑 (50% 几率成功)\n"
            "击败怪物获得经验值, 升级后属性提升!\n"
            "难度影响怪物强度和奖励倍数。"
        ),
        "press_enter": "按回车继续...",
        "settings_title": "设置",
        "settings_lang": "1) 语言: {value}",
        "settings_sound": "2) 声音: {value}",
        "settings_volume": "3) 音量: {value}",
        "settings_difficulty": "4) 难度: {value}",
        "settings_back": "b) 返回",
        "scores_title": "排行榜 (Top 10)",
        "scores_empty": "暂无成绩",
        "scores_row": "{rank:>2}. {name:<12} {score:>4} 分  ({difficulty})",
        "name_prompt": "姓名(空= 不保存): ",
        "round_intro": "第 {wave} 波! 一只 {monster} 出现了!",
        "hero_status": ("英雄 Lv.{lvl} | HP: {hp}/{max_hp} | "
                        "经验: {xp}/{next}"),
        "monster_status": "{name} | HP: {hp}/{max_hp}",
        "battle_menu": ("a)攻击  s)重击  h)治疗({heals})  "
                        "d)防御  f)逃跑"),
        "action_attack": "⚔ 你攻击了 {monster}，造成 {dmg} 点伤害!",
        "action_special": ("💥 你发动重击! {monster} 受到 {dmg} 点伤害，"
                           "但你自伤了 {self_dmg} 点!"),
        "action_heal": "💚 你恢复了 {healed} 点生命值。",
        "action_defend": "🛡 你进入防御姿态。",
        "action_flee_success": "🏃 你成功逃跑了!",
        "action_flee_fail": "💨 逃跑失败!",
        "monster_attack": "👊 {monster} 攻击了你，造成 {dmg} 点伤害!",
        "monster_defend": "🛡 {monster} 进入防御姿态。",
        "monster_special": "🔥 {monster} 发动猛烈攻击! 你受到 {dmg} 点伤害!",
        "battle_win": "🎉 胜利! 你击败了 {monster}!",
        "battle_lose": "💀 你被 {monster} 击败了...",
        "xp_gained": "获得 {xp} 经验值!",
        "level_up": "⬆ 升级! 你达到了 Lv.{lvl}!",
        "no_heals": "治疗次数已用尽!",
        "score_earned": "本次得分: {score}",
        "monster_names": "史莱姆,哥布林,野狼,骷髅,巨魔,巨龙",
        "diff_easy": "简单",
        "diff_normal": "普通",
        "diff_hard": "困难",
        "lang_zh": "中文",
        "lang_en": "英文",
        "on": "开",
        "off": "关",
    },
    "en": {
        "title": "Arena Combat",
        "menu_play": "p) Enter the Arena",
        "menu_help": "h) Help",
        "menu_scores": "l) Leaderboard",
        "menu_settings": "s) Settings",
        "menu_quit": "q) Quit",
        "menu_choice": "Choose > ",
        "bye": "Bye!",
        "unknown": "Unknown option: {choice}",
        "help_title": "Help",
        "help_body": (
            "Arena Combat: Play as a hero fighting monsters turn by turn.\n"
            "Each battle you can:\n"
            "  a = Attack (1x-1.5x base attack damage)\n"
            "  s = Special (2x-3x attack damage, but 25% self-damage)\n"
            "  h = Heal (restore 30% HP, {heals} per battle)\n"
            "  d = Defend (halve incoming damage this turn)\n"
            "  f = Flee (50% chance)\n"
            "Defeat monsters for XP, level up to grow stronger!\n"
            "Difficulty affects monster stats and score multiplier."
        ),
        "press_enter": "Press Enter to continue...",
        "settings_title": "Settings",
        "settings_lang": "1) Language: {value}",
        "settings_sound": "2) Sound: {value}",
        "settings_volume": "3) Volume: {value}",
        "settings_difficulty": "4) Difficulty: {value}",
        "settings_back": "b) Back",
        "scores_title": "Leaderboard (Top 10)",
        "scores_empty": "No scores yet",
        "scores_row": "{rank:>2}. {name:<12} {score:>4} pts  ({difficulty})",
        "name_prompt": "Name (empty = skip save): ",
        "round_intro": "Wave {wave}! A {monster} appears!",
        "hero_status": ("Hero Lv.{lvl} | HP: {hp}/{max_hp} | "
                        "XP: {xp}/{next}"),
        "monster_status": "{name} | HP: {hp}/{max_hp}",
        "battle_menu": ("a)Attack  s)Special  h)Heal({heals})  "
                        "d)Defend  f)Flee"),
        "action_attack": "⚔ You attacked {monster} for {dmg} damage!",
        "action_special": ("💥 Special attack! {monster} took {dmg} damage, "
                           "but you took {self_dmg} self-damage!"),
        "action_heal": "💚 You recovered {healed} HP.",
        "action_defend": "🛡 You take a defensive stance.",
        "action_flee_success": "🏃 You fled successfully!",
        "action_flee_fail": "💨 Flee failed!",
        "monster_attack": "👊 {monster} attacks you for {dmg} damage!",
        "monster_defend": "🛡 {monster} takes a defensive stance.",
        "monster_special": ("🔥 {monster} unleashes a fierce attack! "
                            "You take {dmg} damage!"),
        "battle_win": "🎉 Victory! You defeated {monster}!",
        "battle_lose": "💀 You were defeated by {monster}...",
        "xp_gained": "Gained {xp} XP!",
        "level_up": "⬆ Level Up! You are now Lv.{lvl}!",
        "no_heals": "No heals remaining!",
        "score_earned": "Score: {score}",
        "monster_names": "Slime,Goblin,Wolf,Skeleton,Troll,Dragon",
        "diff_easy": "easy",
        "diff_normal": "normal",
        "diff_hard": "hard",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "on": "on",
        "off": "off",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang) or STRINGS["en"]
    s = table.get(key)
    if s is None:
        s = STRINGS["en"].get(key, key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s