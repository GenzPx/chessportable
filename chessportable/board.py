from __future__ import annotations

import random
import re
from typing import Dict, List, Optional, Tuple


WHITE = 1
BLACK = -1

EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6


WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
BP, BN, BB, BR, BQ, BK = -1, -2, -3, -4, -5, -6


CASTLE_WK = 1
CASTLE_WQ = 2
CASTLE_BK = 4
CASTLE_BQ = 8


FLAG_NORMAL = 0
FLAG_DOUBLE_PAWN = 1
FLAG_EN_PASSANT = 2
FLAG_CASTLE_KING = 3
FLAG_CASTLE_QUEEN = 4

FILES = "abcdefgh"
RANKS = "12345678"

PIECE_TO_CHAR = {
    WP: "P", WN: "N", WB: "B", WR: "R", WQ: "Q", WK: "K",
    BP: "p", BN: "n", BB: "b", BR: "r", BQ: "q", BK: "k",
    EMPTY: ".",
}

CHAR_TO_PIECE = {v: k for k, v in PIECE_TO_CHAR.items() if k != EMPTY}

PIECE_TYPE_TO_SAN = {
    PAWN: "",
    KNIGHT: "N",
    BISHOP: "B",
    ROOK: "R",
    QUEEN: "Q",
    KING: "K",
}

SAN_CHAR_TO_TYPE = {
    "N": KNIGHT,
    "B": BISHOP,
    "R": ROOK,
    "Q": QUEEN,
    "K": KING,
}

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class IllegalMoveError(ValueError):
    pass

class PromotionRequiredError(Exception):

    def __init__(self, moves: List[int]) -> None:
        super().__init__("Promotion piece required")
        self.moves = moves

def encode_move(from_sq: int, to_sq: int, promo: int = 0, flag: int = FLAG_NORMAL) -> int:
    return from_sq | (to_sq << 6) | (promo << 12) | (flag << 15)

def move_from(move: int) -> int:
    return move & 63

def move_to(move: int) -> int:
    return (move >> 6) & 63

def move_promo(move: int) -> int:
    return (move >> 12) & 7

def move_flag(move: int) -> int:
    return (move >> 15) & 7


def sq_to_name(sq: int) -> str:
    return FILES[sq & 7] + RANKS[sq >> 3]

def name_to_sq(name: str) -> int:
    if len(name) != 2:
        return -1
    f = FILES.find(name[0].lower())
    r = RANKS.find(name[1])
    if f < 0 or r < 0:
        return -1
    return (r << 3) | f

def move_to_uci(move: int) -> str:
    s = sq_to_name(move & 63) + sq_to_name((move >> 6) & 63)
    p = (move >> 12) & 7
    if p:
        s += PIECE_TYPE_TO_SAN[p].lower()
    return s

KNIGHT_MOVES: Tuple[Tuple[int, ...], ...] = ()
KING_MOVES: Tuple[Tuple[int, ...], ...] = ()
DIAG_RAYS: Tuple[Tuple[Tuple[int, ...], ...], ...] = ()
ORTHO_RAYS: Tuple[Tuple[Tuple[int, ...], ...], ...] = ()

PAWN_ATTACKERS: Dict[int, Tuple[Tuple[int, ...], ...]] = {}

PAWN_CAPTURES: Dict[int, Tuple[Tuple[int, ...], ...]] = {}

CASTLING_MASK = [15] * 64
CASTLING_MASK[0] &= ~CASTLE_WQ
CASTLING_MASK[4] &= ~(CASTLE_WK | CASTLE_WQ)
CASTLING_MASK[7] &= ~CASTLE_WK
CASTLING_MASK[56] &= ~CASTLE_BQ
CASTLING_MASK[60] &= ~(CASTLE_BK | CASTLE_BQ)
CASTLING_MASK[63] &= ~CASTLE_BK

