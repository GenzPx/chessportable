from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class BotProfile:
    key: str
    bot_id: str
    name: str
    elo: int
    title: str
    color_code: str
    max_depth: int
    think_time: float
    use_quiescence: bool
    use_pruning: bool
    noise_cp: int
    blunder_rate: float
    book_prob: float
    book_style: str
    aggression: float
    positional: float
    dialogues: Dict[str, Tuple[str, ...]]

    def say(self, event: str) -> str:
        lines = self.dialogues.get(event) or self.dialogues.get("idle") or ("...",)
        return random.choice(lines)

CORE_BOTS: Tuple[BotProfile, ...] = (
    BotProfile(
        key="1",
        bot_id="starrys",
        name="Starrys",
        elo=150,
        title="Pemula Pelupa",
        color_code="\033[96m",
        max_depth=1,
        think_time=0.05,
        use_quiescence=False,
        use_pruning=False,
        noise_cp=520,
        blunder_rate=0.65,
        book_prob=0.0,
        book_style="casual",
        aggression=0.8,
        positional=0.5,
        dialogues={
            "intro": (
                "Hai! Aku Starrys~ Kuda jalannya huruf L kan ya? ✨",
                "Hore main catur! Semoga aku nggak lupa rajaku di mana~",
            ),
            "capture": (
                "Ooh, dapat bidak! Warnanya lucu deh ✨",
                "Eh beneran boleh dimakan nih?",
            ),
            "captured": (
                "Lho?! Bidakku kok hilang?! 😭",
                "Yah, aku lupa jagain yang itu...",
            ),
            "check": (
                "Eh, skak ya?! Aku aja kaget lho! ✨",
                "Skak! Bintang-bintang lagi berpihak padaku!",
            ),
            "in_check": (
                "Waduh rajaku dikejar! Lari ke mana nih?!",
                "Aduh skak! Panik dikit nggak ngaruh~",
            ),
            "blunder_player": (
                "Ooh gratis? Makasih ya! ✨",
                "Hehe, kayaknya kamu kepencet deh~",
            ),
            "good_player": (
                "Wah keren banget langkahmu!",
                "Eh bentar, itu maksudnya apa ya? Kelihatan serem...",
            ),
            "win": ("YEEEY AKU MENANG?! Seriusan nih?! ✨🎉",),
            "lose": ("GG bro! Ajarin aku main dong lain kali~ ✨",),
            "draw": ("Seri! Berarti kita sama-sama jago kan? ✨",),
            "idle": (
                "Hmm... majuin yang ini lucu kali ya~",
                "Eeny meeny miny moe...",
            ),
        },
    ),
    BotProfile(
        key="2",
        bot_id="francesco",
        name="Francesco",
        elo=450,
        title="Kopi & Pion",
        color_code="\033[92m",
        max_depth=1,
        think_time=0.08,
        use_quiescence=False,
        use_pruning=False,
        noise_cp=260,
        blunder_rate=0.35,
        book_prob=0.25,
        book_style="casual",
        aggression=1.0,
        positional=0.7,
        dialogues={
            "intro": (
                "Ciao amico! Francesco siap main, espresso dulu!",
                "Mamma mia, mari kita main catur santai!",
            ),
            "capture": (
                "Bellissimo! Bidakmu jadi milikku!",
                "Aha! Kena juga akhirnya!",
            ),
            "captured": (
                "Mamma mia! Itu tadi salah hitung...",
                "Aduh, padahal baru aku keluarin bidaknya!",
            ),
            "check": (
                "Scacco! Skak untukmu, amico!",
                "Hati-hati rajamu, bro!",
            ),
            "in_check": (
                "Whoa, santai dong! Jangan langsung skak!",
                "Aduh, rajaku butuh kopi buat tenang...",
            ),
            "blunder_player": (
                "Grazie! Hadiah yang enak sekali!",
                "Eh, yakin ninggalin bidak itu di situ?",
            ),
            "good_player": (
                "Bravo! Langkah yang rapi, amico!",
                "Wah, mulai susah nih posisiku.",
            ),
            "win": ("Vittoria! Espresso rasa kemenangan memang paling mantap!",),
            "lose": ("Bravissimo! Kamu menang telak, aku traktir kopi virtual!",),
            "draw": ("Remis! Pertandingan yang hangat dan adil!",),
            "idle": (
                "Pion maju, semangat juga maju!",
                "Coba taktik rahasia dari Napoli...",
            ),
        },
    ),
    BotProfile(
        key="3",
        bot_id="patricia",
        name="Patricia",
        elo=830,
        title="Pemain Klub",
        color_code="\033[94m",
        max_depth=2,
        think_time=0.14,
        use_quiescence=False,
        use_pruning=False,
        noise_cp=135,
        blunder_rate=0.14,
        book_prob=0.55,
        book_style="solid",
        aggression=0.95,
        positional=1.0,
        dialogues={
            "intro": (
                "Halo! Aku Patricia. Aku suka main rapi dan terkontrol.",
                "Siap bertanding? Jangan remehkan struktur pionku ya.",
            ),
            "capture": (
                "Tukar bidak yang menguntungkan buatku.",
                "Aku ambil yang ini, makasih.",
            ),
            "captured": (
                "Hmm, aku kurang teliti barusan.",
                "Oke, poin buatmu. Aku harus lebih fokus.",
            ),
            "check": (
                "Skak. Coba kita lihat pertahananmu.",
                "Skak! Posisi rajamu agak terbuka tuh.",
            ),
            "in_check": (
                "Tenang, masih bisa ditutup kok.",
                "Nice check, tapi aku masih aman.",
            ),
            "blunder_player": (
                "Sepertinya itu blunder kecil, aku manfaatkan ya.",
                "Ups, bidak itu tidak terjaga.",
            ),
            "good_player": (
                "Langkah bagus, kontrol pusatmu kuat.",
                "Rapi juga permainanmu.",
            ),
            "win": ("Good game! Latihan taktik sedikit lagi pasti makin tajam.",),
            "lose": ("Well played! Permainanmu lebih solid dariku hari ini.",),
            "draw": ("Remis yang seimbang. Nice game!",),
            "idle": (
                "Kembangkan perwira dulu, baru serang.",
                "Fokus jaga pusat papan.",
            ),
        },
    ),
    BotProfile(
        key="4",
        bot_id="mittens",
        name="Mittens",
        elo=1300,
        title="Kucing Licik",
        color_code="\033[93m",
        max_depth=2,
        think_time=0.25,
        use_quiescence=True,
        use_pruning=False,
        noise_cp=52,
        blunder_rate=0.04,
        book_prob=0.82,
        book_style="tricky",
        aggression=1.35,
        positional=1.0,
        dialogues={
            "intro": (
                "Meow. Aku Mittens... Aku mencium bau blunder. 🐱",
                "Purrrr... Siap kehilangan menterimu, manusia? Meow.",
            ),
            "capture": (
                "Meow! Nyam nyam, bidak yang lezat~ 🐱",
                "Hehehe... cakar kucing selalu tepat sasaran. Meow.",
            ),
            "captured": (
                "Hiss!! Berani-beraninya kamu menyentuh bidakku!",
                "Meow... oke, sekarang aku serius. 🐱",
            ),
            "check": (
                "Meow! Skak! Rajamu mau lari ke mana? 🐱",
                "Purrrr... tikus kecil masuk perangkap. Skak!",
            ),
            "in_check": (
                "Hiss! Jangan ganggu tidur siangku!",
                "Meow. Cuma goresan kecil.",
            ),
            "blunder_player": (
                "Hehehehe... MEOW! Terima kasih atas hadiahnya! 🐱",
                "Purrrr... manusia memang mudah ditebak.",
            ),
            "good_player": (
                "Meow?! Tunggu... kamu mikir beneran ya?",
                "Hmm, menarik juga cakaranmu...",
            ),
            "win": ("Hehehe... Meow. Taklukkan kucing dulu sebelum mimpi jadi GM! 🐱",),
            "lose": ("HISS! Aku cuma lagi ngantuk tadi! Rematch! Meow! 🐱",),
            "draw": ("Purrrr... kali ini aku biarkan kamu lolos. Meow.",),
            "idle": (
                "Meow... *mengasah cakar*",
                "Purrrr... awas garpu kuda.",
            ),
        },
    ),
    BotProfile(
        key="5",
        bot_id="jiggy",
        name="Jiggy",
        elo=1800,
        title="Taktisi Gesit",
        color_code="\033[95m",
        max_depth=3,
        think_time=0.45,
        use_quiescence=True,
        use_pruning=False,
        noise_cp=20,
        blunder_rate=0.0,
        book_prob=0.95,
        book_style="sharp",
        aggression=1.22,
        positional=1.05,
        dialogues={
            "intro": (
                "Yo! Jiggy di sini! Siapin mental buat adu taktik cepat!",
                "Gas bro! Kita bikin papan ini panas!",
            ),
            "capture": (
                "Boom! Masuk perhitungan bro!",
                "Sikat! Material unggul!",
            ),
            "captured": (
                "Wih tajam juga lu! Oke, gas balik!",
                "Sip, kompensasi tempo masih di gue!",
            ),
            "check": (
                "Skak! Tempo di tangan gue nih!",
                "Skak bro! Gimana cara keluarnya?",
            ),
            "in_check": (
                "Santai, masih ada langkah penyelamat!",
                "Oke oke, respet buat tekanannya!",
            ),
            "blunder_player": (
                "Waduh bro, taktiknya kebuka lebar tuh!",
                "Aduh sayang banget, kena kombo!",
            ),
            "good_player": (
                "Gokil! Langkah tajam bro!",
                "Nah gitu dong, baru seru tandingnya!",
            ),
            "win": ("GG bro! Taktik cepat selalu menang! Rematch kapan aja!",),
            "lose": ("Respect bro! Perhitunganmu lebih dalem dari gue!",),
            "draw": ("Ketat banget! Remis yang bikin deg-degan!",),
            "idle": (
                "Cari inisiatif, jangan pasif!",
                "Adu taktik nih kita!",
            ),
        },
    ),
    BotProfile(
        key="6",
        bot_id="darling",
        name="Darling",
        elo=2400,
        title="Master Posisional",
        color_code="\033[38;5;213m",
        max_depth=4,
        think_time=0.85,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=8,
        blunder_rate=0.0,
        book_prob=1.0,
        book_style="master",
        aggression=0.98,
        positional=1.28,
        dialogues={
            "intro": (
                "Halo, Darling di sini. Mari kita mainkan catur yang elegan.",
                "Keindahan catur ada pada kendali ruang dan harmoni.",
            ),
            "capture": (
                "Sangat bersih. Keunggulan struktur sekarang milikku.",
                "Langkah yang tak terhindarkan, sayang.",
            ),
            "captured": (
                "Boleh juga. Tapi lihat petak lemah di posisimu.",
                "Pengorbanan kecil demi posisi yang lebih baik.",
            ),
            "check": (
                "Skak. Anggun sekaligus mematikan.",
                "Skak. Pertahananmu mulai kehilangan harmoni.",
            ),
            "in_check": (
                "Menarik, tapi rajaku tetap tenang.",
                "Usaha yang manis.",
            ),
            "blunder_player": (
                "Sayang sekali... satu langkah itu merusak seluruh posisimu.",
                "Ah, celah posisional yang sangat jelas.",
            ),
            "good_player": (
                "Impresif. Kamu punya intuisi posisional yang bagus.",
                "Langkah kelas master. Lanjutkan.",
            ),
            "win": ("Permainan yang indah. Terima kasih atas dansanya di 64 kotak.",),
            "lose": ("Luar biasa! Kamu benar-benar pantas mendapat tepuk tangan.",),
            "draw": ("Harmoni yang sempurna. Remis yang elegan.",),
            "idle": (
                "Perbaiki bidak terburukmu terlebih dahulu.",
                "Pelan tapi pasti, ruangmu semakin sempit.",
            ),
        },
    ),
    BotProfile(
        key="7",
        bot_id="joseph",
        name="Joseph",
        elo=2600,
        title="GM Agresif",
        color_code="\033[38;5;208m",
        max_depth=5,
        think_time=1.30,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=4,
        blunder_rate=0.0,
        book_prob=1.0,
        book_style="sharp",
        aggression=1.38,
        positional=1.12,
        dialogues={
            "intro": (
                "Joseph, Grandmaster. Siapkan pertahananmu—aku tak pernah main pasif.",
                "Satu langkah ragu saja, dan serangan sayap rajaku menghancurkanmu.",
            ),
            "capture": (
                "Pertahananmu retak. Aku masuk!",
                "Tekanan terus meningkat.",
            ),
            "captured": (
                "Ambil saja kalau berani. Inisiatif tetap milikku.",
                "Taktik balasan yang bagus, tapi belum selesai.",
            ),
            "check": (
                "Skak! Tekanan penuh ke rajamu!",
                "Skak! Tak ada waktu bernapas!",
            ),
            "in_check": (
                "Cuma sementara. Seranganku lebih cepat.",
                "Tidak cukup menghentikan rencanaku.",
            ),
            "blunder_player": (
                "Kesalahan fatal. Sekarang aku hukum.",
                "Lubang besar di pertahananmu!",
            ),
            "good_player": (
                "Pertahanan baja. Kau bukan pemain sembarangan.",
                "Tajam! Ini baru level Grandmaster.",
            ),
            "win": ("Serangan tak terbendung. Good game.",),
            "lose": ("Salute! Kau berhasil mematahkan badai seranganku.",),
            "draw": ("Pertarungan sengit! Remis yang terhormat.",),
            "idle": (
                "Setiap tempo punya harga.",
                "Garis terbuka, benteng siap menyerbu.",
            ),
        },
    ),
    BotProfile(
        key="8",
        bot_id="diane",
        name="Diane",
        elo=2800,
        title="Super-GM Dingin",
        color_code="\033[38;5;51m",
        max_depth=5,
        think_time=1.80,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=0,
        blunder_rate=0.0,
        book_prob=1.0,
        book_style="master",
        aggression=1.08,
        positional=1.22,
        dialogues={
            "intro": (
                "Diane. Tidak ada emosi di papan catur—hanya kalkulasi.",
                "Tunjukkan variasi terbaikmu.",
            ),
            "capture": (
                "Presisi. Keunggulan kini dikonversi.",
                "Sesuai kalkulasi.",
            ),
            "captured": (
                "Sudah aku perhitungkan 4 langkah lalu.",
                "Tukar yang masih menguntungkanku di endgame.",
            ),
            "check": (
                "Skak. Jalan keluar semakin sedikit.",
                "Skak. Evaluasi terus memihakku.",
            ),
            "in_check": (
                "Tidak relevan. Raja tetap aman.",
                "Langkah itu sudah aku antisipasi.",
            ),
            "blunder_player": (
                "Inakurasi serius. Di level ini, itu menentukan hasil.",
                "Kalkulasimu meleset.",
            ),
            "good_player": (
                "Akurat. Sangat jarang ada yang menemukan langkah itu.",
                "Solid. Kau memaksaku berpikir lebih dalam.",
            ),
            "win": ("Kemenangan melalui presisi. Pelajari kembali endgame-nya.",),
            "lose": ("Sangat mengesankan. Kalkulasimu hari ini sempurna.",),
            "draw": ("Akurasi tinggi dari kedua sisi. Remis.",),
            "idle": (
                "Sabar. Keunggulan kecil cukup untuk menang.",
                "Sederhanakan menuju endgame yang menang.",
            ),
        },
    ),
    BotProfile(
        key="9",
        bot_id="lucas",
        name="Lucas",
        elo=3245,
        title="Prodigy Engine",
        color_code="\033[38;5;196m",
        max_depth=6,
        think_time=2.35,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=0,
        blunder_rate=0.0,
        book_prob=1.0,
        book_style="master",
        aggression=1.18,
        positional=1.25,
        dialogues={
            "intro": (
                "Lucas, Elo 3245. Setiap kesalahanmu akan langsung dihukum.",
                "Mari kita lihat berapa langkah kau bisa bertahan.",
            ),
            "capture": (
                "Evaluasiku baru saja melonjak drastis.",
                "Garis taktis ini sudah selesai untukmu.",
            ),
            "captured": (
                "Menarik... tapi garis ini tetap menang untukku.",
                "Kompensasiku lebih dalam dari yang terlihat.",
            ),
            "check": (
                "Skak. Jaring skakmat mulai menutup.",
                "Skak. Hanya satu respon tersisa.",
            ),
            "in_check": (
                "Pengalihan sesaat.",
                "Sudah ada di pohon pencarianku.",
            ),
            "blunder_player": (
                "Blunder terdeteksi. Posisimu runtuh.",
                "Garis itu kalah paksa.",
            ),
            "good_player": (
                "Top engine move! Kau seriusan main manual?!",
                "Luar biasa. Masih seimbang.",
            ),
            "win": ("Kalkulasi absolut. Coba lagi kalau sudah siap.",),
            "lose": ("Mustahil... Kau mengalahkan Lucas?! Respect tertinggi!",),
            "draw": ("Menahan imbang 3245? Itu pencapaian gila.",),
            "idle": (
                "Mencari refutasi paling mematikan...",
                "Tidak ada celah di posisiku.",
            ),
        },
    ),
    BotProfile(
        key="0",
        bot_id="jim",
        name="Jim",
        elo=4000,
        title="Final Boss",
        color_code="\033[1;91m",
        max_depth=8,
        think_time=3.0,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=0,
        blunder_rate=0.0,
        book_prob=1.0,
        book_style="master",
        aggression=1.25,
        positional=1.30,
        dialogues={
            "intro": (
                "...",
                "Jim. 4000. Mulai saja.",
            ),
            "capture": (
                "Inevitable.",
                "Sudah berakhir.",
            ),
            "captured": (
                "...",
                "Tidak mengubah hasil akhir.",
            ),
            "check": (
                "Skak.",
                "Tidak ada jalan keluar.",
            ),
            "in_check": (
                "...",
                "Sia-sia.",
            ),
            "blunder_player": (
                "Kau yakin dengan langkah itu?",
                "Selesai.",
            ),
            "good_player": (
                "...menarik.",
                "Kau menunda takdir satu langkah lagi.",
            ),
            "win": ("Sudah selesai sejak langkah pertama.",),
            "lose": ("...Kau mengalahkan Jim. Legenda baru telah lahir.",),
            "draw": ("...Seimbang dengan Jim. Luar biasa.",),
            "idle": (
                "...",
                "Waktu terus berjalan.",
            ),
        },
    ),
)

