from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from .board import (
    BISHOP,
    BLACK,
    Board,
    CASTLE_BK,
    CASTLE_BQ,
    CASTLE_WK,
    CASTLE_WQ,
    EMPTY,
    FLAG_EN_PASSANT,
    KING,
    KNIGHT,
    PAWN,
    QUEEN,
    ROOK,
    WHITE,
    move_promo,
    move_to_uci,
    sq_to_name,
)
from .bots import BotProfile

if TYPE_CHECKING:
    from .evolving import EvolvingBrain

MATE_SCORE = 30000
MATE_THRESHOLD = 29000
INF = 32000

TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2

MG_VALUE = (0, 82, 337, 365, 477, 1025, 0)
EG_VALUE = (0, 94, 281, 297, 512, 936, 0)
PHASE_INC = (0, 0, 1, 1, 2, 4, 0)

_MG_PAWN = (
      0,   0,   0,   0,   0,   0,   0,   0,
     98, 134,  61,  95,  68, 126,  34, -11,
     -6,   7,  26,  31,  65,  56,  25, -20,
    -14,  13,   6,  21,  23,  12,  17, -23,
    -27,  -2,  -5,  12,  17,   6,  10, -25,
    -26,  -4,  -4, -10,   3,   3,  33, -12,
    -35,  -1, -20, -23, -15,  24,  38, -22,
      0,   0,   0,   0,   0,   0,   0,   0,
)
_EG_PAWN = (
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0,
)
_MG_KNIGHT = (
   -167, -89, -34, -49,  61, -97, -15,-107,
    -73, -41,  72,  36,  23,  62,   7, -17,
    -47,  60,  37,  65,  84, 129,  73,  44,
     -9,  17,  19,  53,  37,  69,  18,  22,
    -13,   4,  16,  13,  28,  19,  21,  -8,
    -23,  -9,  12,  10,  19,  17,  25, -16,
    -29, -53, -12,  -3,  -1,  18, -14, -19,
   -105, -21, -58, -33, -17, -28, -19, -23,
)
_EG_KNIGHT = (
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64,
)
_MG_BISHOP = (
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
)
_EG_BISHOP = (
    -14, -21, -11,  -8,  -7,  -9, -17, -24,
     -8,  -4,   7, -12,  -3, -13,  -4, -14,
      2,  -8,   0,  -1,  -2,   6,   0,   4,
     -3,   9,  12,   9,  14,  10,   3,   2,
     -6,   3,  13,  19,   7,  10,  -3,  -9,
    -12,  -3,   8,  10,  13,   3,  -7, -15,
    -14, -18,  -7,  -1,   4,  -9, -15, -27,
    -23,  -9, -23,  -5,  -9, -16,  -5, -17,
)
_MG_ROOK = (
     32,  42,  32,  51,  63,   9,  31,  43,
     27,  32,  58,  62,  80,  67,  26,  44,
     -5,  19,  26,  36,  17,  45,  61,  16,
    -24, -11,   7,  26,  24,  35,  -8, -20,
    -36, -26, -12,  -1,   9,  -7,   6, -23,
    -45, -25, -16, -17,   3,   0,  -5, -33,
    -44, -16, -20,  -9,  -1,  11,  -6, -71,
    -19, -13,   1,  17,  16,   7, -37, -26,
)
_EG_ROOK = (
     13,  10,  18,  15,  12,  12,   8,   5,
     11,  13,  13,  11,  -3,   3,   8,   3,
      7,   7,   7,   5,   4,  -3,  -5,  -3,
      4,   3,  13,   1,   2,   1,  -1,   2,
      3,   5,   8,   4,  -5,  -6,  -8, -11,
     -4,   0,  -5,  -1,  -7, -12,  -8, -16,
     -6,  -6,   0,   2,  -9,  -9, -11,  -3,
     -9,   2,   3,  -1,  -5, -13,   4, -20,
)
_MG_QUEEN = (
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
)
_EG_QUEEN = (
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  57,  40,  57,  36,
    -18,  28,  19,  47,  31,  34,  39,  23,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41,
)
_MG_KING = (
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
)
_EG_KING = (
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43,
)

def _flip_v(table: Tuple[int, ...]) -> Tuple[int, ...]:
    out = [0] * 64
    for sq in range(64):
        r, f = sq >> 3, sq & 7
        out[sq] = table[((7 - r) << 3) | f]
    return tuple(out)

def _mirror_for_black(table: Tuple[int, ...]) -> Tuple[int, ...]:
    out = [0] * 64
    for sq in range(64):
        r, f = sq >> 3, sq & 7
        out[sq] = table[(r << 3) | f]
    return tuple(out)

_RAW_MG = (None, _MG_PAWN, _MG_KNIGHT, _MG_BISHOP, _MG_ROOK, _MG_QUEEN, _MG_KING)
_RAW_EG = (None, _EG_PAWN, _EG_KNIGHT, _EG_BISHOP, _EG_ROOK, _EG_QUEEN, _EG_KING)

MG_PST: List[Tuple[int, ...]] = [tuple([0] * 64) for _ in range(13)]
EG_PST: List[Tuple[int, ...]] = [tuple([0] * 64) for _ in range(13)]

for _pt in range(1, 7):
    _w_mg = _flip_v(_RAW_MG[_pt])
    _w_eg = _flip_v(_RAW_EG[_pt])
    _b_mg = _mirror_for_black(_RAW_MG[_pt])
    _b_eg = _mirror_for_black(_RAW_EG[_pt])
    MG_PST[_pt + 6] = tuple(MG_VALUE[_pt] + _w_mg[s] for s in range(64))
    EG_PST[_pt + 6] = tuple(EG_VALUE[_pt] + _w_eg[s] for s in range(64))
    MG_PST[-_pt + 6] = tuple(-(MG_VALUE[_pt] + _b_mg[s]) for s in range(64))
    EG_PST[-_pt + 6] = tuple(-(EG_VALUE[_pt] + _b_eg[s]) for s in range(64))

