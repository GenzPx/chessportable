from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from chessportable.ai import ChessAI
from chessportable.board import (
    BLACK,
    Board,
    IllegalMoveError,
    PromotionRequiredError,
    START_FEN,
    WHITE,
    move_to_uci,
)
from chessportable.bots import BOT_BY_KEY, BOTS, CORE_BOTS, EXTRA_BOTS
from chessportable.cli import _parse_menu_selection
from chessportable.dialogue import react_to_bot_move, react_to_player_move
from chessportable.evolving import (
    EvolvingAdaptiveController,
    EvolvingBrain,
    MatchTracker,
    PlayerDNA,
    classify_move,
    format_move_callout,
)
from chessportable.openings import OPENING_INDEX, detect_opening
from chessportable.puzzles import PUZZLES
from chessportable.storage import (
    ACHIEVEMENTS,
    check_match_achievements,
    export_pgn_file,
    get_bot_adaptive_state,
    get_bot_brain,
    is_bot_defeated,
    list_saves,
    load_game,
    load_profile,
    record_bot_result,
    record_per_bot_adaptive_result,
    reset_bot_adaptive,
    save_game,
    set_bot_brain,
)
from chessportable.themes import THEMES, get_theme
from chessportable.ui import (
    render_adaptive_roster,
    render_eval_graph,
    render_extra_bots_menu,
    render_main_menu,
    render_match_analysis,
    render_move_review,
)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


