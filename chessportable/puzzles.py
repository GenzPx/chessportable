from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

@dataclass(frozen=True)
class Puzzle:
    puzzle_id: str
    title: str
    rating: int
    theme: str
    fen: str

    solution: Tuple[str, ...]
    hint: str
    must_mate: bool = True


PUZZLES: Tuple[Puzzle, ...] = (
    Puzzle(
        puzzle_id="p01",
        title="Scholar's Strike",
        rating=600,
        theme="Skakmat 1 Langkah",
        fen="r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
        solution=("h5f7",),
        hint="Serang petak lemah f7 dengan Menteri yang dijaga Gajah!",
    ),
    Puzzle(
        puzzle_id="p02",
        title="Back-Rank Knockout",
        rating=650,
        theme="Skakmat Baris Belakang",
        fen="6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1",
        solution=("d1d8",),
        hint="Raja Hitam terjebak oleh pion-pionnya sendiri di baris ke-8.",
    ),
    Puzzle(
        puzzle_id="p03",
        title="Kiss of Death",
        rating=700,
        theme="Skakmat 1 Langkah",
        fen="6k1/5p1p/8/6Q1/8/2B5/6PP/6K1 w - - 0 1",
        solution=("g5g7",),
        hint="Menteri dan Gajah di diagonal panjang bisa menutup seluruh ruang Raja.",
    ),
    Puzzle(
        puzzle_id="p04",
        title="Black Back-Rank",
        rating=750,
        theme="Skakmat 1 Langkah (Hitam)",
        fen="3r2k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1",
        solution=("d8d1",),
        hint="Kamu main Hitam! Turunkan Benteng ke baris pertama.",
    ),
    Puzzle(
        puzzle_id="p05",
        title="Mini Smothered Mate",
        rating=850,
        theme="Skakmat Kuda Terkurung",
        fen="6rk/6pp/8/4N3/8/8/6PP/6K1 w - - 0 1",
        solution=("e5f7",),
        hint="Raja di sudut h8 terkunci total oleh Benteng dan pionnya sendiri!",
    ),
    Puzzle(
        puzzle_id="p06",
        title="Arabian Mate",
        rating=950,
        theme="Skakmat Arab",
        fen="7k/7p/5N2/8/8/8/6R1/6K1 w - - 0 1",
        solution=("g2g8",),
        hint="Kuda di f6 menjaga petak g8 sekaligus menutup pelarian h7.",
    ),
    Puzzle(
        puzzle_id="p07",
        title="Royal Promotion",
        rating=1000,
        theme="Promosi Skakmat",
        fen="6k1/4Pppp/8/8/8/8/8/6K1 w - - 0 1",
        solution=("e7e8q",),
        hint="Promosikan pionmu di baris 8 untuk langsung skakmat!",
    ),
    Puzzle(
        puzzle_id="p08",
        title="Royal Knight Fork",
        rating=1100,
        theme="Garpu Kuda (Menang Menteri)",
        fen="2q1k3/8/8/8/4N3/8/8/4K3 w - - 0 1",
        solution=("e4d6",),
        hint="Cari satu petak di mana Kuda menyerang Raja dan Menteri bersamaan!",
        must_mate=False,
    ),
    Puzzle(
        puzzle_id="p09",
        title="Sneaky Underpromotion",
        rating=1250,
        theme="Promosi Kuda (Garpu!)",
        fen="8/5P1k/4q3/8/8/8/8/6K1 w - - 0 1",
        solution=("f7f8n",),
        hint="Jangan promosi jadi Menteri! Promosi jadi Kuda untuk garpu Raja & Menteri!",
        must_mate=False,
    ),
    Puzzle(
        puzzle_id="p10",
        title="Damiano's Finish",
        rating=1300,
        theme="Skakmat 2 Langkah",
        fen="6k1/5p1p/6P1/8/8/8/5Q2/6K1 w - - 0 1",
        solution=("f2f7", "g8h8", "f7h7"),
        hint="Pion di g6 menjaga f7 dan h7. Mulai dengan skak di f7!",
    ),
    Puzzle(
        puzzle_id="p11",
        title="Battery Back-Rank",
        rating=1350,
        theme="Pengorbanan Menteri (M2)",
        fen="3r2k1/5ppp/1q6/8/8/8/4QPPP/4R1K1 w - - 0 1",
        solution=("e2e8", "d8e8", "e1e8"),
        hint="Korbankan Menterimu di baris belakang agar Benteng menyelesaikan tugas!",
    ),
    Puzzle(
        puzzle_id="p12",
        title="Bishop-Queen Crush",
        rating=1450,
        theme="Skakmat 2 Langkah",
        fen="2r3k1/4pppp/8/8/8/3B3Q/5PPP/6K1 w - - 0 1",
        solution=("h3h7", "g8f8", "h7h8"),
        hint="Pecahkan benteng raja di h7 dengan dukungan Gajah d3!",
    ),
    Puzzle(
        puzzle_id="p13",
        title="Legal's Mate Trap",
        rating=1550,
        theme="Skakmat 2 Langkah (Klasik)",
        fen="r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0",
        solution=("d5f6", "g7f6", "c4f7"),
        hint="Lompatkan Kuda ke f6 dengan skak, lalu Gajah c4 menyelesaikannya!",
    ),
    Puzzle(
        puzzle_id="p14",
        title="Anastasia's Mate",
        rating=1650,
        theme="Pengorbanan Menteri (M2)",
        fen="5r1k/1b2Nppp/8/7Q/8/4R3/5PPP/6K1 w - - 0 1",
        solution=("h5h7", "h8h7", "e3h3"),
        hint="Korbankan Menteri di h7 untuk membuka lajur h bagi Benteng!",
    ),
    Puzzle(
        puzzle_id="p15",
        title="Philidor's Legacy",
        rating=1750,
        theme="Smothered Mate (M2)",
        fen="5r1k/6pp/7N/8/8/1Q6/5PPP/6K1 w - - 0 1",
        solution=("b3g8", "f8g8", "h6f7"),
        hint="Korbankan Menteri tepat di samping Raja Hitam (g8) agar Benteng mengurungnya!",
    ),
    Puzzle(
        puzzle_id="p16",
        title="Dark Philidor (Hitam)",
        rating=1800,
        theme="Smothered Mate (Hitam, M2)",
        fen="6k1/5ppp/1q6/8/8/7n/6PP/5R1K b - - 0 1",
        solution=("b6g1", "f1g1", "h3f2"),
        hint="Kamu main Hitam! Korbankan Menteri di g1 lalu akhiri dengan Kuda!",
    ),
    Puzzle(
        puzzle_id="p17",
        title="Morphy's Opera Game",
        rating=1900,
        theme="Immortal M2 (Paul Morphy 1858)",
        fen="4kb1r/p2n1ppp/4q3/4p1B1/4P3/1Q6/PPP2PPP/2KR4 w k - 1 16",
        solution=("b3b8", "d7b8", "d1d8"),
        hint="Pengorbanan Menteri paling legendaris sepanjang sejarah di b8!",
    ),
    Puzzle(
        puzzle_id="p18",
        title="Boden's Mate",
        rating=2000,
        theme="Pengorbanan Menteri + 2 Gajah (M2)",
        fen="2kr4/pp1b1ppp/2n5/8/5B2/2Q5/PPP2PPP/3R1BK1 w - - 0 1",
        solution=("c3c6", "b7c6", "f1a6"),
        hint="Hancurkan pelindung c6 dengan Menteri, lalu dua Gajah menyilang mematikan!",
    ),
    Puzzle(
        puzzle_id="p19",
        title="Réti's Double Check",
        rating=2150,
        theme="Skak Ganda Legendaris (M3)",
        fen="rnb1kb1r/pp3ppp/2p5/8/4n3/3Q4/PPPB1PPP/2KR1BNR w kq - 0 9",
        solution=("d3d8", "e8d8", "d2g5", "d8e8", "d1d8"),
        hint="Korbankan Menteri di d8! Setelah Kxd8, temukan Skak Ganda (Double Check)!",
    ),
    Puzzle(
        puzzle_id="p20",
        title="Queen Sacrifice Corridor",
        rating=2200,
        theme="Skakmat 2 Langkah",
        fen="r4rk1/ppp2ppp/8/4N3/8/8/PPP2QPP/4R2K w - - 0 1",
        solution=("f2f7", "f8f7", "e5f7"),
        hint="Bongkar petak f7 untuk memenangkan kualitas besar (Benteng + pion)!",
        must_mate=False,
    ),
)

def puzzles_near_rating(rating: int, solved_ids: List[str]) -> List[Puzzle]:

    solved = set(solved_ids)
    unsolved = [p for p in PUZZLES if p.puzzle_id not in solved]
    pool = unsolved if unsolved else list(PUZZLES)
    return sorted(pool, key=lambda p: abs(p.rating - rating))