def _init_tables() -> None:
    global KNIGHT_MOVES, KING_MOVES, DIAG_RAYS, ORTHO_RAYS, PAWN_ATTACKERS, PAWN_CAPTURES
    kn_list = []
    ki_list = []
    diag_list = []
    ortho_list = []
    wp_att = []
    bp_att = []
    wp_cap = []
    bp_cap = []

    knight_deltas = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    king_deltas = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    diag_dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    ortho_dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

    for sq in range(64):
        r, f = sq >> 3, sq & 7

        kn_list.append(tuple(
            ((r + dr) << 3) | (f + df)
            for dr, df in knight_deltas
            if 0 <= r + dr < 8 and 0 <= f + df < 8
        ))
        ki_list.append(tuple(
            ((r + dr) << 3) | (f + df)
            for dr, df in king_deltas
            if 0 <= r + dr < 8 and 0 <= f + df < 8
        ))

        d_rays = []
        for dr, df in diag_dirs:
            ray = []
            nr, nf = r + dr, f + df
            while 0 <= nr < 8 and 0 <= nf < 8:
                ray.append((nr << 3) | nf)
                nr += dr
                nf += df
            if ray:
                d_rays.append(tuple(ray))
        diag_list.append(tuple(d_rays))

        o_rays = []
        for dr, df in ortho_dirs:
            ray = []
            nr, nf = r + dr, f + df
            while 0 <= nr < 8 and 0 <= nf < 8:
                ray.append((nr << 3) | nf)
                nr += dr
                nf += df
            if ray:
                o_rays.append(tuple(ray))
        ortho_list.append(tuple(o_rays))

        wa = []
        if r > 0:
            if f > 0:
                wa.append(((r - 1) << 3) | (f - 1))
            if f < 7:
                wa.append(((r - 1) << 3) | (f + 1))
        wp_att.append(tuple(wa))


        ba = []
        if r < 7:
            if f > 0:
                ba.append(((r + 1) << 3) | (f - 1))
            if f < 7:
                ba.append(((r + 1) << 3) | (f + 1))
        bp_att.append(tuple(ba))


        wc = []
        if r < 7:
            if f > 0:
                wc.append(((r + 1) << 3) | (f - 1))
            if f < 7:
                wc.append(((r + 1) << 3) | (f + 1))
        wp_cap.append(tuple(wc))

        bc = []
        if r > 0:
            if f > 0:
                bc.append(((r - 1) << 3) | (f - 1))
            if f < 7:
                bc.append(((r - 1) << 3) | (f + 1))
        bp_cap.append(tuple(bc))

    KNIGHT_MOVES = tuple(kn_list)
    KING_MOVES = tuple(ki_list)
    DIAG_RAYS = tuple(diag_list)
    ORTHO_RAYS = tuple(ortho_list)
    PAWN_ATTACKERS = {WHITE: tuple(wp_att), BLACK: tuple(bp_att)}
    PAWN_CAPTURES = {WHITE: tuple(wp_cap), BLACK: tuple(bp_cap)}


_init_tables()

_rng = random.Random(0xC4E55001)

ZOBRIST_PIECE: List[List[int]] = [
    [_rng.getrandbits(64) for _ in range(64)] for _ in range(13)
]
ZOBRIST_SIDE: int = _rng.getrandbits(64)
ZOBRIST_CASTLING: List[int] = [_rng.getrandbits(64) for _ in range(16)]
ZOBRIST_EP: List[int] = [_rng.getrandbits(64) for _ in range(8)]

