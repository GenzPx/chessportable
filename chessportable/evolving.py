from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .bots import BotProfile, make_adaptive_profile, nearest_bot_for_elo

@dataclass(frozen=True)
class MoveGrade:
    symbol: str
    label: str
    color: str
    cp_loss: int
    accuracy: float
    code: str = "good"

def move_accuracy_from_cp(cp_loss: int) -> float:
    loss = max(0, cp_loss)
    return round(max(0.0, min(100.0, 100.0 * math.exp(-0.0036 * loss))), 1)

def classify_move(
    cp_loss: int,
    is_book: bool = False,
    is_tactical_best: bool = False,
    missed_win: bool = False,
) -> MoveGrade:
    if is_book and cp_loss <= 35:
        return MoveGrade("📖", "Teori Buku", "\033[96m", cp_loss, 100.0, "book")
    acc = move_accuracy_from_cp(cp_loss)
    if cp_loss <= 8 and is_tactical_best:
        return MoveGrade("!!", "Brilian", "\033[1;96m", cp_loss, 100.0, "brilliant")
    if cp_loss <= 18:
        return MoveGrade("!", "Hebat", "\033[92m", cp_loss, acc, "great")
    if cp_loss <= 50:
        return MoveGrade("✓", "Bagus", "\033[32m", cp_loss, acc, "good")
    if missed_win and cp_loss >= 150:
        return MoveGrade("✕", "Terlewat", "\033[1;95m", cp_loss, acc, "miss")
    if cp_loss <= 115:
        return MoveGrade("?!", "Kurang Pas", "\033[93m", cp_loss, acc, "inaccuracy")
    if cp_loss <= 225:
        return MoveGrade("?", "Kesalahan", "\033[38;5;208m", cp_loss, acc, "mistake")
    return MoveGrade("??", "Blunder", "\033[1;91m", cp_loss, acc, "blunder")

def format_move_callout(grade: MoveGrade, san: str, best_san: str = "") -> str:
    R = "\033[0m"
    D = "\033[2m"
    alt = f" {D}(tadi lebih enak: {best_san}){R}" if best_san and best_san != san else ""
    if grade.code == "brilliant":
        return f"{grade.color}★★ BRILIAN!! ({san}) — Langkah luar biasa tajam!{R}"
    if grade.code == "book":
        return f"{grade.color}📖 Teori Pembukaan ({san}){R}"
    if grade.code == "great":
        return f"{grade.color}★ Hebat! ({san}){R}"
    if grade.code == "good":
        return f"{grade.color}✓ Bagus ({san}){R}"
    if grade.code == "inaccuracy":
        return f"{grade.color}?! Kurang pas ({san}){R}{alt}"
    if grade.code == "mistake":
        return f"{grade.color}⚠ Kesalahan! ({san}){R}{alt}"
    if grade.code == "miss":
        return f"{grade.color}✕ PELUANG TERLEWAT! ({san}){R}{alt}"
    return f"{grade.color}✖ BLUNDER!! ({san}) — Hati-hati, posisi langsung terancam!{R}{alt}"

def game_phase_name(ply: int) -> str:
    if ply <= 16:
        return "opening"
    if ply <= 44:
        return "middlegame"
    return "endgame"

@dataclass
class RecordedPlayerMove:
    ply: int
    san: str
    cp_loss: int
    grade: MoveGrade
    best_san: str
    phase: str
    is_capture: bool
    is_check: bool
    is_castle: bool
    is_promo: bool
    eval_white_cp: int = 0