class TestBoardRules(unittest.TestCase):
    def test_perft_and_zobrist_consistency(self) -> None:
        cases = [
            (START_FEN, 3, 8902),
            ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 3, 97862),
            ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 4, 43238),
            ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 3, 62379),
        ]
        for fen, depth, expected in cases:
            b = Board(fen)
            self.assertEqual(b.perft(depth), expected, f"Perft failed for {fen}")
            self.assertEqual(b.fen(), fen)
            self.assertEqual(b.zobrist, b._compute_zobrist())

        kb = Board("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
        for mv in kb.legal_moves():
            self.assertTrue(kb.make_move(mv, record_san=True))
            self.assertEqual(kb.zobrist, kb._compute_zobrist())
            kb.unmake_move(pop_history=True)
            self.assertEqual(kb.zobrist, kb._compute_zobrist())

    def test_san_coordinate_and_pgn_with_eco(self) -> None:
        b = Board()
        for txt, expected_uci in [
            ("E4", "e2e4"),
            ("e7e5", "e7e5"),
            ("nf3", "g1f3"),
            ("b8 c6", "b8c6"),
            ("Bb5", "f1b5"),
            ("a6", "a7a6"),
            ("Ba4", "b5a4"),
            ("Nf6", "g8f6"),
            ("O-O", "e1g1"),
        ]:
            mv = b.parse_move(txt)
            self.assertEqual(move_to_uci(mv), expected_uci)
            self.assertTrue(b.make_move(mv, record_san=True))

        pgn = b.to_pgn("Kamu", "Jim", "1500", "4000", result="*", eco="C78", opening="Ruy Lopez: Morphy Defense")
        self.assertIn('[White "Kamu"]', pgn)
        self.assertIn('[ECO "C78"]', pgn)
        self.assertIn('[Opening "Ruy Lopez: Morphy Defense"]', pgn)
        self.assertIn("1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O *", pgn)

    def test_illegal_moves_rejected(self) -> None:
        b = Board()
        with self.assertRaises(IllegalMoveError):
            b.parse_move("e5")
        with self.assertRaises(IllegalMoveError):
            b.parse_move("Z99")
        with self.assertRaises(IllegalMoveError):
            b.parse_move("O-O")

        pinned = Board("4r2k/8/8/8/8/8/4N3/4K3 w - - 0 1")
        with self.assertRaises(IllegalMoveError) as ctx:
            pinned.parse_move("Nf4")
        self.assertIn("skak", str(ctx.exception).lower())

        ambig = Board("4k3/8/8/8/8/8/8/1N3NK1 w - - 0 1")
        with self.assertRaises(IllegalMoveError) as ctx2:
            ambig.parse_move("Nd2")
        self.assertIn("ambigu", str(ctx2.exception).lower())
        self.assertEqual(move_to_uci(ambig.parse_move("Nbd2")), "b1d2")

    def test_promotion_and_endings(self) -> None:
        b = Board("8/4P2k/8/8/8/8/8/4K3 w - - 0 1")
        with self.assertRaises(PromotionRequiredError) as ctx:
            b.parse_move("e8")
        self.assertEqual(len(ctx.exception.moves), 4)
        self.assertEqual(move_to_uci(b.parse_move("e8=Q")), "e7e8q")

        fm = Board()
        for m in ("f3", "e5", "g4", "Qh4"):
            fm.make_move(fm.parse_move(m), record_san=True)
        self.assertEqual(fm.game_result()[0], "0-1")

        st = Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertEqual(st.game_result()[0], "1/2-1/2")

class TestOpeningsCoachAndPV(unittest.TestCase):
    def test_eco_opening_detector(self) -> None:
        self.assertGreaterEqual(len(OPENING_INDEX), 125)

        b1 = Board()
        for m in ("e4", "e5", "Nf3", "Nc6", "Bc4"):
            b1.make_move(b1.parse_move(m), record_san=True)
        hit1 = detect_opening(b1)
        self.assertIsNotNone(hit1)
        self.assertEqual(hit1[0], "C50")
        self.assertIn("Italian", hit1[1])

        b2 = Board()
        for m in ("e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"):
            b2.make_move(b2.parse_move(m), record_san=True)
        hit2 = detect_opening(b2)
        self.assertIsNotNone(hit2)
        self.assertEqual(hit2[0], "B90")
        self.assertIn("Najdorf", hit2[1])

        b3 = Board()
        for m in ("d4", "d5", "c4", "e6"):
            b3.make_move(b3.parse_move(m), record_san=True)
        hit3 = detect_opening(b3)
        self.assertIsNotNone(hit3)
        self.assertIn("Queen's Gambit", hit3[1])

        b4 = Board()
        for m in ("e4", "e5", "Ke2"):
            b4.make_move(b4.parse_move(m), record_san=True)
        hit4 = detect_opening(b4)
        self.assertIsNotNone(hit4)
        self.assertIn("Bongcloud", hit4[1])

        b5 = Board()
        for m in ("e4", "d5", "exd5", "Qxd5"):
            b5.make_move(b5.parse_move(m), record_san=True)
        hit5 = detect_opening(b5)
        self.assertIsNotNone(hit5)
        self.assertIn("Scandinavian", hit5[1])

    def test_pv_tactical_coach_and_connected_rooks(self) -> None:
        ai = ChessAI()


        b = Board("4k3/8/8/7r/1b6/2N5/8/3Q2K1 w - - 0 1")
        adv = ai.coach_advice(b)
        self.assertTrue(adv["best_move"])
        self.assertGreaterEqual(len(adv["pv"]), 1)
        tips_joined = " ".join(adv["tips"]).lower()
        self.assertIn("tidak terjaga", tips_joined)
        self.assertIn("menggantung", tips_joined)


        b_conn = Board("4k3/8/8/8/8/8/8/R2R2K1 w - - 0 1")
        b_blocked = Board("4k3/8/8/8/8/8/8/R1NR2K1 w - - 0 1")
        self.assertIsInstance(ai.evaluate(b_conn), int)
        self.assertIsInstance(ai.evaluate(b_blocked), int)

class TestAIAndEvolving(unittest.TestCase):
    def test_all_20_bots_and_tactics(self) -> None:
        self.assertEqual(len(CORE_BOTS), 10)
        self.assertEqual(len(EXTRA_BOTS), 10)
        self.assertEqual(len(BOTS), 20)
        self.assertEqual(len(BOT_BY_KEY), 20)
        ai = ChessAI()

        m1 = Board("r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
        res = ai.choose_move(m1, BOT_BY_KEY["4"])
        self.assertEqual(m1.move_to_san(res.move), "Qxf7#")

        m2 = Board("r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0")
        res2 = ai.choose_move(m2, BOT_BY_KEY["0"])
        self.assertEqual(m2.move_to_san(res2.move), "Nf6+")

        mid = Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
        fen0 = mid.fen()
        for bot in BOTS:
            r = ai.choose_move(mid, bot, time_override=0.10)
            self.assertIn(r.move, mid.legal_moves())
            self.assertEqual(mid.fen(), fen0)

    def test_living_dialogues_and_eval_graph(self) -> None:
        bot = BOT_BY_KEY["4"]
        line = react_to_player_move(
            bot=bot, san="e4", ply=1, captured_piece=0, is_ep=False,
            is_castle_k=False, is_castle_q=False, promo_piece=0, gave_check=False,
            grade_code="book", opening_name="", opening_just_changed=False,
            from_arc=False, pieces_left=32,
        )
        self.assertIsNotNone(line)
        self.assertIn("e4", line.lower())

        line_it = react_to_player_move(
            bot=BOT_BY_KEY["13"], san="Bc4", ply=5, captured_piece=0, is_ep=False,
            is_castle_k=False, is_castle_q=False, promo_piece=0, gave_check=False,
            grade_code="book", opening_name="Italian Game", opening_just_changed=True,
            from_arc=False, pieces_left=32,
        )
        self.assertIsNotNone(line_it)

        line_bot = react_to_bot_move(
            bot=BOT_BY_KEY["19"], san="Qxd4", ply=12, captured_piece=5, is_ep=False,
            gave_check=False, memory_note=None, opening_name="",
            opening_just_changed=False, pieces_left=26,
        )
        self.assertIsNotNone(line_bot)

        miss_g = classify_move(175, is_book=False, missed_win=True)
        self.assertEqual(miss_g.code, "miss")
        self.assertEqual(miss_g.symbol, "✕")

        callout = strip_ansi(format_move_callout(classify_move(4, is_tactical_best=True), "Qxf7+", "Qxf7+"))
        self.assertIn("BRILIAN", callout)

        g_lines = render_eval_graph([20, 40, 120, 310, 80, -90, -290])
        self.assertGreaterEqual(len(g_lines), 6)

    def test_per_bot_adaptive_all_20_bots_and_brain(self) -> None:
        prof = {"adaptive_elo": 1000}

        for key, bot in BOT_BY_KEY.items():
            self.assertEqual(_parse_menu_selection(f"A {key}", prof), ("adaptive_bot", (bot, False)))
            self.assertEqual(_parse_menu_selection(f"a{key}", prof), ("adaptive_bot", (bot, False)))
            self.assertEqual(_parse_menu_selection(f"A {key} fresh", prof), ("adaptive_bot", (bot, True)))

        self.assertEqual(_parse_menu_selection("B", prof), ("extra_bots", None))
        self.assertEqual(_parse_menu_selection("13", prof), ("bot", BOT_BY_KEY["13"]))
        self.assertEqual(_parse_menu_selection("noctis", prof), ("bot", BOT_BY_KEY["19"]))
        self.assertEqual(_parse_menu_selection("A", prof), ("adaptive_global", 1000))
        self.assertEqual(_parse_menu_selection("A 1750", prof), ("adaptive_global", 1750))
        self.assertEqual(_parse_menu_selection("A list", prof), ("adaptive_roster", None))
        self.assertEqual(_parse_menu_selection("G", prof), ("gauntlet", None))
        self.assertEqual(_parse_menu_selection("P", prof), ("puzzles", None))
        self.assertEqual(_parse_menu_selection("2P", prof), ("pvp", None))
        self.assertEqual(_parse_menu_selection("D", prof), ("dna", None))

        dna = PlayerDNA()
        brain_mittens = EvolvingBrain()
        mittens = BOT_BY_KEY["4"]
        ctrl = EvolvingAdaptiveController(mittens.elo, dna, brain_mittens, anchor_bot=mittens)
        self.assertTrue(ctrl.is_per_bot)
        self.assertEqual(ctrl.profile().name, "Adaptif · Mittens")
        d_up, tier_chg = ctrl.update_after_player_move(cp_loss=5, ply=6)
        self.assertGreater(d_up, 0)
        self.assertIsNone(tier_chg)
        self.assertEqual(ctrl.profile().name, "Adaptif · Mittens")

        ai = ChessAI()
        brain = EvolvingBrain()
        tracker = MatchTracker()
        tracker.opening_eco = "C50"
        tracker.opening_name = "Italian Game"
        b = Board("r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 7")
        zhex = f"{b.zobrist:016x}"
        bot = BOT_BY_KEY["6"]
        natural_res = ai.choose_move(b, bot, time_override=0.25)
        natural_uci = move_to_uci(natural_res.move)

        tracker.record_ai_decision(zhex, natural_uci, ply=6, eval_ai=30)
        tracker.record_ai_decision("0000000000000001", "a7a6", ply=8, eval_ai=-210)
        for i in range(6):
            tracker.record_player_move(
                ply=2 * i + 1, san="Nf3", cp_loss=10, best_san="Nf3",
                is_capture=(i % 2 == 0), is_check=(i == 4), is_castle=(i == 2),
                eval_white_cp=40 + i * 35, player_eval_after=40 + i * 35,
            )
        dna.ingest_match(tracker)
        self.assertIn("C50 Italian Game", dna.favorite_openings)
        lessons = brain.learn_from_match(tracker, outcome_from_player="win")
        self.assertGreater(lessons, 0)
        self.assertEqual(brain.generation, 2)
        self.assertIn(natural_uci, brain.avoided_moves(zhex))

        evolved_res = ai.choose_move(b, bot, time_override=0.25, brain=brain)
        self.assertIn(evolved_res.move, b.legal_moves())
        if move_to_uci(evolved_res.move) != natural_uci:
            self.assertEqual(evolved_res.memory_note, "avoided")

        rev = strip_ansi(render_move_review(tracker))
        self.assertIn("CATATAN LANGKAH PER LANGKAH", rev)
        self.assertIn("Nf3", rev)
        anl = strip_ansi(render_match_analysis(tracker, 2400, "win", lessons, brain.generation))
        self.assertIn("Peringkat", anl)
        self.assertIn("Grafik Momentum", anl)

    def test_move_grading_and_all_20_puzzles(self) -> None:
        self.assertEqual(classify_move(0, is_book=True).symbol, "📖")
        self.assertEqual(classify_move(4, is_tactical_best=True).symbol, "!!")
        self.assertEqual(classify_move(10).symbol, "!")
        self.assertEqual(classify_move(300).symbol, "??")

        self.assertEqual(len(PUZZLES), 20)
        for p in PUZZLES:
            b = Board(p.fen)
            for uci in p.solution:
                legal = {move_to_uci(m): m for m in b.legal_moves()}
                self.assertIn(uci, legal, f"Puzzle {p.puzzle_id} illegal move {uci}")
                b.make_move(legal[uci], record_san=True)
            if p.must_mate:
                self.assertTrue(b.is_checkmate(), f"Puzzle {p.puzzle_id} did not checkmate")

class TestStorageThemesAndCLI(unittest.TestCase):
    def test_themes_storage_per_bot_adaptive_and_pgn(self) -> None:
        self.assertEqual(len(THEMES), 6)
        self.assertEqual(get_theme("neon").theme_id, "neon")

        with tempfile.TemporaryDirectory() as tmp:
            old_env = os.environ.get("CHESSPORTABLE_HOME")
            os.environ["CHESSPORTABLE_HOME"] = tmp
            try:
                prof = load_profile()

                b_m = get_bot_brain(prof, "mittens", 1300)
                b_m.generation = 4
                set_bot_brain(prof, "mittens", 1300, b_m)
                record_per_bot_adaptive_result(prof, "mittens", 1300, "win", 1420)

                prof2 = load_profile()
                self.assertEqual(get_bot_adaptive_state(prof2, "mittens", 1300)["elo"], 1420)
                self.assertEqual(get_bot_brain(prof2, "mittens", 1300).generation, 4)

                self.assertEqual(get_bot_adaptive_state(prof2, "jim", 4000)["elo"], 4000)
                self.assertEqual(get_bot_brain(prof2, "jim", 4000).generation, 1)

                menu_txt = strip_ansi(render_main_menu(prof2))
                self.assertIn("A 0-19", menu_txt)
                self.assertIn("Adaptif 1420", menu_txt)
                extra_txt = strip_ansi(render_extra_bots_menu(prof2))
                self.assertIn("Budi", extra_txt)
                self.assertIn("Noctis", extra_txt)
                roster_txt = strip_ansi(render_adaptive_roster(prof2))
                self.assertIn("A 0", roster_txt)
                self.assertIn("A 19", roster_txt)


                reset_bot_adaptive(prof2, "mittens", 1300)
                self.assertEqual(get_bot_adaptive_state(load_profile(), "mittens", 1300)["elo"], 1300)

                record_bot_result(prof2, "mittens", "win")
                self.assertTrue(is_bot_defeated(load_profile(), "mittens"))

                tr = MatchTracker()
                for i in range(8):
                    tr.record_player_move(i + 1, "e4", 5, "e4", is_castle=(i == 4))
                new_achs = check_match_achievements(
                    prof2, "win", "mittens", 1300, False, 1, tr, total_plies=16
                )
                self.assertIn("first_blood", new_achs)
                self.assertIn("cat_tamer", new_achs)
                self.assertEqual(len(ACHIEVEMENTS), 12)

                b = Board()
                for m in ("e4", "e5", "Nf3", "Nc6", "Bc4"):
                    b.make_move(b.parse_move(m), record_san=True)
                save_game(
                    "slot_a4", b, WHITE, "4", "Adaptive·Mittens", 1420,
                    True, 1420, 1300, adaptive_anchor_key="4"
                )
                self.assertEqual(len(list_saves()), 1)
                loaded_b, meta = load_game("slot_a4")
                self.assertEqual(loaded_b.fen(), b.fen())
                self.assertEqual(meta["adaptive_anchor_key"], "4")

                pgn_path = export_pgn_file(
                    b, "test_export", "Kamu", "Mittens", "1200", "1300",
                    eco="C50", opening="Italian Game"
                )
                pgn_txt = pgn_path.read_text(encoding="utf-8")
                self.assertIn('[ECO "C50"]', pgn_txt)
                self.assertIn('[Opening "Italian Game"]', pgn_txt)
            finally:
                if old_env is None:
                    os.environ.pop("CHESSPORTABLE_HOME", None)
                else:
                    os.environ["CHESSPORTABLE_HOME"] = old_env

    def test_cli_v30_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["CHESSPORTABLE_HOME"] = tmp
            root = str(Path(__file__).resolve().parent.parent)
            env["PYTHONPATH"] = root

            script = "\n".join([
                "A list",
                "",
                "A 4",
                "1",
                "e5",
                "E4",
                "coach",
                "moves g1",
                "theme neon",
                "style",
                "hint",
                "gaya",
                "export myg",
                "save demo",
                "resign",
                "y",
                "v",
                "2",
                "B",
                "13",
                "2",
                "quit",
            ]) + "\n"

            proc = subprocess.run(
                [sys.executable, "-m", "chessportable"],
                input=script,
                text=True,
                capture_output=True,
                env=env,
                timeout=45,
            )
            self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
            out = strip_ansi(proc.stdout)
            self.assertIn("Hi! Choose your ai!", out)
            self.assertIn("(1) [✦] Starrys - Elo 150", out)
            self.assertIn("(0) [✦] Jim - Elo 4000", out)
            self.assertIn("Please Type A for adaptive version", out)
            self.assertIn("DAFTAR LAWAN ADAPTIF", out)
            self.assertIn("Lawan Adaptif:", out)
            self.assertIn("Adaptif · Mittens", out)
            self.assertIn("Pilih sisi mainmu:", out)
            self.assertIn("Illegal!", out)
            self.assertIn("SARAN PELATIH", out)
            self.assertIn("Midnight Cyber", out)
            self.assertIn("ASCII Berwarna", out)
            self.assertIn("Saran terbaik:", out)
            self.assertIn("CATATAN GAYA MAINMU", out)
            self.assertIn("PGN berhasil diekspor", out)
            self.assertIn("disimpan sebagai 'demo'", out)
            self.assertIn("EVALUASI AKHIR PERTANDINGAN", out)
            self.assertIn("CATATAN LANGKAH PER LANGKAH", out)
            self.assertIn("BOT KLUB & LEGENDA", out)
            self.assertIn("Kakek Hasan", out)

            arc_script = "\n".join([
                "1",
                "1",
                "ARC e4 kh3 z99",
                "quit",
            ]) + "\n"
            proc_arc = subprocess.run(
                [sys.executable, "-m", "chessportable"],
                input=arc_script,
                text=True,
                capture_output=True,
                env=env,
                timeout=25,
            )
            self.assertEqual(proc_arc.returncode, 0, f"stderr: {proc_arc.stderr}")
            out_arc = strip_ansi(proc_arc.stdout)
            self.assertIn("ARC aktif (3 langkah otomatis)", out_arc)
            self.assertIn("(e4)", out_arc)
            self.assertIn("(Nh3)", out_arc)
            self.assertIn("ARC berhenti!", out_arc)


            puz_script = "\n".join([
                "P",
                "hint",
                "e8=Q",
                "m",
                "Q",
            ]) + "\n"
            proc_p = subprocess.run(
                [sys.executable, "-m", "chessportable"],
                input=puz_script,
                text=True,
                capture_output=True,
                env=env,
                timeout=20,
            )
            self.assertEqual(proc_p.returncode, 0, f"stderr: {proc_p.stderr}")
            out_p = strip_ansi(proc_p.stdout)
            self.assertIn("PUZZLE #P07", out_p)
            self.assertIn("PUZZLE SELESAI", out_p)

if __name__ == "__main__":
    unittest.main()
