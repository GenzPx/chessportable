from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .board import Board, START_FEN, WHITE, move_to_uci
from .bots import BOTS
from .evolving import DEFAULT_BRAIN, DEFAULT_DNA, EvolvingBrain, MatchTracker, PlayerDNA

ACHIEVEMENTS: Dict[str, Tuple[str, str, str]] = {
    "first_blood": ("⚔", "Kemenangan Pertama", "Menangkan pertandingan pertamamu melawan bot."),
    "cat_tamer": ("🐱", "Penjinak Kucing", "Taklukkan Mittens si kucing licik (Elo 1300)."),
    "giant_slayer": ("👑", "Penakluk Master", "Kalahkan bot kelas Master ke atas (Elo 2400+)."),
    "godslayer": ("🔥", "Legenda Baru", "Kalahkan Jim sang penantang puncak (Elo 4000)!"),
    "flawless": ("💎", "Main Sempurna", "Menang dengan akurasi pertandingan minimal 90%."),
    "evo_survivor": ("★", "Rival Tangguh", "Kalahkan lawan adaptif setelah 5 kali pertemuan."),
    "quick_mate": ("⚡", "Skakmat Kilat", "Skakmat lawan dalam 15 langkah atau kurang."),
    "promo_master": ("♛", "Pion Jadi Raja", "Promosikan pion dan menangkan pertandingan."),
    "castle_king": ("🏰", "Benteng Kokoh", "Lakukan rokade dan menangkan pertandingan."),
    "puzzle_10": ("🧩", "Ahli Taktik", "Selesaikan 10 puzzle taktik berbeda."),
    "gauntlet_clear": ("🏆", "Juara Turnamen", "Tamatkan Tantangan Beruntun 10 Bot (Starrys -> Jim)."),
    "collector_all": ("★", "Kolektor Lengkap", "Kalahkan seluruh 20 bot di ChessPortable!"),
}

TIME_CONTROLS: Dict[str, Tuple[str, int, int]] = {
    "unlimited": ("Tanpa Batas Waktu", 0, 0),
    "bullet_1_0": ("Bullet 1+0 (1 menit)", 60, 0),
    "blitz_3_2": ("Blitz 3+2 (3 mnt + 2 dtk)", 180, 2),
    "blitz_5_0": ("Blitz 5+0 (5 menit)", 300, 0),
    "rapid_10_5": ("Rapid 10+5 (10 mnt + 5 dtk)", 600, 5),
}


def data_dir() -> Path:
    custom = os.environ.get("CHESSPORTABLE_HOME")
    base = Path(custom) if custom else Path.home() / ".chessportable"
    base.mkdir(parents=True, exist_ok=True)
    return base

def saves_dir() -> Path:
    d = data_dir() / "saves"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pgn_dir() -> Path:
    d = data_dir() / "pgn"
    d.mkdir(parents=True, exist_ok=True)
    return d


def profile_path() -> Path:
    return data_dir() / "profile.json"

DEFAULT_PROFILE: Dict[str, Any] = {
    "board_style": "unicode",
    "theme": "sage",
    "show_eval": True,
    "show_grades": True,
    "sound_bell": False,
    "time_control": "unlimited",
    "adaptive_elo": 1000,
    "adaptive_peak": 1000,
    "adaptive_stats": {"wins": 0, "losses": 0, "draws": 0},
    "bot_stats": {},
    "bot_adaptive": {},
    "think_override": None,
    "player_dna": DEFAULT_DNA,
    "evolving_brain": DEFAULT_BRAIN,
    "puzzle_rating": 1000,
    "solved_puzzles": [],
    "gauntlet_stage": 0,
    "gauntlet_clears": 0,
    "achievements": [],
}

def load_profile() -> Dict[str, Any]:
    path = profile_path()
    data = json.loads(json.dumps(DEFAULT_PROFILE))
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update(loaded)
        except (OSError, json.JSONDecodeError):
            pass
    for key in ("bot_stats", "bot_adaptive", "adaptive_stats", "player_dna", "evolving_brain"):
        if not isinstance(data.get(key), dict):
            data[key] = json.loads(json.dumps(DEFAULT_PROFILE[key]))
    for key in ("solved_puzzles", "achievements"):
        if not isinstance(data.get(key), list):
            data[key] = []
    return data


def save_profile(profile: Dict[str, Any]) -> None:
    path = profile_path()
    try:
        path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    except OSError:
        pass

def get_dna(profile: Dict[str, Any]) -> PlayerDNA:
    return PlayerDNA(profile.get("player_dna"))

def set_dna(profile: Dict[str, Any], dna: PlayerDNA) -> None:
    profile["player_dna"] = dna.to_dict()


def get_brain(profile: Dict[str, Any]) -> EvolvingBrain:
    return EvolvingBrain(profile.get("evolving_brain"))