@dataclass
class MatchTracker:
    player_moves: List[RecordedPlayerMove] = field(default_factory=list)
    ai_decisions: List[Tuple[str, str, int, int]] = field(default_factory=list)
    eval_history: List[int] = field(default_factory=list)
    opening_tags: List[str] = field(default_factory=list)
    opening_eco: Optional[str] = None
    opening_name: Optional[str] = None
    used_castle: bool = False
    used_promo: bool = False
    undo_count: int = 0
    memory_hits: int = 0

    def record_eval(self, white_cp: int) -> None:
        self.eval_history.append(max(-1200, min(1200, int(white_cp))))

    def record_player_move(
        self,
        ply: int,
        san: str,
        cp_loss: int,
        best_san: str,
        is_book: bool = False,
        is_capture: bool = False,
        is_check: bool = False,
        is_castle: bool = False,
        is_promo: bool = False,
        eval_white_cp: int = 0,
        player_eval_after: int = 0,
    ) -> MoveGrade:
        is_tactical_best = (is_capture or is_check or is_promo) and cp_loss <= 8 and ply >= 6
        best_possible = player_eval_after + cp_loss
        missed_win = best_possible >= 280 and player_eval_after < 140 and cp_loss >= 150
        grade = classify_move(
            cp_loss,
            is_book=is_book,
            is_tactical_best=is_tactical_best,
            missed_win=missed_win,
        )
        phase = game_phase_name(ply)
        self.player_moves.append(
            RecordedPlayerMove(
                ply=ply,
                san=san,
                cp_loss=cp_loss,
                grade=grade,
                best_san=best_san,
                phase=phase,
                is_capture=is_capture,
                is_check=is_check,
                is_castle=is_castle,
                is_promo=is_promo,
                eval_white_cp=eval_white_cp,
            )
        )
        self.record_eval(eval_white_cp)
        if len(self.opening_tags) < 3:
            self.opening_tags.append(san)
        if is_castle:
            self.used_castle = True
        if is_promo:
            self.used_promo = True
        return grade

    def record_ai_decision(self, zobrist_hex: str, uci: str, ply: int, eval_ai: int) -> None:
        self.ai_decisions.append((zobrist_hex, uci, ply, eval_ai))

    def pop_last_turn(self) -> None:
        if self.player_moves:
            self.player_moves.pop()
        if self.ai_decisions:
            self.ai_decisions.pop()
        if len(self.eval_history) >= 2:
            self.eval_history.pop()
            self.eval_history.pop()
        elif self.eval_history:
            self.eval_history.pop()
        self.undo_count += 1

    def accuracy_percent(self) -> float:
        if not self.player_moves:
            return 0.0
        vals = [m.grade.accuracy for m in self.player_moves]
        return round(sum(vals) / len(vals), 1)

    def average_cpl(self) -> float:
        if not self.player_moves:
            return 0.0
        return round(sum(min(600, m.cp_loss) for m in self.player_moves) / len(self.player_moves), 1)

    def grade_counts(self) -> Dict[str, int]:
        counts = {"!!": 0, "!": 0, "✓": 0, "?!": 0, "?": 0, "??": 0, "✕": 0, "📖": 0}
        for m in self.player_moves:
            if m.grade.symbol in counts:
                counts[m.grade.symbol] += 1
        return counts

    def phase_acpl(self) -> Dict[str, Optional[float]]:
        out: Dict[str, Optional[float]] = {"opening": None, "middlegame": None, "endgame": None}
        for ph in out:
            arr = [min(600, m.cp_loss) for m in self.player_moves if m.phase == ph]
            if arr:
                out[ph] = round(sum(arr) / len(arr), 1)
        return out

    def phase_letter_grades(self) -> Dict[str, str]:
        acpls = self.phase_acpl()
        out: Dict[str, str] = {}
        for ph, val in acpls.items():
            if val is None:
                out[ph] = "-"
            elif val <= 20:
                out[ph] = "S"
            elif val <= 45:
                out[ph] = "A"
            elif val <= 85:
                out[ph] = "B"
            elif val <= 150:
                out[ph] = "C"
            else:
                out[ph] = "D"
        return out

    def match_rank(self) -> Tuple[str, str, str]:
        acc = self.accuracy_percent()
        if not self.player_moves:
            return ("-", "Terlalu singkat", "\033[90m")
        if acc >= 94:
            return ("S+", "Kelas Master!", "\033[1;96m")
        if acc >= 86:
            return ("S", "Sangat Tajam", "\033[1;92m")
        if acc >= 76:
            return ("A", "Solid & Rapi", "\033[92m")
        if acc >= 64:
            return ("B", "Cukup Bagus", "\033[93m")
        if acc >= 50:
            return ("C", "Masih Bisa Lebih Rapi", "\033[38;5;208m")
        return ("D", "Banyak Pelajaran Baru", "\033[91m")

    def match_story(self, outcome: str) -> str:
        counts = self.grade_counts()
        acc = self.accuracy_percent()
        if not self.player_moves:
            return "Pertandingan berhenti terlalu cepat untuk dibaca ceritanya."
        if outcome == "win":
            if counts["??"] == 0 and acc >= 88:
                return "Permainan yang super bersih! Lawan sama sekali tidak diberi celah untuk balik melawan."
            if counts["!!"] >= 1:
                return "Kemenangan penuh gaya — momen brilianmu benar-benar membalikkan papan!"
            if counts["??"] >= 1:
                return "Sempat tegang gara-gara blunder, tapi mentalmu kuat buat membalikkan keadaan!"
            return "Kemenangan yang rapi dan konsisten dari awal sampai akhir."
        if outcome == "draw":
            return "Duel sengit yang berimbang! Kedua sisi saling mengunci sampai titik akhir."
        if counts["??"] >= 2:
            return "Beberapa blunder kecil jadi penentu hari ini — pelan-pelan cek ancaman lawan sebelum melangkah."
        if counts["✕"] >= 1:
            return "Sebenarnya kamu sempat punya peluang emas! Cek [V] Review buat lihat langkah kuncinya."
        if acc >= 78:
            return "Mainmu sebenarnya udah rapi banget, cuma lawan sedikit lebih tajam di momen penting."
        return "Pertandingan yang bagus buat pemanasan — coba lihat [V] Review biar makin tajam di rematch!"

    def biggest_blunder(self) -> Optional[RecordedPlayerMove]:
        blunders = [m for m in self.player_moves if m.cp_loss >= 115]
        if not blunders:
            return None
        return max(blunders, key=lambda m: m.cp_loss)

    def best_moment(self) -> Optional[RecordedPlayerMove]:
        best = [m for m in self.player_moves if m.grade.symbol in ("!!", "!") and m.ply >= 6]
        if not best:
            return None
        return max(best, key=lambda m: (m.grade.symbol == "!!", m.is_check or m.is_capture, m.ply))

    def estimated_perf_elo(self, opponent_elo: int, outcome: str) -> int:
        acc = self.accuracy_percent()
        outcome_bonus = 240 if outcome == "win" else (-210 if outcome == "loss" else 15)
        acc_elo = int(200 + (acc / 100.0) ** 1.45 * 2900)
        blended = int(0.55 * (opponent_elo + outcome_bonus) + 0.45 * acc_elo)
        return max(150, min(3800, blended))


