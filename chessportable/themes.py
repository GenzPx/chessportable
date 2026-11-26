from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class BoardTheme:
    theme_id: str
    name: str
    desc: str
    bg_light: str
    bg_dark: str
    bg_last_light: str
    bg_last_dark: str
    bg_target_light: str
    bg_target_dark: str
    bg_check: str
    fg_white: str
    fg_black: str
    accent: str

THEMES: Tuple[BoardTheme, ...] = (
    BoardTheme(
        theme_id="sage",
        name="Tournament Sage",
        desc="Hijau-krem klasik ala turnamen Lichess/Chess.com",
        bg_light="\033[48;5;180m",
        bg_dark="\033[48;5;108m",
        bg_last_light="\033[48;5;186m",
        bg_last_dark="\033[48;5;143m",
        bg_target_light="\033[48;5;117m",
        bg_target_dark="\033[48;5;74m",
        bg_check="\033[48;5;160m",
        fg_white="\033[1;38;5;231m",
        fg_black="\033[1;38;5;16m",
        accent="\033[96m",
    ),
    BoardTheme(
        theme_id="wood",
        name="Classic Walnut",
        desc="Kayu cokelat hangat khas papan catur kayu",
        bg_light="\033[48;5;222m",
        bg_dark="\033[48;5;137m",
        bg_last_light="\033[48;5;227m",
        bg_last_dark="\033[48;5;178m",
        bg_target_light="\033[48;5;151m",
        bg_target_dark="\033[48;5;108m",
        bg_check="\033[48;5;160m",
        fg_white="\033[1;38;5;231m",
        fg_black="\033[1;38;5;16m",
        accent="\033[93m",
    ),
    BoardTheme(
        theme_id="ocean",
        name="Ocean Slate",
        desc="Biru laut sejuk & kontras tajam di layar AMOLED",
        bg_light="\033[48;5;153m",
        bg_dark="\033[48;5;68m",
        bg_last_light="\033[48;5;195m",
        bg_last_dark="\033[48;5;111m",
        bg_target_light="\033[48;5;157m",
        bg_target_dark="\033[48;5;78m",
        bg_check="\033[48;5;196m",
        fg_white="\033[1;38;5;231m",
        fg_black="\033[1;38;5;16m",
        accent="\033[94m",
    ),
    BoardTheme(
        theme_id="neon",
        name="Midnight Cyber",
        desc="Nuansa ungu-cyan cyberpunk buat Termux dark mode",
        bg_light="\033[48;5;146m",
        bg_dark="\033[48;5;61m",
        bg_last_light="\033[48;5;183m",
        bg_last_dark="\033[48;5;134m",
        bg_target_light="\033[48;5;122m",
        bg_target_dark="\033[48;5;37m",
        bg_check="\033[48;5;197m",
        fg_white="\033[1;38;5;231m",
        fg_black="\033[1;38;5;16m",
        accent="\033[95m",
    ),
    BoardTheme(
        theme_id="crimson",
        name="Crimson Boss",
        desc="Tema merah marun & abu gelap ala Final Boss Jim",
        bg_light="\033[48;5;181m",
        bg_dark="\033[48;5;95m",
        bg_last_light="\033[48;5;216m",
        bg_last_dark="\033[48;5;167m",
        bg_target_light="\033[48;5;222m",
        bg_target_dark="\033[48;5;172m",
        bg_check="\033[48;5;196m",
        fg_white="\033[1;38;5;231m",
        fg_black="\033[1;38;5;16m",
        accent="\033[91m",
    ),
    BoardTheme(
        theme_id="mono",
        name="Slate Mono",
        desc="Minimalis abu terang & gelap, super bersih",
        bg_light="\033[48;5;250m",
        bg_dark="\033[48;5;242m",
        bg_last_light="\033[48;5;229m",
        bg_last_dark="\033[48;5;185m",
        bg_target_light="\033[48;5;152m",
        bg_target_dark="\033[48;5;109m",
        bg_check="\033[48;5;160m",
        fg_white="\033[1;38;5;231m",
        fg_black="\033[1;38;5;16m",
        accent="\033[97m",
    ),
)

THEME_BY_ID: Dict[str, BoardTheme] = {t.theme_id: t for t in THEMES}

def get_theme(theme_id: str) -> BoardTheme:
    return THEME_BY_ID.get(theme_id, THEMES[0])
