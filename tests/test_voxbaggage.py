# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxbaggage (URDRBAG1) — which executed operations exist only because we are measuring?"""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxbaggage as BG                                       # noqa: E402
import voxtile as TL                                          # noqa: E402
import voxwork as VO                                          # noqa: E402


class TheAnalysis(unittest.TestCase):
    def test_the_analysis_can_tell_the_two_apart(self):
        """Without the control the headline is an inability, not a measurement."""
        self.assertTrue(BG.the_analysis_can_tell_the_two_apart())

    def test_the_dead_structure_is_still_dead(self):
        """Reddens the day `voxtile` starts reading its owner index cold — the good outcome."""
        self.assertTrue(BG.the_dead_structure_is_still_dead())
        self.assertEqual(BG.liveness("by_key")[1], 0)

    def test_the_control_is_read_on_both_paths(self):
        self.assertTrue(BG.the_control_is_read_on_both_paths())
        self.assertGreater(BG.liveness("bins")[1], 0)

    def test_the_analysis_reads_the_subject_and_not_a_copy(self):
        self.assertEqual(BG.SUBJECT, "voxtile.py")
        self.assertTrue(os.path.exists(os.path.join(_ROOT, "tools", "terrain", BG.SUBJECT)))

    def test_construction_is_not_counted_as_a_read(self):
        """`setdefault` builds the index; counting it as a read would call every structure live."""
        total, cold, live = BG.liveness("by_key")
        self.assertEqual(total, 1)
        self.assertFalse(live)

    def test_an_undeclared_structure_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.liveness("wishful")


class TheClassification(unittest.TestCase):
    def test_every_charged_term_carries_a_claim(self):
        """A term counted without an argument about what it is FOR leaves the reader to guess."""
        self.assertTrue(BG.every_charged_term_carries_a_claim())
        self.assertEqual(len(BG.CLAIMS), len(BG.TERMS))

    def test_the_categories_are_declared_and_the_liveness_is_derived(self):
        """The boundary that is the whole integrity of a classification."""
        self.assertTrue(BG.the_categories_are_declared_and_the_liveness_is_derived())

    def test_every_claim_names_a_declared_category(self):
        for _n, cat, _why in BG.CLAIMS:
            self.assertIn(cat, BG.CATEGORIES)

    def test_every_claim_carries_a_reason(self):
        for _n, _cat, why in BG.CLAIMS:
            self.assertGreater(len(why), 20)

    def test_the_proof_terms_are_not_instrumentation(self):
        """`complete` looks like a debug check and is load-bearing."""
        self.assertTrue(BG.the_proof_terms_are_not_instrumentation())
        self.assertEqual(BG.claim("complete")[0], "proof")

    def test_the_proof_terms_are_charged_only_to_the_warm_arm(self):
        for n in BG.TERMS:
            if BG.claim(n)[0] == "proof":
                self.assertEqual(BG.charged("cold", n, BG.FIXTURE), 0)
                self.assertGreater(BG.charged("warm", n, BG.FIXTURE), 0)

    def test_the_essential_terms_are_charged_to_both_arms(self):
        for n in ("range", "index", "visit"):
            self.assertEqual(BG.claim(n)[0], "essential")
            self.assertEqual(BG.charged("cold", n, BG.FIXTURE), BG.charged("warm", n, BG.FIXTURE))

    def test_an_undeclared_term_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.charged("cold", "wishful", BG.FIXTURE)

    def test_an_undeclared_path_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.charged("tepid", "visit", BG.FIXTURE)

    def test_a_term_with_no_claim_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.claim("wishful")


class TheBlastRadius(unittest.TestCase):
    def test_the_dead_work_is_charged_and_it_is_not_nothing(self):
        self.assertTrue(BG.the_dead_work_is_charged_and_it_is_not_nothing())
        self.assertEqual(len({BG.dead_cost(t) for t in BG.FIXTURE_TILES}), 1)

    def test_only_the_baseline_is_overstated(self):
        """`net` is untouched, so voxtile's headline and all five verdicts stand exactly."""
        self.assertTrue(BG.only_the_baseline_is_overstated())
        self.assertTrue(TL.the_arrangement_gets_under_the_committed_reference())

    def test_the_correction_changes_no_verdict(self):
        """A constant subtracted from every point cannot reorder them — checked, not argued."""
        self.assertTrue(BG.the_correction_changes_no_verdict())

    def test_the_corrected_figures_are_smaller_and_by_the_same_constant(self):
        for t in BG.FIXTURE_TILES:
            self.assertEqual(BG.FIXTURE_TAX[t] - BG.corrected_tax(t), BG.dead_cost(t))
            self.assertEqual(BG.FIXTURE_RETIRED[t] - BG.corrected_retired(t), BG.dead_cost(t))

    def test_voxtile_is_untouched_and_still_binds(self):
        """Nothing is corrected: the fixed pair ships beside the committed one."""
        self.assertTrue(TL.the_record_is_bound_to_the_live_code())
        self.assertTrue(TL.the_record_names_this_world())