class Board:

    __slots__ = (
        "squares",
        "turn",
        "castling",
        "ep_sq",
        "halfmove",
        "fullmove",
        "king_sq",
        "zobrist",
        "undo_stack",
        "hash_history",
        "move_history",
        "san_history",
    )

    def __init__(self, fen: str = START_FEN) -> None:
        self.squares: List[int] = [EMPTY] * 64
        self.turn: int = WHITE
        self.castling: int = 0
        self.ep_sq: int = -1
        self.halfmove: int = 0
        self.fullmove: int = 1
        self.king_sq: Dict[int, int] = {WHITE: 4, BLACK: 60}
        self.zobrist: int = 0
        self.undo_stack: List[Tuple[int, int, int, int, int, int, int, bool]] = []
        self.hash_history: List[int] = []
        self.move_history: List[int] = []
        self.san_history: List[str] = []
        self.set_fen(fen)

    def copy(self) -> "Board":
        b = Board.__new__(Board)
        b.squares = self.squares[:]
        b.turn = self.turn
        b.castling = self.castling
        b.ep_sq = self.ep_sq
        b.halfmove = self.halfmove
        b.fullmove = self.fullmove
        b.king_sq = {WHITE: self.king_sq[WHITE], BLACK: self.king_sq[BLACK]}
        b.zobrist = self.zobrist
        b.undo_stack = self.undo_stack[:]
        b.hash_history = self.hash_history[:]
        b.move_history = self.move_history[:]
        b.san_history = self.san_history[:]
        return b

    def set_fen(self, fen: str) -> None:
        parts = fen.strip().split()
        if len(parts) < 4:
            raise ValueError(f"Invalid FEN: {fen}")
        rows = parts[0].split("/")
        if len(rows) != 8:
            raise ValueError(f"Invalid FEN board rows: {fen}")

        self.squares = [EMPTY] * 64
        self.king_sq = {WHITE: -1, BLACK: -1}

        for r_idx, row in enumerate(rows):
            rank = 7 - r_idx
            file_idx = 0
            for ch in row:
                if ch.isdigit():
                    file_idx += int(ch)
                else:
                    piece = CHAR_TO_PIECE.get(ch)
                    if piece is None or file_idx >= 8:
                        raise ValueError(f"Invalid FEN piece '{ch}' in {fen}")
                    sq = (rank << 3) | file_idx
                    self.squares[sq] = piece
                    if piece == WK:
                        self.king_sq[WHITE] = sq
                    elif piece == BK:
                        self.king_sq[BLACK] = sq
                    file_idx += 1
            if file_idx != 8:
                raise ValueError(f"Invalid FEN rank width in {fen}")

        self.turn = WHITE if parts[1] == "w" else BLACK

        self.castling = 0
        c_str = parts[2]
        if "K" in c_str:
            self.castling |= CASTLE_WK
        if "Q" in c_str:
            self.castling |= CASTLE_WQ
        if "k" in c_str:
            self.castling |= CASTLE_BK
        if "q" in c_str:
            self.castling |= CASTLE_BQ

        self.ep_sq = -1 if parts[3] == "-" else name_to_sq(parts[3])
        self.halfmove = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove = int(parts[5]) if len(parts) > 5 else 1

        self.zobrist = self._compute_zobrist()
        self.undo_stack = []
        self.hash_history = [self.zobrist]
        self.move_history = []
        self.san_history = []

    def fen(self) -> str:
        rows = []
        for rank in range(7, -1, -1):
            empty_run = 0
            row_chars = []
            base = rank << 3
            for f in range(8):
                p = self.squares[base | f]
                if p == EMPTY:
                    empty_run += 1
                else:
                    if empty_run:
                        row_chars.append(str(empty_run))
                        empty_run = 0
                    row_chars.append(PIECE_TO_CHAR[p])
            if empty_run:
                row_chars.append(str(empty_run))
            rows.append("".join(row_chars))

        turn_ch = "w" if self.turn == WHITE else "b"
        c_str = ""
        if self.castling & CASTLE_WK:
            c_str += "K"
        if self.castling & CASTLE_WQ:
            c_str += "Q"
        if self.castling & CASTLE_BK:
            c_str += "k"
        if self.castling & CASTLE_BQ:
            c_str += "q"
        if not c_str:
            c_str = "-"
        ep_str = "-" if self.ep_sq == -1 else sq_to_name(self.ep_sq)
        return f"{'/'.join(rows)} {turn_ch} {c_str} {ep_str} {self.halfmove} {self.fullmove}"

    def _compute_zobrist(self) -> int:
        h = 0
        sq_arr = self.squares
        zp = ZOBRIST_PIECE
        for sq in range(64):
            p = sq_arr[sq]
            if p:
                h ^= zp[p + 6][sq]
        if self.turn == BLACK:
            h ^= ZOBRIST_SIDE
        h ^= ZOBRIST_CASTLING[self.castling]
        if self.ep_sq != -1:
            h ^= ZOBRIST_EP[self.ep_sq & 7]
        return h

    def is_square_attacked(self, sq: int, by_side: int) -> bool:
        squares = self.squares


        enemy_pawn = by_side
        for att_sq in PAWN_ATTACKERS[by_side][sq]:
            if squares[att_sq] == enemy_pawn:
                return True


        enemy_knight = by_side * KNIGHT
        for att_sq in KNIGHT_MOVES[sq]:
            if squares[att_sq] == enemy_knight:
                return True


        enemy_king = by_side * KING
        for att_sq in KING_MOVES[sq]:
            if squares[att_sq] == enemy_king:
                return True


        enemy_bishop = by_side * BISHOP
        enemy_queen = by_side * QUEEN
        for ray in DIAG_RAYS[sq]:
            for t in ray:
                p = squares[t]
                if p:
                    if p == enemy_bishop or p == enemy_queen:
                        return True
                    break


        enemy_rook = by_side * ROOK
        for ray in ORTHO_RAYS[sq]:
            for t in ray:
                p = squares[t]
                if p:
                    if p == enemy_rook or p == enemy_queen:
                        return True
                    break

        return False

    def in_check(self, side: Optional[int] = None) -> bool:
        if side is None:
            side = self.turn
        ksq = self.king_sq[side]
        if ksq < 0:
            return False
        return self.is_square_attacked(ksq, -side)

    def generate_pseudo_legal_moves(self, captures_only: bool = False) -> List[int]:
        moves: List[int] = []
        squares = self.squares
        side = self.turn
        ep_sq = self.ep_sq
        pawn_cap_table = PAWN_CAPTURES[side]
        forward = 8 if side == WHITE else -8
        start_rank = 1 if side == WHITE else 6
        promo_rank = 7 if side == WHITE else 0

        for sq in range(64):
            piece = squares[sq]
            if piece == EMPTY or (piece > 0) != (side > 0):
                continue

            ptype = piece if piece > 0 else -piece

            if ptype == PAWN:
                rank = sq >> 3

                for target in pawn_cap_table[sq]:
                    tp = squares[target]
                    if tp != EMPTY and (tp > 0) != (side > 0):
                        if (target >> 3) == promo_rank:
                            moves.append(sq | (target << 6) | (QUEEN << 12))
                            moves.append(sq | (target << 6) | (ROOK << 12))
                            moves.append(sq | (target << 6) | (BISHOP << 12))
                            moves.append(sq | (target << 6) | (KNIGHT << 12))
                        else:
                            moves.append(sq | (target << 6))
                    elif target == ep_sq:
                        moves.append(sq | (target << 6) | (FLAG_EN_PASSANT << 15))


                one = sq + forward
                if squares[one] == EMPTY:
                    if (one >> 3) == promo_rank:

                        moves.append(sq | (one << 6) | (QUEEN << 12))
                        moves.append(sq | (one << 6) | (ROOK << 12))
                        moves.append(sq | (one << 6) | (BISHOP << 12))
                        moves.append(sq | (one << 6) | (KNIGHT << 12))
                    elif not captures_only:
                        moves.append(sq | (one << 6))
                        if rank == start_rank:
                            two = one + forward
                            if squares[two] == EMPTY:
                                moves.append(sq | (two << 6) | (FLAG_DOUBLE_PAWN << 15))

            elif ptype == KNIGHT:
                for target in KNIGHT_MOVES[sq]:
                    tp = squares[target]
                    if tp == EMPTY:
                        if not captures_only:
                            moves.append(sq | (target << 6))
                    elif (tp > 0) != (side > 0):
                        moves.append(sq | (target << 6))

            elif ptype == BISHOP:
                for ray in DIAG_RAYS[sq]:
                    for target in ray:
                        tp = squares[target]
                        if tp == EMPTY:
                            if not captures_only:
                                moves.append(sq | (target << 6))
                        else:
                            if (tp > 0) != (side > 0):
                                moves.append(sq | (target << 6))
                            break

            elif ptype == ROOK:
                for ray in ORTHO_RAYS[sq]:
                    for target in ray:
                        tp = squares[target]
                        if tp == EMPTY:
                            if not captures_only:
                                moves.append(sq | (target << 6))
                        else:
                            if (tp > 0) != (side > 0):
                                moves.append(sq | (target << 6))
                            break

            elif ptype == QUEEN:
                for ray in DIAG_RAYS[sq]:
                    for target in ray:
                        tp = squares[target]
                        if tp == EMPTY:
                            if not captures_only:
                                moves.append(sq | (target << 6))
                        else:
                            if (tp > 0) != (side > 0):
                                moves.append(sq | (target << 6))
                            break
                for ray in ORTHO_RAYS[sq]:
                    for target in ray:
                        tp = squares[target]
                        if tp == EMPTY:
                            if not captures_only:
                                moves.append(sq | (target << 6))
                        else:
                            if (tp > 0) != (side > 0):
                                moves.append(sq | (target << 6))
                            break

            elif ptype == KING:
                for target in KING_MOVES[sq]:
                    tp = squares[target]
                    if tp == EMPTY:
                        if not captures_only:
                            moves.append(sq | (target << 6))
                    elif (tp > 0) != (side > 0):
                        moves.append(sq | (target << 6))

                if not captures_only:
                    c = self.castling
                    if side == WHITE and sq == 4:
                        if (c & CASTLE_WK) and squares[5] == EMPTY and squares[6] == EMPTY and squares[7] == WR:
                            if (
                                not self.is_square_attacked(4, BLACK)
                                and not self.is_square_attacked(5, BLACK)
                                and not self.is_square_attacked(6, BLACK)
                            ):
                                moves.append(4 | (6 << 6) | (FLAG_CASTLE_KING << 15))
                        if (
                            (c & CASTLE_WQ)
                            and squares[3] == EMPTY
                            and squares[2] == EMPTY
                            and squares[1] == EMPTY
                            and squares[0] == WR
                        ):
                            if (
                                not self.is_square_attacked(4, BLACK)
                                and not self.is_square_attacked(3, BLACK)
                                and not self.is_square_attacked(2, BLACK)
                            ):
                                moves.append(4 | (2 << 6) | (FLAG_CASTLE_QUEEN << 15))
                    elif side == BLACK and sq == 60:
                        if (c & CASTLE_BK) and squares[61] == EMPTY and squares[62] == EMPTY and squares[63] == BR:
                            if (
                                not self.is_square_attacked(60, WHITE)
                                and not self.is_square_attacked(61, WHITE)
                                and not self.is_square_attacked(62, WHITE)
                            ):
                                moves.append(60 | (62 << 6) | (FLAG_CASTLE_KING << 15))
                        if (
                            (c & CASTLE_BQ)
                            and squares[59] == EMPTY
                            and squares[58] == EMPTY
                            and squares[57] == EMPTY
                            and squares[56] == BR
                        ):
                            if (
                                not self.is_square_attacked(60, WHITE)
                                and not self.is_square_attacked(59, WHITE)
                                and not self.is_square_attacked(58, WHITE)
                            ):
                                moves.append(60 | (58 << 6) | (FLAG_CASTLE_QUEEN << 15))

        return moves

    def make_move(self, move: int, record_san: bool = False) -> bool:

        san_text = ""
        if record_san:
            san_text = self.move_to_san(move)

        squares = self.squares
        side = self.turn
        from_sq = move & 63
        to_sq = (move >> 6) & 63
        promo = (move >> 12) & 7
        flag = (move >> 15) & 7

        moved = squares[from_sq]
        captured = squares[to_sq]

        old_castling = self.castling
        old_ep = self.ep_sq
        old_halfmove = self.halfmove
        old_hash = self.zobrist
        old_king = self.king_sq[side]

        h = old_hash
        zp = ZOBRIST_PIECE

        if old_ep != -1:
            h ^= ZOBRIST_EP[old_ep & 7]
        h ^= ZOBRIST_CASTLING[old_castling]

        h ^= zp[moved + 6][from_sq]
        squares[from_sq] = EMPTY

        if flag == FLAG_EN_PASSANT:
            cap_sq = to_sq - 8 if side == WHITE else to_sq + 8
            captured = squares[cap_sq]
            h ^= zp[captured + 6][cap_sq]
            squares[cap_sq] = EMPTY
        elif captured != EMPTY:
            h ^= zp[captured + 6][to_sq]

        placed = (side * promo) if promo else moved
        squares[to_sq] = placed
        h ^= zp[placed + 6][to_sq]

        if moved == WK or moved == BK:
            self.king_sq[side] = to_sq
            if flag == FLAG_CASTLE_KING:
                r_from, r_to = (7, 5) if side == WHITE else (63, 61)
                rook = squares[r_from]
                h ^= zp[rook + 6][r_from] ^ zp[rook + 6][r_to]
                squares[r_from] = EMPTY
                squares[r_to] = rook
            elif flag == FLAG_CASTLE_QUEEN:
                r_from, r_to = (0, 3) if side == WHITE else (56, 59)
                rook = squares[r_from]
                h ^= zp[rook + 6][r_from] ^ zp[rook + 6][r_to]
                squares[r_from] = EMPTY
                squares[r_to] = rook


        new_castling = old_castling & CASTLING_MASK[from_sq] & CASTLING_MASK[to_sq]
        self.castling = new_castling
        h ^= ZOBRIST_CASTLING[new_castling]


        if flag == FLAG_DOUBLE_PAWN:
            new_ep = (from_sq + to_sq) >> 1
            self.ep_sq = new_ep
            h ^= ZOBRIST_EP[new_ep & 7]
        else:
            self.ep_sq = -1

        if (moved == WP or moved == BP) or captured != EMPTY:
            self.halfmove = 0
        else:
            self.halfmove = old_halfmove + 1

        if side == BLACK:
            self.fullmove += 1

        self.turn = -side
        h ^= ZOBRIST_SIDE
        self.zobrist = h

        self.undo_stack.append((move, captured, old_castling, old_ep, old_halfmove, old_hash, old_king, record_san))


        if self.is_square_attacked(self.king_sq[side], -side):
            self.unmake_move(pop_history=False)
            return False

        self.hash_history.append(h)
        self.move_history.append(move)
        if record_san:
            self.san_history.append(san_text)
        return True

    def unmake_move(self, pop_history: bool = True) -> None:
        move, captured, old_castling, old_ep, old_halfmove, old_hash, old_king, did_san = self.undo_stack.pop()

        if pop_history:
            self.hash_history.pop()
            self.move_history.pop()
            if did_san and self.san_history:
                self.san_history.pop()

        self.turn = -self.turn
        side = self.turn
        if side == BLACK:
            self.fullmove -= 1

        self.castling = old_castling
        self.ep_sq = old_ep
        self.halfmove = old_halfmove
        self.zobrist = old_hash
        self.king_sq[side] = old_king

        squares = self.squares
        from_sq = move & 63
        to_sq = (move >> 6) & 63
        promo = (move >> 12) & 7
        flag = (move >> 15) & 7

        moved = (side * PAWN) if promo else squares[to_sq]
        squares[from_sq] = moved

        if flag == FLAG_EN_PASSANT:
            squares[to_sq] = EMPTY
            cap_sq = to_sq - 8 if side == WHITE else to_sq + 8
            squares[cap_sq] = captured
        else:
            squares[to_sq] = captured

        if flag == FLAG_CASTLE_KING:
            r_from, r_to = (7, 5) if side == WHITE else (63, 61)
            squares[r_from] = squares[r_to]
            squares[r_to] = EMPTY
        elif flag == FLAG_CASTLE_QUEEN:
            r_from, r_to = (0, 3) if side == WHITE else (56, 59)
            squares[r_from] = squares[r_to]
            squares[r_to] = EMPTY

    def make_null_move(self) -> Tuple[int, int]:

        old_ep = self.ep_sq
        old_hash = self.zobrist
        h = old_hash
        if old_ep != -1:
            h ^= ZOBRIST_EP[old_ep & 7]
            self.ep_sq = -1
        self.turn = -self.turn
        h ^= ZOBRIST_SIDE
        self.zobrist = h
        return old_ep, old_hash

    def unmake_null_move(self, old_ep: int, old_hash: int) -> None:
        self.turn = -self.turn
        self.ep_sq = old_ep
        self.zobrist = old_hash

    def legal_moves(self) -> List[int]:
        legal: List[int] = []
        for mv in self.generate_pseudo_legal_moves(captures_only=False):
            if self.make_move(mv, record_san=False):
                legal.append(mv)
                self.unmake_move(pop_history=True)
        return legal

    def has_legal_moves(self) -> bool:
        for mv in self.generate_pseudo_legal_moves(captures_only=False):
            if self.make_move(mv, record_san=False):
                self.unmake_move(pop_history=True)
                return True
        return False

    def is_checkmate(self) -> bool:
        return self.in_check() and not self.has_legal_moves()

    def is_stalemate(self) -> bool:
        return not self.in_check() and not self.has_legal_moves()

    def is_fifty_moves(self) -> bool:
        return self.halfmove >= 100

    def is_threefold_repetition(self) -> bool:
        cur = self.zobrist
        count = 0

        start = max(0, len(self.hash_history) - 1 - self.halfmove)
        for i in range(len(self.hash_history) - 1, start - 1, -2):
            if self.hash_history[i] == cur:
                count += 1
                if count >= 3:
                    return True
        return False

    def is_insufficient_material(self) -> bool:
        minors: List[Tuple[int, int]] = []
        for sq, p in enumerate(self.squares):
            if p == EMPTY or p == WK or p == BK:
                continue
            pt = abs(p)
            if pt in (PAWN, ROOK, QUEEN):
                return False
            minors.append((pt, ((sq >> 3) + (sq & 7)) & 1))
            if len(minors) > 2:
                return False
        if len(minors) <= 1:
            return True

        if len(minors) == 2 and minors[0][0] == BISHOP and minors[1][0] == BISHOP:


            if minors[0][1] == minors[1][1]:
                return True
        return False

    def game_result(self) -> Optional[Tuple[str, str]]:

        if not self.has_legal_moves():
            if self.in_check():
                winner = "0-1" if self.turn == WHITE else "1-0"
                return (winner, "Skakmat (Checkmate)")
            return ("1/2-1/2", "Remis — Stalemate (Buntu)")
        if self.is_threefold_repetition():
            return ("1/2-1/2", "Remis — Pengulangan posisi 3x (Threefold Repetition)")
        if self.is_fifty_moves():
            return ("1/2-1/2", "Remis — Aturan 50 langkah (50-Move Rule)")
        if self.is_insufficient_material():
            return ("1/2-1/2", "Remis — Materi tidak cukup (Insufficient Material)")
        return None

    def captured_pieces(self) -> Tuple[List[int], List[int]]:

        start_counts = {
            WP: 8, WN: 2, WB: 2, WR: 2, WQ: 1,
            BP: 8, BN: 2, BB: 2, BR: 2, BQ: 1,
        }
        cur_counts: Dict[int, int] = {k: 0 for k in start_counts}
        for p in self.squares:
            if p in cur_counts:
                cur_counts[p] += 1

        cap_by_white: List[int] = []
        cap_by_black: List[int] = []
        for pt in (QUEEN, ROOK, BISHOP, KNIGHT, PAWN):
            missing_black = max(0, start_counts[-pt] - cur_counts[-pt])
            cap_by_white.extend([-pt] * missing_black)
            missing_white = max(0, start_counts[pt] - cur_counts[pt])
            cap_by_black.extend([pt] * missing_white)
        return cap_by_white, cap_by_black

    def material_balance(self) -> int:

        vals = {PAWN: 1, KNIGHT: 3, BISHOP: 3, ROOK: 5, QUEEN: 9, KING: 0}
        total = 0
        for p in self.squares:
            if p > 0:
                total += vals[p]
            elif p < 0:
                total -= vals[-p]
        return total

    def move_to_san(self, move: int) -> str:
        from_sq = move & 63
        to_sq = (move >> 6) & 63
        promo = (move >> 12) & 7
        flag = (move >> 15) & 7

        piece = self.squares[from_sq]
        ptype = abs(piece)
        is_capture = (self.squares[to_sq] != EMPTY) or (flag == FLAG_EN_PASSANT)

        if flag == FLAG_CASTLE_KING:
            san = "O-O"
        elif flag == FLAG_CASTLE_QUEEN:
            san = "O-O-O"
        elif ptype == PAWN:
            if is_capture:
                san = FILES[from_sq & 7] + "x" + sq_to_name(to_sq)
            else:
                san = sq_to_name(to_sq)
            if promo:
                san += "=" + PIECE_TYPE_TO_SAN[promo]
        else:

            others = [
                m for m in self.legal_moves()
                if m != move
                and ((m >> 6) & 63) == to_sq
                and self.squares[m & 63] == piece
            ]
            disamb = ""
            if others:
                same_file = any(((m & 63) & 7) == (from_sq & 7) for m in others)
                same_rank = any(((m & 63) >> 3) == (from_sq >> 3) for m in others)
                if not same_file:
                    disamb = FILES[from_sq & 7]
                elif not same_rank:
                    disamb = RANKS[from_sq >> 3]
                else:
                    disamb = sq_to_name(from_sq)
            san = PIECE_TYPE_TO_SAN[ptype] + disamb + ("x" if is_capture else "") + sq_to_name(to_sq)

        if self.make_move(move, record_san=False):
            if self.in_check():
                if not self.has_legal_moves():
                    san += "#"
                else:
                    san += "+"
            self.unmake_move(pop_history=True)
        return san

    def parse_move(self, raw_text: str) -> int:


        text = raw_text.strip()
        if not text:
            raise IllegalMoveError("Langkah kosong.")

        legal = self.legal_moves()
        if not legal:
            raise IllegalMoveError("Permainan sudah selesai, tidak ada langkah legal.")

        clean = re.sub(r"[+#!?]+$", "", text).strip()


        norm_castle = clean.upper().replace("0", "O")
        if norm_castle in ("O-O", "OO"):
            for mv in legal:
                if move_flag(mv) == FLAG_CASTLE_KING:
                    return mv
            raise IllegalMoveError(self._diagnose_castling(kingside=True))
        if norm_castle in ("O-O-O", "OOO"):
            for mv in legal:
                if move_flag(mv) == FLAG_CASTLE_QUEEN:
                    return mv
            raise IllegalMoveError(self._diagnose_castling(kingside=False))


        coord_m = re.fullmatch(r"([a-hA-H][1-8])[\s\-xX]?([a-hA-H][1-8])(?:=?([qrbnQRBN]))?", clean)
        if coord_m:
            f_sq = name_to_sq(coord_m.group(1))
            t_sq = name_to_sq(coord_m.group(2))
            p_ch = coord_m.group(3)
            promo_req = SAN_CHAR_TO_TYPE[p_ch.upper()] if p_ch else 0

            matches = [m for m in legal if (m & 63) == f_sq and ((m >> 6) & 63) == t_sq]
            if matches:
                if any(move_promo(m) != 0 for m in matches):
                    if promo_req:
                        for m in matches:
                            if move_promo(m) == promo_req:
                                return m
                        raise IllegalMoveError("Bidak promosi tidak valid (pilih Q, R, B, atau N).")
                    raise PromotionRequiredError(matches)
                if promo_req:
                    raise IllegalMoveError("Langkah ini bukan promosi pion.")
                return matches[0]
            raise IllegalMoveError(self._diagnose_illegal_coord(f_sq, t_sq))

        san_map = [(mv, self.move_to_san(mv)) for mv in legal]
        for mv, san in san_map:
            if san.rstrip("+#") == clean:
                return mv

        promo_req = 0
        body = clean
        promo_m = re.search(r"=([qrbnQRBN])$", body)
        if promo_m:
            promo_req = SAN_CHAR_TO_TYPE[promo_m.group(1).upper()]
            body = body[: promo_m.start()]
        elif re.search(r"[a-hA-H][18][qrbnQRBN]$", body):
            promo_req = SAN_CHAR_TO_TYPE[body[-1].upper()]
            body = body[:-1]


        san_m = re.fullmatch(
            r"([KQRBNkqrbn])?([a-hA-H])?([1-8])?[xX]?([a-hA-H][1-8])",
            body,
        )
        if not san_m:
            raise IllegalMoveError(
                f"Format '{raw_text}' tidak dikenali. Contoh: e4, Nf3, Bxc6, O-O, atau e2e4."
            )

        lead_piece = san_m.group(1)
        dis_file = san_m.group(2)
        dis_rank = san_m.group(3)
        dest_sq = name_to_sq(san_m.group(4))
        has_capture_mark = "x" in body.lower()


        candidates_interpretations: List[Tuple[int, Optional[int], Optional[int]]] = []
        if lead_piece is None:

            f_idx = FILES.find(dis_file.lower()) if dis_file else None
            r_idx = RANKS.find(dis_rank) if dis_rank else None
            candidates_interpretations.append((PAWN, f_idx, r_idx))
        elif lead_piece in ("B", "b"):

            f_idx = FILES.find(dis_file.lower()) if dis_file else None
            r_idx = RANKS.find(dis_rank) if dis_rank else None
            if lead_piece == "B":

                candidates_interpretations.append((BISHOP, f_idx, r_idx))
                if dis_file is None and dis_rank is None:
                    candidates_interpretations.append((PAWN, 1, None))
            else:

                if dis_file is None and dis_rank is None:
                    candidates_interpretations.append((PAWN, 1, None))
                candidates_interpretations.append((BISHOP, f_idx, r_idx))
        else:
            ptype = SAN_CHAR_TO_TYPE[lead_piece.upper()]
            f_idx = FILES.find(dis_file.lower()) if dis_file else None
            r_idx = RANKS.find(dis_rank) if dis_rank else None
            candidates_interpretations.append((ptype, f_idx, r_idx))

        for ptype, f_idx, r_idx in candidates_interpretations:
            matches = []
            for mv in legal:
                fsq = mv & 63
                tsq = (mv >> 6) & 63
                if tsq != dest_sq:
                    continue
                if abs(self.squares[fsq]) != ptype:
                    continue
                if f_idx is not None and (fsq & 7) != f_idx:
                    continue
                if r_idx is not None and (fsq >> 3) != r_idx:
                    continue
                if ptype == PAWN and has_capture_mark:
                    is_cap = self.squares[tsq] != EMPTY or move_flag(mv) == FLAG_EN_PASSANT
                    if not is_cap:
                        continue
                matches.append(mv)

            if matches:

                if any(move_promo(m) != 0 for m in matches):
                    if promo_req:
                        promo_matches = [m for m in matches if move_promo(m) == promo_req]
                        if len(promo_matches) == 1:
                            return promo_matches[0]
                        if len(promo_matches) > 1:
                            opts = ", ".join(self.move_to_san(m) for m in promo_matches)
                            raise IllegalMoveError(f"Langkah ambigu! Tulis lebih spesifik: {opts}")
                    else:

                        origins = {m & 63 for m in matches}
                        if len(origins) == 1:
                            raise PromotionRequiredError(matches)
                        opts = ", ".join(
                            sorted({self.move_to_san(m).split("=")[0] for m in matches})
                        )
                        raise IllegalMoveError(f"Langkah promosi ambigu! Pilih: {opts}")
                if promo_req:
                    raise IllegalMoveError("Langkah ini bukan promosi pion.")
                if len(matches) == 1:
                    return matches[0]
                opts = ", ".join(self.move_to_san(m) for m in matches)
                raise IllegalMoveError(f"Langkah ambigu! Tulis lebih spesifik: {opts}")

        raise IllegalMoveError(self._diagnose_illegal_san(candidates_interpretations, dest_sq, raw_text))

    def _diagnose_castling(self, kingside: bool) -> str:
        side = self.turn
        if self.in_check(side):
            return "Tidak bisa rokade saat raja sedang dalam skak!"
        right = (CASTLE_WK if kingside else CASTLE_WQ) if side == WHITE else (CASTLE_BK if kingside else CASTLE_BQ)
        if not (self.castling & right):
            return "Hak rokade sisi ini sudah hilang (raja/benteng pernah bergerak)."
        path = (
            ((5, 6) if kingside else (3, 2, 1))
            if side == WHITE
            else ((61, 62) if kingside else (59, 58, 57))
        )
        for sq in path:
            if self.squares[sq] != EMPTY:
                return f"Tidak bisa rokade, kotak {sq_to_name(sq)} masih terhalang bidak."
        king_path = (
            ((5, 6) if kingside else (3, 2))
            if side == WHITE
            else ((61, 62) if kingside else (59, 58))
        )
        for sq in king_path:
            if self.is_square_attacked(sq, -side):
                return f"Tidak bisa rokade, raja melewati/menuju kotak terancam ({sq_to_name(sq)})."
        return "Rokade tidak sah di posisi ini."

    def _diagnose_illegal_coord(self, f_sq: int, t_sq: int) -> str:
        p = self.squares[f_sq]
        if p == EMPTY:
            return f"Tidak ada bidak di kotak {sq_to_name(f_sq)}."
        if (p > 0) != (self.turn > 0):
            return f"Bidak di {sq_to_name(f_sq)} bukan milikmu."

        for mv in self.generate_pseudo_legal_moves():
            if (mv & 63) == f_sq and ((mv >> 6) & 63) == t_sq:
                if self.in_check():
                    return "Raja kamu sedang skak! Kamu harus menyelamatkan raja dulu."
                return "Langkah itu membuka skak ke rajamu sendiri (pinned)."
        return f"Bidak di {sq_to_name(f_sq)} tidak bisa melangkah ke {sq_to_name(t_sq)}."

    def _diagnose_illegal_san(
        self,
        interpretations: List[Tuple[int, Optional[int], Optional[int]]],
        dest_sq: int,
        raw_text: str,
    ) -> str:

        pseudo = self.generate_pseudo_legal_moves()
        for ptype, f_idx, r_idx in interpretations:
            for mv in pseudo:
                fsq = mv & 63
                tsq = (mv >> 6) & 63
                if tsq != dest_sq or abs(self.squares[fsq]) != ptype:
                    continue
                if f_idx is not None and (fsq & 7) != f_idx:
                    continue
                if r_idx is not None and (fsq >> 3) != r_idx:
                    continue
                if self.in_check():
                    return "Raja kamu sedang skak! Selamatkan rajamu dulu."
                return f"Langkah '{raw_text}' membuat rajamu terkena skak (ter-pin)."
        if self.in_check():
            return f"Tidak ada bidak yang bisa melangkah '{raw_text}' (ingat: raja sedang skak!)."
        return f"Tidak ada bidak yang bisa melakukan langkah '{raw_text}'."

    def perft(self, depth: int) -> int:
        if depth == 0:
            return 1
        nodes = 0
        for mv in self.generate_pseudo_legal_moves():
            if self.make_move(mv, record_san=False):
                nodes += self.perft(depth - 1)
                self.unmake_move(pop_history=True)
        return nodes

    def to_pgn(
        self,
        white_name: str = "Player",
        black_name: str = "ChessPortable AI",
        white_elo: str = "?",
        black_elo: str = "?",
        event: str = "ChessPortable CLI Match",
        result: str = "*",
        date_str: str = "????.??.??",
        eco: Optional[str] = None,
        opening: Optional[str] = None,
    ) -> str:

        headers = [
            f'[Event "{event}"]',
            '[Site "Termux ChessPortable"]',
            f'[Date "{date_str}"]',
            f'[White "{white_name}"]',
            f'[Black "{black_name}"]',
            f'[WhiteElo "{white_elo}"]',
            f'[BlackElo "{black_elo}"]',
            f'[Result "{result}"]',
        ]
        if eco:
            headers.append(f'[ECO "{eco}"]')
        if opening:
            headers.append(f'[Opening "{opening}"]')
        tokens: List[str] = []
        for i in range(0, len(self.san_history), 2):
            mnum = (i // 2) + 1
            tokens.append(f"{mnum}. {self.san_history[i]}")
            if i + 1 < len(self.san_history):
                tokens.append(self.san_history[i + 1])
        tokens.append(result)

        body_lines: List[str] = []
        cur = ""
        for tok in tokens:
            if cur and len(cur) + 1 + len(tok) > 78:
                body_lines.append(cur)
                cur = tok
            else:
                cur = f"{cur} {tok}" if cur else tok
        if cur:
            body_lines.append(cur)

        return "\n".join(headers) + "\n\n" + "\n".join(body_lines) + "\n"
