from __future__ import annotations

import argparse
import random
import re
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import readline
except ImportError:
    pass

from . import __author__, __version__
from .ai import ChessAI
from .board import (
    BLACK,
    Board,
    EMPTY,
    FLAG_CASTLE_KING,
    FLAG_CASTLE_QUEEN,
    FLAG_EN_PASSANT,
    IllegalMoveError,
    KNIGHT,
    PAWN,
    PromotionRequiredError,
    QUEEN,
    SAN_CHAR_TO_TYPE,
    WHITE,
    move_flag,
    move_from,
    move_promo,
    move_to,
    move_to_uci,
    name_to_sq,
)
from .bots import BOT_BY_KEY, BOTS, CORE_BOTS, EXTRA_BOTS, BotProfile, nearest_bot_for_elo
from .dialogue import react_to_bot_move, react_to_player_move
from .evolving import (
    DEFAULT_BRAIN,
    DEFAULT_DNA,
    EvolvingAdaptiveController,
    EvolvingBrain,
    MatchTracker,
    PlayerDNA,
    format_move_callout,
)
from .openings import detect_opening
from .puzzles import PUZZLES, Puzzle, puzzles_near_rating
from .storage import (
    TIME_CONTROLS,
    check_match_achievements,
    export_pgn_file,
    get_bot_adaptive_state,
    get_bot_brain,
    get_brain,
    get_dna,
    is_bot_defeated,
    list_saves,
    load_game,
    load_profile,
    record_adaptive_result,
    record_bot_result,
    record_per_bot_adaptive_result,
    reset_bot_adaptive,
    save_game,
    save_profile,
    set_bot_brain,
    set_brain,
    set_dna,
    unlock_achievement,
)
from .themes import THEMES, THEME_BY_ID
from .ui import (
    BOLD,
    CYAN,
    DIM,
    GRAY,
    GREEN,
    MAGENTA,
    RED,
    RESET,
    WHITE_FG,
    YELLOW,
    clear_screen,
    render_adaptive_roster,
    render_board,
    render_dna_lab,
    render_eval_bar,
    render_extra_bots_menu,
    render_help,
    render_main_menu,
    render_match_analysis,
    render_move_review,
    render_records,
    render_settings_menu,
    ring_bell,
)

STYLE_CYCLE = ("unicode", "ascii", "ascii_plain")
STYLE_LABELS = {
    "unicode": "Unicode Berwarna (♔♕♖♗♘♙)",
    "ascii": "ASCII Berwarna (K Q R B N P)",
    "ascii_plain": "ASCII Klasik (Tanpa Background)",
}
TC_KEYS = tuple(TIME_CONTROLS.keys())

def _safe_input(prompt: str) -> Optional[str]:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None

def _parse_menu_selection(
    raw: str, profile: Dict[str, Any]
) -> Tuple[str, Optional[Any]]:
    cleaned = raw.strip().strip("'\"")
    if not cleaned:
        return ("invalid", "Pilih 0-19, B (Bot Ekstra), A (Adaptif), G (Turnamen), P (Puzzle), 2P, D, T, L, R, atau Q.")

    low = cleaned.lower()
    if low in ("q", "quit", "exit"):
        return ("quit", None)
    if low in ("b", "bots", "ekstra", "extra", "more", "lain"):
        return ("extra_bots", None)
    if low in ("r", "rekor", "stats", "record", "records", "achievements"):
        return ("records", None)
    if low in ("l", "load", "saves", "lanjut"):
        return ("load", None)
    if low in ("d", "dna", "gaya", "profil", "lab", "evolving"):
        return ("dna", None)
    if low in ("t", "theme", "themes", "settings", "clock", "jam", "tema"):
        return ("settings", None)
    if low in ("g", "gauntlet", "rush", "boss", "turnamen"):
        return ("gauntlet", None)
    if low in ("p", "puzzle", "puzzles", "tactic", "tactics"):
        return ("puzzles", None)
    if low in ("2p", "pvp", "2player", "local", "vs", "berdua"):
        return ("pvp", None)
    if low in ("style", "ascii", "unicode"):
        return ("style", low)
    if low in ("help", "?", "h"):
        return ("help", None)

    if cleaned in BOT_BY_KEY:
        return ("bot", BOT_BY_KEY[cleaned])

    if re.fullmatch(r"(?:a|adaptive|adaptif)\s+(?:list|roster|all|bots|daftar)", low):
        return ("adaptive_roster", None)

    ad_bot_m = re.fullmatch(r"(?:a|adaptive|adaptif)\s*(1[0-9]|[0-9])(?:\s+(fresh|reset))?", low)
    if ad_bot_m:
        key = ad_bot_m.group(1)
        fresh = ad_bot_m.group(2) is not None
        return ("adaptive_bot", (BOT_BY_KEY[key], fresh))

    ad_glob_m = re.fullmatch(r"(?:a|adaptive|adaptif)(?:\s+([0-9]+))?", low)
    if ad_glob_m:
        arg = ad_glob_m.group(1)
        if arg is None:
            return ("adaptive_global", int(profile.get("adaptive_elo", 1000)))
        elo_num = int(arg)
        if 100 <= elo_num <= 4000:
            return ("adaptive_global", elo_num)
        return ("invalid", f"Elo '{arg}' di luar jangkauan. Gunakan A, A 0-19, A list, atau Elo 100-4000.")

    for bot in BOTS:
        if low == bot.bot_id or low == bot.name.lower():
            return ("bot", bot)

    return ("invalid", f"Pilihan '{cleaned}' tidak dikenal. Ketik 0-19, B, A, A 0-19, A list, G, P, 2P, D, T, L, atau R.")

def _choose_player_color() -> Optional[int]:
    print(f"\n{BOLD}Pilih sisi mainmu:{RESET}")
    print(f"  ({BOLD}1{RESET}) {WHITE_FG}♔ Putih{RESET}  {DIM}— Jalan duluan{RESET}")
    print(f"  ({BOLD}2{RESET}) {CYAN}♚ Hitam{RESET}  {DIM}— Baca langkah lawan dulu{RESET}")
    print(f"  ({BOLD}3{RESET}) {YELLOW}Acak{RESET}     {DIM}— Biar takdir yang pilih{RESET}")
    ans = _safe_input(f"{BOLD}Pilih [1/2/3 atau W/B/R]{RESET} {DIM}(Enter=Putih){RESET}: ")
    if ans is None:
        return None
    low = ans.strip().lower()
    if low in ("", "1", "w", "white", "putih", "p"):
        return WHITE
    if low in ("2", "b", "black", "hitam", "h"):
        return BLACK
    if low in ("3", "r", "random", "acak", "a"):
        chosen = random.choice((WHITE, BLACK))
        label = "Putih (♔)" if chosen == WHITE else "Hitam (♚)"
        print(f"{CYAN}Pilihan acak: Kamu main {BOLD}{label}{RESET}{CYAN}!{RESET}")
        return chosen
    print(f"{YELLOW}Pilihan tidak dikenali, kamu main Putih duluan ya.{RESET}")
    return WHITE

def _pick_saved_game() -> Optional[Tuple[Board, Dict[str, Any]]]:
    saves = list_saves()
    if not saves:
        print(f"{YELLOW}Belum ada permainan yang disimpan.{RESET}")
        return None
    print(f"\n{BOLD}{CYAN}═══ PERMAINAN TERSIMPAN ═══{RESET}")
    for idx, sv in enumerate(saves, 1):
        mode_tag = (
            f"Adaptif Elo {sv.get('adaptive_elo', '?')}"
            if sv.get("is_adaptive")
            else f"{sv.get('bot_name', '?')} (Elo {sv.get('bot_elo', '?')})"
        )
        turns = (int(sv.get("moves", 0)) + 1) // 2
        print(
            f"  ({BOLD}{idx}{RESET}) {GREEN}{sv['name']}{RESET}  ·  vs {mode_tag}  ·  "
            f"{turns} langkah  ·  {DIM}{sv.get('saved_at', '')}{RESET}"
        )
    ans = _safe_input(f"Pilih nomor atau nama save {DIM}(Enter=batal){RESET}: ")
    if ans is None or not ans.strip():
        return None
    choice = ans.strip()
    slot_name = choice
    if choice.isdigit():
        i = int(choice)
        if 1 <= i <= len(saves):
            slot_name = saves[i - 1]["name"]
        else:
            print(f"{RED}Nomor save tidak valid.{RESET}")
            return None
    try:
        return load_game(slot_name)
    except FileNotFoundError as exc:
        print(f"{RED}{exc}{RESET}")
        return None

def _prompt_promotion(board: Board, matches: List[int]) -> Optional[int]:
    ans = _safe_input(f"{YELLOW}Promosi pion!{RESET} Pilih bidak [Q/R/B/N] {DIM}(Enter=Q){RESET}: ")
    if ans is None:
        return None
    ch = ans.strip().upper() or "Q"
    if ch not in SAN_CHAR_TO_TYPE or ch == "K":
        print(f"{YELLOW}Pilihan tidak valid, promosi ke Menteri (Q).{RESET}")
        ch = "Q"
    wanted = SAN_CHAR_TO_TYPE[ch]
    for mv in matches:
        if move_promo(mv) == wanted:
            return mv
    return matches[0]

