from __future__ import annotations

import os
import shutil
import sys
from typing import Any, Dict, List, Optional, Set

from . import __author__, __version__
from .ai import MATE_SCORE, MATE_THRESHOLD
from .board import (
    BISHOP,
    BLACK,
    Board,
    EMPTY,
    FILES,
    KING,
    KNIGHT,
    PAWN,
    PIECE_TO_CHAR,
    QUEEN,
    ROOK,
    WHITE,
    move_from,
    move_to,
)
from .bots import BOTS, BotProfile
from .evolving import EvolvingBrain, MatchTracker, PlayerDNA
from .storage import (
    ACHIEVEMENTS,
    TIME_CONTROLS,
    get_bot_adaptive_state,
    get_bot_record_str,
    get_brain,
    get_dna,
    is_bot_defeated,
)
from .themes import THEMES, get_theme


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE_FG = "\033[97m"
GRAY = "\033[90m"

UNICODE_SOLID = {
    PAWN: "♟",
    KNIGHT: "♞",
    BISHOP: "♝",
    ROOK: "♜",
    QUEEN: "♛",
    KING: "♚",
}

UNICODE_OUTLINE = {
    PAWN: "♙",
    KNIGHT: "♘",
    BISHOP: "♗",
    ROOK: "♖",
    QUEEN: "♕",
    KING: "♔",
}

def clear_screen() -> None:
    if sys.stdout.isatty():
        os.system("clear" if os.name != "nt" else "cls")


def terminal_width() -> int:
    try:
        return shutil.get_terminal_size((56, 24)).columns
    except OSError:
        return 56


def ring_bell(enabled: bool) -> None:
    if enabled and sys.stdout.isatty():
        sys.stdout.write("\a")
        sys.stdout.flush()

def format_clock(seconds: Optional[float]) -> str:
    if seconds is None:
        return ""
    s = max(0, int(seconds))
    mins, secs = divmod(s, 60)
    txt = f"{mins:02d}:{secs:02d}"
    if s <= 10:
        return f"{BOLD}{RED}⏱ {txt}{RESET}"
    if s <= 30:
        return f"{BOLD}{YELLOW}⏱ {txt}{RESET}"
    return f"{CYAN}⏱ {txt}{RESET}"


def format_eval_score(score_cp: int, side_to_move: int) -> str:
    white_score = score_cp if side_to_move == WHITE else -score_cp
    if abs(white_score) >= MATE_THRESHOLD:
        plies = max(1, MATE_SCORE - abs(white_score))
        moves_to_mate = (plies + 1) // 2
        sign = "+" if white_score > 0 else "-"
        return f"{sign}M{moves_to_mate}"
    return f"{white_score / 100.0:+.2f}"


def render_eval_bar(score_cp: int, side_to_move: int, width: int = 20) -> str:
    white_score = score_cp if side_to_move == WHITE else -score_cp
    if abs(white_score) >= MATE_THRESHOLD:
        ratio = 1.0 if white_score > 0 else 0.0
    else:
        clamped = max(-800, min(800, white_score))
        ratio = 0.5 + (clamped / 1600.0)
    w_cells = max(0, min(width, round(ratio * width)))
    b_cells = width - w_cells
    bar = f"{WHITE_FG}{'█' * w_cells}{GRAY}{'░' * b_cells}{RESET}"
    label = format_eval_score(score_cp, side_to_move)
    return f"[{bar}] {BOLD}{label}{RESET}"


def render_stat_bar(value: float, max_val: float = 100.0, width: int = 16, color: str = CYAN) -> str:
    ratio = max(0.0, min(1.0, value / max(1.0, max_val)))
    filled = round(ratio * width)
    return f"{color}{'█' * filled}{GRAY}{'░' * (width - filled)}{RESET}"

def _format_captured(pieces: List[int], style: str) -> str:
    if not pieces:
        return f"{GRAY}-{RESET}"
    if style == "unicode":
        return "".join(
            UNICODE_OUTLINE[abs(p)] if p > 0 else UNICODE_SOLID[abs(p)] for p in pieces
        )
    return "".join(PIECE_TO_CHAR[p] for p in pieces)