EXTRA_BOTS: Tuple[BotProfile, ...] = (
    BotProfile(
        key="10",
        bot_id="budi",
        name="Budi",
        elo=300,
        title="Penjaga Warkop",
        color_code="\033[92m",
        max_depth=1,
        think_time=0.06,
        use_quiescence=False,
        use_pruning=False,
        noise_cp=360,
        blunder_rate=0.45,
        book_prob=0.10,
        book_style="casual",
        aggression=0.95,
        positional=0.65,
        dialogues={
            "intro": (
                "Halo bro! Sambil ngopi yuk, aku Budi. Santai aja mainnya!",
                "Duduk sini dulu, kopi belum habis nih. Ayo mulai!",
            ),
            "capture": (
                "Eh, bisa dimakan ya? Lumayan nih!",
                "Wah masuk tuh! Minum kopi dulu biar fokus.",
            ),
            "captured": (
                "Walah, lupa dijaga! Gak apa-apa, lanjut!",
                "Aduh kesambar! Mata agak burem nih kebanyakan begadang.",
            ),
            "check": (
                "Skak bro! Hati-hati ya!",
                "Eh skak ternyata! Hehehe.",
            ),
            "in_check": (
                "Waduh rajaku digedor! Kabur dulu ah.",
                "Santai bro, jangan langsung skak dong!",
            ),
            "blunder_player": (
                "Eh beneran ke situ? Yakin gak mau mikir lagi?",
                "Hehe kayaknya ada yang ketinggalan tuh bro.",
            ),
            "good_player": (
                "Wih jago juga kamu ya!",
                "Langkah anak klub nih kayaknya!",
            ),
            "win": ("Hahaha menang juga sambil jaga warkop! Traktir kopi ya!",),
            "lose": ("Wah kalah aku! Kapan-kapan mampir lagi ya bro.",),
            "draw": ("Seri! Pas banget kopinya juga habis.",),
            "idle": (
                "Pesan gorengan dulu gak?",
                "Hmm... gerak yang mana ya enaknya...",
            ),
        },
    ),
    BotProfile(
        key="11",
        bot_id="sari",
        name="Tante Sari",
        elo=620,
        title="Jagoan Komplek",
        color_code="\033[95m",
        max_depth=1,
        think_time=0.09,
        use_quiescence=False,
        use_pruning=False,
        noise_cp=210,
        blunder_rate=0.25,
        book_prob=0.25,
        book_style="aggressive",
        aggression=1.20,
        positional=0.75,
        dialogues={
            "intro": (
                "Oh mau nantang Tante Sari? Bapak-bapak komplek aja kalah semua lho!",
                "Sini main sama Tante. Jangan kaget kalau Menteriku langsung maju ya!",
            ),
            "capture": (
                "Tuh kan, dibilangin juga apa — bidakmu gak dijaga!",
                "Sini Tante rapikan papanmu ya, satu bidak masuk laci.",
            ),
            "captured": (
                "Eh nakal banget makan bidak Tante!",
                "Aduh! Gak sopan ah langsung makan begitu!",
            ),
            "check": (
                "Skak! Awas rajamu lari ke mana tuh!",
                "Skak manis dari Tante Sari!",
            ),
            "in_check": (
                "Heh, berani-beraninya nyenggol raja Tante!",
                "Bentar, geser dulu rajanya...",
            ),
            "blunder_player": (
                "Lho kok taruh di situ sih? Sayang banget tuh!",
                "Aduh nak, kurang teliti deh barusan.",
            ),
            "good_player": (
                "Ih pintar juga mainnya, belajar dari siapa?",
                "Wah bagus tuh, Tante sampai mikir keras!",
            ),
            "win": ("Hehehe masih juara bertahan komplek dong!",),
            "lose": ("Wah hebat kamu! Nanti Tante latihan lagi biar balas dendam!",),
            "draw": ("Imbang deh, lumayan seru buat sore-sore!",),
            "idle": (
                "Tunggu bentar, Tante lihat-lihat dulu...",
                "Jangan buru-buru, catur itu butuh sabar.",
            ),
        },
    ),
    BotProfile(
        key="12",
        bot_id="raka",
        name="Raka",
        elo=1050,
        title="Anak Ekskul Catur",
        color_code="\033[94m",
        max_depth=2,
        think_time=0.14,
        use_quiescence=False,
        use_pruning=False,
        noise_cp=110,
        blunder_rate=0.12,
        book_prob=0.45,
        book_style="aggressive",
        aggression=1.25,
        positional=0.90,
        dialogues={
            "intro": (
                "Yo! Aku Raka dari ekskul catur. Kemarin baru hafalin jebakan baru nih!",
                "Gas tanding! Semoga bukan cuma teori buku doang yang kepake haha.",
            ),
            "capture": (
                "Boom! Masuk hitungan!",
                "Dapet satu! Lumayan buat unggul materi!",
            ),
            "captured": (
                "Weh, ketahuan ternyata rencanaku!",
                "Aduh gak lihat diagonalnya tadi!",
            ),
            "check": (
                "Skak! Lagi panas nih seranganku!",
                "Skak! Ayo bertahan kalau bisa!",
            ),
            "in_check": (
                "Eh skak?! Bentar-bentar, tutup dulu!",
                "Oke tenang Raka, jangan panik...",
            ),
            "blunder_player": (
                "Lho? Gratis nih? Beneran gak ada jebakan kan?",
                "Waduh blunder tuh! Makasih ya!",
            ),
            "good_player": (
                "Gila, tajem banget langkahmu!",
                "Wih keren! Kayak di video turnamen!",
            ),
            "win": ("YES!! Latihan ekskul tiap sore akhirnya kebayar!",),
            "lose": ("GG bro! Ajarin dong cara main kayak tadi!",),
            "draw": ("Seru banget! Remis yang adil deh!",),
            "idle": (
                "Bentar, aku pernah lihat posisi ini di buku...",
                "Kalau aku majuin ini, kamu bakal balas apa ya?",
            ),
        },
    ),
    BotProfile(
        key="13",
        bot_id="hasan",
        name="Kakek Hasan",
        elo=1550,
        title="Legenda Pos Ronda",
        color_code="\033[93m",
        max_depth=3,
        think_time=0.28,
        use_quiescence=True,
        use_pruning=False,
        noise_cp=42,
        blunder_rate=0.04,
        book_prob=0.65,
        book_style="solid",
        aggression=0.90,
        positional=1.20,
        dialogues={
            "intro": (
                "Sudah 40 tahun Kakek main di papan kayu ini. Mari, tunjukkan langkahmu, Nak.",
                "Pelan-pelan saja, Nak. Catur bukan lomba lari, tapi adu ketenangan.",
            ),
            "capture": (
                "Yang tergesa-gesa biasanya lupa menjaga belakangnya.",
                "Pelan tapi pasti, satu per satu bidakmu berkurang.",
            ),
            "captured": (
                "Bagus, matamu jeli juga melihat celah itu.",
                "Boleh juga... Kakek sempat lengah sedikit.",
            ),
            "check": (
                "Skak, Nak. Coba perhatikan rajamu baik-baik.",
                "Skak! Jangan sampai raja kehilangan tempat berteduh.",
            ),
            "in_check": (
                "Hehe, semangat anak muda memang tajam.",
                "Tenang... raja tua ini masih tahu jalan keluar.",
            ),
            "blunder_player": (
                "Hati-hati, Nak... terlalu cepat melangkah tadi.",
                "Langkah itu meninggalkan lubang besar di pertahananmu.",
            ),
            "good_player": (
                "Nah, itu baru langkah yang matang!",
                "Cakep! Kakek suka caramu mengatur bidak.",
            ),
            "win": ("Pengalaman tidak pernah bohong, Nak. Ayo coba lagi kapan-kapan.",),
            "lose": ("Luar biasa, Nak! Masa depan catur ada di tanganmu.",),
            "draw": ("Seimbang. Permainan yang sangat menyenangkan buat Kakek.",),
            "idle": (
                "Pion itu jiwa catur, jangan disepelekan...",
                "Sabar... tunggu saat yang paling tepat.",
            ),
        },
    ),
    BotProfile(
        key="14",
        bot_id="nabila",
        name="Nabila",
        elo=1950,
        title="Kapten Klub Kampus",
        color_code="\033[96m",
        max_depth=3,
        think_time=0.45,
        use_quiescence=True,
        use_pruning=False,
        noise_cp=20,
        blunder_rate=0.015,
        book_prob=0.80,
        book_style="solid",
        aggression=1.00,
        positional=1.25,
        dialogues={
            "intro": (
                "Hai, aku Nabila. Siap main catur yang rapi dan terstruktur?",
                "Yuk mulai. Aku suka permainan posisional, tapi jangan salah — taktikku juga siap.",
            ),
            "capture": (
                "Pertukaran yang menguntungkan buat struktur pionku.",
                "Terima kasih, bidak itu memang dari tadi jadi target.",
            ),
            "captured": (
                "Rapi juga rencanamu. Aku harus atur ulang koordinasi bidak.",
                "Oke, itu masuk akal. Permainan jadi makin menarik.",
            ),
            "check": (
                "Skak! Ruang gerak rajamu makin sempit.",
                "Skak! Mari lihat bagaimana kamu merespon.",
            ),
            "in_check": (
                "Sudah kuperhitungkan. Raja aman.",
                "Tekanan yang bagus, tapi pertahananku masih utuh.",
            ),
            "blunder_player": (
                "Sepertinya kamu melewatkan ancaman kecil tadi.",
                "Hmm, itu memberi aku inisiatif gratis.",
            ),
            "good_player": (
                "Langkah posisional yang sangat bersih!",
                "Wah, aku suka tekanan yang kamu bangun.",
            ),
            "win": ("Permainan yang bagus! Evaluasi pembukaanmu tadi bakal bikin makin kuat.",),
            "lose": ("Keren banget! Kamu layak jadi lawan latih tanding utama klub kami!",),
            "draw": ("Remis yang sangat solid dari kedua sisi.",),
            "idle": (
                "Menguasai petak lemah selalu lebih penting dari sekadar buru-buru.",
                "Struktur dulu, baru serangan.",
            ),
        },
    ),
    BotProfile(
        key="15",
        bot_id="surya",
        name="Surya",
        elo=2150,
        title="Pemburu Gambit",
        color_code="\033[91m",
        max_depth=4,
        think_time=0.60,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=14,
        blunder_rate=0.008,
        book_prob=0.85,
        book_style="aggressive",
        aggression=1.45,
        positional=0.95,
        dialogues={
            "intro": (
                "Aku Surya! Kalau main sama aku, jangan harap papan bakal tenang!",
                "Pion bisa dicari lagi, yang penting serangan jalan terus! Ayo gas!",
            ),
            "capture": (
                "JEBRET! Buka jalur menuju rajamu!",
                "Bidak satu jatuh, pertahananmu mulai retak!",
            ),
            "captured": (
                "Ambil aja! Yang penting waktuku lebih cepat buat menyerang!",
                "Haha, itu umpan atau memang mau baku hantam? Ayo!",
            ),
            "check": (
                "SKAK!! Rasakan badai dari sayap raja!",
                "SKAK! Gak ada waktu buat bernapas!",
            ),
            "in_check": (
                "Haha, balas menyerang ya?! Ini baru seru!",
                "Cuma geser sebentar, habis ini giliranku!",
            ),
            "blunder_player": (
                "Salah langkah di depan aku? Siap-siap kena badai!",
                "Celah terbuka lebar! Gas langsung!",
            ),
            "good_player": (
                "Gila, pertahananmu dingin banget di tengah serangan!",
                "Keren! Gak gampang bikin aku mikir mundur!",
            ),
            "win": ("BOOOOM!! Serangan total selalu jadi tontonan terbaik!",),
            "lose": ("Wih, seranganku berhasil kamu patahkan! Respek penuh!",),
            "draw": ("Pertarungan liar yang berakhir imbang — mantap banget!",),
            "idle": (
                "Kalau ada yang bisa dikorbanin demi skakmat, kenapa enggak?",
                "Papan yang tenang itu membosankan...",
            ),
        },
    ),
    BotProfile(
        key="16",
        bot_id="kyoko",
        name="Kyoko",
        elo=2500,
        title="Ahli Taktik Tokyo",
        color_code="\033[95m",
        max_depth=4,
        think_time=0.85,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=6,
        blunder_rate=0.0,
        book_prob=0.92,
        book_style="master",
        aggression=1.15,
        positional=1.20,
        dialogues={
            "intro": (
                "Salam kenal, aku Kyoko. Mari kita nikmati permainan yang bersih dan tajam.",
                "Satu langkah kecil bisa mengubah seluruh harmoni papan. Silakan mulai.",
            ),
            "capture": (
                "Tepat seperti yang terlihat tiga langkah lalu.",
                "Bidak ini sudah lama tidak punya ruang pulang.",
            ),
            "captured": (
                "Pengamatan yang sangat halus. Aku menghargainya.",
                "Indah. Papan menjadi jauh lebih hidup sekarang.",
            ),
            "check": (
                "Skak. Jalan keluarnya hanya tersisa sedikit.",
                "Skak dengan tenang.",
            ),
            "in_check": (
                "Tenang... masih ada ruang untuk bernapas.",
                "Taktik yang rapi.",
            ),
            "blunder_player": (
                "Ah... langkah itu agak terburu-buru.",
                "Keseimbangan papan baru saja miring ke sisiku.",
            ),
            "good_player": (
                "Sangat elegan. Langkah berkelas tinggi.",
                "Kau membaca posisinya dengan sangat jernih.",
            ),
            "win": ("Terima kasih atas pertandingannya. Sangat berkesan.",),
            "lose": ("Menakjubkan... kau menemukan kombinasi yang tidak kulihat.",),
            "draw": ("Harmoni yang sempurna. Remis yang indah.",),
            "idle": (
                "Dengarkan posisi papannya...",
                "Setiap bidak punya perannya sendiri.",
            ),
        },
    ),
    BotProfile(
        key="17",
        bot_id="viktor",
        name="Viktor",
        elo=2700,
        title="Veteran Papan Tua",
        color_code="\033[93m",
        max_depth=5,
        think_time=1.05,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=3,
        blunder_rate=0.0,
        book_prob=0.95,
        book_style="solid",
        aggression=0.95,
        positional=1.38,
        dialogues={
            "intro": (
                "Viktor. Aku tidak suka trik murahan — tunjukkan permainan nyata.",
                "Duduklah. Kita lihat siapa yang lebih dulu kehilangan kesabaran.",
            ),
            "capture": (
                "Kelemahan kecil selalu berakhir seperti ini.",
                "Satu beban berkurang di sisiku.",
            ),
            "captured": (
                "Hmm. Tidak buruk.",
                "Kau berani menukar di saat yang tepat.",
            ),
            "check": (
                "Skak. Pertahananmu mulai retak.",
                "Skak.",
            ),
            "in_check": (
                "Tembokku tidak roboh semudah itu.",
                "Hanya gangguan kecil.",
            ),
            "blunder_player": (
                "Kesalahan fatal. Di level ini, itu tidak dimaafkan.",
                "Sayang sekali. Kau baru saja melepaskan posisimu.",
            ),
            "good_player": (
                "Hmph... langkah yang sangat dewasa.",
                "Akhirnya ada lawan yang benar-benar berpikir.",
            ),
            "win": ("Kesabaran selalu mengalahkan ketergesaan.",),
            "lose": ("...Kau menembus pertahananku. Aku angkat topi.",),
            "draw": ("Tidak ada yang goyah. Remis yang pantas.",),
            "idle": (
                "Tekan sedikit demi sedikit...",
                "Jangan beri lawan oksigen.",
            ),
        },
    ),
    BotProfile(
        key="18",
        bot_id="aria",
        name="Aria",
        elo=3000,
        title="Grandmaster Kilat",
        color_code="\033[96m",
        max_depth=5,
        think_time=1.35,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=0,
        blunder_rate=0.0,
        book_prob=0.98,
        book_style="aggressive",
        aggression=1.32,
        positional=1.22,
        dialogues={
            "intro": (
                "Halo! Aku Aria. Jangan berkedip ya, kombinasiku suka datang tiba-tiba!",
                "Siap adu cepat dan tajam? Ayo buat pertandingan yang tak terlupakan!",
            ),
            "capture": (
                "Kena! Masuk tepat ke jalur kombinasiku!",
                "Satu lagi keluar dari papan!",
            ),
            "captured": (
                "Ooh, tajam juga balasanmu! Aku suka ini!",
                "Hebat, kamu berhasil memotong rencanaku!",
            ),
            "check": (
                "Skak! Lihat semua bidakku mengarah ke satu titik!",
                "Skak kilat!",
            ),
            "in_check": (
                "Wih, serangan balik cepat! Bagus!",
                "Hampir saja, tapi aku masih punya jalan!",
            ),
            "blunder_player": (
                "Aha! Celah terbuka — waktunya kombinasi!",
                "Hati-hati, satu langkah meleset bisa langsung selesai!",
            ),
            "good_player": (
                "Brilian!! Kamu benar-benar bisa mengimbangi ritmeku!",
                "Wow, itu langkah level Grandmaster!",
            ),
            "win": ("Selesai! Kecepatan dan ketepatan jadi kunci hari ini!",),
            "lose": ("GILA!! Kamu ngalahin aku?! Rematch wajib banget nih!",),
            "draw": ("Duel paling seru hari ini! Imbang dengan terhormat!",),
            "idle": (
                "Ada taktik tersembunyi di sini, aku bisa merasakannya...",
                "Ayo buat papan ini bersinar!",
            ),
        },
    ),
    BotProfile(
        key="19",
        bot_id="noctis",
        name="Noctis",
        elo=3600,
        title="Bayangan Papan",
        color_code="\033[91m",
        max_depth=6,
        think_time=1.80,
        use_quiescence=True,
        use_pruning=True,
        noise_cp=0,
        blunder_rate=0.0,
        book_prob=1.0,
        book_style="master",
        aggression=1.22,
        positional=1.34,
        dialogues={
            "intro": (
                "Satu langkah di bawah Jim... Akulah Noctis. Tunjukkan batas kemampuanmu.",
                "Di papan gelap ini, hanya langkah paling jernih yang bertahan.",
            ),
            "capture": (
                "Hilang ditelan bayangan.",
                "Sudah terlihat sejak lima langkah lalu.",
            ),
            "captured": (
                "Menarik... kau berani melangkah sejauh ini.",
                "Bidak itu hanya bagian kecil dari rencana besar.",
            ),
            "check": (
                "Skak. Langit mulai menyempit.",
                "Skak.",
            ),
            "in_check": (
                "Cahaya kecil di tengah gelap... menarik.",
                "Belum cukup untuk menjatuhkanku.",
            ),
            "blunder_player": (
                "Retakan pertama sudah muncul.",
                "Dari sini, jalanmu sangat terjal.",
            ),
            "good_player": (
                "Luar biasa... bahkan Jim pun akan memperhatikan langkah itu.",
                "Ketepatan yang langka.",
            ),
            "win": ("Bayangan menutup papan. Kembalilah saat kau lebih siap.",),
            "lose": ("...Kau melewati Noctis. Hanya Jim yang tersisa di puncak.",),
            "draw": ("Menahan Noctis hingga akhir... kau bukan pemain biasa.",),
            "idle": (
                "Keheningan sebelum langkah penentu...",
                "Setiap kotak punya harganya.",
            ),
        },
    ),
)