def _tokenize_arc_args(arg: str) -> List[str]:
    return [t for t in re.split(r"[\s,;]+", arg.strip()) if t]

def _parse_arc_move(board: Board, tok: str) -> int:
    try:
        return board.parse_move(tok)
    except PromotionRequiredError as prom:
        for mv in prom.moves:
            if move_promo(mv) == QUEEN:
                return mv
        return prom.moves[0]
    except IllegalMoveError:
        if len(tok) >= 3 and tok[0] in ("k", "K"):
            alt = "N" + tok[1:]
            try:
                return board.parse_move(alt)
            except PromotionRequiredError as prom:
                return prom.moves[0]
        if len(tok) >= 3 and tok[0] in ("m", "M"):
            alt = "Q" + tok[1:]
            try:
                return board.parse_move(alt)
            except PromotionRequiredError as prom:
                return prom.moves[0]
        raise

def _filter_legal_moves(board: Board, filter_arg: str) -> Tuple[List[int], int, Set[int]]:

    legal = board.legal_moves()
    filt = filter_arg.strip()
    if not filt:
        return legal, -1, set()

    sq = name_to_sq(filt)
    if sq >= 0:
        matched = [m for m in legal if move_from(m) == sq]
        return matched, sq, {move_to(m) for m in matched}
    if len(filt) == 1 and filt.upper() in SAN_CHAR_TO_TYPE:
        pt = SAN_CHAR_TO_TYPE[filt.upper()]
        matched = [m for m in legal if abs(board.squares[move_from(m)]) == pt]
        return matched, -1, {move_to(m) for m in matched}
    if len(filt) == 1 and filt.lower() == "p":
        matched = [m for m in legal if abs(board.squares[move_from(m)]) == PAWN]
        return matched, -1, {move_to(m) for m in matched}
    matched = [m for m in legal if filt.lower() in board.move_to_san(m).lower()]
    return matched, -1, {move_to(m) for m in matched}

def _format_moves_list(board: Board, moves: List[int], filter_arg: str = "") -> str:
    if not moves:
        return f"{YELLOW}Tidak ada langkah legal yang cocok dengan '{filter_arg}'.{RESET}"
    sans = sorted(board.move_to_san(m) for m in moves)
    lines: List[str] = []
    cur = "  "
    for s in sans:
        if len(cur) + len(s) + 2 > 48:
            lines.append(cur.rstrip())
            cur = "  "
        cur += f"{s:<7}"
    if cur.strip():
        lines.append(cur.rstrip())
    return f"{BOLD}{CYAN}Langkah legal ({len(sans)}):{RESET}\n" + "\n".join(lines)