def render_main_menu(profile: Dict[str, Any]) -> str:
    theme = get_theme(profile.get("theme", "sage"))
    brain = get_brain(profile)
    stage, _ = brain.stage_info()
    adaptive_elo = int(profile.get("adaptive_elo", 1000))
    tc_key = profile.get("time_control", "unlimited")
    tc_label = TIME_CONTROLS.get(tc_key, TIME_CONTROLS["unlimited"])[0]
    gauntlet_stage = int(profile.get("gauntlet_stage", 0))
    puzzle_elo = int(profile.get("puzzle_rating", 1000))
    bot_adaptive_map = profile.get("bot_adaptive", {})

    lines: List[str] = []
    lines.append(f"{BOLD}{theme.accent}╔══════════════════════════════════════════════════╗{RESET}")
    lines.append(
        f"{BOLD}{theme.accent}║{RESET}  {BOLD}{WHITE_FG}♟  C H E S S P O R T A B L E  v{__version__}{RESET} "
        f"{DIM}by {__author__}{RESET}  {BOLD}{theme.accent}║{RESET}"
    )
    lines.append(f"{BOLD}{theme.accent}╚══════════════════════════════════════════════════╝{RESET}")
    lines.append("")
    lines.append(f"{BOLD}{WHITE_FG}Hi! Choose your ai!{RESET}")

    for bot in BOTS:
        defeated = is_bot_defeated(profile, bot.bot_id)
        badge = f"{BOLD}{YELLOW}[★]{RESET}" if defeated else f"{bot.color_code}[✦]{RESET}"
        rec = get_bot_record_str(profile, bot.bot_id)
        rec_part = f" {DIM}{rec}{RESET}" if rec else ""

        evo_part = ""
        ba = bot_adaptive_map.get(bot.bot_id)
        if isinstance(ba, dict):
            bgen = int(ba.get("brain", {}).get("generation", 1))
            belo = int(ba.get("elo", bot.elo))
            if bgen > 1 or belo != bot.elo:
                evo_part = f" {MAGENTA}🧬A:{belo}(G{bgen}){RESET}"
        lines.append(
            f"({BOLD}{bot.key}{RESET}) {badge} {BOLD}{bot.name}{RESET} - Elo {bot.elo}{rec_part}{evo_part}"
        )

    lines.append(f"{CYAN}Please Type A for adaptive version{RESET}")
    lines.append(
        f"{DIM}Adaptive: {RESET}{BOLD}{CYAN}A{RESET}{DIM} (Global Elo {adaptive_elo} · 🧬G{brain.generation} {stage})  |  "
        f"{RESET}{BOLD}{CYAN}A 0-9{RESET}{DIM} (Adaptive tiap bot!)  |  {RESET}{BOLD}A list{RESET}"
    )
    lines.append(
        f"{DIM}Mode: {RESET}{BOLD}{MAGENTA}G{RESET}{DIM}=Gauntlet({gauntlet_stage}/10)  "
        f"{RESET}{BOLD}{YELLOW}P{RESET}{DIM}=Puzzle({puzzle_elo})  "
        f"{RESET}{BOLD}{GREEN}2P{RESET}{DIM}=2-Player  "
        f"{RESET}{BOLD}D{RESET}{DIM}=DNA  "
        f"{RESET}{BOLD}T{RESET}{DIM}=Tema&Jam({tc_label.split()[0]})  "
        f"{RESET}{BOLD}L{RESET}{DIM}=Load  "
        f"{RESET}{BOLD}R{RESET}{DIM}=Rekor  "
        f"{RESET}{BOLD}Q{RESET}{DIM}=Keluar{RESET}"
    )
    return "\n".join(lines)