def set_brain(profile: Dict[str, Any], brain: EvolvingBrain) -> None:
    profile["evolving_brain"] = brain.to_dict()

def get_bot_adaptive_state(profile: Dict[str, Any], bot_id: str, base_elo: int) -> Dict[str, Any]:

    all_ba = profile.setdefault("bot_adaptive", {})
    st = all_ba.get(bot_id)
    if not isinstance(st, dict):
        st = {
            "elo": int(base_elo),
            "peak_elo": int(base_elo),
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "brain": json.loads(json.dumps(DEFAULT_BRAIN)),
        }
        all_ba[bot_id] = st
    st.setdefault("elo", int(base_elo))
    st.setdefault("peak_elo", int(st["elo"]))
    st.setdefault("wins", 0)
    st.setdefault("losses", 0)
    st.setdefault("draws", 0)
    if not isinstance(st.get("brain"), dict):
        st["brain"] = json.loads(json.dumps(DEFAULT_BRAIN))
    return st


def get_bot_brain(profile: Dict[str, Any], bot_id: str, base_elo: int) -> EvolvingBrain:
    st = get_bot_adaptive_state(profile, bot_id, base_elo)
    return EvolvingBrain(st.get("brain"))


def set_bot_brain(profile: Dict[str, Any], bot_id: str, base_elo: int, brain: EvolvingBrain) -> None:
    st = get_bot_adaptive_state(profile, bot_id, base_elo)
    st["brain"] = brain.to_dict()

def reset_bot_adaptive(profile: Dict[str, Any], bot_id: str, base_elo: int) -> None:
    profile.setdefault("bot_adaptive", {})[bot_id] = {
        "elo": int(base_elo),
        "peak_elo": int(base_elo),
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "brain": json.loads(json.dumps(DEFAULT_BRAIN)),
    }
    save_profile(profile)

def record_per_bot_adaptive_result(
    profile: Dict[str, Any],
    bot_id: str,
    base_elo: int,
    outcome: str,
    new_elo: int,
) -> None:
    st = get_bot_adaptive_state(profile, bot_id, base_elo)
    if outcome == "win":
        st["wins"] = st.get("wins", 0) + 1
    elif outcome == "loss":
        st["losses"] = st.get("losses", 0) + 1
    else:
        st["draws"] = st.get("draws", 0) + 1
    st["elo"] = int(new_elo)
    st["peak_elo"] = max(int(st.get("peak_elo", base_elo)), int(new_elo))

    if outcome == "win":
        bstats = profile.setdefault("bot_stats", {}).setdefault(
            bot_id, {"wins": 0, "losses": 0, "draws": 0}
        )
        bstats["wins"] = bstats.get("wins", 0) + 1
    save_profile(profile)

def unlock_achievement(profile: Dict[str, Any], ach_id: str) -> bool:

    if ach_id not in ACHIEVEMENTS:
        return False
    owned = profile.setdefault("achievements", [])
    if ach_id in owned:
        return False
    owned.append(ach_id)
    save_profile(profile)
    return True

def check_match_achievements(
    profile: Dict[str, Any],
    outcome: str,
    bot_id: str,
    bot_elo: int,
    is_adaptive: bool,
    generation: int,
    tracker: MatchTracker,
    total_plies: int,
) -> List[str]:

    newly: List[str] = []
    if outcome == "win":
        if unlock_achievement(profile, "first_blood"):
            newly.append("first_blood")
        if "mittens" in bot_id:
            if unlock_achievement(profile, "cat_tamer"):
                newly.append("cat_tamer")
        if bot_elo >= 2400:
            if unlock_achievement(profile, "giant_slayer"):
                newly.append("giant_slayer")
        if "jim" in bot_id or bot_elo >= 3800:
            if unlock_achievement(profile, "godslayer"):
                newly.append("godslayer")
        if tracker.accuracy_percent() >= 90.0 and len(tracker.player_moves) >= 8 and tracker.undo_count == 0:
            if unlock_achievement(profile, "flawless"):
                newly.append("flawless")
        if is_adaptive and generation >= 5:
            if unlock_achievement(profile, "evo_survivor"):
                newly.append("evo_survivor")
        if total_plies <= 30 and total_plies >= 4:
            if unlock_achievement(profile, "quick_mate"):
                newly.append("quick_mate")
        if tracker.used_promo:
            if unlock_achievement(profile, "promo_master"):
                newly.append("promo_master")
        if tracker.used_castle:
            if unlock_achievement(profile, "castle_king"):
                newly.append("castle_king")
        if all(is_bot_defeated(profile, b.bot_id) for b in BOTS):
            if unlock_achievement(profile, "collector_all"):
                newly.append("collector_all")
    return newly


