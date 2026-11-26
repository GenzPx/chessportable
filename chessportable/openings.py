from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .board import Board, move_to_uci

_OPENING_DEFS: List[Tuple[str, str, str]] = [
    ("B00", "King's Pawn Opening", "e2e4"),
    ("C20", "King's Pawn Game", "e2e4 e7e5"),
    ("C20", "Wayward Queen Attack", "e2e4 e7e5 d1h5"),
    ("C20", "Wayward Queen — Kiddie Counter", "e2e4 e7e5 d1h5 b8c6 f1c4 g7g6"),
    ("C20", "Bongcloud Attack", "e2e4 e7e5 e1e2"),
    ("C20", "Alapin Opening", "e2e4 e7e5 g1e2"),
    ("C21", "Center Game", "e2e4 e7e5 d2d4 e5d4"),
    ("C21", "Danish Gambit", "e2e4 e7e5 d2d4 e5d4 c2c3"),
    ("C21", "Danish Gambit Accepted", "e2e4 e7e5 d2d4 e5d4 c2c3 d4c3 f1c4"),
    ("C22", "Center Game — Hall Variation", "e2e4 e7e5 d2d4 e5d4 d1d4 b8c6 d4e3"),
    ("C23", "Bishop's Opening", "e2e4 e7e5 f1c4"),
    ("C24", "Bishop's Opening — Berlin Defense", "e2e4 e7e5 f1c4 g8f6"),
    ("C25", "Vienna Game", "e2e4 e7e5 b1c3"),
    ("C26", "Vienna Game — Falkbeer", "e2e4 e7e5 b1c3 g8f6"),
    ("C27", "Vienna — Frankenstein-Dracula", "e2e4 e7e5 b1c3 g8f6 f1c4 f6e4"),
    ("C29", "Vienna Gambit", "e2e4 e7e5 b1c3 g8f6 f2f4"),
    ("C30", "King's Gambit", "e2e4 e7e5 f2f4"),
    ("C30", "King's Gambit Declined", "e2e4 e7e5 f2f4 f8c5"),
    ("C31", "Falkbeer Countergambit", "e2e4 e7e5 f2f4 d7d5"),
    ("C33", "King's Gambit Accepted", "e2e4 e7e5 f2f4 e5f4"),
    ("C34", "King's Gambit — Knight's Gambit", "e2e4 e7e5 f2f4 e5f4 g1f3"),
    ("C37", "Muzio Gambit", "e2e4 e7e5 f2f4 e5f4 g1f3 g7g5 f1c4 g5g4 e1g1"),
    ("C40", "King's Knight Opening", "e2e4 e7e5 g1f3"),
    ("C40", "Elephant Gambit", "e2e4 e7e5 g1f3 d7d5"),
    ("C40", "Latvian Gambit", "e2e4 e7e5 g1f3 f7f5"),
    ("C40", "Damiano Defense", "e2e4 e7e5 g1f3 f7f6"),
    ("C41", "Philidor Defense", "e2e4 e7e5 g1f3 d7d6"),
    ("C41", "Philidor — Hanham Variation", "e2e4 e7e5 g1f3 d7d6 d2d4 b8d7"),
    ("C42", "Petrov's Defense", "e2e4 e7e5 g1f3 g8f6"),
    ("C42", "Stafford Gambit", "e2e4 e7e5 g1f3 g8f6 f3e5 b8c6"),
    ("C43", "Petrov — Steinitz Attack", "e2e4 e7e5 g1f3 g8f6 d2d4"),
    ("C44", "Scotch Game", "e2e4 e7e5 g1f3 b8c6 d2d4"),
    ("C44", "Scotch Gambit", "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f1c4"),
    ("C44", "Ponziani Opening", "e2e4 e7e5 g1f3 b8c6 c2c3"),
    ("C45", "Scotch Game — Classical", "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f3d4"),
    ("C46", "Three Knights Game", "e2e4 e7e5 g1f3 b8c6 b1c3"),
    ("C47", "Four Knights Game", "e2e4 e7e5 g1f3 b8c6 b1c3 g8f6"),
    ("C48", "Four Knights — Spanish", "e2e4 e7e5 g1f3 b8c6 b1c3 g8f6 f1b5"),
    ("C49", "Four Knights — Double Spanish", "e2e4 e7e5 g1f3 b8c6 b1c3 g8f6 f1b5 f8b4"),
    ("C50", "Italian Game", "e2e4 e7e5 g1f3 b8c6 f1c4"),
    ("C50", "Giuoco Piano", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5"),
    ("C50", "Giuoco Pianissimo", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 d2d3"),
    ("C50", "Hungarian Defense", "e2e4 e7e5 g1f3 b8c6 f1c4 f8e7"),
    ("C50", "Blackburne Shilling Gambit", "e2e4 e7e5 g1f3 b8c6 f1c4 c6d4"),
    ("C51", "Evans Gambit", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 b2b4"),
    ("C52", "Evans Gambit Accepted", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 b2b4 c5b4"),
    ("C53", "Giuoco Piano — Main Line", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3"),
    ("C55", "Two Knights Defense", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6"),
    ("C57", "Fried Liver Attack Setup", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5"),
    ("C57", "Traxler Counterattack", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5 f8c5"),
    ("C57", "Two Knights — Polerio Defense", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5 d7d5 e4d5 c6a5"),
    ("C60", "Ruy Lopez", "e2e4 e7e5 g1f3 b8c6 f1b5"),
    ("C62", "Ruy Lopez — Old Steinitz", "e2e4 e7e5 g1f3 b8c6 f1b5 d7d6"),
    ("C63", "Ruy Lopez — Schliemann Gambit", "e2e4 e7e5 g1f3 b8c6 f1b5 f7f5"),
    ("C65", "Ruy Lopez — Berlin Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 g8f6"),
    ("C68", "Ruy Lopez — Exchange Variation", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5c6"),
    ("C70", "Ruy Lopez — Morphy Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6"),
    ("C78", "Ruy Lopez — Closed Morphy", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 f1a4 g8f6 e1g1"),
    ("C84", "Ruy Lopez — Closed Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 f1a4 g8f6 e1g1 f8e7"),
    ("C89", "Ruy Lopez — Marshall Attack", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 f1a4 g8f6 e1g1 f8e7 f1e1 b7b5 a4b3 e8g8 c2c3 d7d5"),

    ("B20", "Sicilian Defense", "e2e4 c7c5"),
    ("B21", "Sicilian — Smith-Morra Gambit", "e2e4 c7c5 d2d4 c5d4 c2c3"),
    ("B21", "Sicilian — McDonnell Attack", "e2e4 c7c5 f2f4"),
    ("B22", "Sicilian — Alapin Variation", "e2e4 c7c5 c2c3"),
    ("B23", "Sicilian — Closed Variation", "e2e4 c7c5 b1c3"),
    ("B23", "Sicilian — Grand Prix Attack", "e2e4 c7c5 b1c3 b8c6 f2f4"),
    ("B27", "Sicilian — Hyperaccelerated Dragon", "e2e4 c7c5 g1f3 g7g6"),
    ("B30", "Sicilian — Rossolimo", "e2e4 c7c5 g1f3 b8c6 f1b5"),
    ("B32", "Sicilian — Open Variation", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4"),
    ("B33", "Sicilian — Sveshnikov", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e5"),
    ("B35", "Sicilian — Accelerated Dragon", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g7g6"),
    ("B40", "Sicilian — Pin / Paulsen", "e2e4 c7c5 g1f3 e7e6"),
    ("B42", "Sicilian — Kan Variation", "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 a7a6"),
    ("B45", "Sicilian — Taimanov", "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 b8c6"),
    ("B50", "Sicilian — Modern", "e2e4 c7c5 g1f3 d7d6"),
    ("B51", "Sicilian — Moscow Variation", "e2e4 c7c5 g1f3 d7d6 f1b5"),
    ("B56", "Sicilian — Classical", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 b8c6"),
    ("B70", "Sicilian — Dragon Variation", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6"),
    ("B80", "Sicilian — Scheveningen", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e6"),
    ("B90", "Sicilian — Najdorf Variation", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6"),

    ("C00", "French Defense", "e2e4 e7e6"),
    ("C01", "French — Exchange Variation", "e2e4 e7e6 d2d4 d7d5 e4d5 e6d5"),
    ("C02", "French — Advance Variation", "e2e4 e7e6 d2d4 d7d5 e4e5"),
    ("C03", "French — Tarrasch Variation", "e2e4 e7e6 d2d4 d7d5 b1d2"),
    ("C10", "French — Rubinstein Variation", "e2e4 e7e6 d2d4 d7d5 b1c3 d5e4"),
    ("C11", "French — Classical Variation", "e2e4 e7e6 d2d4 d7d5 b1c3 g8f6"),
    ("C15", "French — Winawer Variation", "e2e4 e7e6 d2d4 d7d5 b1c3 f8b4"),

    ("B10", "Caro-Kann Defense", "e2e4 c7c6"),
    ("B10", "Caro-Kann — Two Knights Attack", "e2e4 c7c6 b1c3 d7d5 g1f3"),
    ("B12", "Caro-Kann — Advance Variation", "e2e4 c7c6 d2d4 d7d5 e4e5"),
    ("B13", "Caro-Kann — Exchange Variation", "e2e4 c7c6 d2d4 d7d5 e4d5 c6d5"),
    ("B13", "Caro-Kann — Panov-Botvinnik", "e2e4 c7c6 d2d4 d7d5 e4d5 c6d5 c2c4"),
    ("B15", "Caro-Kann — Main Line", "e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4"),
    ("B18", "Caro-Kann — Classical", "e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5"),

    ("B01", "Scandinavian Defense", "e2e4 d7d5"),
    ("B01", "Scandinavian — Queen Recapture", "e2e4 d7d5 e4d5 d8d5"),
    ("B01", "Scandinavian — Mieses-Kotrc", "e2e4 d7d5 e4d5 d8d5 b1c3"),
    ("B01", "Scandinavian — Modern", "e2e4 d7d5 e4d5 g8f6"),
    ("B02", "Alekhine's Defense", "e2e4 g8f6"),
    ("B03", "Alekhine — Four Pawns Attack", "e2e4 g8f6 e4e5 f6d5 d2d4 d7d6 c2c4 d5b6 f2f4"),
    ("B06", "Modern Defense", "e2e4 g7g6"),
    ("B07", "Pirc Defense", "e2e4 d7d6 d2d4 g8f6 b1c3"),
    ("B09", "Pirc — Austrian Attack", "e2e4 d7d6 d2d4 g8f6 b1c3 g7g6 f2f4"),
    ("B00", "Nimzowitsch Defense", "e2e4 b8c6"),
    ("B00", "Owen's Defense", "e2e4 b7b6"),

    ("A40", "Queen's Pawn Opening", "d2d4"),
    ("A40", "Englund Gambit", "d2d4 e7e5"),
    ("A45", "Trompowsky Attack", "d2d4 g8f6 c1g5"),
    ("D00", "Queen's Pawn Game", "d2d4 d7d5"),
    ("D00", "London System", "d2d4 d7d5 c1f4"),
    ("D00", "Jobava London System", "d2d4 d7d5 b1c3 g8f6 c1f4"),
    ("D00", "Blackmar-Diemer Gambit", "d2d4 d7d5 e2e4"),
    ("D01", "Richter-Veresov Attack", "d2d4 d7d5 b1c3 g8f6 c1g5"),
    ("D02", "London System — Accelerated", "d2d4 d7d5 g1f3 g8f6 c1f4"),
    ("D04", "Colle System", "d2d4 d7d5 g1f3 g8f6 e2e3"),
    ("D06", "Queen's Gambit", "d2d4 d7d5 c2c4"),
    ("D07", "Chigorin Defense", "d2d4 d7d5 c2c4 b8c6"),
    ("D08", "Albin Countergambit", "d2d4 d7d5 c2c4 e7e5"),
    ("D10", "Slav Defense", "d2d4 d7d5 c2c4 c7c6"),
    ("D15", "Slav — Main Line", "d2d4 d7d5 c2c4 c7c6 g1f3 g8f6 b1c3"),
    ("D20", "Queen's Gambit Accepted", "d2d4 d7d5 c2c4 d5c4"),
    ("D30", "Queen's Gambit Declined", "d2d4 d7d5 c2c4 e7e6"),
    ("D35", "QGD — Exchange Variation", "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c4d5 e6d5"),
    ("D37", "QGD — Three Knights", "d2d4 d7d5 c2c4 e7e6 g1f3 g8f6 b1c3"),
    ("D43", "Semi-Slav Defense", "d2d4 d7d5 c2c4 e7e6 g1f3 g8f6 b1c3 c7c6"),

    ("A45", "Indian Defense", "d2d4 g8f6"),
    ("A50", "Indian Game", "d2d4 g8f6 c2c4"),
    ("A52", "Budapest Gambit", "d2d4 g8f6 c2c4 e7e5"),
    ("A53", "Old Indian Defense", "d2d4 g8f6 c2c4 d7d6"),
    ("A57", "Benko Gambit", "d2d4 g8f6 c2c4 c7c5 d4d5 b7b5"),
    ("A60", "Benoni Defense", "d2d4 g8f6 c2c4 c7c5 d4d5"),
    ("E00", "Catalan Opening", "d2d4 g8f6 c2c4 e7e6 g2g3"),
    ("E11", "Bogo-Indian Defense", "d2d4 g8f6 c2c4 e7e6 g1f3 f8b4"),
    ("E12", "Queen's Indian Defense", "d2d4 g8f6 c2c4 e7e6 g1f3 b7b6"),
    ("E20", "Nimzo-Indian Defense", "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4"),
    ("E60", "King's Indian Defense", "d2d4 g8f6 c2c4 g7g6"),
    ("E62", "King's Indian — Fianchetto", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 g1f3 e8g8 g2g3"),
    ("E76", "King's Indian — Four Pawns", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 f2f4"),
    ("E80", "King's Indian — Samisch", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 f2f3"),
    ("D80", "Grunfeld Defense", "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5"),
    ("D85", "Grunfeld — Exchange Variation", "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5 c4d5 f6d5 e2e4"),
    ("A80", "Dutch Defense", "d2d4 f7f5"),
    ("A81", "Dutch — Leningrad", "d2d4 f7f5 g2g3 g8f6 f1g2 g7g6"),
    ("A90", "Dutch — Stonewall", "d2d4 f7f5 c2c4 g8f6 g2g3 e7e6 f1g2 d7d5"),

    ("A10", "English Opening", "c2c4"),
    ("A13", "English — Agincourt Defense", "c2c4 e7e6"),
    ("A15", "English — Anglo-Indian", "c2c4 g8f6"),
    ("A20", "English — Reversed Sicilian", "c2c4 e7e5"),
    ("A30", "English — Symmetrical", "c2c4 c7c5"),
    ("A04", "Reti Opening", "g1f3"),
    ("A05", "Reti — King's Indian Attack", "g1f3 g8f6 g2g3"),
    ("A09", "Reti — Advance Variation", "g1f3 d7d5 c2c4"),
    ("A02", "Bird's Opening", "f2f4"),
    ("A03", "Bird — Dutch Reversed", "f2f4 d7d5"),
    ("A01", "Nimzowitsch-Larsen Attack", "b2b3"),
    ("A00", "King's Fianchetto Opening", "g2g3"),
    ("A00", "Grob's Attack", "g2g4"),
    ("A00", "Polish Opening (Orangutan)", "b2b4"),
    ("A00", "Dunst Opening", "b1c3"),
]

def _build_opening_index() -> Dict[int, Tuple[str, str]]:
    idx: Dict[int, Tuple[str, str]] = {}
    for eco, name, uci_line in _OPENING_DEFS:
        b = Board()
        ok = True
        for uci in uci_line.split():
            found = 0
            for mv in b.legal_moves():
                if move_to_uci(mv) == uci:
                    found = mv
                    break
            if not found:
                ok = False
                break
            b.make_move(found, record_san=False)
        if ok:
            idx[b.zobrist] = (eco, name)
    return idx

OPENING_INDEX: Dict[int, Tuple[str, str]] = _build_opening_index()

def detect_opening(board: Board) -> Optional[Tuple[str, str]]:
    return OPENING_INDEX.get(board.zobrist)