def render_adaptive_roster(profile: Dict[str, Any]) -> str:

    brain = get_brain(profile)
    stage, _ = brain.stage_info()
    g_elo = int(profile.get("adaptive_elo", 1000))
    g_peak = int(profile.get("adaptive_peak", 1000))

    lines: List[str] = [
        f"{BOLD}{CYAN}═══ ADAPTIVE EVOLVING ROSTER (A & A 0-9) ═══{RESET}",
        f"  {BOLD}{CYAN}A{RESET}      Global Adaptive · Elo {BOLD}{g_elo}{RESET} (Peak {g_peak}) · 🧬 Gen {brain.generation} {stage}",
        "",
    ]
    for bot in BOTS:
        st = get_bot_adaptive_state(profile, bot.bot_id, bot.elo)
        b_brain = EvolvingBrain(st.get("brain"))
        b_stage, _ = b_brain.stage_info()
        w, d, l = st.get("wins", 0), st.get("draws", 0), st.get("losses", 0)
        elo_now = int(st.get("elo", bot.elo))
        delta = elo_now - bot.elo
        d_str = f"{GREEN}+{delta}{RESET}" if delta > 0 else (f"{RED}{delta}{RESET}" if delta < 0 else f"{DIM}±0{RESET}")
        rec = f"{GREEN}{w}W{RESET}-{YELLOW}{d}D{RESET}-{RED}{l}L{RESET}" if (w + d + l) else f"{GRAY}Baru{RESET}"
        lines.append(
            f"  {BOLD}{CYAN}A {bot.key}{RESET}    {bot.color_code}[✦]{RESET} {BOLD}{bot.name:<10}{RESET} "
            f"Elo {BOLD}{elo_now:>4}{RESET} ({d_str}) · 🧬G{b_brain.generation} {b_stage:<9} {rec}"
        )
    lines.append("")
    lines.append(f"{DIM}Ketik 'A <0-9>' buat tanding (mis: A 1, A 4, A 0) atau 'A <0-9> fresh' buat reset bot tsb.{RESET}")
    return "\n".join(lines)

def render_move_review(tracker: MatchTracker) -> str:

    if not tracker.player_moves:
        return f"{DIM}Belum ada langkah untuk direview.{RESET}"
    lines: List[str] = [
        f"{BOLD}{CYAN}═══ REVIEW LANGKAH PER LANGKAH ═══{RESET}",
        f"  {DIM}{'No':>3}  {'Langkah':<8} {'Grade':<15} {'CPL':>4}  Saran Terbaik{RESET}",
    ]
    for m in tracker.player_moves:
        mnum = (m.ply + 1) // 2
        g_txt = f"{m.grade.color}{m.grade.symbol} {m.grade.label}{RESET}"
        best_note = ""
        if m.cp_loss >= 45 and m.best_san and m.best_san != m.san:
            best_note = f"{GREEN}→ {m.best_san}{RESET}"
        elif m.cp_loss <= 18:
            best_note = f"{DIM}✓ top{RESET}"
        lines.append(
            f"  {mnum:>3}. {BOLD}{m.san:<8}{RESET} {g_txt:<24} {m.cp_loss:>4}  {best_note}"
        )
    return "\n".join(lines)

