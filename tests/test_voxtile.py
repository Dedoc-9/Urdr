# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxtile (URDRVTL1) — the tile size was never a tuning parameter, it was the answer."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxtile as TL                                          # noqa: E402
import voxbreak as VB                                         # noqa: E402
import voxschism as VC                                        # noqa: E402
import voxmanifold as VM                                      # noqa: E402
import voxcond as VD                                          # noqa: E402
import voxref as VR                                           # noqa: E402
import voxwork as VO                                          # noqa: E402


class TheSweep(unittest.TestCase):
    def test_the_observable_never_moves_at_any_tile_size(self):
        """A tile size that changed what is seen would be a bug, not a faster arrangement."""
        self.assertTrue(TL.the_observable_never_moves_at_any_tile_size())

    def test_the_tile_sizes_divide_the_frame(self):
        """A sweep where some sizes tile evenly and others do not measures two things at once."""
        self.assertTrue(TL.the_tile_sizes_divide_the_frame())
        for t in TL.TILES:
            self.assertEqual(VR.W % t, 0)
            self.assertEqual(VR.H % t, 0)

    def test_every_declared_size_is_swept(self):
        self.assertEqual(len(TL.TILES), 8)
        for t in TL.TILES:
            self.assertGreater(TL.cold(t), 0)
            self.assertGreater(TL.certified(t), 0)

    def test_an_undeclared_tile_size_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.sweep(5)

    def test_a_render_at_an_undeclared_size_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.render(0, 5, None)

    def test_an_unknown_phase_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.bookkeeping(8, "tepid")

    def test_retirement_is_measured_against_the_same_size(self):
        """Retirement never crosses tile sizes: the baseline is the cold loop of the SAME size."""
        for t in TL.TILES:
            self.assertEqual(TL.retired(t), TL.cold(t) - TL.certified(t))

    def test_the_tax_is_measured_against_the_committed_reference(self):
        for t in TL.TILES:
            self.assertEqual(TL.tax(t), TL.cold(t) - VM.reference_cost())


class TheAnchors(unittest.TestCase):
    def test_the_unit_tile_is_the_reference_exactly(self):
        """Unit binning walks precisely each triangle's own bounding box, and nothing else."""
        self.assertTrue(TL.the_unit_tile_is_the_reference_exactly())
        self.assertEqual(TL.cold(1, book=False), VM.reference_cost())

    def test_the_committed_tile_reproduces_voxbreaks_figures(self):
        """The same instrument re-parameterised, not a second measurement that drifted."""
        self.assertTrue(TL.the_committed_tile_reproduces_voxbreaks_figures())
        self.assertEqual(TL.cold(TL.COMMITTED, book=False), VB.spend("none"))
        self.assertEqual(TL.certified(TL.COMMITTED, book=False), VB.spend("all"))

    def test_the_committed_size_is_inherited_and_not_redeclared(self):
        self.assertEqual(TL.COMMITTED, VD.TILE)
        self.assertIn(TL.COMMITTED, TL.TILES)


class TheBookkeeping(unittest.TestCase):
    def test_the_bookkeeping_is_charged_and_it_moved_the_answer(self):
        """THE HONESTY LAW. Uncharged the unit tile wins; charged it does not."""
        self.assertTrue(TL.the_bookkeeping_is_charged_and_it_moved_the_answer())

    def test_the_uncharged_sweep_was_strictly_rosier(self):
        self.assertLess(TL.certified(1, book=False), TL.certified(TL.best()))

    def test_the_optimum_moves_when_the_charge_is_applied(self):
        self.assertEqual(TL.best(book=False), 1)
        self.assertNotEqual(TL.best(book=True), 1)

    def test_every_bookkeeping_term_is_reported_separately(self):
        """A record that declares five terms and prints one total is naming, not describing."""
        self.assertEqual(len(TL.BOOK_TERMS), 5)
        for t in TL.TILES:
            self.assertEqual(TL.bookkeeping(t, "warm"),
                             sum(TL.sweep(t)["warm"][n] for n in TL.BOOK_TERMS))

    def test_the_tile_independent_terms_really_are_tile_independent(self):
        """`range` and `owners` are per-triangle, so they must not move with the tile — if they did,
        the decomposition would be wrong."""
        for term in ("range", "owners"):
            vals = {TL.sweep(t)["warm"][term] for t in TL.TILES}
            self.assertEqual(len(vals), 1)

    def test_the_tile_dependent_terms_fall_as_the_tile_grows(self):
        for term in ("index", "visit"):
            seq = [TL.sweep(t)["warm"][term] for t in TL.TILES]
            self.assertEqual(seq, sorted(seq, reverse=True))

    def test_the_bookkeeping_favoured_the_small_tile(self):
        self.assertGreater(TL.bookkeeping(1, "warm"), 3 * TL.bookkeeping(TL.COMMITTED, "warm"))