DEFAULT_DNA: Dict[str, Any] = {
    "games_analyzed": 0,
    "aggression": 50.0,
    "positional": 50.0,
    "tactical": 50.0,
    "avg_accuracy": 65.0,
    "opening_acpl": 70.0,
    "middlegame_acpl": 90.0,
    "endgame_acpl": 95.0,
    "castle_rate": 50.0,
    "favorite_openings": {},
}

DEFAULT_BRAIN: Dict[str, Any] = {
    "generation": 1,
    "total_lessons": 0,
    "avoid_memory": {},
    "trap_memory": {},
    "last_counter_trait": "Adaptive Mirror",
}

class PlayerDNA:

    def __init__(self, raw: Optional[Dict[str, Any]] = None) -> None:
        data = dict(DEFAULT_DNA)
        if isinstance(raw, dict):
            data.update(raw)
        self.games_analyzed: int = int(data.get("games_analyzed", 0))
        self.aggression: float = float(data.get("aggression", 50.0))
        self.positional: float = float(data.get("positional", 50.0))
        self.tactical: float = float(data.get("tactical", 50.0))
        self.avg_accuracy: float = float(data.get("avg_accuracy", 65.0))
        self.opening_acpl: float = float(data.get("opening_acpl", 70.0))
        self.middlegame_acpl: float = float(data.get("middlegame_acpl", 90.0))
        self.endgame_acpl: float = float(data.get("endgame_acpl", 95.0))
        self.castle_rate: float = float(data.get("castle_rate", 50.0))
        fav = data.get("favorite_openings")
        self.favorite_openings: Dict[str, int] = dict(fav) if isinstance(fav, dict) else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "games_analyzed": self.games_analyzed,
            "aggression": round(self.aggression, 1),
            "positional": round(self.positional, 1),
            "tactical": round(self.tactical, 1),
            "avg_accuracy": round(self.avg_accuracy, 1),
            "opening_acpl": round(self.opening_acpl, 1),
            "middlegame_acpl": round(self.middlegame_acpl, 1),
            "endgame_acpl": round(self.endgame_acpl, 1),
            "castle_rate": round(self.castle_rate, 1),
            "favorite_openings": self.favorite_openings,
        }

    def ingest_match(self, tracker: MatchTracker) -> None:
        if len(tracker.player_moves) < 3:
            return
        n = len(tracker.player_moves)

        w = 0.45 if self.games_analyzed < 4 else 0.25

        checks = sum(1 for m in tracker.player_moves if m.is_check)
        captures = sum(1 for m in tracker.player_moves if m.is_capture)
        acc = tracker.accuracy_percent()
        acpl = tracker.average_cpl()

        game_agg = min(100.0, 22.0 + (checks / n) * 140.0 + (captures / n) * 85.0)
        game_tac = min(100.0, max(5.0, acc * 0.95 + max(0.0, 40.0 - acpl * 0.25) * 0.25))
        quiet_good = sum(
            1 for m in tracker.player_moves if not m.is_capture and not m.is_check and m.cp_loss <= 45
        )
        game_pos = min(
            100.0,
            25.0 + (30.0 if tracker.used_castle else 0.0) + (quiet_good / n) * 58.0,
        )

        self.aggression = (1 - w) * self.aggression + w * game_agg
        self.tactical = (1 - w) * self.tactical + w * game_tac
        self.positional = (1 - w) * self.positional + w * game_pos
        self.avg_accuracy = (1 - w) * self.avg_accuracy + w * acc
        self.castle_rate = (1 - w) * self.castle_rate + w * (100.0 if tracker.used_castle else 0.0)

        ph = tracker.phase_acpl()
        if ph["opening"] is not None:
            self.opening_acpl = (1 - w) * self.opening_acpl + w * ph["opening"]
        if ph["middlegame"] is not None:
            self.middlegame_acpl = (1 - w) * self.middlegame_acpl + w * ph["middlegame"]
        if ph["endgame"] is not None:
            self.endgame_acpl = (1 - w) * self.endgame_acpl + w * ph["endgame"]

        if tracker.opening_name:
            sig = f"{tracker.opening_eco} {tracker.opening_name}" if tracker.opening_eco else tracker.opening_name
            self.favorite_openings[sig] = self.favorite_openings.get(sig, 0) + 1
        elif len(tracker.opening_tags) >= 2:
            sig = " · ".join(tracker.opening_tags[:3])
            self.favorite_openings[sig] = self.favorite_openings.get(sig, 0) + 1

        if len(self.favorite_openings) > 12:
            top_items = sorted(self.favorite_openings.items(), key=lambda kv: kv[1], reverse=True)[:12]
            self.favorite_openings = dict(top_items)

        self.games_analyzed += 1

    def archetype(self) -> Tuple[str, str]:
        if self.games_analyzed == 0:
            return ("Penantang Baru", "Mainkan 1+ pertandingan agar gaya mainmu mulai terbaca.")
        if self.aggression >= 62 and self.tactical >= 65:
            return ("Penyerang Tajam", "Agresif, berani membuka posisi, dan mematikan di serangan raja.")
        if self.aggression >= 62:
            return ("Pemburu Serangan", "Suka tempo cepat, penuh tekanan & taktik tak terduga.")
        if self.positional >= 65 and self.tactical >= 68:
            return ("Arsitek Papan", "Rapi, sabar, jarang blunder, dan kuat mengendalikan ruang.")
        if self.positional >= 62:
            return ("Benteng Kokoh", "Solid, tenang membangun posisi & susah ditembus lawan.")
        if self.tactical >= 72:
            return ("Mata Elang", "Teliti banget dan cepat menghukum kesalahan lawan.")
        return ("Pemain Serba Bisa", "Gaya seimbang — nyaman menyerang maupun bertahan.")

    def weakest_phase(self) -> str:
        phases = {
            "Pembukaan": self.opening_acpl,
            "Tengah": self.middlegame_acpl,
            "Akhir": self.endgame_acpl,
        }
        return max(phases, key=lambda k: phases[k])

    def strongest_phase(self) -> str:
        phases = {
            "Pembukaan": self.opening_acpl,
            "Tengah": self.middlegame_acpl,
            "Akhir": self.endgame_acpl,
        }
        return min(phases, key=lambda k: phases[k])

    def top_openings(self, limit: int = 3) -> List[Tuple[str, int]]:
        return sorted(self.favorite_openings.items(), key=lambda kv: kv[1], reverse=True)[:limit]