def render_dna_lab(profile: Dict[str, Any]) -> str:
    dna = get_dna(profile)
    brain = get_brain(profile)
    arch_name, arch_desc = dna.archetype()
    stage_name, stage_desc = brain.stage_info()
    trait, _, _, _ = brain.compute_counter_strategy(dna)

    lines: List[str] = [
        f"{BOLD}{MAGENTA}╔══════════════════════════════════════════════╗{RESET}",
        f"{BOLD}{MAGENTA}║{RESET}     {BOLD}{WHITE_FG}🧬  PLAYER DNA & EVOLVING AI LAB{RESET}         {BOLD}{MAGENTA}║{RESET}",
        f"{BOLD}{MAGENTA}╚══════════════════════════════════════════════╝{RESET}",
        "",
        f"{BOLD}{WHITE_FG}Profil Gaya Mainmu:{RESET} {BOLD}{CYAN}{arch_name}{RESET}",
        f"  {DIM}{arch_desc}{RESET}",
        f"  Game Dianalisis : {BOLD}{dna.games_analyzed}{RESET}  ·  Akurasi Rata-rata: {BOLD}{GREEN}{dna.avg_accuracy:.1f}%{RESET}",
        "",
        f"  Agresi    {render_stat_bar(dna.aggression, 100, 18, RED)} {dna.aggression:5.1f}",
        f"  Posisional{render_stat_bar(dna.positional, 100, 18, BLUE)} {dna.positional:5.1f}",
        f"  Taktik    {render_stat_bar(dna.tactical, 100, 18, YELLOW)} {dna.tactical:5.1f}",
        f"  Rokade    {render_stat_bar(dna.castle_rate, 100, 18, GREEN)} {dna.castle_rate:5.1f}%",
        "",
        f"  Fase Terkuat : {GREEN}{dna.strongest_phase()}{RESET}   ·   "
        f"Titik Lemah : {RED}{dna.weakest_phase()}{RESET}",
        f"  {DIM}ACPL -> Opening: {dna.opening_acpl:.0f} | Midgame: {dna.middlegame_acpl:.0f} | Endgame: {dna.endgame_acpl:.0f}{RESET}",
    ]

    top_op = dna.top_openings(3)
    if top_op:
        lines.append("")
        lines.append(f"{BOLD}Pembukaan Favoritmu:{RESET}")
        for sig, cnt in top_op:
            lines.append(f"  • {CYAN}{sig}{RESET} {DIM}({cnt}x){RESET}")

    avoid_cnt = sum(len(v) for v in brain.avoid_memory.values())
    trap_cnt = sum(len(v) for v in brain.trap_memory.values())
    lines.extend([
        "",
        f"{BOLD}{CYAN}═══ OTAK EVOLVING AI ═══{RESET}",
        f"  Generasi      : {BOLD}{MAGENTA}Gen {brain.generation} — {stage_name}{RESET} {DIM}({stage_desc}){RESET}",
        f"  Strategi Lawan: {BOLD}{YELLOW}{trait}{RESET}",
        f"  Memori Aktif  : {GREEN}{avoid_cnt}{RESET} pola jebakan dihindari · {RED}{trap_cnt}{RESET} senjata taktis disimpan",
        f"  Total Pelajaran: {BOLD}{brain.total_lessons}{RESET} pola telah dipelajari dari pertandinganmu",
    ])
    return "\n".join(lines)

def render_records(profile: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"{BOLD}{YELLOW}═══ REKOR, TROFI & MEDALI CHESSPORTABLE ═══{RESET}")
    defeated_count = sum(1 for b in BOTS if is_bot_defeated(profile, b.bot_id))
    ad_elo = profile.get("adaptive_elo", 1000)
    ad_peak = profile.get("adaptive_peak", 1000)
    ad_st = profile.get("adaptive_stats", {})
    puz_elo = profile.get("puzzle_rating", 1000)
    puz_cnt = len(profile.get("solved_puzzles", []))
    g_stage = profile.get("gauntlet_stage", 0)
    g_clears = profile.get("gauntlet_clears", 0)

    lines.append(f"  Bot Dikalahkan : {BOLD}{GREEN}{defeated_count}/{len(BOTS)}{RESET}   ·   Gauntlet: {MAGENTA}{g_stage}/10{RESET} (Clear: {g_clears}x)")
    lines.append(
        f"  Adaptive Elo   : {BOLD}{CYAN}{ad_elo}{RESET} (Peak {YELLOW}{ad_peak}{RESET}) · "
        f"{ad_st.get('wins', 0)}W-{ad_st.get('draws', 0)}D-{ad_st.get('losses', 0)}L"
    )
    lines.append(f"  Puzzle Rating  : {BOLD}{YELLOW}{puz_elo}{RESET} ({puz_cnt}/20 solved)")
    lines.append("")
    for bot in BOTS:
        st = profile.get("bot_stats", {}).get(bot.bot_id, {})
        w, d, l = st.get("wins", 0), st.get("draws", 0), st.get("losses", 0)
        mark = f"{BOLD}{YELLOW}[★]{RESET}" if w > 0 else f"{GRAY}[✦]{RESET}"
        status = (
            f"{GREEN}{w}W{RESET}-{YELLOW}{d}D{RESET}-{RED}{l}L{RESET}"
            if (w + d + l)
            else f"{GRAY}Belum tanding{RESET}"
        )
        lines.append(f"  {mark} {bot.name:<10} (Elo {bot.elo:>4})  {status}")

    owned = set(profile.get("achievements", []))
    lines.append("")
    lines.append(f"{BOLD}{CYAN}═══ ACHIEVEMENTS ({len(owned)}/{len(ACHIEVEMENTS)}) ═══{RESET}")
    for ach_id, (emoji, title, desc) in ACHIEVEMENTS.items():
        if ach_id in owned:
            lines.append(f"  {GREEN}✔{RESET} {emoji} {BOLD}{title}{RESET} — {DIM}{desc}{RESET}")
        else:
            lines.append(f"  {GRAY}○ 🔒 {title} — {desc}{RESET}")
    return "\n".join(lines)

