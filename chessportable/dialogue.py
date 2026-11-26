from __future__ import annotations

import random
from typing import Dict, List, Optional

from .board import BISHOP, KNIGHT, PAWN, QUEEN, ROOK
from .bots import BotProfile

FIRST_MOVE_QUOTES: Dict[str, List[str]] = {
    "e4": [
        "e4 ya... Kau mau main apa?",
        "e4 lagi! Klasik banget, mau Italian atau Ruy Lopez nih?",
        "Langsung buka tengah pakai e4... ayo kita lihat rencanamu!",
        "e4! Langkah paling legendaris sepanjang masa. Siap duel terbuka?",
    ],
    "d4": [
        "d4 ya... Mau main Queen's Gambit atau London System nih?",
        "Hmm, d4... Gaya main sabar dan rapi ya?",
        "Buka pakai d4! Oke, mari kita adu strategi di pusat papan.",
    ],
    "c4": [
        "Wah, c4! English Opening nih, suka main posisional ya?",
        "c4 dari langkah pertama... licin juga cara bukamu!",
    ],
    "Nf3": [
        "Nf3 dulu? Santai tapi penuh rencana ya...",
        "Reti Opening! Fleksibel banget, bikin aku harus menebak arahmu.",
    ],
    "f4": [
        "f4?! Bird's Opening? Berani banget buka sayap raja di awal!",
        "Wah, langsung f4! Kamu suka permainan tajam dan nekat ya?",
    ],
    "g4": [
        "g4?! Grob's Attack beneran nih?! Oke, tantangannya aku terima!",
        "Eh... beneran g4? Jangan-jangan kamu nyimpen jebakan aneh!",
    ],
    "b3": [
        "b3... Mau pasang gajah sniper di diagonal panjang ya?",
        "Larsen Opening! Santai dari pinggir dulu nih.",
    ],
    "b4": [
        "b4! Orangutan Opening?! Wah jarang banget ada yang berani main ini!",
    ],
    "g3": [
        "g3 dulu, langsung fianchetto ya... main rapi nih kayaknya.",
    ],
    "Nc3": [
        "Nc3 dari awal! Unik juga pilihanmu, ayo lanjut!",
    ],
}

OPENING_REACTION_BY_KEYWORD: List[tuple] = [
    ("Bongcloud", [
        "RAJA MAJU KE E2?! Ini main catur atau lagi bercanda nih?!",
        "Bongcloud?! Wah berani banget nantangin pakai raja di awal!",
    ]),
    ("Wayward Queen", [
        "Haha, mau coba Scholar's Mate ya? Gak bakal semudah itu!",
        "Menteri udah keluar duluan ke h5... hati-hati malah jadi target lho!",
    ]),
    ("Fried Liver", [
        "Waduh, mau masak Fried Liver di f7 ya?! Awas kena balik!",
        "Ng5! Kuda langsung ngincar f7, panas nih suasananya!",
    ]),
    ("Traxler", [
        "Traxler Counterattack?! Gila, ini bakal penuh korban dan chaos!",
    ]),
    ("Italian", [
        "Italian Game! Gajah langsung nunjuk f7, klasik dan tajam.",
        "Giuoco Piano ya... tenang di awal, tapi bisa meledak kapan aja.",
    ]),
    ("Evans Gambit", [
        "Evans Gambit! Korban pion b4 buat ngebut serang pusat — keren!",
    ]),
    ("Ruy Lopez", [
        "Ruy Lopez! Pembukaan favorit para juara dunia nih.",
        "Gajah ke b5... oke, mari kita main catur serius!",
    ]),
    ("Sicilian", [
        "Sisilia! Berarti kamu gak mau main imbang — maunya langsung tempur!",
        "Sicilian Defense ya... siap-siap papan bakal makin tajam!",
    ]),
    ("Najdorf", [
        "Najdorf! Wah selera pembukaanmu kelas berat nih!",
    ]),
    ("Dragon", [
        "Sicilian Dragon! Gajah g7 siap menyembur sepanjang diagonal!",
    ]),
    ("French", [
        "French Defense ya... benteng pion rapat, sabar nunggu serangan balik.",
    ]),
    ("Caro-Kann", [
        "Caro-Kann! Pertahanan kokoh banget, susah ditembus kalau gak teliti.",
    ]),
    ("Scandinavian", [
        "Scandinavian Defense! Langsung tabrak pion e4 di langkah pertama!",
    ]),
    ("Alekhine", [
        "Alekhine's Defense! Mancing pionku maju terus diserang balik ya?",
    ]),
    ("Queen's Gambit", [
        "Queen's Gambit! Mau aku terima atau aku tolak nih pion c4-nya?",
        "Klasik banget — Queen's Gambit. Mari kita adu kontrol tengah!",
    ]),
    ("London", [
        "London System lagi! Piramida solid yang susah digoyang ya.",
    ]),
    ("King's Gambit", [
        "King's Gambit!! Main gaya romantis abad ke-19 nih, seru!",
    ]),
    ("Scotch", [
        "Scotch Game! Langsung buka pusat tanpa basa-basi!",
    ]),
    ("Vienna", [
        "Vienna Game ya... diam-diam biasanya nyiapin f4 nih!",
    ]),
    ("Petrov", [
        "Petrov's Defense — meniru langkahku ya? Hati-hati jebakannya!",
    ]),
    ("King's Indian", [
        "King's Indian! Biarin pusat dikuasai dulu, nanti balik menyerang sayap raja!",
    ]),
    ("Slav", [
        "Slav Defense! Pion d5 dijaga rapat, solid banget.",
    ]),
    ("Dutch", [
        "Dutch Defense! Dari langkah pertama udah kelihatan agresif.",
    ]),
    ("English", [
        "English Opening! Pelan tapi menekan seluruh papan.",
    ]),
    ("Danish", [
        "Danish Gambit?! Dua pion dikasih gratis demi dua gajah maut!",
    ]),
]