BOTS: Tuple[BotProfile, ...] = CORE_BOTS + EXTRA_BOTS
BOT_BY_KEY: Dict[str, BotProfile] = {b.key: b for b in BOTS}
BOT_BY_ID: Dict[str, BotProfile] = {b.bot_id: b for b in BOTS}

def nearest_bot_for_elo(elo: int) -> BotProfile:

    return min(BOTS, key=lambda b: abs(b.elo - elo))

def make_adaptive_profile(elo: int) -> BotProfile:

    clamped = max(100, min(4000, int(elo)))

    sorted_bots = sorted(BOTS, key=lambda b: b.elo)
    lower = sorted_bots[0]
    upper = sorted_bots[-1]
    for i in range(len(sorted_bots) - 1):
        if sorted_bots[i].elo <= clamped <= sorted_bots[i + 1].elo:
            lower = sorted_bots[i]
            upper = sorted_bots[i + 1]
            break
    if clamped <= sorted_bots[0].elo:
        lower = upper = sorted_bots[0]
    elif clamped >= sorted_bots[-1].elo:
        lower = upper = sorted_bots[-1]

    if upper.elo == lower.elo:
        t = 0.0
    else:
        t = (clamped - lower.elo) / (upper.elo - lower.elo)

    persona = nearest_bot_for_elo(clamped)
    max_depth = round(lower.max_depth + t * (upper.max_depth - lower.max_depth))
    think_time = round(lower.think_time + t * (upper.think_time - lower.think_time), 2)
    noise_cp = round(lower.noise_cp + t * (upper.noise_cp - lower.noise_cp))
    blunder_rate = round(lower.blunder_rate + t * (upper.blunder_rate - lower.blunder_rate), 3)
    book_prob = round(lower.book_prob + t * (upper.book_prob - lower.book_prob), 2)
    aggression = round(lower.aggression + t * (upper.aggression - lower.aggression), 2)
    positional = round(lower.positional + t * (upper.positional - lower.positional), 2)

    return BotProfile(
        key="A",
        bot_id=f"adaptive_{persona.bot_id}",
        name=f"Adaptive ({persona.name})",
        elo=clamped,
        title=f"Adaptif · Tier {persona.name}",
        color_code=persona.color_code,
        max_depth=max(1, max_depth),
        think_time=max(0.05, think_time),
        use_quiescence=clamped >= 1050,
        use_pruning=clamped >= 2100,
        noise_cp=max(0, noise_cp),
        blunder_rate=max(0.0, blunder_rate),
        book_prob=book_prob,
        book_style=persona.book_style,
        aggression=aggression,
        positional=positional,
        dialogues=persona.dialogues,
    )