class TheResult(unittest.TestCase):
    def test_the_arrangement_gets_under_the_committed_reference(self):
        """The first time in this arc that anything BUILDABLE has beaten the reference."""
        self.assertTrue(TL.the_arrangement_gets_under_the_committed_reference())
        self.assertLess(TL.net(TL.best()), 0)

    def test_more_than_one_size_gets_under_it(self):
        self.assertGreater(len([t for t in TL.TILES if TL.net(t) < 0]), 1)

    def test_the_committed_tile_is_still_underwater(self):
        self.assertGreater(TL.net(TL.COMMITTED), 0)

    def test_the_earlier_verdict_was_conditional_on_a_constant(self):
        """Nothing earlier is retracted: both earlier verdicts are RUN here, not cited."""
        self.assertTrue(TL.the_earlier_verdict_was_conditional_on_a_constant())
        self.assertTrue(VB.the_inequality_has_no_solution_on_this_loop())
        self.assertTrue(VC.the_tiled_traversal_is_dominated_everywhere())

    def test_no_selector_is_used(self):
        """The margin is taken without solving the problem `voxschism` proved unsolvable."""
        self.assertTrue(TL.no_selector_is_used())
        self.assertTrue(VC.no_free_signal_captures_any_of_the_margin())

    def test_the_certificate_is_voxconds_and_no_new_one_is_invented(self):
        self.assertTrue(VD.sound("P4"))
        for p in ("P2", "P3", "P5"):
            self.assertFalse(VD.sound(p))

    def test_nothing_is_promoted(self):
        self.assertTrue(TL.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(TL.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_is_quoted_from_the_earlier_commit(self):
        """COMMIT ORDER is the only mechanism that proves a prediction came first."""
        self.assertTrue(TL.the_prediction_is_quoted_from_the_earlier_commit())

    def test_the_verdicts_match_the_committed_prediction(self):
        self.assertTrue(TL.the_verdicts_match_the_committed_prediction())
        self.assertEqual(len(TL.PREDICTIONS), 5)

    def test_the_record_carries_hits_and_misses(self):
        self.assertTrue(TL.the_record_carries_hits_and_misses())

    def test_the_registered_long_shot_is_the_one_that_hit(self):
        """T3 is the prediction the pre-registration itself named as most likely to miss."""
        self.assertIn("T3", TL.hits())

    def test_the_monotone_retirement_claim_missed(self):
        self.assertIn("T2", TL.misses())
        self.assertNotEqual(TL.best_retirement(), TL.TILES[0])
        self.assertNotEqual(TL.best_retirement(), TL.TILES[-1])


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(TL.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(TL.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(TL.a_tampered_row_refuses())

    def test_a_tile_row_naming_no_declared_size_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\ntile 5 1 2 3 4 5 6\n")

    def test_a_book_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\nbook 8 1 2\n")

    def test_a_bare_row_naming_no_declared_size_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\nbare 5 1 2\n")

    def test_a_verdict_row_naming_no_prediction_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\nverdict T9 HIT nothing\n")

    def test_a_verdict_row_of_an_unknown_outcome_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\nverdict T1 MAYBE nothing\n")

    def test_a_best_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\nbest 2\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(TL.generate(), TL._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in TL.SCENES:
            self.assertEqual(TL.scene_result(name), TL.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.scene_case("sweep2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(TL.VoxtileError):
            TL.golden("nope")


if __name__ == "__main__":
    unittest.main()