class TheDependency(unittest.TestCase):
    """The lattice was right about more than depth, and these keep it right."""

    def test_the_subject_is_not_imported(self):
        """A census that imported its subject would sit on that subject's import chain, and the
        sealed ceiling is a MEASUREMENT rather than a budget."""
        self.assertTrue(BG.the_subject_is_not_imported())

    def test_the_fixture_matches_the_live_subject(self):
        """A fixture nobody compares is a guess with a comment on it. The TEST may import the
        subject; the MODULE may not."""
        self.assertTrue(BG.the_fixture_matches_the_live_subject(TL))

    def test_the_declared_terms_are_the_subjects_own(self):
        self.assertEqual(tuple(TL.COLUMNS), BG.TERMS)
        self.assertEqual(tuple(TL.TILES), BG.FIXTURE_TILES)

    def test_the_carried_figures_are_the_subjects_own(self):
        for t in BG.FIXTURE_TILES:
            self.assertEqual(TL.tax(t), BG.FIXTURE_TAX[t])
            self.assertEqual(TL.retired(t), BG.FIXTURE_RETIRED[t])
        self.assertEqual(TL.best(), BG.FIXTURE_BEST)
        self.assertEqual(TL.best_retirement(), BG.FIXTURE_BEST_RETIRED)

    def test_the_dead_cost_is_the_subjects_own(self):
        for t in BG.FIXTURE_TILES:
            self.assertEqual(TL.sweep(t)["cold"]["owners"], BG.FIXTURE_DEAD)

    def test_the_subjects_own_laws_still_hold(self):
        """Run here rather than cited: this rung corrects nothing and must not be able to."""
        self.assertTrue(TL.the_arrangement_gets_under_the_committed_reference())
        self.assertTrue(TL.the_verdicts_match_the_committed_prediction())
        self.assertTrue(TL.the_record_is_bound_to_the_live_code())

    def test_a_count_the_fixture_does_not_name_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.charged("cold", "visit", {})


class TheAnswer(unittest.TestCase):
    def test_the_removable_layer_is_not_a_speedup(self):
        """The answer the census exists to give, and not the one the hypothesis expected."""
        self.assertTrue(BG.the_removable_layer_is_not_a_speedup())

    def test_the_dead_work_is_smaller_than_the_proof_machinery(self):
        self.assertLess(BG.dead_total(), BG.proof_total())

    def test_the_dead_work_is_charged_to_the_baseline_too(self):
        """It is charged to BOTH arms — which is why removing it shrinks a claim, not a runtime."""
        self.assertEqual(BG.charged("cold", "owners", BG.FIXTURE), BG.charged("warm", "owners", BG.FIXTURE))

    def test_no_economics_are_claimed(self):
        """The boundary between a census and the business it exists to decide on."""
        self.assertTrue(BG.no_economics_are_claimed())

    def test_nothing_is_promoted(self):
        self.assertTrue(BG.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(BG.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_ships_before_the_stripping(self):
        self.assertTrue(BG.the_prediction_ships_before_the_stripping())

    def test_the_prediction_names_no_result(self):
        self.assertTrue(BG.the_prediction_names_no_result())

    def test_the_prediction_declares_five(self):
        t = BG.prediction_text()
        self.assertEqual(sum(1 for ln in t.split("\n") if ln.startswith("predict ")), 5)

    def test_the_prediction_digest_is_pinned(self):
        self.assertEqual(BG.prediction_digest(), BG.golden("prediction"))

    def test_the_safety_contract_is_not_scored_as_a_prediction(self):
        """Stripping may never move `O_t`. That is a precondition, not a result."""
        t = BG.prediction_text()
        self.assertIn("NOT A PREDICTION", t)
        self.assertNotIn("predict S6", t)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(BG.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(BG.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(BG.a_tampered_row_refuses())

    def test_a_term_row_naming_no_term_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("# world x\nterm wishful proof 1 2\n")

    def test_a_term_row_naming_no_category_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("# world x\nterm owners delicious 1 2\n")

    def test_a_live_row_naming_no_structure_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("# world x\nlive wishful 1 0 False\n")

    def test_a_fix_row_naming_no_tile_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("# world x\nfix 5 1 2\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(BG.generate(), BG._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in BG.SCENES:
            self.assertEqual(BG.scene_result(name), BG.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.scene_case("terms2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(BG.VoxbaggageError):
            BG.golden("nope")


if __name__ == "__main__":
    unittest.main()
