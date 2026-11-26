from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .board import Board, move_to_uci


_OPENING_DEFS: List[Tuple[str, str, str]] = [

    ("B00", "King's Pawn Opening", "e2e4"),
    ("C20", "King's Pawn Game", "e2e4 e7e5"),
    ("C20", "Wayward Queen Attack (Scholar's Trap)", "e2e4 e7e5 d1h5"),
    ("C20", "Wayward Queen — Kiddie Counter", "e2e4 e7e5 d1h5 b8c6 f1c4 g7g6"),
    ("C20", "Bongcloud Attack (!?)", "e2e4 e7e5 e1e2"),
    ("C21", "Center Game", "e2e4 e7e5 d2d4 e5d4"),
    ("C21", "Danish Gambit", "e2e4 e7e5 d2d4 e5d4 c2c3"),
    ("C23", "Bishop's Opening", "e2e4 e7e5 f1c4"),
    ("C25", "Vienna Game", "e2e4 e7e5 b1c3"),
    ("C29", "Vienna Gambit", "e2e4 e7e5 b1c3 g8f6 f2f4"),
    ("C30", "King's Gambit", "e2e4 e7e5 f2f4"),
    ("C33", "King's Gambit Accepted", "e2e4 e7e5 f2f4 e5f4"),
    ("C40", "King's Knight Opening", "e2e4 e7e5 g1f3"),
    ("C40", "Latvian Gambit", "e2e4 e7e5 g1f3 f7f5"),
    ("C41", "Philidor Defense", "e2e4 e7e5 g1f3 d7d6"),
    ("C42", "Petrov's Defense (Russian Game)", "e2e4 e7e5 g1f3 g8f6"),
    ("C44", "Scotch Game", "e2e4 e7e5 g1f3 b8c6 d2d4"),
    ("C45", "Scotch Game — Classical", "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f3d4"),
    ("C46", "Three Knights Game", "e2e4 e7e5 g1f3 b8c6 b1c3"),
    ("C47", "Four Knights Game", "e2e4 e7e5 g1f3 b8c6 b1c3 g8f6"),
    ("C50", "Italian Game", "e2e4 e7e5 g1f3 b8c6 f1c4"),
    ("C50", "Giuoco Piano", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5"),
    ("C51", "Evans Gambit", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 b2b4"),
    ("C53", "Giuoco Piano — Main Line", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3"),
    ("C55", "Two Knights Defense", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6"),
    ("C57", "Fried Liver Attack Setup", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5"),
    ("C57", "Two Knights — Polerio Defense", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5 d7d5 e4d5 c6a5"),
    ("C60", "Ruy Lopez (Spanish Opening)", "e2e4 e7e5 g1f3 b8c6 f1b5"),
    ("C65", "Ruy Lopez — Berlin Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 g8f6"),
    ("C70", "Ruy Lopez — Morphy Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6"),
    ("C78", "Ruy Lopez — Closed Morphy", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 f1a4 g8f6 e1g1"),

    ("B20", "Sicilian Defense", "e2e4 c7c5"),
    ("B21", "Sicilian — Smith-Morra Gambit", "e2e4 c7c5 d2d4 c5d4 c2c3"),
    ("B22", "Sicilian — Alapin Variation", "e2e4 c7c5 c2c3"),
    ("B23", "Sicilian — Closed Variation", "e2e4 c7c5 b1c3"),
    ("B27", "Sicilian — Open Setup", "e2e4 c7c5 g1f3"),
    ("B30", "Sicilian — Old Sicilian", "e2e4 c7c5 g1f3 b8c6"),
    ("B32", "Sicilian — Open (Nc6)", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4"),
    ("B33", "Sicilian — Sveshnikov Variation", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e5"),
    ("B40", "Sicilian — French Variation", "e2e4 c7c5 g1f3 e7e6"),
    ("B50", "Sicilian — Modern (d6)", "e2e4 c7c5 g1f3 d7d6"),
    ("B70", "Sicilian — Dragon Variation", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6"),
    ("B90", "Sicilian — Najdorf Variation", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6"),

    ("C00", "French Defense", "e2e4 e7e6"),
    ("C01", "French — Exchange Variation", "e2e4 e7e6 d2d4 d7d5 e4d5 e6d5"),
    ("C02", "French — Advance Variation", "e2e4 e7e6 d2d4 d7d5 e4e5"),
    ("C03", "French — Tarrasch Variation", "e2e4 e7e6 d2d4 d7d5 b1d2"),
    ("C11", "French — Classical Variation", "e2e4 e7e6 d2d4 d7d5 b1c3 g8f6"),
    ("B10", "Caro-Kann Defense", "e2e4 c7c6"),
    ("B12", "Caro-Kann — Advance Variation", "e2e4 c7c6 d2d4 d7d5 e4e5"),
    ("B13", "Caro-Kann — Exchange Variation", "e2e4 c7c6 d2d4 d7d5 e4d5 c6d5"),
    ("B18", "Caro-Kann — Classical Variation", "e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5"),
    ("B01", "Scandinavian Defense", "e2e4 d7d5"),
    ("B01", "Scandinavian — Main Line", "e2e4 d7d5 e4d5 d8d5 b1c3"),
    ("B02", "Alekhine's Defense", "e2e4 g8f6"),
    ("B06", "Modern Defense", "e2e4 g7g6"),
    ("B07", "Pirc Defense", "e2e4 d7d6 d2d4 g8f6 b1c3"),
    ("B00", "Nimzowitsch Defense", "e2e4 b8c6"),

    ("A40", "Queen's Pawn Opening", "d2d4"),
    ("D00", "Queen's Pawn Game", "d2d4 d7d5"),
    ("D00", "Blackmar-Diemer Gambit", "d2d4 d7d5 e2e4 d5e4"),
    ("D02", "London System", "d2d4 d7d5 c1f4"),
    ("D02", "London System — Classical", "d2d4 d7d5 c1f4 g8f6 e2e3"),
    ("D04", "Colle System", "d2d4 d7d5 g1f3 g8f6 e2e3"),
    ("D06", "Queen's Gambit", "d2d4 d7d5 c2c4"),
    ("D10", "Slav Defense", "d2d4 d7d5 c2c4 c7c6"),
    ("D20", "Queen's Gambit Accepted", "d2d4 d7d5 c2c4 d5c4"),
    ("D30", "Queen's Gambit Declined", "d2d4 d7d5 c2c4 e7e6"),
    ("D37", "QGD — Three Knights", "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6"),
    ("A45", "Indian Defense", "d2d4 g8f6"),
    ("A45", "Trompowsky Attack", "d2d4 g8f6 c1g5"),
    ("A50", "Indian Game (c4)", "d2d4 g8f6 c2c4"),
    ("A56", "Benoni Defense", "d2d4 g8f6 c2c4 c7c5 d4d5"),
    ("E00", "Catalan Opening", "d2d4 g8f6 c2c4 e7e6 g2g3"),
    ("E20", "Nimzo-Indian Defense", "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4"),
    ("E60", "King's Indian Defense", "d2d4 g8f6 c2c4 g7g6"),
    ("E70", "King's Indian — Classical", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6"),
    ("D80", "Grünfeld Defense", "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5"),
    ("A80", "Dutch Defense", "d2d4 f7f5"),
    ("A40", "Englund Gambit", "d2d4 e7e5"),

    ("A10", "English Opening", "c2c4"),
    ("A20", "English — Reversed Sicilian", "c2c4 e7e5"),
    ("A15", "English — Anglo-Indian", "c2c4 g8f6"),
    ("A04", "Réti Opening", "g1f3"),
    ("A09", "Réti Gambit", "g1f3 d7d5 c2c4"),
    ("A02", "Bird's Opening", "f2f4"),
    ("A00", "King's Fianchetto Opening", "g2g3"),
    ("A00", "Larsen's Opening", "b2b3"),
]

def _build_opening_index() -> Dict[int, Tuple[str, str]]:
    idx: Dict[int, Tuple[str, str]] = {}
    for eco, name, line in _OPENING_DEFS:
        b = Board()
        ok = True
        for uci in line.split():
            legal = {move_to_uci(m): m for m in b.legal_moves()}
            if uci not in legal:
                ok = False
                break
            b.make_move(legal[uci], record_san=False)
        if ok:
            idx[b.zobrist] = (eco, name)
    return idx


OPENING_INDEX: Dict[int, Tuple[str, str]] = _build_opening_index()

def detect_opening(board: Board) -> Optional[Tuple[str, str]]:


    hist = board.hash_history
    max_idx = min(len(hist) - 1, 20)
    for i in range(max_idx, 0, -1):
        hit = OPENING_INDEX.get(hist[i])
        if hit is not None:
            return hit
    return None