CENTER_DIST = tuple(max(abs((sq >> 3) - 3.5), abs((sq & 7) - 3.5)) for sq in range(64))
PASSED_BONUS_MG = (0, 6, 12, 22, 40, 72, 120, 0)
PASSED_BONUS_EG = (0, 14, 24, 44, 78, 135, 205, 0)

MVV_VICTIM = (0, 100, 320, 330, 500, 900, 10000)
MVV_ATTACKER = (0, 1, 2, 3, 4, 5, 6)


_BOOK_LINES: List[Tuple[str, str]] = [

    ("master", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 f1a4 g8f6 e1g1 f8e7 f1e1 b7b5 a4b3 d7d6 c2c3 e8g8"),
    ("master", "e2e4 e7e5 g1f3 b8c6 f1b5 g8f6 e1g1 f6e4 d2d4 f8e7 d1e2 e4d6"),
    ("master", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3 g8f6 d2d3 d7d6 e1g1 a7a6"),
    ("master", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 d2d3 f8c5 c2c3 d7d6 e1g1 e8g8"),
    ("master", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6 f1e2 e7e5 d4b3 f8e7"),
    ("master", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e5 d4b5 d7d6 c1g5 a7a6"),
    ("master", "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 a7a6 f1d3 g8f6 e1g1 d8c7"),
    ("master", "e2e4 c7c5 c2c3 d7d5 e4d5 d8d5 d2d4 g8f6 g1f3 e7e6 f1e2 b8c6"),
    ("master", "e2e4 e7e6 d2d4 d7d5 b1c3 g8f6 e4e5 f6d7 f2f4 c7c5 g1f3 b8c6 c1e3"),
    ("master", "e2e4 e7e6 d2d4 d7d5 b1d2 c7c5 e4d5 e6d5 g1f3 b8c6 f1b5 f8d6"),
    ("master", "e2e4 e7e6 d2d4 d7d5 e4e5 c7c5 c2c3 b8c6 g1f3 d8b6 a2a3"),
    ("master", "e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5 e4g3 f5g6 h2h4 h7h6 g1f3"),
    ("master", "e2e4 c7c6 d2d4 d7d5 e4e5 c8f5 g1f3 e7e6 f1e2 c6c5 c1e3"),
    ("master", "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c4d5 e6d5 c1g5 f8e7 e2e3 e8g8 f1d3"),
    ("master", "d2d4 d7d5 c2c4 c7c6 g1f3 g8f6 b1c3 d5c4 a2a4 c8f5 e2e3 e7e6"),
    ("master", "d2d4 d7d5 c2c4 d5c4 g1f3 g8f6 e2e3 e7e6 f1c4 c7c5 e1g1"),
    ("master", "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4 e2e3 e8g8 f1d3 d7d5 g1f3 c7c5"),
    ("master", "d2d4 g8f6 c2c4 e7e6 g1f3 d7d5 g2g3 f8e7 f1g2 e8g8 e1g1"),
    ("master", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 g1f3 e8g8 f1e2 e7e5 e1g1"),
    ("master", "d2d4 d7d5 c1f4 g8f6 e2e3 c7c5 c2c3 b8c6 b1d2 e7e6 g1f3 f8d6"),
    ("master", "c2c4 e7e5 b1c3 g8f6 g1f3 b8c6 g2g3 d7d5 c4d5 f6d5 f1g2"),
    ("master", "c2c4 g8f6 b1c3 e7e6 e2e4 d7d5 e4e5 d5d4 e5f6 d4c3"),
    ("master", "g1f3 d7d5 g2g3 g8f6 f1g2 e7e6 e1g1 f8e7 d2d4 e8g8 c2c4"),

    ("master", "e2e4 e7e5 d1h5 b8c6 f1c4 g7g6 h5f3 g8f6 g1e2 f8g7"),
    ("master", "e2e4 e7e5 f1c4 g8f6 d1h5 b8c6 h5f3 g7g6"),
    ("solid",  "e2e4 e7e5 d1h5 b8c6 f1c4 g7g6 h5f3 g8f6"),
    ("tricky", "e2e4 e7e5 d1h5 b8c6 f1c4 g7g6 h5f3 g8f6 d2d3 c6d4"),
    ("sharp",  "e2e4 e7e5 d1h5 b8c6 f1c4 g7g6 h5f3 g8f6 c2c3 f8g7"),

    ("sharp", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6 c1e3 f8g7 f2f3 e8g8 d1d2 b8c6"),
    ("sharp", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6 c1g5 e7e6 f2f4"),
    ("sharp", "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f3d4 g8f6 b1c3 f8b4 d4c6 b7c6 f1d3"),
    ("sharp", "e2e4 e7e5 f2f4 e5f4 g1f3 g7g5 f1c4 f8g7 e1g1 d7d6 d2d4"),
    ("sharp", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 b2b4 c5b4 c2c3 b4a5 d2d4 e5d4"),
    ("sharp", "e2e4 c7c5 b1c3 b8c6 f2f4 g7g6 g1f3 f8g7 f1b5 c6d4"),
    ("sharp", "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5 c4d5 f6d5 e2e4 d5c3 b2c3 f8g7 f1c4"),
    ("sharp", "d2d4 g8f6 c2c4 c7c5 d4d5 e7e6 b1c3 e6d5 c4d5 d7d6 e2e4 g7g6"),
    ("sharp", "e2e4 d7d5 e4d5 d8d5 b1c3 d5a5 d2d4 g8f6 g1f3 c8f5 f1c4"),
    ("sharp", "e2e4 g8f6 e4e5 f6d5 d2d4 d7d6 g1f3 c8g4 f1e2 e7e6"),

    ("tricky", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5 d7d5 e4d5 c6a5 c4b5 c7c6 d5c6 b7c6"),
    ("tricky", "e2e4 e7e5 b1c3 g8f6 f2f4 d7d5 f4e5 f6e4 g1f3 f8e7"),
    ("tricky", "e2e4 c7c5 d2d4 c5d4 c2c3 d4c3 b1c3 b8c6 g1f3 d7d6 f1c4 e7e6"),
    ("tricky", "e2e4 e7e5 g1f3 f7f5 f3e5 d8f6 d2d4 d7d6 e5c4 f5e4"),
    ("tricky", "d2d4 f7f5 c2c4 g8f6 g2g3 e7e6 f1g2 f8e7 g1f3 e8g8"),
    ("tricky", "e2e4 b8c6 d2d4 d7d5 e4e5 c8f5 g1f3 e7e6"),
    ("tricky", "e2e4 e7e5 g1f3 g8f6 f3e5 d7d6 e5f3 f6e4 d2d4 d6d5"),
    ("tricky", "d2d4 d7d5 e2e4 d5e4 b1c3 g8f6 f2f3 e4f3 g1f3"),
    ("tricky", "e2e4 d7d6 d2d4 g8f6 b1c3 g7g6 f2f4 f8g7 g1f3 e8g8"),

    ("solid", "e2e4 e7e5 g1f3 b8c6 b1c3 g8f6 f1b5 f8b4 e1g1 e8g1 d2d3"),
    ("solid", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 d2d3 d7d6 c2c3 g8f6"),
    ("solid", "d2d4 d7d5 g1f3 g8f6 c1f4 e7e6 e2e3 f8d6 f4g3 e8g8"),
    ("solid", "e2e4 c7c6 d2d4 d7d5 e4d5 c6d5 f1d3 b8c6 c2c3 g8f6"),
    ("solid", "e2e4 d7d6 d2d4 g8f6 b1c3 g7g6 g1f3 f8g7 f1e2 e8g8"),
    ("solid", "d2d4 g8f6 g1f3 e7e6 c1f4 d7d5 e2e3 f8d6"),

    ("casual", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 d2d3 g8f6"),
    ("casual", "d2d4 d7d5 b1c3 g8f6 c1f4 e7e6"),
    ("casual", "e2e4 e7e5 b1c3 b8c6 f1c4 g8f6 d2d3"),
]

def _build_opening_book() -> Dict[str, Dict[int, List[str]]]:

    books: Dict[str, Dict[int, List[str]]] = {
        "casual": {},
        "solid": {},
        "tricky": {},
        "sharp": {},
        "master": {},
        "all": {},
    }
    for style, line in _BOOK_LINES:
        moves = line.split()
        b = Board()
        for uci in moves:
            legal = {move_to_uci(m): m for m in b.legal_moves()}
            if uci not in legal:
                break
            zkey = b.zobrist
            books[style].setdefault(zkey, []).append(uci)
            books["all"].setdefault(zkey, []).append(uci)
            b.make_move(legal[uci], record_san=False)
    return books


OPENING_BOOKS = _build_opening_book()


def is_book_move(board_before: Board, uci: str) -> bool:
    if board_before.fullmove > 12:
        return False
    choices = OPENING_BOOKS["all"].get(board_before.zobrist)
    return bool(choices and uci in choices)

def lookup_book_move(
    board: Board,
    style: str,
    avoid_ucis: Optional[Set[str]] = None,
) -> Optional[int]:

    if board.fullmove > 12:
        return None
    zkey = board.zobrist
    avoid = avoid_ucis or set()
    choices = OPENING_BOOKS.get(style, {}).get(zkey)
    if not choices and style in ("master", "sharp", "solid", "tricky"):
        choices = OPENING_BOOKS["all"].get(zkey)
    if not choices:
        return None
    legal = {move_to_uci(m): m for m in board.legal_moves()}
    filtered = [legal[u] for u in choices if u in legal and u not in avoid]
    if filtered:
        return random.choice(filtered)

    all_choices = OPENING_BOOKS["all"].get(zkey, [])
    alt = [legal[u] for u in all_choices if u in legal and u not in avoid]
    if alt:
        return random.choice(alt)
    return None

@dataclass
class SearchResult:
    move: int
    score_cp: int
    depth: int
    nodes: int
    elapsed: float
    from_book: bool = False
    memory_note: Optional[str] = None

class SearchTimeout(Exception):
    pass

class ChessAI:


    def __init__(self) -> None:
        self.tt: Dict[int, Tuple[int, int, int, int]] = {}
        self.killers: List[List[int]] = [[0, 0] for _ in range(64)]
        self.history: Dict[int, List[List[int]]] = {
            WHITE: [[0] * 64 for _ in range(64)],
            BLACK: [[0] * 64 for _ in range(64)],
        }
        self.nodes: int = 0
        self.deadline: float = 0.0
        self.use_quiescence: bool = True
        self.use_pruning: bool = True
        self.aggression: float = 1.0
        self.positional: float = 1.0

    def clear_tables(self) -> None:
        if len(self.tt) > 140000:
            self.tt.clear()
        self.killers = [[0, 0] for _ in range(64)]
        for side in (WHITE, BLACK):
            h = self.history[side]
            for i in range(64):
                row = h[i]
                for j in range(64):
                    row[j] >>= 2

    def evaluate(self, board: Board) -> int:

        squares = board.squares
        mg = 0
        eg = 0
        phase = 0

        w_bishops = 0
        b_bishops = 0
        w_pawns_file = [0] * 8
        b_pawns_file = [0] * 8
        w_pawn_max_rank = [0] * 8
        b_pawn_min_rank = [7] * 8
        w_pawns_sq: List[int] = []
        b_pawns_sq: List[int] = []
        w_knights_sq: List[int] = []
        b_knights_sq: List[int] = []
        w_rooks_sq: List[int] = []
        b_rooks_sq: List[int] = []

        mg_pst = MG_PST
        eg_pst = EG_PST
        phase_inc = PHASE_INC

        wk = board.king_sq[WHITE]
        bk = board.king_sq[BLACK]
        wkr, wkf = wk >> 3, wk & 7
        bkr, bkf = bk >> 3, bk & 7
        king_pressure = 0

        for sq in range(64):
            p = squares[sq]
            if p == EMPTY:
                continue
            idx = p + 6
            mg += mg_pst[idx][sq]
            eg += eg_pst[idx][sq]
            pt = p if p > 0 else -p
            phase += phase_inc[pt]

            if p == PAWN:
                f, r = sq & 7, sq >> 3
                w_pawns_file[f] += 1
                if r > w_pawn_max_rank[f]:
                    w_pawn_max_rank[f] = r
                w_pawns_sq.append(sq)
            elif p == -PAWN:
                f, r = sq & 7, sq >> 3
                b_pawns_file[f] += 1
                if r < b_pawn_min_rank[f]:
                    b_pawn_min_rank[f] = r
                b_pawns_sq.append(sq)
            elif p == KNIGHT:
                w_knights_sq.append(sq)

                if abs((sq >> 3) - bkr) + abs((sq & 7) - bkf) <= 3:
                    king_pressure += 14
            elif p == -KNIGHT:
                b_knights_sq.append(sq)
                if abs((sq >> 3) - wkr) + abs((sq & 7) - wkf) <= 3:
                    king_pressure -= 14
            elif p == BISHOP:
                w_bishops += 1
            elif p == -BISHOP:
                b_bishops += 1
            elif p == ROOK:
                w_rooks_sq.append(sq)
            elif p == -ROOK:
                b_rooks_sq.append(sq)
            elif p == QUEEN:
                if abs((sq >> 3) - bkr) + abs((sq & 7) - bkf) <= 4:
                    king_pressure += 22
            elif p == -QUEEN:
                if abs((sq >> 3) - wkr) + abs((sq & 7) - wkf) <= 4:
                    king_pressure -= 22

        pos_mult = self.positional
        agg_mult = self.aggression

        if phase > 6 and king_pressure:
            mg += int(king_pressure * agg_mult)

        if w_bishops >= 2:
            mg += int(34 * pos_mult)
            eg += int(52 * pos_mult)
        if b_bishops >= 2:
            mg -= int(34 * pos_mult)
            eg -= int(52 * pos_mult)

        struct_mg = 0
        struct_eg = 0
        for f in range(8):
            wc = w_pawns_file[f]
            if wc > 1:
                struct_mg -= 13 * (wc - 1)
                struct_eg -= 19 * (wc - 1)
            if wc > 0:
                left = w_pawns_file[f - 1] if f > 0 else 0
                right = w_pawns_file[f + 1] if f < 7 else 0
                if left == 0 and right == 0:
                    struct_mg -= 12 * wc
                    struct_eg -= 15 * wc

            bc = b_pawns_file[f]
            if bc > 1:
                struct_mg += 13 * (bc - 1)
                struct_eg += 19 * (bc - 1)
            if bc > 0:
                left = b_pawns_file[f - 1] if f > 0 else 0
                right = b_pawns_file[f + 1] if f < 7 else 0
                if left == 0 and right == 0:
                    struct_mg += 12 * bc
                    struct_eg += 15 * bc


        for sq in w_pawns_sq:
            r, f = sq >> 3, sq & 7
            blocked = False
            for df in (-1, 0, 1):
                nf = f + df
                if 0 <= nf < 8 and b_pawns_file[nf] > 0 and b_pawn_min_rank[nf] > r:
                    for bsq in b_pawns_sq:
                        if (bsq & 7) == nf and (bsq >> 3) > r:
                            blocked = True
                            break
                if blocked:
                    break
            if not blocked:
                struct_mg += PASSED_BONUS_MG[r]
                struct_eg += PASSED_BONUS_EG[r]

        for sq in b_pawns_sq:
            r, f = sq >> 3, sq & 7
            blocked = False
            for df in (-1, 0, 1):
                nf = f + df
                if 0 <= nf < 8 and w_pawns_file[nf] > 0 and w_pawn_max_rank[nf] < r:
                    for wsq in w_pawns_sq:
                        if (wsq & 7) == nf and (wsq >> 3) < r:
                            blocked = True
                            break
                if blocked:
                    break
            if not blocked:
                struct_mg -= PASSED_BONUS_MG[7 - r]
                struct_eg -= PASSED_BONUS_EG[7 - r]


        for sq in w_knights_sq:
            r, f = sq >> 3, sq & 7
            if 3 <= r <= 5 and 1 <= f <= 6:
                supported = (squares[((r - 1) << 3) | (f - 1)] == PAWN) or (
                    squares[((r - 1) << 3) | (f + 1)] == PAWN
                )
                if supported:
                    struct_mg += 20
                    struct_eg += 10
        for sq in b_knights_sq:
            r, f = sq >> 3, sq & 7
            if 2 <= r <= 4 and 1 <= f <= 6:
                supported = (squares[((r + 1) << 3) | (f - 1)] == -PAWN) or (
                    squares[((r + 1) << 3) | (f + 1)] == -PAWN
                )
                if supported:
                    struct_mg -= 20
                    struct_eg -= 10

        for sq in w_rooks_sq:
            f, r = sq & 7, sq >> 3
            if w_pawns_file[f] == 0:
                if b_pawns_file[f] == 0:
                    struct_mg += int(24 * agg_mult)
                    struct_eg += 14
                else:
                    struct_mg += int(12 * agg_mult)
            if r == 6:
                struct_mg += 20
                struct_eg += 26

        for sq in b_rooks_sq:
            f, r = sq & 7, sq >> 3
            if b_pawns_file[f] == 0:
                if w_pawns_file[f] == 0:
                    struct_mg -= int(24 * agg_mult)
                    struct_eg -= 14
                else:
                    struct_mg -= int(12 * agg_mult)
            if r == 1:
                struct_mg -= 20
                struct_eg -= 26


        if len(w_rooks_sq) == 2:
            s1, s2 = w_rooks_sq[0], w_rooks_sq[1]
            r1, f1 = s1 >> 3, s1 & 7
            r2, f2 = s2 >> 3, s2 & 7
            if r1 == r2:
                step = 1 if s2 > s1 else -1
                if all(squares[x] == EMPTY for x in range(s1 + step, s2, step)):
                    struct_mg += 16
                    struct_eg += 12
            elif f1 == f2:
                step = 8 if s2 > s1 else -8
                if all(squares[x] == EMPTY for x in range(s1 + step, s2, step)):
                    struct_mg += 16
                    struct_eg += 12
        if len(b_rooks_sq) == 2:
            s1, s2 = b_rooks_sq[0], b_rooks_sq[1]
            r1, f1 = s1 >> 3, s1 & 7
            r2, f2 = s2 >> 3, s2 & 7
            if r1 == r2:
                step = 1 if s2 > s1 else -1
                if all(squares[x] == EMPTY for x in range(s1 + step, s2, step)):
                    struct_mg -= 16
                    struct_eg -= 12
            elif f1 == f2:
                step = 8 if s2 > s1 else -8
                if all(squares[x] == EMPTY for x in range(s1 + step, s2, step)):
                    struct_mg -= 16
                    struct_eg -= 12

        mg += int(struct_mg * pos_mult)
        eg += int(struct_eg * pos_mult)


        if phase > 6:
            if wkr <= 1 and (wkf >= 5 or wkf <= 2):
                shield = 0
                for df in (-1, 0, 1):
                    nf = wkf + df
                    if 0 <= nf < 8:
                        if squares[((wkr + 1) << 3) | nf] == PAWN:
                            shield += 15
                        elif wkr + 2 < 8 and squares[((wkr + 2) << 3) | nf] == PAWN:
                            shield += 7
                mg += int(shield * pos_mult)
            if bkr >= 6 and (bkf >= 5 or bkf <= 2):
                shield = 0
                for df in (-1, 0, 1):
                    nf = bkf + df
                    if 0 <= nf < 8:
                        if squares[((bkr - 1) << 3) | nf] == -PAWN:
                            shield += 15
                        elif bkr - 2 >= 0 and squares[((bkr - 2) << 3) | nf] == -PAWN:
                            shield += 7
                mg -= int(shield * pos_mult)

        mg_phase = 24 if phase > 24 else phase
        eg_phase = 24 - mg_phase
        score = (mg * mg_phase + eg * eg_phase) // 24

        if phase <= 6 and abs(score) >= 220:
            king_dist = abs(wkr - bkr) + abs(wkf - bkf)
            if score > 0:
                score += int(CENTER_DIST[bk] * 15) + (14 - king_dist) * 6
            else:
                score -= int(CENTER_DIST[wk] * 15) + (14 - king_dist) * 6

        score += 10 if board.turn == WHITE else -10
        return score if board.turn == WHITE else -score

    def _score_move(self, board: Board, move: int, tt_move: int, ply: int) -> int:
        if move == tt_move:
            return 1_000_000
        squares = board.squares
        from_sq = move & 63
        to_sq = (move >> 6) & 63
        promo = (move >> 12) & 7
        flag = (move >> 15) & 7

        victim = squares[to_sq]
        if victim != EMPTY or flag == FLAG_EN_PASSANT:
            v_type = PAWN if flag == FLAG_EN_PASSANT else abs(victim)
            a_type = abs(squares[from_sq])
            return 500_000 + MVV_VICTIM[v_type] * 10 - MVV_ATTACKER[a_type] + promo * 800
        if promo:
            return 450_000 + promo * 1000
        if ply < 64:
            k = self.killers[ply]
            if move == k[0]:
                return 300_000
            if move == k[1]:
                return 290_000
        return self.history[board.turn][from_sq][to_sq]

    def _has_non_pawn_material(self, board: Board, side: int) -> bool:
        for p in board.squares:
            if p != EMPTY and (p > 0) == (side > 0):
                pt = abs(p)
                if pt in (KNIGHT, BISHOP, ROOK, QUEEN):
                    return True
        return False

    def _is_repetition(self, board: Board) -> bool:
        h = board.zobrist
        hist = board.hash_history
        n = len(hist)
        start = max(0, n - 1 - board.halfmove)
        for i in range(n - 3, start - 1, -2):
            if hist[i] == h:
                return True
        return False

    def _quiescence(self, board: Board, alpha: int, beta: int, ply: int) -> int:
        self.nodes += 1
        if (self.nodes & 1023) == 0 and time.perf_counter() >= self.deadline:
            raise SearchTimeout

        stand_pat = self.evaluate(board)
        if stand_pat >= beta:
            return beta
        if stand_pat + 1050 < alpha:
            return alpha
        if stand_pat > alpha:
            alpha = stand_pat

        if ply >= 60:
            return stand_pat

        moves = board.generate_pseudo_legal_moves(captures_only=True)
        if not moves:
            return alpha

        squares = board.squares
        scored = []
        for mv in moves:
            to_sq = (mv >> 6) & 63
            flag = (mv >> 15) & 7
            v_type = PAWN if flag == FLAG_EN_PASSANT else abs(squares[to_sq])
            a_type = abs(squares[mv & 63])
            promo = (mv >> 12) & 7
            scored.append((MVV_VICTIM[v_type] * 10 - MVV_ATTACKER[a_type] + promo * 800, mv))
        scored.sort(key=lambda x: x[0], reverse=True)

        for _, mv in scored:
            if not board.make_move(mv, record_san=False):
                continue
            score = -self._quiescence(board, -beta, -alpha, ply + 1)
            board.unmake_move(pop_history=True)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def _negamax(
        self,
        board: Board,
        depth: int,
        alpha: int,
        beta: int,
        ply: int,
        allow_null: bool = True,
        extensions: int = 0,
    ) -> int:
        self.nodes += 1
        if (self.nodes & 1023) == 0 and time.perf_counter() >= self.deadline:
            raise SearchTimeout

        if ply > 0:
            if board.halfmove >= 100 or self._is_repetition(board) or board.is_insufficient_material():
                return 0

        in_check = board.in_check()
        if in_check and extensions < 3 and self.use_pruning:
            depth += 1
            extensions += 1

        if depth <= 0:
            if self.use_quiescence:
                return self._quiescence(board, alpha, beta, ply)
            return self.evaluate(board)

        alpha_orig = alpha
        zhash = board.zobrist
        tt_move = 0
        tt_entry = self.tt.get(zhash)
        if tt_entry is not None:
            tt_depth, tt_score, tt_flag, tt_move = tt_entry
            if tt_depth >= depth and ply > 0:
                if tt_score > MATE_THRESHOLD:
                    tt_score -= ply
                elif tt_score < -MATE_THRESHOLD:
                    tt_score += ply
                if tt_flag == TT_EXACT:
                    return tt_score
                if tt_flag == TT_LOWER and tt_score > alpha:
                    alpha = tt_score
                elif tt_flag == TT_UPPER and tt_score < beta:
                    beta = tt_score
                if alpha >= beta:
                    return tt_score

        is_pv = (beta - alpha) > 1


        static_eval = None
        if self.use_pruning and not is_pv and not in_check and ply > 0 and depth <= 2 and abs(beta) < MATE_THRESHOLD:
            static_eval = self.evaluate(board)
            if static_eval - 140 * depth >= beta:
                return static_eval


        if (
            self.use_pruning
            and allow_null
            and depth >= 3
            and ply > 0
            and not in_check
            and beta < MATE_THRESHOLD
            and self._has_non_pawn_material(board, board.turn)
        ):
            old_ep, old_hash = board.make_null_move()
            r = 2 if depth < 6 else 3
            null_score = -self._negamax(board, depth - 1 - r, -beta, -beta + 1, ply + 1, False, extensions)
            board.unmake_null_move(old_ep, old_hash)
            if null_score >= beta:
                return beta

        can_futility = (
            self.use_pruning
            and not is_pv
            and not in_check
            and depth <= 2
            and abs(alpha) < MATE_THRESHOLD
        )
        if can_futility and static_eval is None:
            static_eval = self.evaluate(board)
        futility_margin = 160 * depth

        pseudo = board.generate_pseudo_legal_moves(captures_only=False)
        scored_moves = [(self._score_move(board, mv, tt_move, ply), mv) for mv in pseudo]
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        best_score = -INF
        best_move = 0
        legal_count = 0
        squares = board.squares

        for _, mv in scored_moves:
            is_capture = squares[(mv >> 6) & 63] != EMPTY or ((mv >> 15) & 7) == FLAG_EN_PASSANT
            is_promo = move_promo(mv) != 0

            if not board.make_move(mv, record_san=False):
                continue
            legal_count += 1
            gives_check = board.in_check()

            if (
                can_futility
                and legal_count > 1
                and not is_capture
                and not is_promo
                and not gives_check
                and static_eval is not None
                and static_eval + futility_margin <= alpha
            ):
                board.unmake_move(pop_history=True)
                continue

            if (
                self.use_pruning
                and legal_count >= 4
                and depth >= 3
                and not in_check
                and not is_capture
                and not is_promo
                and not gives_check
            ):
                red = 1 if legal_count < 10 else 2
                score = -self._negamax(board, depth - 1 - red, -alpha - 1, -alpha, ply + 1, True, extensions)
                if score > alpha:
                    score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1, True, extensions)
            elif legal_count == 1:
                score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1, True, extensions)
            else:
                score = -self._negamax(board, depth - 1, -alpha - 1, -alpha, ply + 1, True, extensions)
                if alpha < score < beta:
                    score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1, True, extensions)

            board.unmake_move(pop_history=True)

            if score > best_score:
                best_score = score
                best_move = mv
            if score > alpha:
                alpha = score
                if alpha >= beta:
                    if not is_capture and not is_promo and ply < 64:
                        k = self.killers[ply]
                        if k[0] != mv:
                            k[1] = k[0]
                            k[0] = mv
                        fsq = mv & 63
                        tsq = (mv >> 6) & 63
                        hval = self.history[board.turn][fsq][tsq] + depth * depth
                        self.history[board.turn][fsq][tsq] = min(hval, 250000)
                    break

        if legal_count == 0:
            if in_check:
                return -MATE_SCORE + ply
            return 0

        store_score = best_score
        if store_score > MATE_THRESHOLD:
            store_score += ply
        elif store_score < -MATE_THRESHOLD:
            store_score -= ply

        if best_score <= alpha_orig:
            flag = TT_UPPER
        elif best_score >= beta:
            flag = TT_LOWER
        else:
            flag = TT_EXACT

        if len(self.tt) < 160000:
            self.tt[zhash] = (depth, store_score, flag, best_move)

        return best_score

    def _search_root(
        self,
        board: Board,
        max_depth: int,
        think_time: float,
        noise_cp: int = 0,
        uci_biases: Optional[Dict[str, int]] = None,
    ) -> SearchResult:
        t0 = time.perf_counter()
        self.nodes = 0
        self.deadline = t0 + max(0.03, think_time)
        self.clear_tables()

        work_board = board.copy()
        legal = work_board.legal_moves()
        if not legal:
            return SearchResult(0, 0, 0, 0, 0.0)
        if len(legal) == 1:
            return SearchResult(legal[0], self.evaluate(work_board), 1, 1, time.perf_counter() - t0)

        biases = uci_biases or {}
        best_move = legal[0]
        best_score = -INF
        completed_depth = 0
        root_scores: Dict[int, int] = {}

        for depth in range(1, max_depth + 1):
            try:
                tt_entry = self.tt.get(work_board.zobrist)
                tt_move = tt_entry[3] if tt_entry else best_move
                scored = [(self._score_move(work_board, m, tt_move, 0), m) for m in legal]
                scored.sort(key=lambda x: x[0], reverse=True)

                full_root_window = noise_cp >= 30 and depth <= 2


                if depth >= 4 and not full_root_window and not biases and abs(best_score) < MATE_THRESHOLD:
                    asp_delta = 55
                    alpha = best_score - asp_delta
                    beta = best_score + asp_delta
                else:
                    alpha = -INF
                    beta = INF

                while True:
                    cur_alpha = alpha
                    cur_best_move = scored[0][1]
                    cur_best_score = -INF
                    cur_scores: Dict[int, int] = {}

                    for idx, (_, mv) in enumerate(scored):
                        mv_uci = move_to_uci(mv) if biases else ""
                        is_biased_mv = bool(biases and mv_uci in biases)
                        work_board.make_move(mv, record_san=False)
                        if idx == 0 or full_root_window or is_biased_mv:
                            score = -self._negamax(work_board, depth - 1, -beta, -cur_alpha if not is_biased_mv else INF, 1, True, 0)
                        else:
                            score = -self._negamax(work_board, depth - 1, -cur_alpha - 1, -cur_alpha, 1, True, 0)
                            if cur_alpha < score < beta:
                                score = -self._negamax(work_board, depth - 1, -beta, -cur_alpha, 1, True, 0)
                        work_board.unmake_move(pop_history=True)

                        cur_scores[mv] = score
                        if score > cur_best_score:
                            cur_best_score = score
                            cur_best_move = mv
                        if not full_root_window and not is_biased_mv and score > cur_alpha:
                            cur_alpha = score

                    if (cur_best_score <= alpha or cur_best_score >= beta) and (alpha > -INF or beta < INF):
                        alpha = -INF
                        beta = INF
                        continue
                    break

                best_move = cur_best_move
                best_score = cur_best_score
                root_scores = cur_scores
                completed_depth = depth

                if best_score > MATE_THRESHOLD:
                    break
                if depth >= 2 and (time.perf_counter() - t0) > think_time * 0.55:
                    break
            except SearchTimeout:
                break

        memory_note: Optional[str] = None

        if biases and root_scores and best_score < MATE_THRESHOLD:
            natural_best = best_move
            natural_sc = root_scores[natural_best]
            biased_list = []
            for m, sc in root_scores.items():
                u = move_to_uci(m)
                adj = sc + biases.get(u, 0) if abs(sc) < MATE_THRESHOLD else sc
                biased_list.append((adj, m, sc, u))
            biased_list.sort(key=lambda x: x[0], reverse=True)
            _, picked_m, picked_sc, picked_u = biased_list[0]

            if picked_sc >= natural_sc - 140:
                best_move = picked_m
                best_score = picked_sc
                avoided_was_contender = any(
                    biases.get(move_to_uci(m), 0) < 0 and sc >= natural_sc - 45
                    for m, sc in root_scores.items()
                )
                if avoided_was_contender and biases.get(picked_u, 0) >= 0:
                    memory_note = "avoided"
                elif biases.get(picked_u, 0) > 0:
                    memory_note = "trap"

        if noise_cp > 0 and root_scores:
            mate_moves = [m for m, s in root_scores.items() if s > MATE_THRESHOLD]
            if mate_moves and (noise_cp < 400 or random.random() < 0.45):
                best_move = mate_moves[0]
                best_score = root_scores[best_move]
            elif noise_cp >= 30:
                noisy = [
                    (s + random.randint(-noise_cp, noise_cp), m, s)
                    for m, s in root_scores.items()
                ]
                noisy.sort(key=lambda x: x[0], reverse=True)
                _, best_move, best_score = noisy[0]
            else:
                near_best = [
                    (m, s) for m, s in root_scores.items() if s >= best_score - noise_cp
                ]
                if near_best:
                    best_move, best_score = random.choice(near_best)

        elapsed = time.perf_counter() - t0
        return SearchResult(best_move, best_score, max(1, completed_depth), self.nodes, elapsed, False, memory_note)

    def choose_move(
        self,
        board: Board,
        profile: BotProfile,
        time_override: Optional[float] = None,
        brain: Optional["EvolvingBrain"] = None,
    ) -> SearchResult:

        t0 = time.perf_counter()
        legal = board.legal_moves()
        if not legal:
            return SearchResult(0, 0, 0, 0, 0.0)

        self.use_quiescence = profile.use_quiescence
        self.use_pruning = profile.use_pruning
        self.aggression = profile.aggression
        self.positional = profile.positional

        zhex = f"{board.zobrist:016x}"
        avoid_ucis = brain.avoided_moves(zhex) if brain is not None else set()
        uci_biases = brain.move_bias_map(zhex) if brain is not None else {}


        if profile.book_prob > 0 and random.random() < profile.book_prob:
            bm = lookup_book_move(board, profile.book_style, avoid_ucis=avoid_ucis)
            if bm is not None:
                mem_note = "avoided" if avoid_ucis else None
                return SearchResult(
                    bm, self.evaluate(board), 0, 1, time.perf_counter() - t0, from_book=True, memory_note=mem_note
                )


        if profile.blunder_rate > 0 and len(legal) > 1 and random.random() < profile.blunder_rate:
            has_m1 = False
            if profile.elo >= 1000:
                wb = board.copy()
                for mv in legal:
                    wb.make_move(mv, record_san=False)
                    if wb.is_checkmate():
                        has_m1 = True
                        wb.unmake_move(pop_history=True)
                        break
                    wb.unmake_move(pop_history=True)
            if not has_m1:
                if profile.elo <= 250:
                    mv = random.choice(legal)
                    return SearchResult(mv, self.evaluate(board), 1, len(legal), time.perf_counter() - t0, False)
                wb = board.copy()
                scored = []
                for mv in legal:
                    wb.make_move(mv, record_san=False)
                    sc = -self.evaluate(wb) + random.randint(-profile.noise_cp, profile.noise_cp)
                    wb.unmake_move(pop_history=True)
                    scored.append((sc, mv))
                scored.sort(key=lambda x: x[0], reverse=True)
                pool = scored[: max(2, min(len(scored), 5))]
                _, picked = random.choice(pool)
                return SearchResult(picked, self.evaluate(board), 1, len(legal), time.perf_counter() - t0, False)


        think = time_override if time_override is not None else profile.think_time
        return self._search_root(
            board,
            max_depth=profile.max_depth,
            think_time=think,
            noise_cp=profile.noise_cp,
            uci_biases=uci_biases if uci_biases else None,
        )

    def get_hint(self, board: Board, think_time: float = 0.85) -> SearchResult:

        self.use_quiescence = True
        self.use_pruning = True
        self.aggression = 1.12
        self.positional = 1.12
        bm = lookup_book_move(board, "master")
        if bm is not None:
            return SearchResult(bm, self.evaluate(board), 0, 1, 0.01, from_book=True)
        return self._search_root(board, max_depth=5, think_time=think_time, noise_cp=0)

    def evaluate_player_move(self, board_before: Board, player_move: int) -> Tuple[int, int, int, bool]:


        uci = move_to_uci(player_move)
        book_hit = is_book_move(board_before, uci)

        saved_q, saved_p = self.use_quiescence, self.use_pruning
        self.use_quiescence = True
        self.use_pruning = False
        self.aggression = 1.0
        self.positional = 1.0
        try:
            best_res = self._search_root(board_before, max_depth=2, think_time=0.07, noise_cp=0)
            best_score = best_res.score_cp
            best_move = best_res.move

            if player_move == best_move:
                return 0, best_score, best_move, book_hit

            b_copy = board_before.copy()
            b_copy.make_move(player_move, record_san=False)
            self.nodes = 0
            self.deadline = time.perf_counter() + 0.05
            try:
                reply_score = self._negamax(b_copy, 1, -INF, INF, 1, False, 0)
                player_score = -reply_score
            except SearchTimeout:
                player_score = -self.evaluate(b_copy)

            cp_loss = max(0, best_score - player_score)
            return cp_loss, player_score, best_move, book_hit
        finally:
            self.use_quiescence, self.use_pruning = saved_q, saved_p

    def extract_pv(self, board: Board, first_move: int, max_len: int = 5) -> List[str]:

        if not first_move:
            return []
        wb = board.copy()
        pv_sans: List[str] = []
        seen_hashes: Set[int] = set()
        cur_mv = first_move

        for _ in range(max_len):
            legal = wb.legal_moves()
            if cur_mv not in legal:
                break
            pv_sans.append(wb.move_to_san(cur_mv))
            wb.make_move(cur_mv, record_san=False)
            if wb.zobrist in seen_hashes:
                break
            seen_hashes.add(wb.zobrist)
            tt = self.tt.get(wb.zobrist)
            if not tt or not tt[3]:
                break
            cur_mv = tt[3]
        return pv_sans

    def coach_advice(self, board: Board) -> Dict[str, object]:

        side = board.turn
        enemy = -side
        piece_names_id = {
            PAWN: "Pion",
            KNIGHT: "Kuda",
            BISHOP: "Gajah",
            ROOK: "Benteng",
            QUEEN: "Menteri",
            KING: "Raja",
        }
        our_hanging: List[str] = []
        enemy_hanging: List[str] = []

        for sq, p in enumerate(board.squares):
            if p == EMPTY or abs(p) == KING:
                continue
            pt = abs(p)
            if (p > 0) == (side > 0):
                if pt >= KNIGHT and board.is_square_attacked(sq, enemy) and not board.is_square_attacked(sq, side):
                    our_hanging.append(f"{piece_names_id[pt]} di {sq_to_name(sq)}")
            else:
                if pt >= KNIGHT and board.is_square_attacked(sq, side) and not board.is_square_attacked(sq, enemy):
                    enemy_hanging.append(f"{piece_names_id[pt]} lawan di {sq_to_name(sq)}")

        tips: List[str] = []
        if board.in_check():
            tips.append("Rajamu sedang SKAK! Fokus selamatkan raja atau tutup jalur serangannya.")
        if our_hanging:
            tips.append(f"Awas! Bidak tidak terjaga & terancam: {', '.join(our_hanging[:2])}.")
        if enemy_hanging:
            tips.append(f"Peluang! Bidak lawan menggantung: {', '.join(enemy_hanging[:2])}.")

        can_castle = (
            bool(board.castling & (CASTLE_WK | CASTLE_WQ))
            if side == WHITE
            else bool(board.castling & (CASTLE_BK | CASTLE_BQ))
        )
        if can_castle and 8 <= len(board.move_history) <= 22:
            tips.append("Pertimbangkan rokade (O-O / O-O-O) untuk mengamankan rajamu.")

        hint_res = self.get_hint(board, think_time=0.65)
        pv = self.extract_pv(board, hint_res.move, max_len=5) if hint_res.move else []
        best_san = pv[0] if pv else (board.move_to_san(hint_res.move) if hint_res.move else "-")

        return {
            "best_move": hint_res.move,
            "best_san": best_san,
            "score_cp": hint_res.score_cp,
            "depth": hint_res.depth,
            "from_book": hint_res.from_book,
            "pv": pv,
            "tips": tips,
        }
