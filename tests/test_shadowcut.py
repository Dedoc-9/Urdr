# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""shadowcut (URDRSHC1) — the proposed remedy answers a different question."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import cohort as CO                                            # noqa: E402
import shadowcut as SC                                         # noqa: E402


class TheSubjectIsUntouched(unittest.TestCase):
    def test_the_production_law_is_untouched(self):
        self.assertTrue(SC.the_production_law_is_untouched())
        self.assertEqual(CO.CUT_SEARCH_MAX, 3)

    def test_the_bounded_answer_comes_from_the_subject(self):
        """Called through `cohort`, never reimplemented here."""
        for (n, t) in SC.CASES:
            with self.subTest(case=(n, t)):
                self.assertEqual(SC.answer((n, t), "bounded"),
                                 CO.min_cut(CO.spanning_wall(n, t), n))

    def test_the_bounded_search_is_not_transcribed_here(self):
        self.assertTrue(SC.the_bounded_search_is_not_transcribed_here())

    def test_nothing_is_promoted(self):
        self.assertTrue(SC.nothing_is_promoted())

    def test_no_wall_clock_enters(self):
        self.assertTrue(SC.no_wall_clock_enters_this_rung())


class TheWitness(unittest.TestCase):
    def test_the_witness_is_adjudicated_by_the_subject(self):
        """The oracle proposes and `cohort.free_reaches` decides."""
        self.assertTrue(SC.the_witness_is_adjudicated_by_the_subject())

    def test_every_witness_is_a_subset_of_its_wall(self):
        for (n, t) in SC.CASES:
            with self.subTest(case=(n, t)):
                self.assertTrue(SC.witness((n, t)) <= CO.spanning_wall(n, t))

    def test_every_witness_has_the_size_it_reports(self):
        for c in SC.CASES:
            with self.subTest(case=c):
                self.assertEqual(len(SC.witness(c)), SC.answer(c, "shortest"))

    def test_removing_the_witness_opens_the_wall(self):
        for (n, t) in SC.CASES:
            with self.subTest(case=(n, t)):
                w = CO.spanning_wall(n, t)
                self.assertTrue(CO.free_reaches(w - SC.witness((n, t)), n))

    def test_removing_one_cell_fewer_does_not(self):
        """Minimality of the witness itself, checked by the subject rather than asserted."""
        for (n, t) in SC.CASES:
            cells = sorted(SC.witness((n, t)))
            with self.subTest(case=(n, t)):
                w = CO.spanning_wall(n, t)
                self.assertFalse(CO.free_reaches(w - frozenset(cells[1:]), n))


class TheComparison(unittest.TestCase):
    def test_the_two_oracles_agree_wherever_the_bound_decides(self):
        self.assertTrue(SC.the_two_oracles_agree_wherever_the_bound_decides())

    def test_no_case_diverges(self):
        self.assertEqual(dict(SC.verdict_census())["diverge"], 0)

    def test_the_bound_is_inactive_on_the_pinned_corpus(self):
        self.assertTrue(SC.the_bound_is_inactive_on_the_pinned_corpus())

    def test_the_bound_is_active_immediately_outside_it(self):
        self.assertTrue(SC.the_bound_is_active_immediately_outside_it())

    def test_the_undecided_case_is_exactly_the_one_past_the_cap(self):
        undecided = [c for c in SC.CASES if SC.compare(c) == "undecided"]
        self.assertEqual(undecided, [(6, 4)])
        self.assertGreater(SC.answer((6, 4), "shortest"), CO.CUT_SEARCH_MAX)

    def test_undecided_is_neither_agreement_nor_divergence(self):
        self.assertIn("undecided", SC.VERDICTS)
        self.assertIsNone(SC.answer((6, 4), "bounded"))
        self.assertNotEqual(SC.compare((6, 4)), "agree")
        self.assertNotEqual(SC.compare((6, 4)), "diverge")

    def test_the_extension_straddles_the_cap_from_both_sides(self):
        at = [c for c in SC.EXTENSION if SC.answer(c, "shortest") == CO.CUT_SEARCH_MAX]
        past = [c for c in SC.EXTENSION if SC.answer(c, "shortest") > CO.CUT_SEARCH_MAX]
        self.assertTrue(at, "no extension case sits AT the cap")
        self.assertTrue(past, "no extension case sits PAST the cap")

    def test_the_shortest_answer_equals_the_thickness_on_a_solid_slab(self):
        for (n, t) in SC.CASES:
            with self.subTest(case=(n, t)):
                self.assertEqual(SC.answer((n, t), "shortest"), t)