def render_match_analysis(
    tracker: MatchTracker,
    opponent_elo: int,
    outcome: str,
    learned_lessons: int = 0,
    generation: Optional[int] = None,
    new_achievements: Optional[List[str]] = None,
) -> str:

    lines: List[str] = []
    lines.append(f"{BOLD}{CYAN}═══ ANALISIS PERTANDINGAN ═══{RESET}")
    if tracker.player_moves:
        acc = tracker.accuracy_percent()
        perf = tracker.estimated_perf_elo(opponent_elo, outcome)
        acc_color = GREEN if acc >= 78 else (YELLOW if acc >= 55 else RED)
        counts = tracker.grade_counts()
        lines.append(
            f"  Akurasi Kamu : {BOLD}{acc_color}{acc:.1f}%{RESET}  ·  "
            f"Perf Elo: {BOLD}{YELLOW}~{perf}{RESET}  ·  "
            f"Avg CPL: {tracker.average_cpl():.0f}"
        )
        lines.append(
            f"  Rincian      : {CYAN}!! {counts['!!']}{RESET}  {GREEN}! {counts['!']}{RESET}  "
            f"✓ {counts['✓']}  {YELLOW}?! {counts['?!']}{RESET}  "
            f"{RED}? {counts['?']}  ?? {counts['??']}{RESET}  {DIM}📖 {counts['📖']}{RESET}"
        )
        best = tracker.best_moment()
        if best:
            lines.append(
                f"  Momen Terbaik: Langkah #{(best.ply + 1) // 2} {BOLD}{GREEN}{best.san}{RESET} ({best.grade.symbol} {best.grade.label})"
            )
        blunder = tracker.biggest_blunder()
        if blunder:
            tip = f" — saran terbaik: {GREEN}{blunder.best_san}{RESET}" if blunder.best_san else ""
            lines.append(
                f"  Momen Kritis : Langkah #{(blunder.ply + 1) // 2} {BOLD}{RED}{blunder.san}{RESET} "
                f"({blunder.grade.symbol}, -{blunder.cp_loss}cp){tip}"
            )
    if generation is not None:
        lines.append(
            f"  {MAGENTA}🧬 Evolving AI -> Gen {generation} ({learned_lessons} pola baru dipelajari dari game ini!){RESET}"
        )
    if new_achievements:
        lines.append("")
        for aid in new_achievements:
            if aid in ACHIEVEMENTS:
                em, title, desc = ACHIEVEMENTS[aid]
                lines.append(f"  {BOLD}{YELLOW}🏅 ACHIEVEMENT UNLOCKED: {em} {title}!{RESET} {DIM}({desc}){RESET}")
    return "\n".join(lines)