def record_bot_result(profile: Dict[str, Any], bot_id: str, outcome: str) -> None:
    stats = profile.setdefault("bot_stats", {}).setdefault(
        bot_id, {"wins": 0, "losses": 0, "draws": 0}
    )
    if outcome == "win":
        stats["wins"] = stats.get("wins", 0) + 1
    elif outcome == "loss":
        stats["losses"] = stats.get("losses", 0) + 1
    else:
        stats["draws"] = stats.get("draws", 0) + 1
    save_profile(profile)


def record_adaptive_result(
    profile: Dict[str, Any],
    outcome: str,
    new_elo: int,
    tier_bot_id: Optional[str] = None,
) -> None:
    stats = profile.setdefault("adaptive_stats", {"wins": 0, "losses": 0, "draws": 0})
    if outcome == "win":
        stats["wins"] = stats.get("wins", 0) + 1
    elif outcome == "loss":
        stats["losses"] = stats.get("losses", 0) + 1
    else:
        stats["draws"] = stats.get("draws", 0) + 1

    profile["adaptive_elo"] = int(new_elo)
    profile["adaptive_peak"] = max(int(profile.get("adaptive_peak", 1000)), int(new_elo))
    if tier_bot_id and outcome == "win":
        bstats = profile.setdefault("bot_stats", {}).setdefault(
            tier_bot_id, {"wins": 0, "losses": 0, "draws": 0}
        )
        bstats["wins"] = bstats.get("wins", 0) + 1
    save_profile(profile)


def is_bot_defeated(profile: Dict[str, Any], bot_id: str) -> bool:
    st = profile.get("bot_stats", {}).get(bot_id)
    return bool(st and st.get("wins", 0) > 0)

def get_bot_record_str(profile: Dict[str, Any], bot_id: str) -> str:
    st = profile.get("bot_stats", {}).get(bot_id)
    if not st:
        return ""
    w = st.get("wins", 0)
    d = st.get("draws", 0)
    l = st.get("losses", 0)
    if w + d + l == 0:
        return ""
    return f"({w}W-{d}D-{l}L)"

def _sanitize_save_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip())
    return cleaned[:40] if cleaned else "autosave"

def save_game(
    name: str,
    board: Board,
    player_color: int,
    bot_key: str,
    bot_name: str,
    bot_elo: int,
    is_adaptive: bool,
    adaptive_elo: int,
    adaptive_start_elo: int,
    adaptive_anchor_key: Optional[str] = None,
) -> Path:
    slot = _sanitize_save_name(name)
    path = saves_dir() / f"{slot}.json"
    payload = {
        "name": slot,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "start_fen": START_FEN,
        "fen": board.fen(),
        "uci_history": [move_to_uci(m) for m in board.move_history],
        "san_history": list(board.san_history),
        "player_color": "white" if player_color == WHITE else "black",
        "bot_key": bot_key,
        "bot_name": bot_name,
        "bot_elo": bot_elo,
        "is_adaptive": is_adaptive,
        "adaptive_elo": adaptive_elo,
        "adaptive_start_elo": adaptive_start_elo,
        "adaptive_anchor_key": adaptive_anchor_key,
        "moves": len(board.move_history),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

def list_saves() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for p in sorted(saves_dir().glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("name", p.stem)
                items.append(data)
        except (OSError, json.JSONDecodeError):
            continue
    return items


def load_game(name: str) -> Tuple[Board, Dict[str, Any]]:
    slot = _sanitize_save_name(name)
    path = saves_dir() / f"{slot}.json"
    if not path.exists():
        raise FileNotFoundError(f"Save '{slot}' tidak ditemukan.")
    data = json.loads(path.read_text(encoding="utf-8"))
    start_fen = data.get("start_fen", START_FEN)
    board = Board(start_fen)
    replayed_ok = True
    for uci in data.get("uci_history", []):
        legal = {move_to_uci(m): m for m in board.legal_moves()}
        if uci in legal:
            board.make_move(legal[uci], record_san=True)
        else:
            replayed_ok = False
            break
    if not replayed_ok:
        board = Board(data["fen"])
    return board, data

def export_pgn_file(
    board: Board,
    filename: str,
    white_name: str,
    black_name: str,
    white_elo: str,
    black_elo: str,
    event: str = "ChessPortable v3.0 Match",
    result: str = "*",
    eco: Optional[str] = None,
    opening: Optional[str] = None,
) -> Path:
    stem = _sanitize_save_name(filename.removesuffix(".pgn")) if filename.strip() else datetime.now().strftime("match_%Y%m%d_%H%M%S")
    out = pgn_dir() / f"{stem}.pgn"
    text = board.to_pgn(
        white_name=white_name,
        black_name=black_name,
        white_elo=white_elo,
        black_elo=black_elo,
        event=event,
        result=result,
        date_str=datetime.now().strftime("%Y.%m.%d"),
        eco=eco,
        opening=opening,
    )
    out.write_text(text, encoding="utf-8")
    return out