PLAYER_CAPTURES_BOT: Dict[int, List[str]] = {
    QUEEN: [
        "MENTERIKU!! Aduh sakit banget tuh...",
        "Yah, Menteriku tumbang... tapi permainan belum selesai!",
        "Menteriku kena! Oke, aku harus berjuang ekstra keras sekarang.",
    ],
    ROOK: [
        "Bentengku roboh! Gak bisa dibiarin nih.",
        "Aduh, Bentengku hilang satu... mulai kerasa berat!",
        "Wah, kamu ngincar Bentengku dari tadi ya?",
    ],
    BISHOP: [
        "Gajahku jatuh, diagonal jadi kebuka lebar...",
        "Sayang banget Gajahku kena tangkap.",
        "Oke, Gajahku hilang — tapi masih banyak bidak lain!",
    ],
    KNIGHT: [
        "Kudaku tumbang! Padahal lagi enak posisinya.",
        "Kudaku gak sempat kabur deh...",
        "Wah, Kuda kesayanganku hilang!",
    ],
    PAWN: [
        "Satu pion doang... tenang, masih panjang.",
        "Boleh lah makan pion itu, tapi lihat posisi setelah ini ya.",
        "Pion hilang satu, jangan sampai kamu lengah gara-gara itu.",
    ],
}

BOT_CAPTURES_PLAYER: Dict[int, List[str]] = {
    QUEEN: [
        "Menterimu resmi masuk kotak! Pelan-pelan ya~",
        "Ups! Menterimu ketinggalan di sini, aku ambil ya!",
        "Kehilangan Menteri itu berat... masih mau lanjut?",
    ],
    ROOK: [
        "Bentengmu aku pinjam dulu ya, gak dibalikin hehe.",
        "Satu Benteng bersih! Papan makin lega buatku.",
        "Bentengmu kurang penjagaan tuh!",
    ],
    BISHOP: [
        "Gajahmu lengah di diagonal tuh, lumayan!",
        "Gajahmu aku amankan dulu ya.",
    ],
    KNIGHT: [
        "Kudamu kebanyakan lompat, sini aku tangkap!",
        "Kuda keluar kandang tanpa pengawal? Aku makan ya!",
    ],
    PAWN: [
        "Pion gratisan? Lumayan buat bekal akhir permainan!",
        "Satu pion dulu, pelan-pelan kumpulin keunggulan.",
    ],
}

CASTLE_K_QUOTES = [
    "Rajanya langsung masuk benteng ya, rapi banget.",
    "Rokade pendek — aman dulu baru serang, cakep!",
    "O-O! Raja aman, benteng siap ikut main.",
]

CASTLE_Q_QUOTES = [
    "Rokade panjang! Wah bakal saling serang sayap nih, seru!",
    "O-O-O! Berani banget, papan bakal jadi ajang adu cepat!",
]

EN_PASSANT_QUOTES = [
    "WOOOH! En passant!! Keren banget masih ingat aturan langka ini!",
    "En passant! Gak semua orang sadar langkah itu ada lho!",
]

PROMO_QUEEN_QUOTES = [
    "Pionmu jadi Menteri?! Wah bahaya besar nih!",
    "Menteri baru turun ke papan! Tekanan makin berat!",
]

PROMO_UNDER_QUOTES = [
    "Promosi bukan ke Menteri?! Gila, trik berkelas banget!",
]