class EvolvingBrain:


    MAX_POSITIONS = 400

    def __init__(self, raw: Optional[Dict[str, Any]] = None) -> None:
        data = dict(DEFAULT_BRAIN)
        if isinstance(raw, dict):
            data.update(raw)
        self.generation: int = max(1, int(data.get("generation", 1)))
        self.total_lessons: int = max(0, int(data.get("total_lessons", 0)))
        am = data.get("avoid_memory")
        tm = data.get("trap_memory")
        self.avoid_memory: Dict[str, Dict[str, int]] = (
            {k: dict(v) for k, v in am.items() if isinstance(v, dict)} if isinstance(am, dict) else {}
        )
        self.trap_memory: Dict[str, Dict[str, int]] = (
            {k: dict(v) for k, v in tm.items() if isinstance(v, dict)} if isinstance(tm, dict) else {}
        )
        self.last_counter_trait: str = str(data.get("last_counter_trait", "Adaptive Mirror"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "total_lessons": self.total_lessons,
            "avoid_memory": self.avoid_memory,
            "trap_memory": self.trap_memory,
            "last_counter_trait": self.last_counter_trait,
        }

    def stage_info(self) -> Tuple[str, str]:
        g = self.generation
        if g <= 2:
            return ("Baru Kenal", "Baru mulai mengamati cara mainmu")
        if g <= 5:
            return ("Mulai Hafal", "Mulai ingat pola pembukaan & jebakanmu")
        if g <= 10:
            return ("Cerdik", "Aktif membaca kelemahan dan kebiasaanmu")
        if g <= 18:
            return ("Lihai", "Sangat paham ritme dan gaya permainanmu")
        if g <= 30:
            return ("Rival Sejati", "Hafal hampir semua kebiasaanmu di papan")
        return ("Master Rival", "Tantangan penuh yang dibuat khusus untukmu")

    def compute_counter_strategy(self, dna: PlayerDNA) -> Tuple[str, float, float, Optional[str]]:
        if dna.games_analyzed == 0:
            self.last_counter_trait = "Menyesuaikan Gaya"
            return ("Menyesuaikan Gaya", 1.0, 1.0, None)

        weak = dna.weakest_phase()
        if dna.aggression >= 62:
            self.last_counter_trait = "Pertahanan Balik"
            return ("Pertahanan Balik", 1.08, 1.24, "solid")
        if dna.positional >= 64:
            self.last_counter_trait = "Pemecah Posisi"
            return ("Pemecah Posisi", 1.32, 0.96, "sharp")
        if weak == "Pembukaan" and dna.opening_acpl >= 65:
            self.last_counter_trait = "Penjebak Pembukaan"
            return ("Penjebak Pembukaan", 1.18, 1.08, "tricky")
        if weak == "Akhir" and dna.endgame_acpl >= 80:
            self.last_counter_trait = "Penguasa Akhir"
            return ("Penguasa Akhir", 0.94, 1.28, "master")
        self.last_counter_trait = "Fleksibel"
        return ("Fleksibel", 1.15, 1.12, None)

    def move_bias_map(self, zobrist_hex: str) -> Dict[str, int]:

        biases: Dict[str, int] = {}
        for uci, count in self.avoid_memory.get(zobrist_hex, {}).items():
            biases[uci] = biases.get(uci, 0) - min(360, 165 * count)
        for uci, count in self.trap_memory.get(zobrist_hex, {}).items():
            biases[uci] = biases.get(uci, 0) + min(140, 55 * count)
        return biases

    def avoided_moves(self, zobrist_hex: str) -> set:
        return set(self.avoid_memory.get(zobrist_hex, {}).keys())

    def learn_from_match(self, tracker: MatchTracker, outcome_from_player: str) -> int:

        learned = 0

        decisions = tracker.ai_decisions
        if outcome_from_player == "win" and decisions:

            for i in range(len(decisions) - 1):
                z_hex, uci, ply, ev_before = decisions[i]
                _, _, _, ev_next = decisions[i + 1]
                if ply <= 26 and (ev_before - ev_next) >= 130:
                    slot = self.avoid_memory.setdefault(z_hex, {})
                    slot[uci] = min(4, slot.get(uci, 0) + 1)
                    learned += 1

            for z_hex, uci, ply, _ in decisions[:3]:
                if ply <= 10:
                    slot = self.avoid_memory.setdefault(z_hex, {})
                    slot[uci] = min(3, slot.get(uci, 0) + 1)
                    learned += 1


        player_by_ply = {m.ply: m for m in tracker.player_moves}
        for z_hex, uci, ai_ply, _ in decisions:
            reply = player_by_ply.get(ai_ply + 1)
            if reply is not None and reply.cp_loss >= 170 and ai_ply <= 30:
                slot = self.trap_memory.setdefault(z_hex, {})
                slot[uci] = min(4, slot.get(uci, 0) + 1)
                learned += 1

        for mem in (self.avoid_memory, self.trap_memory):
            while len(mem) > self.MAX_POSITIONS:
                oldest = next(iter(mem))
                del mem[oldest]

        self.generation += 1
        self.total_lessons += learned
        return learned

class EvolvingAdaptiveController:

    def __init__(
        self,
        start_elo: int,
        dna: PlayerDNA,
        brain: EvolvingBrain,
        anchor_bot: Optional[BotProfile] = None,
    ) -> None:
        self.elo: int = max(100, min(4000, int(start_elo)))
        self.start_elo: int = self.elo
        self.dna: PlayerDNA = dna
        self.brain: EvolvingBrain = brain
        self.anchor_bot: Optional[BotProfile] = anchor_bot
        self.accurate_streak: int = 0
        self.blunder_streak: int = 0
        self.last_delta: int = 0
        self.current_persona_id: str = (
            anchor_bot.bot_id if anchor_bot is not None else nearest_bot_for_elo(self.elo).bot_id
        )
        self.counter_trait, self.agg_mult, self.pos_mult, self.override_book = (
            self.brain.compute_counter_strategy(self.dna)
        )

    @property
    def is_per_bot(self) -> bool:
        return self.anchor_bot is not None

    def profile(self) -> BotProfile:
        base = make_adaptive_profile(self.elo)
        stage, _ = self.brain.stage_info()

        if self.anchor_bot is not None:


            persona = self.anchor_bot
            blended_agg = (base.aggression * 0.6 + persona.aggression * 0.4) * self.agg_mult
            blended_pos = (base.positional * 0.6 + persona.positional * 0.4) * self.pos_mult
            mutated_agg = round(max(0.65, min(1.70, blended_agg)), 2)
            mutated_pos = round(max(0.65, min(1.70, blended_pos)), 2)
            book_style = self.override_book or persona.book_style
            return BotProfile(
                key=f"A {persona.key}",
                bot_id=f"adaptive_{persona.bot_id}",
                name=f"Adaptif · {persona.name}",
                elo=self.elo,
                title=f"{stage} · {self.counter_trait} (Asal Elo {persona.elo})",
                color_code=persona.color_code,
                max_depth=base.max_depth,
                think_time=base.think_time,
                use_quiescence=base.use_quiescence,
                use_pruning=base.use_pruning,
                noise_cp=base.noise_cp,
                blunder_rate=base.blunder_rate,
                book_prob=base.book_prob,
                book_style=book_style,
                aggression=mutated_agg,
                positional=mutated_pos,
                dialogues=persona.dialogues,
            )


        mutated_agg = round(max(0.65, min(1.65, base.aggression * self.agg_mult)), 2)
        mutated_pos = round(max(0.65, min(1.65, base.positional * self.pos_mult)), 2)
        book_style = self.override_book or base.book_style
        persona = nearest_bot_for_elo(self.elo)
        return BotProfile(
            key="A",
            bot_id=f"adaptive_{persona.bot_id}",
            name=f"Adaptif ({persona.name})",
            elo=self.elo,
            title=f"{stage} · {self.counter_trait}",
            color_code=persona.color_code,
            max_depth=base.max_depth,
            think_time=base.think_time,
            use_quiescence=base.use_quiescence,
            use_pruning=base.use_pruning,
            noise_cp=base.noise_cp,
            blunder_rate=base.blunder_rate,
            book_prob=base.book_prob,
            book_style=book_style,
            aggression=mutated_agg,
            positional=mutated_pos,
            dialogues=persona.dialogues,
        )

    def update_after_player_move(self, cp_loss: int, ply: int) -> Tuple[int, Optional[BotProfile]]:
        if ply < 3:
            self.last_delta = 0
            return 0, None

        old_elo = self.elo
        if cp_loss <= 22:
            self.accurate_streak += 1
            self.blunder_streak = 0
            step = 12 + min(26, self.accurate_streak * 4)
            if self.elo < 1200:
                step = int(step * 1.45)
            self.elo = min(4000, self.elo + step)
        elif cp_loss <= 65:
            self.accurate_streak = max(0, self.accurate_streak - 1)
            self.blunder_streak = 0
            self.elo = min(4000, self.elo + 4)
        elif cp_loss <= 165:
            self.accurate_streak = 0
            self.blunder_streak += 1
            self.elo = max(100, self.elo - 12)
        else:
            self.accurate_streak = 0
            self.blunder_streak += 1
            drop = 24 + min(34, self.blunder_streak * 8)
            self.elo = max(100, self.elo - drop)

        self.last_delta = self.elo - old_elo

        if self.anchor_bot is not None:
            return self.last_delta, None

        new_persona = nearest_bot_for_elo(self.elo)
        tier_changed = None
        if new_persona.bot_id != self.current_persona_id:
            self.current_persona_id = new_persona.bot_id
            tier_changed = new_persona
        return self.last_delta, tier_changed

    def update_after_game(self, outcome: str, match_accuracy: float = 65.0) -> int:
        old = self.elo
        acc_bonus = int((match_accuracy - 60.0) * 0.6)
        if outcome == "win":
            base_bump = 90 if self.elo < 1500 else (70 if self.elo < 2600 else 55)
            self.elo = min(4000, self.elo + max(30, base_bump + max(0, acc_bonus)))
        elif outcome == "loss":
            base_drop = 65 if self.elo > 1000 else 40
            self.elo = max(100, self.elo - max(15, base_drop - max(0, acc_bonus // 2)))
        else:
            self.elo = min(4000, max(100, self.elo + 18 + acc_bonus // 2))

        self.last_delta = self.elo - old
        if self.anchor_bot is None:
            self.current_persona_id = nearest_bot_for_elo(self.elo).bot_id
        return self.last_delta