def _format_pgn_history(board: Board) -> str:
    if not board.san_history:
        return f"{DIM}Belum ada langkah dimainkan.{RESET}"
    parts: List[str] = []
    sh = board.san_history
    for i in range(0, len(sh), 2):
        num = (i // 2) + 1
        w = sh[i]
        b = sh[i + 1] if i + 1 < len(sh) else ""
        parts.append(f"{num}. {w}" + (f" {b}" if b else ""))
    lines: List[str] = []
    cur = ""
    for p in parts:
        if len(cur) + len(p) + 2 > 52:
            lines.append(cur.rstrip())
            cur = ""
        cur += p + "  "
    if cur.strip():
        lines.append(cur.rstrip())
    return f"{BOLD}{CYAN}Riwayat Langkah:{RESET}\n" + "\n".join(lines)

def run_settings_loop(profile: Dict[str, Any]) -> None:
    while True:
        clear_screen()
        print(render_settings_menu(profile))
        print()
        ans = _safe_input(f"{BOLD}{CYAN}Pengaturan > {RESET}")
        if ans is None:
            return
        low = ans.strip().lower()
        if low in ("0", "", "q", "back", "menu"):
            return
        if low.isdigit() and 1 <= int(low) <= len(THEMES):
            chosen = THEMES[int(low) - 1]
            profile["theme"] = chosen.theme_id
            save_profile(profile)
            print(f"{GREEN}Tema diubah ke {chosen.name}!{RESET}")
            continue
        if low == "s":
            cur = profile.get("board_style", "unicode")
            nxt = STYLE_CYCLE[(STYLE_CYCLE.index(cur) + 1) % len(STYLE_CYCLE)] if cur in STYLE_CYCLE else "unicode"
            profile["board_style"] = nxt
            save_profile(profile)
            continue
        if low == "c":
            cur = profile.get("time_control", "unlimited")
            idx = TC_KEYS.index(cur) if cur in TC_KEYS else 0
            profile["time_control"] = TC_KEYS[(idx + 1) % len(TC_KEYS)]
            save_profile(profile)
            continue
        if low == "e":
            profile["show_eval"] = not bool(profile.get("show_eval", True))
            save_profile(profile)
            continue
        if low == "m":
            profile["show_grades"] = not bool(profile.get("show_grades", True))
            save_profile(profile)
            continue
        if low == "b":
            profile["sound_bell"] = not bool(profile.get("sound_bell", False))
            save_profile(profile)
            continue


def run_dna_lab(profile: Dict[str, Any]) -> None:
    while True:
        clear_screen()
        print(render_dna_lab(profile))
        print()
        ans = _safe_input(
            f"{DIM}[Enter] Kembali  |  'daftar' Adaptif 0-19  |  'reset-memori'  |  'reset-gaya':{RESET} "
        )
        if ans is None:
            return
        low = ans.strip().lower()
        if low in ("roster", "list", "bots", "a", "daftar"):
            clear_screen()
            print(render_adaptive_roster(profile))
            print()
            _safe_input(f"{DIM}Tekan Enter untuk kembali...{RESET}")
            continue
        if low in ("reset-brain", "reset-memori"):
            set_brain(profile, EvolvingBrain(DEFAULT_BRAIN))
            save_profile(profile)
            print(f"{YELLOW}Ingatan lawan adaptif sudah direset seperti baru kenalan.{RESET}")
            time.sleep(0.6)
            continue
        if low in ("reset-dna", "reset-gaya"):
            set_dna(profile, PlayerDNA(DEFAULT_DNA))
            save_profile(profile)
            print(f"{YELLOW}Catatan gaya mainmu sudah dibersihkan.{RESET}")
            time.sleep(0.6)
            continue
        return

def run_puzzles_mode(profile: Dict[str, Any]) -> None:

    style = profile.get("board_style", "unicode")
    theme_id = profile.get("theme", "sage")

    while True:
        rating = int(profile.get("puzzle_rating", 1000))
        solved_ids: List[str] = list(profile.get("solved_puzzles", []))
        candidates = puzzles_near_rating(rating, solved_ids)
        puzzle: Puzzle = candidates[0]

        board = Board(puzzle.fen)
        player_color = board.turn
        step = 0
        failed_once = False
        status_note: Optional[str] = f"{YELLOW}🎯 Tugas: {puzzle.theme} — Temukan langkah terbaik!{RESET}"
        highlight_targets: Set[int] = set()
        highlight_origin = -1

        while step < len(puzzle.solution):
            clear_screen()
            banner = (
                f"{BOLD}{YELLOW}🧩 PUZZLE #{puzzle.puzzle_id.upper()}: {puzzle.title}{RESET}  "
                f"{DIM}(Rating Puzzle: {puzzle.rating} | Rating Kamu: {rating} | Solved: {len(solved_ids)}/{len(PUZZLES)}){RESET}"
            )
            print(
                render_board(
                    board,
                    bot=None,
                    player_color=player_color,
                    style=style,
                    theme_id=theme_id,
                    show_eval=False,
                    status_note=status_note,
                    highlight_targets=highlight_targets,
                    highlight_origin=highlight_origin,
                    banner_title=banner,
                )
            )
            print()
            highlight_targets = set()
            highlight_origin = -1

            side_lbl = "Putih" if board.turn == WHITE else "Hitam"
            raw = _safe_input(f"{BOLD}Puzzle ({side_lbl}){RESET} {DIM}[langkah / hint / moves / skip / menu]{RESET}: ")
            if raw is None:
                return
            cmd_raw = raw.strip()
            if not cmd_raw:
                continue
            parts = cmd_raw.split()
            cmd = parts[0].lower()
            arg = " ".join(parts[1:]).strip()

            if cmd in ("menu", "q", "quit", "exit", "back"):
                return
            if cmd in ("skip", "next"):
                rating = max(400, rating - 15)
                profile["puzzle_rating"] = rating
                save_profile(profile)
                print(f"{YELLOW}Puzzle dilewati. Solusi: {puzzle.solution[step]}{RESET}")
                break
            if cmd in ("hint", "h"):
                status_note = f"{CYAN}💡 Hint: {puzzle.hint}{RESET}"
                continue
            if cmd in ("moves", "m"):
                matched, origin, targets = _filter_legal_moves(board, arg)
                highlight_origin = origin
                highlight_targets = targets
                status_note = _format_moves_list(board, matched, arg)
                continue
            if cmd in ("style", "unicode", "ascii"):
                idx = STYLE_CYCLE.index(style) if style in STYLE_CYCLE else 0
                style = STYLE_CYCLE[(idx + 1) % len(STYLE_CYCLE)]
                profile["board_style"] = style
                save_profile(profile)
                continue

            try:
                mv = board.parse_move(cmd_raw)
            except PromotionRequiredError as prom:
                picked = _prompt_promotion(board, prom.moves)
                if picked is None:
                    continue
                mv = picked
            except IllegalMoveError as exc:
                status_note = f"{BOLD}{RED}Illegal!{RESET} {RED}{exc}{RESET}"
                continue

            uci = move_to_uci(mv)
            expected_uci = puzzle.solution[step]

            is_alt_mate = False
            if step == len(puzzle.solution) - 1 and puzzle.must_mate:
                b_test = board.copy()
                b_test.make_move(mv, record_san=False)
                if b_test.is_checkmate():
                    is_alt_mate = True

            if uci == expected_uci or is_alt_mate:
                san = board.move_to_san(mv)
                board.make_move(mv, record_san=True)
                step += 1
                if step < len(puzzle.solution):

                    reply_uci = puzzle.solution[step]
                    legal_map = {move_to_uci(m): m for m in board.legal_moves()}
                    reply_mv = legal_map[reply_uci]
                    reply_san = board.move_to_san(reply_mv)
                    board.make_move(reply_mv, record_san=True)
                    step += 1
                    status_note = f"{GREEN}✔ Tepat ({san})! Lawan merespon: {BOLD}{reply_san}{RESET} — Lanjutkan!"
                else:

                    gain = 25 if not failed_once else 10
                    if puzzle.rating > rating:
                        gain += 10
                    new_rating = min(2800, rating + gain)
                    profile["puzzle_rating"] = new_rating
                    if puzzle.puzzle_id not in solved_ids:
                        solved_ids.append(puzzle.puzzle_id)
                        profile["solved_puzzles"] = solved_ids
                    save_profile(profile)

                    clear_screen()
                    banner_done = f"{BOLD}{GREEN}🏆 PUZZLE SELESAI: {puzzle.title}!{RESET}  {CYAN}Rating: {rating} → {new_rating} (+{gain}▲){RESET}"
                    print(
                        render_board(
                            board,
                            bot=None,
                            player_color=player_color,
                            style=style,
                            theme_id=theme_id,
                            show_eval=False,
                            status_note=f"{GREEN}✔ Langkah pemenang: {BOLD}{san}{RESET}",
                            banner_title=banner_done,
                        )
                    )
                    if len(solved_ids) >= 10 and unlock_achievement(profile, "puzzle_10"):
                        print(f"\n{BOLD}{YELLOW}🏆 MEDALI BARU: 🧩 Ahli Taktik!{RESET}")
                    ans = _safe_input(f"\n[{BOLD}Enter{RESET}] Puzzle berikutnya  [{BOLD}M{RESET}] Kembali ke Menu: ")
                    if ans is None or ans.strip().lower() in ("m", "menu", "q", "quit"):
                        return
                    break
            else:
                failed_once = True
                status_note = f"{RED}✖ Bukan langkah terbaik di puzzle ini! Coba lagi atau ketik 'hint'.{RESET}"

def play_pvp_match(profile: Dict[str, Any]) -> str:

    board = Board()
    style = profile.get("board_style", "unicode")
    theme_id = profile.get("theme", "sage")
    tc_key = profile.get("time_control", "unlimited")
    _, base_sec, inc_sec = TIME_CONTROLS.get(tc_key, TIME_CONTROLS["unlimited"])
    white_clock: Optional[float] = float(base_sec) if base_sec > 0 else None
    black_clock: Optional[float] = float(base_sec) if base_sec > 0 else None

    ans_flip = _safe_input(f"Auto-putar papan tiap giliran? [y/N]: ")
    auto_flip = bool(ans_flip and ans_flip.strip().lower() in ("y", "yes", "ya"))
    flipped = False
    status_note: Optional[str] = f"{GREEN}Mode 2-Player Lokal dimulai! Putih jalan duluan.{RESET}"
    highlight_targets: Set[int] = set()
    highlight_origin = -1
    pvp_arc_queues: Dict[int, List[str]] = {WHITE: [], BLACK: []}

    while True:
        res = board.game_result()
        if res is not None:
            res_code, reason = res
            clear_screen()
            banner = f"{BOLD}{YELLOW}🏆 HASIL 2P: {res_code} — {reason}{RESET}"
            print(
                render_board(
                    board, None, WHITE, style=style, theme_id=theme_id,
                    flipped=flipped, pvp_mode=True, show_eval=False,
                    white_clock=white_clock, black_clock=black_clock,
                    status_note=banner,
                )
            )
            ans = _safe_input(f"\n[{BOLD}1{RESET}] Main lagi  [{BOLD}2{RESET}] Menu utama: ")
            if ans and ans.strip() == "1":
                return "rematch"
            return "menu"

        perspective = board.turn if auto_flip else WHITE
        clear_screen()
        print(
            render_board(
                board, None, perspective, style=style, theme_id=theme_id,
                flipped=flipped, pvp_mode=True, show_eval=False,
                white_clock=white_clock, black_clock=black_clock,
                status_note=status_note,
                highlight_targets=highlight_targets,
                highlight_origin=highlight_origin,
            )
        )
        print()
        highlight_targets = set()
        highlight_origin = -1

        turn_name = "Putih" if board.turn == WHITE else "Hitam"
        side_q = pvp_arc_queues[board.turn]
        if side_q:
            tok = side_q.pop(0)
            if sys.stdout.isatty():
                time.sleep(0.22)
            try:
                mv = _parse_arc_move(board, tok)
            except IllegalMoveError:
                side_q.clear()
                status_note = f"{BOLD}{RED}⚡ ARC berhenti!{RESET} {RED}Langkah '{tok}' Illegal di posisi ini.{RESET}"
                continue
            san = board.move_to_san(mv)
            board.make_move(mv, record_san=True)
            rem = f"sisa {len(side_q)}" if side_q else "selesai"
            status_note = f"{MAGENTA}⚡ [ARC · {rem}]{RESET} {GREEN}{turn_name} otomatis: {BOLD}{san}{RESET}"
            continue

        t_start = time.monotonic()
        raw = _safe_input(f"{BOLD}2P · Giliran {turn_name}{RESET} {DIM}[langkah / ARC ... / undo / moves / menu]{RESET}: ")
        elapsed = time.monotonic() - t_start
        if raw is None:
            return "quit"

        cmd_raw = raw.strip()
        if not cmd_raw:
            continue
        parts = cmd_raw.split()
        cmd = parts[0].lower()
        arg = " ".join(parts[1:]).strip()

        if cmd == "arc":
            toks = _tokenize_arc_args(arg)
            if not toks or arg.lower() in ("stop", "clear", "off"):
                side_q.clear()
                status_note = f"{MAGENTA}⚡ ARC format: ARC <langkah1> <langkah2> ... (contoh: ARC e4 kh3 Bc4){RESET}"
                continue
            pvp_arc_queues[board.turn] = toks
            status_note = f"{MAGENTA}⚡ ARC aktif ({len(toks)} langkah): {' → '.join(toks)}{RESET}"
            continue

        if cmd in ("menu", "new"):
            return "menu"
        if cmd in ("q", "quit", "exit"):
            return "quit"
        if cmd == "flip":
            flipped = not flipped
            continue
        if cmd in ("style", "unicode", "ascii"):
            idx = STYLE_CYCLE.index(style) if style in STYLE_CYCLE else 0
            style = STYLE_CYCLE[(idx + 1) % len(STYLE_CYCLE)]
            profile["board_style"] = style
            save_profile(profile)
            continue
        if cmd in ("u", "undo"):
            if board.move_history:
                board.unmake_move(pop_history=True)
                status_note = f"{YELLOW}↶ 1 langkah dibatalkan.{RESET}"
            continue
        if cmd in ("m", "moves"):
            matched, origin, targets = _filter_legal_moves(board, arg)
            highlight_origin = origin
            highlight_targets = targets
            status_note = _format_moves_list(board, matched, arg)
            continue
        if cmd == "export":
            out = export_pgn_file(board, arg, "Player Putih", "Player Hitam", "?", "?", "ChessPortable 2P Match")
            status_note = f"{GREEN}✔ PGN diekspor ke: {out}{RESET}"
            continue


        if white_clock is not None and black_clock is not None:
            if board.turn == WHITE:
                white_clock -= elapsed
                if white_clock <= 0:
                    print(f"{BOLD}{RED}⏰ WAKTU PUTIH HABIS! Hitam menang!{RESET}")
                    _safe_input("Tekan Enter untuk kembali ke menu...")
                    return "menu"
            else:
                black_clock -= elapsed
                if black_clock <= 0:
                    print(f"{BOLD}{RED}⏰ WAKTU HITAM HABIS! Putih menang!{RESET}")
                    _safe_input("Tekan Enter untuk kembali ke menu...")
                    return "menu"

        try:
            mv = board.parse_move(cmd_raw)
        except PromotionRequiredError as prom:
            picked = _prompt_promotion(board, prom.moves)
            if picked is None:
                continue
            mv = picked
        except IllegalMoveError as exc:
            status_note = f"{BOLD}{RED}Illegal!{RESET} {RED}{exc}{RESET}"
            continue

        san = board.move_to_san(mv)
        mover = board.turn
        board.make_move(mv, record_san=True)
        if white_clock is not None and black_clock is not None and inc_sec > 0:
            if mover == WHITE:
                white_clock += inc_sec
            else:
                black_clock += inc_sec
        status_note = f"{GREEN}✔ {turn_name} melangkah: {BOLD}{san}{RESET}"


def play_match(
    ai: ChessAI,
    profile: Dict[str, Any],
    player_color: int,
    bot: BotProfile,
    is_adaptive: bool = False,
    adaptive: Optional[EvolvingAdaptiveController] = None,
    board: Optional[Board] = None,
    gauntlet_stage: Optional[int] = None,
) -> Tuple[str, Optional[str]]:

    if board is None:
        board = Board()

    style: str = profile.get("board_style", "unicode")
    if style not in STYLE_CYCLE:
        style = "unicode"
    theme_id: str = profile.get("theme", "sage")
    show_eval: bool = bool(profile.get("show_eval", True))
    show_grades: bool = bool(profile.get("show_grades", True))
    sound_bell: bool = bool(profile.get("sound_bell", False))
    think_override: Optional[float] = profile.get("think_override")

    tc_key = profile.get("time_control", "unlimited")
    _, base_sec, inc_sec = TIME_CONTROLS.get(tc_key, TIME_CONTROLS["unlimited"])
    white_clock: Optional[float] = float(base_sec) if base_sec > 0 else None
    black_clock: Optional[float] = float(base_sec) if base_sec > 0 else None

    flipped = False
    tracker = MatchTracker()
    dna = get_dna(profile)

    brain = adaptive.brain if (is_adaptive and adaptive is not None) else None

    active_bot = adaptive.profile() if (is_adaptive and adaptive) else bot
    bot_message: Optional[str] = active_bot.say("intro")
    status_note: Optional[str] = None
    adaptive_delta = 0
    last_eval_cp: Optional[int] = 0
    last_eval_side: int = WHITE
    highlight_targets: Set[int] = set()
    highlight_origin: int = -1
    opening_eco: str = ""
    opening_name: str = ""
    hot_streak: int = 0
    arc_queue: List[str] = []
    needs_render = True

    if board.move_history:
        op_hit = detect_opening(board)
        if op_hit:
            opening_eco, opening_name = op_hit
            tracker.opening_eco, tracker.opening_name = opening_eco, opening_name

    def _update_opening() -> None:
        nonlocal opening_eco, opening_name
        if len(board.move_history) <= 24:
            op_hit = detect_opening(board)
            if op_hit:
                opening_eco, opening_name = op_hit
                tracker.opening_eco = opening_eco
                tracker.opening_name = opening_name

    def _opening_label() -> Optional[str]:
        if opening_name:
            return f"{opening_eco} · {opening_name}" if opening_eco else opening_name
        return None

    def _finish_game(outcome: str, reason: str, res_code: str) -> Tuple[str, str]:
        nonlocal bot_message
        if outcome == "win":
            banner = f"{BOLD}{GREEN}🏆 KAMU MENANG! ({reason}){RESET}"
            bot_message = active_bot.say("lose")
        elif outcome == "loss":
            banner = f"{BOLD}{RED}💀 KAMU KALAH! ({reason}){RESET}"
            bot_message = active_bot.say("win")
        else:
            banner = f"{BOLD}{YELLOW}🤝 REMIS! ({reason}){RESET}"
            bot_message = active_bot.say("draw")


        dna.ingest_match(tracker)
        set_dna(profile, dna)

        learned_lessons = 0
        gen_num: Optional[int] = None

        if is_adaptive and adaptive is not None and brain is not None:
            old_elo = adaptive.elo
            learned_lessons = brain.learn_from_match(tracker, outcome)
            gen_num = brain.generation
            delta = adaptive.update_after_game(outcome, tracker.accuracy_percent())
            if adaptive.anchor_bot is not None:
                anchor = adaptive.anchor_bot
                set_bot_brain(profile, anchor.bot_id, anchor.elo, brain)
                record_per_bot_adaptive_result(
                    profile, anchor.bot_id, anchor.elo, outcome, adaptive.elo
                )
                label_prefix = f"★ Adaptif·{anchor.name} Elo"
            else:
                set_brain(profile, brain)
                tier_bot = nearest_bot_for_elo(old_elo)
                record_adaptive_result(
                    profile,
                    outcome,
                    adaptive.elo,
                    tier_bot_id=tier_bot.bot_id if outcome == "win" else None,
                )
                label_prefix = "★ Adaptif Utama Elo"
            elo_banner = (
                f"{CYAN}{label_prefix}: {old_elo} → {BOLD}{adaptive.elo}{RESET} "
                f"({GREEN}+{delta}▲{RESET})" if delta >= 0 else
                f"{CYAN}{label_prefix}: {old_elo} → {BOLD}{adaptive.elo}{RESET} ({RED}{delta}▼{RESET})"
            )
        else:
            was_defeated = is_bot_defeated(profile, bot.bot_id)
            record_bot_result(profile, bot.bot_id, outcome)
            elo_banner = ""
            if outcome == "win" and not was_defeated:
                elo_banner = f"{BOLD}{YELLOW}★ LENCANA TERBUKA! Kamu berhasil mengalahkan {bot.name} (Elo {bot.elo})! ★{RESET}"

        new_achs = check_match_achievements(
            profile=profile,
            outcome=outcome,
            bot_id=active_bot.bot_id,
            bot_elo=active_bot.elo,
            is_adaptive=is_adaptive,
            generation=brain.generation if brain else 1,
            tracker=tracker,
            total_plies=len(board.move_history),
        )
        save_profile(profile)

        clear_screen()
        evo_tag = f"★ {active_bot.title}" if is_adaptive else None
        banner_title = (
            f"{BOLD}{MAGENTA}🔥 TURNAMEN BABAK {gauntlet_stage + 1}/10 — vs {bot.name}{RESET}"
            if gauntlet_stage is not None
            else None
        )
        print(
            render_board(
                board,
                active_bot,
                player_color,
                style=style,
                theme_id=theme_id,
                flipped=flipped,
                is_adaptive=is_adaptive,
                adaptive_delta=adaptive_delta,
                evo_tag=evo_tag,
                bot_message=bot_message,
                status_note=banner,
                eval_cp=last_eval_cp,
                eval_side=last_eval_side,
                show_eval=show_eval,
                white_clock=white_clock,
                black_clock=black_clock,
                banner_title=banner_title,
                opening_label=_opening_label(),
                hot_streak=hot_streak,
            )
        )
        print()
        if elo_banner:
            print(elo_banner)
        print(
            render_match_analysis(
                tracker=tracker,
                opponent_elo=active_bot.elo,
                outcome=outcome,
                learned_lessons=learned_lessons,
                generation=gen_num,
                new_achievements=new_achs,
            )
        )
        print()
        if gauntlet_stage is not None:
            _safe_input(f"{DIM}Tekan Enter untuk lanjut Gauntlet...{RESET}")
            return ("gauntlet_next", outcome)

        while True:
            ans = _safe_input(
                f"[{BOLD}1{RESET}] Rematch  [{BOLD}2{RESET}] Menu  [{BOLD}V{RESET}] Review  [{BOLD}E{RESET}] Ekspor PGN  [{BOLD}3{RESET}] Keluar: "
            )
            if ans is None:
                return ("quit", outcome)
            low = ans.strip().lower()
            if low in ("v", "review", "rvw"):
                print()
                print(render_move_review(tracker))
                print()
                continue
            if low in ("e", "export", "pgn"):
                w_name = "Kamu" if player_color == WHITE else active_bot.name
                b_name = active_bot.name if player_color == WHITE else "Kamu"
                w_elo = str(profile.get("adaptive_elo", "?")) if player_color == WHITE else str(active_bot.elo)
                b_elo = str(active_bot.elo) if player_color == WHITE else str(profile.get("adaptive_elo", "?"))
                out_p = export_pgn_file(
                    board, "", w_name, b_name, w_elo, b_elo,
                    result=res_code, eco=opening_eco or None, opening=opening_name or None,
                )
                print(f"{GREEN}✔ PGN tersimpan di: {out_p}{RESET}")
                continue
            if low in ("1", "r", "rematch", "y", "yes", ""):
                return ("rematch", outcome)
            if low in ("3", "q", "quit", "exit"):
                return ("quit", outcome)
            return ("menu", outcome)

    while True:
        result = board.game_result()
        if result is not None:
            res_code, reason = result
            if res_code == "1/2-1/2":
                return _finish_game("draw", reason, res_code)
            won = (res_code == "1-0" and player_color == WHITE) or (
                res_code == "0-1" and player_color == BLACK
            )
            return _finish_game("win" if won else "loss", reason, res_code)

        if needs_render:
            clear_screen()
            evo_tag = f"★ {active_bot.title}" if is_adaptive else None
            banner_title = (
                f"{BOLD}{MAGENTA}🔥 TURNAMEN BABAK {gauntlet_stage + 1}/10 — vs {bot.name}{RESET}"
                if gauntlet_stage is not None
                else None
            )
            print(
                render_board(
                    board,
                    active_bot,
                    player_color,
                    style=style,
                    theme_id=theme_id,
                    flipped=flipped,
                    is_adaptive=is_adaptive,
                    adaptive_delta=adaptive_delta,
                    evo_tag=evo_tag,
                    bot_message=bot_message,
                    status_note=status_note,
                    eval_cp=last_eval_cp,
                    eval_side=last_eval_side,
                    show_eval=show_eval,
                    highlight_targets=highlight_targets,
                    highlight_origin=highlight_origin,
                    white_clock=white_clock,
                    black_clock=black_clock,
                    banner_title=banner_title,
                    opening_label=_opening_label(),
                    hot_streak=hot_streak,
                )
            )
            print()
            highlight_targets = set()
            highlight_origin = -1
            needs_render = False

        if board.turn != player_color:
            sys.stdout.write(f"{DIM}{active_bot.name} sedang berpikir...{RESET}")
            sys.stdout.flush()

            zhex_before = f"{board.zobrist:016x}"
            t_ai0 = time.monotonic()
            res = ai.choose_move(board, active_bot, time_override=think_override, brain=brain)
            ai_elapsed = time.monotonic() - t_ai0

            if sys.stdout.isatty():
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()
            else:
                print()

            if res.move == 0:
                continue


            if white_clock is not None and black_clock is not None:
                if board.turn == WHITE:
                    white_clock -= ai_elapsed
                    if white_clock <= 0:
                        return _finish_game("win", "Waktu AI habis (Flag)", "0-1")
                    white_clock += inc_sec
                else:
                    black_clock -= ai_elapsed
                    if black_clock <= 0:
                        return _finish_game("win", "Waktu AI habis (Flag)", "1-0")
                    black_clock += inc_sec

            to_sq = move_to(res.move)
            captured_p = board.squares[to_sq]
            bot_flag = move_flag(res.move)
            is_ep = bot_flag == FLAG_EN_PASSANT
            is_bot_castle = bot_flag in (FLAG_CASTLE_KING, FLAG_CASTLE_QUEEN)
            is_bot_promo = move_promo(res.move) != 0
            bot_san = board.move_to_san(res.move)
            bot_uci = move_to_uci(res.move)
            ai_side = board.turn
            prev_op_name = opening_name

            tracker.record_ai_decision(zhex_before, bot_uci, len(board.move_history) + 1, res.score_cp)
            board.make_move(res.move, record_san=True)
            _update_opening()
            last_eval_cp = res.score_cp
            last_eval_side = ai_side
            white_ev_ai = res.score_cp if ai_side == WHITE else -res.score_cp
            tracker.record_eval(white_ev_ai)

            if board.in_check() or (captured_p != EMPTY and abs(captured_p) >= KNIGHT):
                ring_bell(sound_bell)

            if res.memory_note in ("avoided", "trap"):
                tracker.memory_hits += 1

            pieces_left_ai = sum(1 for sq in board.squares if sq != EMPTY)
            ai_line = react_to_bot_move(
                bot=active_bot,
                san=bot_san,
                ply=len(board.move_history),
                captured_piece=PAWN if is_ep else captured_p,
                is_ep=is_ep,
                gave_check=board.in_check(),
                memory_note=res.memory_note,
                opening_name=opening_name,
                opening_just_changed=(opening_name != prev_op_name),
                pieces_left=pieces_left_ai,
            )
            if ai_line is not None:
                bot_message = ai_line

            extra_tag = ""
            if res.memory_note == "avoided":
                extra_tag = f" {MAGENTA}· ingat pertemuan dulu{RESET}"
            elif res.memory_note == "trap":
                extra_tag = f" {MAGENTA}· siap menguji kamu{RESET}"
            elif res.from_book:
                extra_tag = f" {DIM}· langkah buku{RESET}"
            status_note = f"{CYAN}➜ {active_bot.name} melangkah: {BOLD}{bot_san}{RESET}{extra_tag}"
            needs_render = True
            continue

        turn_label = "Putih" if player_color == WHITE else "Hitam"
        from_arc = False
        pl_elapsed = 0.0
        mv = 0

        if arc_queue:
            arc_tok = arc_queue.pop(0)
            from_arc = True
            if sys.stdout.isatty():
                time.sleep(0.24)
            try:
                mv = _parse_arc_move(board, arc_tok)
            except IllegalMoveError as exc:
                arc_queue.clear()
                status_note = f"{BOLD}{RED}⚡ ARC berhenti!{RESET} {RED}Langkah '{arc_tok}' Illegal ({exc}){RESET}"
                needs_render = True
                continue

        if not from_arc:
            t_pl0 = time.monotonic()
            raw = _safe_input(f"{BOLD}Langkah ({turn_label}){RESET} {DIM}[contoh: e4 / ARC ... / help]{RESET}: ")
            pl_elapsed = time.monotonic() - t_pl0
            if raw is None:
                return ("quit", None)

            cmd_raw = raw.strip()
            if not cmd_raw:
                continue

            parts = cmd_raw.split()
            cmd = parts[0].lower()
            arg = " ".join(parts[1:]).strip()

            if cmd == "arc":
                toks = _tokenize_arc_args(arg)
                if not toks or arg.lower() in ("stop", "clear", "off"):
                    arc_queue.clear()
                    print(f"{MAGENTA}⚡ Format ARC: ARC <langkah1> <langkah2> ... (contoh: ARC e4 kh3 Bc4){RESET}")
                    continue
                arc_queue = toks
                print(f"{MAGENTA}⚡ ARC aktif ({len(toks)} langkah otomatis): {' → '.join(toks)}{RESET}")
                continue
        else:
            cmd_raw = ""
            cmd = ""
            arg = ""

        if cmd in ("help", "?"):
            print()
            print(render_help())
            print()
            continue

        if cmd in ("q", "quit", "exit"):
            return ("quit", None)

        if cmd in ("menu", "new"):
            return ("menu", None)

        if cmd in ("style", "unicode", "ascii", "plain"):
            if cmd == "unicode":
                style = "unicode"
            elif cmd == "ascii":
                style = "ascii"
            elif cmd == "plain":
                style = "ascii_plain"
            else:
                style = STYLE_CYCLE[(STYLE_CYCLE.index(style) + 1) % len(STYLE_CYCLE)]
            profile["board_style"] = style
            save_profile(profile)
            status_note = f"{GREEN}Tampilan diubah ke: {STYLE_LABELS[style]}{RESET}"
            needs_render = True
            continue

        if cmd == "theme":
            if arg.lower() in THEME_BY_ID:
                theme_id = arg.lower()
            else:
                ids = [t.theme_id for t in THEMES]
                theme_id = ids[(ids.index(theme_id) + 1) % len(ids)] if theme_id in ids else "sage"
            profile["theme"] = theme_id
            save_profile(profile)
            status_note = f"{GREEN}Tema warna diubah ke: {THEME_BY_ID[theme_id].name}{RESET}"
            needs_render = True
            continue

        if cmd == "flip":
            flipped = not flipped
            status_note = f"{CYAN}Papan diputar.{RESET}"
            needs_render = True
            continue

        if cmd in ("u", "undo"):
            plies_needed = 2 if len(board.move_history) >= 2 else 0
            if len(board.move_history) == 1 and board.turn != player_color:
                plies_needed = 1
            if plies_needed == 0:
                print(f"{YELLOW}Belum ada langkah kamu yang bisa di-undo.{RESET}")
                continue
            for _ in range(plies_needed):
                board.unmake_move(pop_history=True)
            tracker.pop_last_turn()
            status_note = f"{YELLOW}↶ Langkah terakhir dibatalkan (Undo).{RESET}"
            bot_message = None
            needs_render = True
            continue

        if cmd in ("h", "hint"):
            sys.stdout.write(f"{DIM}Mencari saran langkah terbaik...{RESET}")
            sys.stdout.flush()
            hint_res = ai.get_hint(board)
            if sys.stdout.isatty():
                sys.stdout.write("\r\033[K")
            else:
                print()
            if hint_res.move:
                h_san = board.move_to_san(hint_res.move)
                pv_sans = ai.extract_pv(board, hint_res.move, max_len=5)
                pv_str = f"\n  {DIM}Rencana lanjutan: {' → '.join(pv_sans)}{RESET}" if len(pv_sans) > 1 else ""
                ev_bar = render_eval_bar(hint_res.score_cp, board.turn)
                src = "langkah buku" if hint_res.from_book else "rekomendasi"
                highlight_origin = move_from(hint_res.move)
                highlight_targets = {move_to(hint_res.move)}
                status_note = f"{BOLD}{GREEN}💡 Saran terbaik: {h_san}{RESET} {DIM}({src}){RESET}  {ev_bar}{pv_str}"
                needs_render = True
            continue

        if cmd in ("coach", "saran", "analyze", "analisa", "tips"):
            sys.stdout.write(f"{DIM}Pelatih sedang memperhatikan papan...{RESET}")
            sys.stdout.flush()
            adv = ai.coach_advice(board)
            if sys.stdout.isatty():
                sys.stdout.write("\r\033[K")
            else:
                print()
            best_mv = int(adv["best_move"])
            if best_mv:
                highlight_origin = move_from(best_mv)
                highlight_targets = {move_to(best_mv)}
            pv_list = list(adv["pv"])
            tips_list = list(adv["tips"])
            ev_bar = render_eval_bar(int(adv["score_cp"]), board.turn)
            note_lines = [
                f"{BOLD}{CYAN}♟ SARAN PELATIH{RESET}  {ev_bar}",
                f"  Coba langkah: {BOLD}{GREEN}{adv['best_san']}{RESET}"
                + (f"  {DIM}Lanjutan: {' → '.join(pv_list)}{RESET}" if len(pv_list) > 1 else ""),
            ]
            for tip in tips_list:
                note_lines.append(f"  {YELLOW}• {tip}{RESET}")
            if not tips_list:
                note_lines.append(f"  {DIM}• Posisi cukup rapi — jaga pusat dan kembangkan perwira.{RESET}")
            status_note = "\n".join(note_lines)
            needs_render = True
            continue

        if cmd in ("m", "moves"):
            matched, origin, targets = _filter_legal_moves(board, arg)
            if targets:
                highlight_origin = origin
                highlight_targets = targets
                status_note = _format_moves_list(board, matched, arg)
                needs_render = True
            else:
                print(_format_moves_list(board, matched, arg))
            continue

        if cmd == "eval":
            if arg.lower() in ("on", "off"):
                show_eval = arg.lower() == "on"
                profile["show_eval"] = show_eval
                save_profile(profile)
                status_note = f"{CYAN}Bar Posisi: {'NYALA' if show_eval else 'MATI'}{RESET}"
                needs_render = True
            else:
                ev_res = ai.get_hint(board, think_time=0.50)
                last_eval_cp = ev_res.score_cp
                last_eval_side = board.turn
                pv_sans = ai.extract_pv(board, ev_res.move, max_len=5) if ev_res.move else []
                pv_txt = f"  {DIM}Lanjutan: {' → '.join(pv_sans)}{RESET}" if pv_sans else ""
                print(f"Keunggulan posisi: {render_eval_bar(ev_res.score_cp, board.turn)}{pv_txt}")
            continue

        if cmd in ("dna", "gaya", "profil"):
            print()
            print(render_dna_lab(profile))
            print()
            continue

        if cmd in ("history", "pgn"):
            print(_format_pgn_history(board))
            continue

        if cmd == "fen":
            print(f"{CYAN}FEN:{RESET} {board.fen()}")
            continue

        if cmd == "export":
            w_name = "Kamu" if player_color == WHITE else active_bot.name
            b_name = active_bot.name if player_color == WHITE else "Kamu"
            w_elo = str(profile.get("adaptive_elo", "?")) if player_color == WHITE else str(active_bot.elo)
            b_elo = str(active_bot.elo) if player_color == WHITE else str(profile.get("adaptive_elo", "?"))
            out_p = export_pgn_file(
                board, arg, w_name, b_name, w_elo, b_elo,
                eco=opening_eco or None, opening=opening_name or None,
            )
            print(f"{GREEN}✔ PGN berhasil diekspor ke: {out_p}{RESET}")
            continue

        if cmd == "think":
            if arg.lower() in ("default", "reset", "off", "0"):
                think_override = None
                profile["think_override"] = None
                save_profile(profile)
                print(f"{GREEN}Waktu berpikir AI kembali ke default tiap bot.{RESET}")
            else:
                try:
                    sec = float(arg)
                    if not (0.05 <= sec <= 15.0):
                        raise ValueError
                    think_override = sec
                    profile["think_override"] = sec
                    save_profile(profile)
                    print(f"{GREEN}Batas waktu berpikir AI diset ke {sec:.2f} detik.{RESET}")
                except ValueError:
                    print(f"{RED}Format: think <detik 0.05 - 15> atau 'think default'{RESET}")
            continue

        if cmd == "save":
            slot = arg or "autosave"
            anchor_k = (
                adaptive.anchor_bot.key
                if (is_adaptive and adaptive is not None and adaptive.anchor_bot is not None)
                else None
            )
            p = save_game(
                name=slot,
                board=board,
                player_color=player_color,
                bot_key=bot.key,
                bot_name=active_bot.name,
                bot_elo=active_bot.elo,
                is_adaptive=is_adaptive,
                adaptive_elo=adaptive.elo if adaptive else active_bot.elo,
                adaptive_start_elo=adaptive.start_elo if adaptive else active_bot.elo,
                adaptive_anchor_key=anchor_k,
            )
            print(f"{GREEN}✔ Permainan disimpan sebagai '{p.stem}' ({len(board.move_history)} ply).{RESET}")
            continue

        if cmd == "saves":
            saves = list_saves()
            if not saves:
                print(f"{YELLOW}Belum ada save game.{RESET}")
            else:
                print(f"{BOLD}{CYAN}Daftar Save Game:{RESET}")
                for sv in saves:
                    print(
                        f"  • {GREEN}{sv['name']}{RESET} — vs {sv.get('bot_name')} ({sv.get('moves', 0)} ply, {sv.get('saved_at', '')})"
                    )
            continue

        if cmd == "load":
            loaded = None
            if arg:
                try:
                    loaded = load_game(arg)
                except FileNotFoundError as exc:
                    print(f"{RED}{exc}{RESET}")
                    continue
            else:
                loaded = _pick_saved_game()
            if loaded is not None:
                board, meta = loaded
                player_color = WHITE if meta.get("player_color", "white") == "white" else BLACK
                is_adaptive = bool(meta.get("is_adaptive", False))
                if is_adaptive:
                    anchor_k = meta.get("adaptive_anchor_key")
                    anchor_b = BOT_BY_KEY.get(str(anchor_k)) if anchor_k is not None else None
                    if anchor_b is not None:
                        brain = get_bot_brain(profile, anchor_b.bot_id, anchor_b.elo)
                        adaptive = EvolvingAdaptiveController(
                            int(meta.get("adaptive_elo", anchor_b.elo)), dna, brain, anchor_bot=anchor_b
                        )
                    else:
                        brain = get_brain(profile)
                        adaptive = EvolvingAdaptiveController(int(meta.get("adaptive_elo", 1000)), dna, brain)
                    adaptive.start_elo = int(meta.get("adaptive_start_elo", adaptive.elo))
                    active_bot = adaptive.profile()
                else:
                    bot = BOT_BY_KEY.get(str(meta.get("bot_key", "4")), bot)
                    active_bot = bot
                    brain = None
                _update_opening()
                status_note = f"{GREEN}✔ Save '{meta.get('name')}' berhasil dimuat!{RESET}"
                bot_message = active_bot.say("intro")
                needs_render = True
            continue

        if cmd == "draw":
            ev = ai.evaluate(board)
            ai_score = -ev
            if ai_score <= -30 or (len(board.move_history) >= 30 and ai_score <= 25):
                return _finish_game("draw", f"{active_bot.name} menerima tawaran remis", "1/2-1/2")
            print(f'{active_bot.color_code}{active_bot.name}:{RESET} "Belum saatnya remis! Ayo lanjut tanding!"')
            continue

        if cmd == "resign":
            confirm = _safe_input(f"{RED}Yakin mau menyerah?{RESET} [y/N]: ")
            if confirm and confirm.strip().lower() in ("y", "yes", "ya"):
                res_code = "0-1" if player_color == WHITE else "1-0"
                return _finish_game("loss", "Kamu menyerah", res_code)
            continue

        if not from_arc:
            try:
                mv = board.parse_move(cmd_raw)
            except PromotionRequiredError as prom:
                picked = _prompt_promotion(board, prom.moves)
                if picked is None:
                    continue
                mv = picked
            except IllegalMoveError as exc:
                print(f"{BOLD}{RED}Illegal!{RESET} {RED}{exc}{RESET}")
                continue


        if white_clock is not None and black_clock is not None:
            if player_color == WHITE:
                white_clock -= pl_elapsed
                if white_clock <= 0:
                    return _finish_game("loss", "Waktu kamu habis (Flag)", "0-1")
                white_clock += inc_sec
            else:
                black_clock -= pl_elapsed
                if black_clock <= 0:
                    return _finish_game("loss", "Waktu kamu habis (Flag)", "1-0")
                black_clock += inc_sec


        cp_loss, player_eval_after, best_mv, book_hit = ai.evaluate_player_move(board, mv)
        best_san = board.move_to_san(best_mv) if best_mv else ""

        captured_by_player = board.squares[move_to(mv)]
        mv_flag = move_flag(mv)
        is_ep_player = mv_flag == FLAG_EN_PASSANT
        is_cap = captured_by_player != EMPTY or is_ep_player
        is_castle = mv_flag in (FLAG_CASTLE_KING, FLAG_CASTLE_QUEEN)
        is_promo = move_promo(mv) != 0
        prev_op_name = opening_name

        player_san = board.move_to_san(mv)
        board.make_move(mv, record_san=True)
        _update_opening()
        gave_check = board.in_check()

        last_eval_cp = player_eval_after
        last_eval_side = player_color
        eval_white_cp = player_eval_after if player_color == WHITE else -player_eval_after

        grade = tracker.record_player_move(
            ply=len(board.move_history),
            san=player_san,
            cp_loss=cp_loss,
            best_san=best_san,
            is_book=book_hit,
            is_capture=is_cap,
            is_check=gave_check,
            is_castle=is_castle,
            is_promo=is_promo,
            eval_white_cp=eval_white_cp,
            player_eval_after=player_eval_after,
        )

        if cp_loss <= 35:
            hot_streak += 1
        else:
            hot_streak = 0

        if gave_check:
            ring_bell(sound_bell)

        tier_notice = ""
        if is_adaptive and adaptive is not None:
            adaptive_delta, new_tier = adaptive.update_after_player_move(cp_loss, len(board.move_history))
            active_bot = adaptive.profile()
            if new_tier is not None:
                direction = "naik" if adaptive_delta >= 0 else "turun"
                tier_notice = f"\n  {MAGENTA}★ Level adaptif {direction} setara {new_tier.name} (Elo {adaptive.elo})!{RESET}"

        pieces_left_pl = sum(1 for sq in board.squares if sq != EMPTY)
        p_line = react_to_player_move(
            bot=active_bot,
            san=player_san,
            ply=len(board.move_history),
            captured_piece=PAWN if is_ep_player else captured_by_player,
            is_ep=is_ep_player,
            is_castle_k=(mv_flag == FLAG_CASTLE_KING),
            is_castle_q=(mv_flag == FLAG_CASTLE_QUEEN),
            promo_piece=move_promo(mv),
            gave_check=gave_check,
            grade_code=grade.code,
            opening_name=opening_name,
            opening_just_changed=(opening_name != prev_op_name),
            from_arc=from_arc,
            pieces_left=pieces_left_pl,
        )
        if p_line is not None:
            bot_message = p_line

        if from_arc:
            rem_txt = f"sisa {len(arc_queue)}" if arc_queue else "selesai"
            arc_tag = f"{MAGENTA}⚡ [ARC · {rem_txt}]{RESET} "
        else:
            arc_tag = ""

        if show_grades:
            callout = format_move_callout(grade, player_san, best_san)
            status_note = f"{arc_tag}{callout}{tier_notice}"
        else:
            status_note = f"{arc_tag}{GREEN}✔ Langkahmu: {BOLD}{player_san}{RESET}{tier_notice}"
        needs_render = True


def run_gauntlet_mode(ai: ChessAI, profile: Dict[str, Any]) -> str:
    while True:
        stage = int(profile.get("gauntlet_stage", 0))
        if stage >= len(CORE_BOTS):
            stage = 0
            profile["gauntlet_stage"] = 0
            save_profile(profile)

        clear_screen()
        print(f"{BOLD}{MAGENTA}╔══════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{MAGENTA}║{RESET}        {BOLD}{WHITE_FG}♟  TURNAMEN BERUNTUN (10 BOT){RESET}         {BOLD}{MAGENTA}║{RESET}")
        print(f"{BOLD}{MAGENTA}╚══════════════════════════════════════════════╝{RESET}")
        print()
        for idx, b in enumerate(CORE_BOTS):
            if idx < stage:
                mark = f"{GREEN}✔ MENANG{RESET}"
            elif idx == stage:
                mark = f"{BOLD}{YELLOW}◀ LAWAN BERIKUTNYA{RESET}"
            else:
                mark = f"{GRAY}🔒 Terkunci{RESET}"
            print(f"  Babak {idx + 1:>2}/10 · {b.name:<10} (Elo {b.elo:>4})  {mark}")
        print()
        ans = _safe_input(
            f"[{BOLD}Enter{RESET}] Lawan {BOLD}{CORE_BOTS[stage].name}{RESET}  [{BOLD}R{RESET}] Ulang  [{BOLD}M{RESET}] Menu: "
        )
        if ans is None:
            return "quit"
        low = ans.strip().lower()
        if low in ("m", "menu", "q", "quit"):
            return "menu"
        if low == "r":
            profile["gauntlet_stage"] = 0
            save_profile(profile)
            continue

        color = _choose_player_color()
        if color is None:
            return "quit"

        nav, outcome = play_match(
            ai=ai,
            profile=profile,
            player_color=color,
            bot=CORE_BOTS[stage],
            is_adaptive=False,
            gauntlet_stage=stage,
        )
        if nav == "quit":
            return "quit"
        if nav == "menu":
            return "menu"

        if outcome == "win":
            stage += 1
            if stage >= len(CORE_BOTS):
                profile["gauntlet_stage"] = 0
                profile["gauntlet_clears"] = int(profile.get("gauntlet_clears", 0)) + 1
                unlock_achievement(profile, "gauntlet_clear")
                save_profile(profile)
                print(f"\n{BOLD}{YELLOW}🏆🔥 SELAMAT!! KAMU JUARA TURNAMEN 10 BOT (10/10)!! 🔥🏆{RESET}")
                _safe_input("Tekan Enter untuk kembali ke menu...")
                return "menu"
            else:
                profile["gauntlet_stage"] = stage
                save_profile(profile)
        elif outcome == "loss":
            print(f"{RED}Kamu gugur di Babak {stage + 1} ({CORE_BOTS[stage].name}). Coba lagi kapan saja!{RESET}")

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chessportable",
        description=f"ChessPortable v{__version__} by {__author__} - Full CLI Pure-Python Chess for Termux.",
    )
    p.add_argument("-v", "--version", action="version", version=f"chessportable {__version__} by {__author__}")
    p.add_argument("--ascii", action="store_true", help="Gunakan tampilan papan ASCII berwarna.")
    p.add_argument("--plain", action="store_true", help="Gunakan tampilan papan ASCII klasik.")
    p.add_argument("--theme", choices=tuple(THEME_BY_ID.keys()), default=None, help="Pilih tema warna papan.")
    p.add_argument("--bot", type=str, default=None, help="Langsung lawan bot nomor 0-19 (misal: --bot 4 atau --bot 13).")
    p.add_argument("--adaptive", nargs="?", const="default", default=None, help="Langsung main Adaptif (utama atau per-bot 0-19, mis: --adaptive 4).")
    p.add_argument("--puzzles", action="store_true", help="Langsung masuk mode Tactical Puzzles.")
    p.add_argument("--gauntlet", action="store_true", help="Langsung masuk mode Gauntlet Boss Rush.")
    p.add_argument("--color", choices=("white", "black", "random"), default=None, help="Pilih warna langsung.")
    return p