BRILLIANT_QUOTES = [
    "Tunggu dulu... langkah barusan GILA banget!! Kok kepikiran?!",
    "Waduh... itu langkah brilian! Aku sampai kaget lihat papan!",
    "Astaga, langkah macam apa itu?! Luar biasa tajam!",
]

MISS_QUOTES = [
    "Fyuuh! Untung kamu gak lihat taktik barusan, jantungku hampir copot!",
    "Wah nyaris banget! Tadi kamu punya peluang emas lho...",
]

ARC_QUOTES = [
    "Waduh, premove beruntun?! Ngebut banget mainnya!",
    "Eh kok bidakmu jalan sendiri cepat banget?! Pakai ARC ya!",
    "Tenang dong, langkahmu udah disiapkan dari tadi ya?",
]

ENDGAME_QUOTES = [
    "Bidak makin tipis... sekarang adu ketenangan di akhir permainan.",
    "Masuk endgame nih — satu langkah pion bisa menentukan semuanya.",
]

def react_to_player_move(
    bot: BotProfile,
    san: str,
    ply: int,
    captured_piece: int,
    is_ep: bool,
    is_castle_k: bool,
    is_castle_q: bool,
    promo_piece: int,
    gave_check: bool,
    grade_code: str,
    opening_name: str,
    opening_just_changed: bool,
    from_arc: bool,
    pieces_left: int,
) -> Optional[str]:
    if ply == 1 and san in FIRST_MOVE_QUOTES:
        return random.choice(FIRST_MOVE_QUOTES[san])

    if is_ep:
        return random.choice(EN_PASSANT_QUOTES)

    if promo_piece:
        return random.choice(PROMO_QUEEN_QUOTES if promo_piece == QUEEN else PROMO_UNDER_QUOTES)

    if grade_code == "brilliant":
        return random.choice(BRILLIANT_QUOTES)

    if grade_code == "miss":
        return random.choice(MISS_QUOTES)

    if grade_code == "blunder":
        return bot.say("blunder_player")

    if opening_just_changed and opening_name:
        for kw, quotes in OPENING_REACTION_BY_KEYWORD:
            if kw.lower() in opening_name.lower():
                return random.choice(quotes)
        if ply <= 10 and random.random() < 0.7:
            return f"{opening_name} ya... Pilihan pembukaan yang menarik!"

    if is_castle_q:
        return random.choice(CASTLE_Q_QUOTES)
    if is_castle_k and random.random() < 0.75:
        return random.choice(CASTLE_K_QUOTES)

    if gave_check:
        return bot.say("in_check")

    if captured_piece:
        pt = abs(captured_piece)
        if pt >= KNIGHT or random.random() < 0.45:
            pool = PLAYER_CAPTURES_BOT.get(pt)
            if pool and random.random() < 0.75:
                return random.choice(pool)
            return bot.say("captured")

    if from_arc and random.random() < 0.6:
        return random.choice(ARC_QUOTES)

    if grade_code == "great" and ply >= 8 and random.random() < 0.45:
        return bot.say("good_player")

    if pieces_left <= 10 and ply >= 30 and random.random() < 0.35:
        return random.choice(ENDGAME_QUOTES)

    return None

def react_to_bot_move(
    bot: BotProfile,
    san: str,
    ply: int,
    captured_piece: int,
    is_ep: bool,
    gave_check: bool,
    memory_note: Optional[str],
    opening_name: str,
    opening_just_changed: bool,
    pieces_left: int,
) -> Optional[str]:
    if memory_note == "avoided":
        return "Aku masih ingat jebakanmu di posisi ini waktu itu — kali ini aku pilih jalur lain!"
    if memory_note == "trap":
        return "Posisi ini dulu sempat bikin kamu mikir lama... masih ingat jawabannya?"

    if is_ep:
        return "Hehe, kena en passant nih!"

    if gave_check:
        return bot.say("check")

    if captured_piece:
        pt = abs(captured_piece)
        if pt >= KNIGHT:
            pool = BOT_CAPTURES_PLAYER.get(pt)
            if pool and random.random() < 0.75:
                return random.choice(pool)
            return bot.say("capture")
        if random.random() < 0.38:
            return random.choice(BOT_CAPTURES_PLAYER[PAWN])

    if opening_just_changed and opening_name and ply <= 10:
        for kw, quotes in OPENING_REACTION_BY_KEYWORD:
            if kw.lower() in opening_name.lower():
                return random.choice(quotes)

    if pieces_left <= 10 and ply >= 30 and random.random() < 0.3:
        return random.choice(ENDGAME_QUOTES)

    if random.random() < 0.24:
        return bot.say("idle")

    return None