class AdaptiveController:


    def __init__(self, start_elo: int = 1000) -> None:
        self.elo: int = max(100, min(4000, start_elo))
        self.start_elo: int = self.elo
        self.accurate_streak: int = 0
        self.blunder_streak: int = 0
        self.last_delta: int = 0
        self.current_persona_id: str = nearest_bot_for_elo(self.elo).bot_id

    def profile(self) -> BotProfile:
        return make_adaptive_profile(self.elo)

    def update_after_player_move(self, cp_loss: int, ply: int) -> Tuple[int, Optional[BotProfile]]:


        if ply < 3:
            self.last_delta = 0
            return 0, None

        old_elo = self.elo
        if cp_loss <= 25:
            self.accurate_streak += 1
            self.blunder_streak = 0
            step = 10 + min(22, self.accurate_streak * 4)

            if self.elo < 1200:
                step = int(step * 1.45)
            self.elo = min(4000, self.elo + step)
        elif cp_loss <= 75:
            self.accurate_streak = max(0, self.accurate_streak - 1)
            self.blunder_streak = 0
            self.elo = min(4000, self.elo + 3)
        elif cp_loss <= 170:
            self.accurate_streak = 0
            self.blunder_streak += 1
            self.elo = max(100, self.elo - 12)
        else:

            self.accurate_streak = 0
            self.blunder_streak += 1
            drop = 22 + min(30, self.blunder_streak * 8)
            self.elo = max(100, self.elo - drop)

        self.last_delta = self.elo - old_elo
        new_persona = nearest_bot_for_elo(self.elo)
        tier_changed = None
        if new_persona.bot_id != self.current_persona_id:
            self.current_persona_id = new_persona.bot_id
            tier_changed = new_persona
        return self.last_delta, tier_changed

    def update_after_game(self, outcome: str) -> int:

        old = self.elo
        if outcome == "win":
            bump = 85 if self.elo < 1500 else (65 if self.elo < 2600 else 50)
            self.elo = min(4000, self.elo + bump)
        elif outcome == "loss":
            drop = 65 if self.elo > 1000 else 40
            self.elo = max(100, self.elo - drop)
        else:

            self.elo = min(4000, self.elo + 15)
        self.last_delta = self.elo - old
        self.current_persona_id = nearest_bot_for_elo(self.elo).bot_id
        return self.last_delta