class TheMaxFlowFinding(unittest.TestCase):
    def test_max_flow_answers_a_different_question(self):
        self.assertTrue(SC.the_max_flow_formulation_answers_a_different_question())

    def test_max_flow_is_the_cross_section(self):
        for c in SC.CASES:
            with self.subTest(case=c):
                self.assertEqual(SC.answer(c, "maxflow"), SC.cross_section(c))

    def test_max_flow_does_not_move_with_thickness(self):
        """The decisive shape: same n, different t, same answer — while `shortest` tracks t."""
        for n in sorted({a for a, _b in SC.CASES}):
            ts = [t for (m, t) in SC.CASES if m == n]
            if len(ts) < 2:
                continue
            with self.subTest(n=n):
                flows = {SC.answer((n, t), "maxflow") for t in ts}
                shorts = {SC.answer((n, t), "shortest") for t in ts}
                self.assertEqual(len(flows), 1)
                self.assertGreater(len(shorts), 1)

    def test_the_duality_it_needed_was_already_refuted(self):
        self.assertTrue(SC.the_duality_it_needed_was_already_refuted())

    def test_the_refutation_is_unpacked_and_not_returned_whole(self):
        """A non-empty tuple is truthy whatever it holds, so a law handing it back could not fail."""
        triple = CO.hex_duality_fails_in_3d()
        self.assertEqual(len(triple), 3)
        self.assertTrue(all(triple))
        self.assertIsInstance(SC.the_duality_it_needed_was_already_refuted(), bool)


class TheGeometryPlants(unittest.TestCase):
    def test_the_oracles_track_geometry_and_not_the_parameter(self):
        self.assertTrue(SC.the_oracles_track_geometry_and_not_the_thickness_parameter())

    def test_a_breached_wall_is_zero_under_both(self):
        self.assertTrue(SC.a_breached_wall_is_zero_under_both())

    def test_a_holed_wall_is_answered_by_its_hole(self):
        n = 5
        holed = CO.spanning_wall(n, 2) - frozenset({(1, 2, 2)})
        k, cells = SC.shortest_cut(holed, n)
        self.assertEqual(k, 1)
        self.assertEqual(CO.min_cut(holed, n), 1)
        self.assertTrue(CO.free_reaches(holed - cells, n))


class TheRefusals(unittest.TestCase):
    def test_an_unknown_case_refuses(self):
        for call in (SC.witness, SC.cross_section):
            with self.assertRaises(SC.ShadowcutError):
                call((99, 1))

    def test_an_unknown_oracle_refuses(self):
        with self.assertRaises(SC.ShadowcutError):
            SC.answer(SC.CASES[0], "wishful")

    def test_an_unknown_case_refuses_on_answer(self):
        with self.assertRaises(SC.ShadowcutError):
            SC.answer((99, 1), "shortest")

    def test_a_wall_that_fills_the_world_refuses_rather_than_returning(self):
        """There is no face-to-face route at all when every cell is wall; the oracle refuses instead
        of reporting a number it did not find."""
        n = 3
        with self.assertRaises(SC.ShadowcutError):
            SC.shortest_cut(frozenset(), 0)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(SC.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(SC.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(SC.a_tampered_row_refuses())

    def test_the_generated_record_is_the_committed_one(self):
        with open(os.path.join(_ROOT, SC.RECORD), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), SC.generate())

    def test_rows_of_unknown_kinds_refuse(self):
        head = "# world x\n"
        for bad in ("case 99 1 1 1 9 9 pinned", "case 3 1 1 1 9 9 wishful",
                    "verdict thrived 1", "rumour 1"):
            with self.subTest(row=bad):
                with self.assertRaises(SC.ShadowcutError):
                    SC.parse(head + bad + "\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(SC.ShadowcutError):
            SC.parse("verdict agree 8\n")

    def test_a_record_with_no_rows_refuses(self):
        with self.assertRaises(SC.ShadowcutError):
            SC.parse("# world x\n")

    def test_the_scenes_match_their_goldens(self):
        for n in SC.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(SC.scene_result(n), SC.golden(n))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(SC.ShadowcutError):
            SC.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(SC.ShadowcutError):
            SC.golden("wishful")


if __name__ == "__main__":
    unittest.main(verbosity=2)