def _spawn_adaptive_bot(
    profile: Dict[str, Any], anchor_bot: BotProfile, fresh: bool = False
) -> Tuple[EvolvingAdaptiveController, BotProfile]:
    if fresh:
        reset_bot_adaptive(profile, anchor_bot.bot_id, anchor_bot.elo)
    st = get_bot_adaptive_state(profile, anchor_bot.bot_id, anchor_bot.elo)
    b_brain = get_bot_brain(profile, anchor_bot.bot_id, anchor_bot.elo)
    ctrl = EvolvingAdaptiveController(
        int(st["elo"]), get_dna(profile), b_brain, anchor_bot=anchor_bot
    )
    return ctrl, ctrl.profile()


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    profile = load_profile()
    ai = ChessAI()

    if args.ascii:
        profile["board_style"] = "ascii"
    elif args.plain:
        profile["board_style"] = "ascii_plain"
    if args.theme:
        profile["theme"] = args.theme

    if args.puzzles:
        run_puzzles_mode(profile)
        return 0
    if args.gauntlet:
        run_gauntlet_mode(ai, profile)
        return 0

    pending_selection: Optional[Tuple[str, Any]] = None
    if args.adaptive is not None:
        if args.adaptive == "default":
            pending_selection = ("adaptive_global", int(profile.get("adaptive_elo", 1000)))
        elif args.adaptive in BOT_BY_KEY:
            pending_selection = ("adaptive_bot", (BOT_BY_KEY[args.adaptive], False))
        elif args.adaptive.isdigit():
            pending_selection = ("adaptive_global", max(100, min(4000, int(args.adaptive))))
    elif args.bot is not None and args.bot in BOT_BY_KEY:
        pending_selection = ("bot", BOT_BY_KEY[args.bot])

    while True:
        loaded_board: Optional[Board] = None
        selected_bot: Optional[BotProfile] = None
        is_adaptive = False
        adaptive_ctrl: Optional[EvolvingAdaptiveController] = None
        player_color: Optional[int] = None

        if pending_selection is not None:
            action, payload = pending_selection
            pending_selection = None
            if action == "bot":
                selected_bot = payload
            elif action == "adaptive_bot":
                anchor_b, fresh = payload
                is_adaptive = True
                adaptive_ctrl, selected_bot = _spawn_adaptive_bot(profile, anchor_b, fresh=fresh)
            elif action == "adaptive_global":
                is_adaptive = True
                adaptive_ctrl = EvolvingAdaptiveController(int(payload), get_dna(profile), get_brain(profile))
                selected_bot = adaptive_ctrl.profile()
            if args.color == "white":
                player_color = WHITE
            elif args.color == "black":
                player_color = BLACK
            elif args.color == "random":
                player_color = random.choice((WHITE, BLACK))
        else:
            clear_screen()
            print(render_main_menu(profile))
            print()
            while True:
                raw = _safe_input(f"{BOLD}{CYAN}> {RESET}")
                if raw is None:
                    print(f"{DIM}Sampai jumpa di papan catur!{RESET}")
                    return 0
                action, payload = _parse_menu_selection(raw, profile)
                if action == "quit":
                    print(f"{DIM}Sampai jumpa di papan catur!{RESET}")
                    return 0
                if action == "extra_bots":
                    clear_screen()
                    print(render_extra_bots_menu(profile))
                    print()
                    sub_raw = _safe_input(f"{BOLD}{YELLOW}Pilih Bot Ekstra (10-19 / A 10-19 / Enter=Kembali): {RESET}")
                    if sub_raw is None:
                        print(f"{DIM}Sampai jumpa di papan catur!{RESET}")
                        return 0
                    sub_clean = sub_raw.strip()
                    if not sub_clean:
                        break
                    sub_act, sub_pay = _parse_menu_selection(sub_clean, profile)
                    if sub_act == "bot":
                        selected_bot = sub_pay
                        print(
                            f"\n{selected_bot.color_code}[✦]{RESET} Kamu memilih {BOLD}{selected_bot.name}{RESET} "
                            f"(Elo {selected_bot.elo} · {selected_bot.title})"
                        )
                        break
                    if sub_act == "adaptive_bot":
                        anchor_b, fresh = sub_pay
                        is_adaptive = True
                        adaptive_ctrl, selected_bot = _spawn_adaptive_bot(profile, anchor_b, fresh=fresh)
                        stage, _ = adaptive_ctrl.brain.stage_info()
                        reset_note = f" {YELLOW}(Reset ke Elo {anchor_b.elo}){RESET}" if fresh else ""
                        print(
                            f"\n{MAGENTA}★ Lawan Adaptif: {anchor_b.color_code}[✦]{RESET} "
                            f"{BOLD}Adaptif·{anchor_b.name}{RESET}{reset_note}"
                        )
                        print(
                            f"  Elo Saat Ini: {BOLD}{adaptive_ctrl.elo}{RESET} · "
                            f"{CYAN}{stage}{RESET} · Gaya: {YELLOW}{adaptive_ctrl.counter_trait}{RESET}"
                        )
                        break
                    if sub_act == "adaptive_global":
                        is_adaptive = True
                        start_elo = int(sub_pay)
                        adaptive_ctrl = EvolvingAdaptiveController(start_elo, get_dna(profile), get_brain(profile))
                        selected_bot = adaptive_ctrl.profile()
                        break
                    print(f"{YELLOW}Pilihan tidak ditemukan, kembali ke menu utama.{RESET}")
                    break
                if action == "records":
                    clear_screen()
                    print(render_records(profile))
                    print()
                    _safe_input(f"{DIM}Tekan Enter untuk kembali ke menu...{RESET}")
                    break
                if action == "adaptive_roster":
                    clear_screen()
                    print(render_adaptive_roster(profile))
                    print()
                    _safe_input(f"{DIM}Tekan Enter untuk kembali ke menu...{RESET}")
                    break
                if action == "dna":
                    run_dna_lab(profile)
                    break
                if action == "settings":
                    run_settings_loop(profile)
                    break
                if action == "puzzles":
                    run_puzzles_mode(profile)
                    break
                if action == "gauntlet":
                    nav = run_gauntlet_mode(ai, profile)
                    if nav == "quit":
                        return 0
                    break
                if action == "pvp":
                    while True:
                        nav = play_pvp_match(profile)
                        if nav == "rematch":
                            continue
                        if nav == "quit":
                            return 0
                        break
                    break
                if action == "help":
                    print()
                    print(render_help())
                    print()
                    continue
                if action == "style":
                    cur = profile.get("board_style", "unicode")
                    if payload in ("unicode", "ascii"):
                        nxt = payload
                    else:
                        nxt = STYLE_CYCLE[(STYLE_CYCLE.index(cur) + 1) % len(STYLE_CYCLE)] if cur in STYLE_CYCLE else "unicode"
                    profile["board_style"] = nxt
                    save_profile(profile)
                    print(f"{GREEN}Tampilan papan diset ke: {STYLE_LABELS[nxt]}{RESET}")
                    continue
                if action == "load":
                    res = _pick_saved_game()
                    if res is None:
                        continue
                    loaded_board, meta = res
                    player_color = WHITE if meta.get("player_color", "white") == "white" else BLACK
                    is_adaptive = bool(meta.get("is_adaptive", False))
                    if is_adaptive:
                        anchor_k = meta.get("adaptive_anchor_key")
                        anchor_b = BOT_BY_KEY.get(str(anchor_k)) if anchor_k is not None else None
                        if anchor_b is not None:
                            b_brain = get_bot_brain(profile, anchor_b.bot_id, anchor_b.elo)
                            adaptive_ctrl = EvolvingAdaptiveController(
                                int(meta.get("adaptive_elo", anchor_b.elo)),
                                get_dna(profile),
                                b_brain,
                                anchor_bot=anchor_b,
                            )
                        else:
                            adaptive_ctrl = EvolvingAdaptiveController(
                                int(meta.get("adaptive_elo", 1000)), get_dna(profile), get_brain(profile)
                            )
                        adaptive_ctrl.start_elo = int(meta.get("adaptive_start_elo", adaptive_ctrl.elo))
                        selected_bot = adaptive_ctrl.profile()
                    else:
                        selected_bot = BOT_BY_KEY.get(str(meta.get("bot_key", "4")), BOTS[3])
                    break
                if action == "bot":
                    selected_bot = payload
                    print(
                        f"\n{selected_bot.color_code}[✦]{RESET} Kamu memilih {BOLD}{selected_bot.name}{RESET} "
                        f"(Elo {selected_bot.elo} · {selected_bot.title})"
                    )
                    break
                if action == "adaptive_bot":
                    anchor_b, fresh = payload
                    is_adaptive = True
                    adaptive_ctrl, selected_bot = _spawn_adaptive_bot(profile, anchor_b, fresh=fresh)
                    stage, _ = adaptive_ctrl.brain.stage_info()
                    reset_note = f" {YELLOW}(Reset ke Elo {anchor_b.elo}){RESET}" if fresh else ""
                    print(
                        f"\n{MAGENTA}★ Lawan Adaptif: {anchor_b.color_code}[✦]{RESET} "
                        f"{BOLD}Adaptif·{anchor_b.name}{RESET}{reset_note}"
                    )
                    print(
                        f"  Elo Saat Ini: {BOLD}{adaptive_ctrl.elo}{RESET} (Dasar {anchor_b.elo}) · "
                        f"{CYAN}{stage}{RESET} · Gaya: {YELLOW}{adaptive_ctrl.counter_trait}{RESET}"
                    )
                    break
                if action == "adaptive_global":
                    is_adaptive = True
                    start_elo = int(payload)
                    dna = get_dna(profile)
                    brain = get_brain(profile)
                    adaptive_ctrl = EvolvingAdaptiveController(start_elo, dna, brain)
                    selected_bot = adaptive_ctrl.profile()
                    base_tier = nearest_bot_for_elo(start_elo)
                    stage, _ = brain.stage_info()
                    print(
                        f"\n{MAGENTA}★ Mode Adaptif Utama aktif!{RESET} "
                        f"Mulai dari Elo {BOLD}{start_elo}{RESET} (setara {base_tier.name}) · "
                        f"{CYAN}{stage}{RESET} · Gaya: {YELLOW}{adaptive_ctrl.counter_trait}{RESET}"
                    )
                    break
                print(f"{RED}{payload}{RESET}")

        if selected_bot is None:
            continue

        if player_color is None:
            player_color = _choose_player_color()
            if player_color is None:
                return 0

        while True:
            outcome_nav, _ = play_match(
                ai=ai,
                profile=profile,
                player_color=player_color,
                bot=selected_bot,
                is_adaptive=is_adaptive,
                adaptive=adaptive_ctrl,
                board=loaded_board,
            )
            loaded_board = None
            if outcome_nav == "rematch":
                if is_adaptive and adaptive_ctrl is not None:

                    if adaptive_ctrl.anchor_bot is not None:
                        adaptive_ctrl, selected_bot = _spawn_adaptive_bot(
                            profile, adaptive_ctrl.anchor_bot, fresh=False
                        )
                    else:
                        adaptive_ctrl = EvolvingAdaptiveController(
                            adaptive_ctrl.elo, get_dna(profile), get_brain(profile)
                        )
                        selected_bot = adaptive_ctrl.profile()
                continue
            if outcome_nav == "quit":
                print(f"{DIM}Terima kasih sudah main ChessPortable v{__version__}!{RESET}")
                return 0
            break