def render_board(
    board: Board,
    bot: Optional[BotProfile],
    player_color: int,
    style: str = "unicode",
    theme_id: str = "sage",
    flipped: bool = False,
    is_adaptive: bool = False,
    adaptive_delta: int = 0,
    evo_tag: Optional[str] = None,
    bot_message: Optional[str] = None,
    status_note: Optional[str] = None,
    eval_cp: Optional[int] = None,
    eval_side: int = WHITE,
    show_eval: bool = True,
    highlight_targets: Optional[Set[int]] = None,
    highlight_origin: int = -1,
    white_clock: Optional[float] = None,
    black_clock: Optional[float] = None,
    pvp_mode: bool = False,
    banner_title: Optional[str] = None,
    opening_label: Optional[str] = None,
    hot_streak: int = 0,
) -> str:

    theme = get_theme(theme_id)
    perspective = -player_color if flipped else player_color
    ranks = range(7, -1, -1) if perspective == WHITE else range(0, 8)
    files = range(0, 8) if perspective == WHITE else range(7, -1, -1)

    last_from = move_from(board.move_history[-1]) if board.move_history else -1
    last_to = move_to(board.move_history[-1]) if board.move_history else -1
    targets = highlight_targets or set()

    check_sq = board.king_sq[board.turn] if board.in_check() else -1

    cap_by_white, cap_by_black = board.captured_pieces()
    mat = board.material_balance()

    top_color = BLACK if perspective == WHITE else WHITE
    bot_color = perspective

    def _clock_for(side: int) -> str:
        c = white_clock if side == WHITE else black_clock
        return f"  {format_clock(c)}" if c is not None else ""

    def _side_label(side: int) -> str:
        side_name = "Putih" if side == WHITE else "Hitam"
        cap = _format_captured(cap_by_white if side == WHITE else cap_by_black, style)
        adv = mat if side == WHITE else -mat
        clk = _clock_for(side)
        if pvp_mode:
            adv_s = f" {GREEN}+{adv}{RESET}" if adv > 0 else ""
            active = f"{YELLOW}◀{RESET}" if board.turn == side else ""
            return f"{BOLD}{WHITE_FG}Player {side_name}{RESET}{clk}  {cap}{adv_s} {active}"

        if side == player_color or bot is None:
            adv_s = f" {GREEN}+{adv}{RESET}" if adv > 0 else ""
            return f"{BOLD}{WHITE_FG}Kamu ({side_name}){RESET}{clk}  {cap}{adv_s}"

        adv_s = f" {RED}+{adv}{RESET}" if adv > 0 else ""
        delta_s = ""
        if is_adaptive and adaptive_delta != 0:
            arrow = f"{GREEN}+{adaptive_delta}▲{RESET}" if adaptive_delta > 0 else f"{RED}{adaptive_delta}▼{RESET}"
            delta_s = f" ({arrow})"
        tag = f"{MAGENTA}🧬{RESET} " if is_adaptive else f"{bot.color_code}[✦]{RESET} "
        return f"{tag}{BOLD}{bot.name}{RESET} {DIM}Elo {bot.elo}{RESET}{delta_s} ({side_name}){clk}  {cap}{adv_s}"

    board_lines: List[str] = []
    if banner_title:
        board_lines.append(banner_title)
    if evo_tag:
        board_lines.append(f"{DIM}{evo_tag}{RESET}")
    board_lines.append(_side_label(top_color))

    file_labels = "  " + " ".join(f" {FILES[f]}" for f in files)

    if style == "ascii_plain":
        border = "  +---+---+---+---+---+---+---+---+"
        board_lines.append(f"{DIM}{border}{RESET}")
        for r in ranks:
            row_cells = []
            for f in files:
                sq = (r << 3) | f
                p = board.squares[sq]
                ch = PIECE_TO_CHAR[p] if p != EMPTY else "."
                if p > 0:
                    cell_txt = f"{BOLD}{YELLOW}{ch}{RESET}"
                elif p < 0:
                    cell_txt = f"{BOLD}{CYAN}{ch}{RESET}"
                else:
                    cell_txt = f"{CYAN}•{RESET}" if sq in targets else f"{DIM}.{RESET}"
                if sq == check_sq:
                    row_cells.append(f"{RED}*{cell_txt}{RED}*{RESET}")
                elif sq in targets:
                    row_cells.append(f"{CYAN}({cell_txt}{CYAN}){RESET}")
                elif sq == last_from or sq == last_to or sq == highlight_origin:
                    row_cells.append(f"{GREEN}[{cell_txt}{GREEN}]{RESET}")
                else:
                    row_cells.append(f" {cell_txt} ")
            board_lines.append(f"{DIM}{r + 1}{RESET} |{'|'.join(row_cells)}|")
            board_lines.append(f"{DIM}{border}{RESET}")
        board_lines.append("    " + "   ".join(FILES[f] for f in files))
    else:
        for r in ranks:
            row_parts = [f"{DIM}{r + 1} {RESET}"]
            for f in files:
                sq = (r << 3) | f
                is_light = ((r + f) & 1) == 1
                if sq == check_sq:
                    bg = theme.bg_check
                elif sq in targets:
                    bg = theme.bg_target_light if is_light else theme.bg_target_dark
                elif sq == last_from or sq == last_to or sq == highlight_origin:
                    bg = theme.bg_last_light if is_light else theme.bg_last_dark
                else:
                    bg = theme.bg_light if is_light else theme.bg_dark

                p = board.squares[sq]
                if p == EMPTY:
                    if sq in targets:
                        cell = f"{bg}{theme.fg_black} · {RESET}"
                    else:
                        cell = f"{bg}   {RESET}"
                else:
                    fg = theme.fg_white if p > 0 else theme.fg_black
                    sym = UNICODE_SOLID[abs(p)] if style == "unicode" else PIECE_TO_CHAR[p]
                    cell = f"{bg}{fg} {sym} {RESET}"
                row_parts.append(cell)
            board_lines.append("".join(row_parts))
        board_lines.append(f"{DIM}{file_labels}{RESET}")

    board_lines.append(_side_label(bot_color))

    if show_eval and eval_cp is not None:
        streak_txt = f"  {BOLD}{YELLOW}🔥 Streak {hot_streak}x{RESET}" if hot_streak >= 3 else ""
        board_lines.append(f"{DIM}Eval:{RESET} {render_eval_bar(eval_cp, eval_side, width=18)}{streak_txt}")
    elif hot_streak >= 3:
        board_lines.append(f"{BOLD}{YELLOW}🔥 Hot Streak: {hot_streak} langkah akurat berturut-turut!{RESET}")


    if opening_label:
        board_lines.append(f"{DIM}Pembukaan:{RESET} {CYAN}{opening_label}{RESET}")

    if board.san_history:
        pairs: List[str] = []
        sh = board.san_history
        for i in range(0, len(sh), 2):
            mnum = (i // 2) + 1
            w_mv = sh[i]
            b_mv = sh[i + 1] if i + 1 < len(sh) else ""
            pairs.append(f"{mnum}. {w_mv}" + (f" {b_mv}" if b_mv else ""))
        recent = "  ".join(pairs[-4:])
        prefix = "... " if len(pairs) > 4 else ""
        board_lines.append(f"{DIM}Langkah: {prefix}{recent}{RESET}")

    if board.in_check() and board.has_legal_moves():
        if pvp_mode:
            who = "Putih" if board.turn == WHITE else "Hitam"
        else:
            who = "Kamu" if board.turn == player_color else (bot.name if bot else "Lawan")
        board_lines.append(f"{BOLD}{RED}⚠ SKAK! ({who} sedang dalam ancaman skak){RESET}")

    if status_note:
        board_lines.append(status_note)

    if bot_message and bot is not None:
        board_lines.append(f'{bot.color_code}{BOLD}{bot.name}:{RESET} {ITALIC}"{bot_message}"{RESET}')

    return "\n".join(board_lines)


def render_settings_menu(profile: Dict[str, Any]) -> str:
    cur_theme = profile.get("theme", "sage")
    cur_style = profile.get("board_style", "unicode")
    cur_tc = profile.get("time_control", "unlimited")
    show_eval = bool(profile.get("show_eval", True))
    show_grades = bool(profile.get("show_grades", True))
    sound_bell = bool(profile.get("sound_bell", False))

    lines = [
        f"{BOLD}{CYAN}═══ TEMA PAPAN, JAM CATUR & PENGATURAN ═══{RESET}",
        "",
        f"{BOLD}Tema Warna Papan:{RESET}",
    ]
    for idx, t in enumerate(THEMES, 1):
        mark = f"{GREEN}◀ aktif{RESET}" if t.theme_id == cur_theme else ""
        swatch = f"{t.bg_light}{t.fg_white} ♞ {RESET}{t.bg_dark}{t.fg_black} ♛ {RESET}"
        lines.append(f"  ({BOLD}{idx}{RESET}) {swatch} {BOLD}{t.name:<17}{RESET} {DIM}{t.desc}{RESET} {mark}")

    lines.append("")
    lines.append(f"{BOLD}Pengaturan Lain:{RESET}")
    lines.append(f"  ({BOLD}S{RESET}) Gaya Bidak     : {YELLOW}{cur_style}{RESET} (unicode / ascii / ascii_plain)")
    lines.append(f"  ({BOLD}C{RESET}) Jam Catur      : {CYAN}{TIME_CONTROLS.get(cur_tc, TIME_CONTROLS['unlimited'])[0]}{RESET}")
    lines.append(f"  ({BOLD}E{RESET}) Live Eval Bar  : {GREEN if show_eval else GRAY}{'ON' if show_eval else 'OFF'}{RESET}")
    lines.append(f"  ({BOLD}M{RESET}) Grade Langkah  : {GREEN if show_grades else GRAY}{'ON (!/??)' if show_grades else 'OFF'}{RESET}")
    lines.append(f"  ({BOLD}B{RESET}) Suara Bell     : {GREEN if sound_bell else GRAY}{'ON' if sound_bell else 'OFF'}{RESET}")
    lines.append(f"  ({BOLD}0{RESET}) Kembali ke Menu")
    return "\n".join(lines)

def render_help() -> str:
    return "\n".join([
        f"{BOLD}{CYAN}═══ PANDUAN & COMMAND CHESSPORTABLE v{__version__} ═══{RESET}",
        f"  {BOLD}Input Langkah:{RESET}",
        f"    SAN       : {GREEN}e4{RESET}, {GREEN}E4{RESET}, {GREEN}Nf3{RESET}, {GREEN}Bxc6{RESET}, {GREEN}O-O{RESET}, {GREEN}O-O-O{RESET}, {GREEN}e8=Q{RESET}",
        f"    Koordinat : {GREEN}e2e4{RESET}, {GREEN}e2 e4{RESET}, {GREEN}e7e8q{RESET}",
        f"    ARC Cheat : {MAGENTA}ARC e4 Nf3 Bc4 ...{RESET} {DIM}(auto-jalan beruntun tanpa input!){RESET}",
        "",
        f"  {BOLD}Command Permainan:{RESET}",
        f"    {YELLOW}undo{RESET} / {YELLOW}u{RESET}          Batalkan langkah terakhir",
        f"    {YELLOW}hint{RESET} / {YELLOW}h{RESET}          Saran langkah terbaik + Principal Variation (PV)",
        f"    {YELLOW}coach{RESET}             Tactical Coach: deteksi bidak gantung, ancaman & garis terbaik!",
        f"    {YELLOW}moves{RESET} [kotak]     Daftar langkah legal + highlight di papan! (mis: moves e2)",
        f"    {YELLOW}eval{RESET}              Hitung evaluasi detail + PV / toggle eval bar",
        f"    {YELLOW}style{RESET}             Ganti Unicode ↔ ASCII ↔ Plain",
        f"    {YELLOW}theme{RESET} [nama]      Ganti tema warna papan (sage/wood/ocean/neon/crimson/mono)",
        f"    {YELLOW}flip{RESET}              Putar sudut pandang papan",
        f"    {YELLOW}save{RESET} [nama]       Simpan permainan",
        f"    {YELLOW}load{RESET} [nama]       Muat permainan tersimpan",
        f"    {YELLOW}export{RESET} [nama]     Ekspor pertandingan ke file .PGN standar (+ ECO Opening)",
        f"    {YELLOW}dna{RESET}               Intip DNA & memori Evolving AI saat ini",
        f"    {YELLOW}history{RESET} / {YELLOW}pgn{RESET}     Lihat riwayat langkah lengkap",
        f"    {YELLOW}fen{RESET}               Tampilkan FEN posisi saat ini",
        f"    {YELLOW}think{RESET} <detik>     Atur batas waktu mikir bot (mis: think 2 / think default)",
        f"    {YELLOW}draw{RESET} / {YELLOW}resign{RESET}     Tawarkan remis / Menyerah",
        f"    {YELLOW}menu{RESET} / {YELLOW}quit{RESET}       Kembali ke menu utama / Keluar",
    ])
