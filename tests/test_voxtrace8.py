# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxtrace8 (URDRTR81) — the arc measured seven cases and called them eight."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxtrace8 as T8                                        # noqa: E402
import voxref as VR                                           # noqa: E402
import voxray as VX                                           # noqa: E402
import voxwork as VO                                          # noqa: E402
import voxsilo as VS                                          # noqa: E402
import voxpath as VP                                          # noqa: E402


class TheDefect(unittest.TestCase):
    def test_the_defect_is_real_and_is_re_run(self):
        """`voxpath` found it; citing a finding is not running it."""
        self.assertTrue(T8.the_defect_is_real_and_is_re_run())

    def test_exactly_one_pair_collapses(self):
        self.assertEqual(len(T8.collapsed_pair()), 2)
        self.assertEqual(T8.collapsed_pair(), (0, 1))

    def test_the_committed_distinctness_law_is_still_correct(self):
        """The reference is right about the winding it was written for."""
        self.assertTrue(VR.every_declared_case_is_distinct())
        self.assertTrue(VP.the_reversed_winding_collapses_a_declared_case())

    def test_the_winding_is_inherited_and_not_redeclared(self):
        self.assertIn(T8.WINDING, VX.WINDINGS)
        self.assertEqual(T8.WINDING, "reversed")


class TheProcedure(unittest.TestCase):
    def test_the_drop_rule_selects_exactly_one_frame(self):
        """A rule selecting both or neither would be a preference dressed as a procedure."""
        self.assertTrue(T8.the_drop_rule_selects_exactly_one_frame())
        self.assertEqual(T8.dropped(), 1)

    def test_the_dropped_frame_is_the_one_inside_solid(self):
        self.assertTrue(VX.eye_is_inside_solid(VR.TRACE[T8.dropped()][1]))
        other = [i for i in T8.collapsed_pair() if i != T8.dropped()][0]
        self.assertFalse(VX.eye_is_inside_solid(VR.TRACE[other][1]))

    def test_the_dropped_frame_is_already_excluded_elsewhere(self):
        """The judgement is inherited from `voxray`, not invented here."""
        self.assertTrue(T8.the_dropped_frame_is_already_excluded_elsewhere())
        self.assertNotIn(T8.dropped(), VX.comparable_frames())

    def test_the_seven_kept_frames_are_verbatim(self):
        """Inherited tuples, never re-typed coordinates."""
        self.assertTrue(T8.the_seven_kept_frames_are_verbatim())
        self.assertEqual(len(T8.kept()), 7)

    def test_the_replacement_is_the_first_qualifying_candidate(self):
        """How a hand-picked frame would be caught: a chosen frame is almost never the first."""
        self.assertTrue(T8.the_replacement_is_the_first_qualifying_candidate())

    def test_the_search_is_reported_honestly(self):
        """A one-line search must not read as a thorough one."""
        self.assertTrue(T8.the_search_is_reported_honestly())
        _found, seen = T8.search()
        self.assertEqual(seen, 2)

    def test_the_only_rejected_candidate_was_rejected_for_a_stated_reason(self):
        """The first candidate fails because its eye is inside solid — not by accident."""
        first = next(T8.candidates())
        self.assertTrue(VX.eye_is_inside_solid(first[1]))

    def test_the_search_forward_is_the_dropped_frames_own(self):
        """Holding it fixed removes a degree of freedom the search could have exploited."""
        self.assertEqual(T8.SEARCH_FORWARD, VR.TRACE[T8.dropped()][2])

    def test_the_candidate_order_is_total_and_fixed(self):
        cells = [c for c, _e in T8.candidates()]
        self.assertEqual(len(cells), VR.N ** 3)
        self.assertEqual(cells, sorted(cells))


class TheCorpus(unittest.TestCase):
    def test_all_eight_cases_are_distinct(self):
        """The thing the old trace failed, and the only property claimed for the new frame."""
        self.assertTrue(T8.all_eight_cases_are_distinct())
        self.assertEqual(len(T8.trace8()), 8)

    def test_the_corpus_is_distinct_under_the_committed_winding_too(self):
        """Measured, not required — the arc uses the corrected winding."""
        self.assertEqual(T8.distinct_under("as-committed"), 8)

    def test_the_replacement_is_in_free_space(self):
        _name, eye, _fwd = T8.replacement()[0]
        self.assertFalse(VX.eye_is_inside_solid(eye))

    def test_an_undeclared_winding_refuses(self):
        with self.assertRaises(VX.VoxrayError):
            T8.distinct_under("sideways")


class TheMeasurements(unittest.TestCase):
    def test_the_instruments_are_imported_and_not_reimplemented(self):
        """This module contains no rasteriser: the eighth transcription the arc did NOT write."""
        self.assertTrue(T8.the_instruments_are_imported_and_not_reimplemented())

    def test_the_floor_uses_every_declared_counter(self):
        for c in VO.COUNTERS:
            self.assertIn(c, T8.floor())

    def test_the_fates_partition_the_walk(self):
        f = T8.fates()
        self.assertEqual(f["outside"] + f["beaten"] + f["written"], T8.floor()["walked"])

    def test_the_overdraw_is_reported_as_a_pair(self):
        """`voxwork`'s own definition: a pair, never a ratio, so no percentage is invented."""
        w, out = T8.overdraw()
        self.assertEqual(out, VR.W * VR.H * 8)
        self.assertGreater(w, 10 * out)

    def test_every_cell_reproduces_the_observable_on_the_new_trace(self):
        """The law that could have found a real bug rather than a bookkeeping one."""
        self.assertTrue(T8.every_cell_reproduces_the_observable_on_the_new_trace())

    def test_the_panel_covers_every_cell_and_column(self):
        for c in VS.CELLS:
            for k in VS.COLUMNS:
                self.assertIn(k, T8.panel(c))

    def test_an_undeclared_cell_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            T8.panel(("Z",))

    def test_an_undeclared_cell_name_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.cell_total("ZZ")


class TheFindings(unittest.TestCase):
    def test_the_findings_survive_the_corrected_corpus(self):
        """A null result is the point — it is only worth having because it could have gone the
        other way."""
        self.assertTrue(T8.the_findings_survive_the_corrected_corpus())

    def test_every_declared_finding_is_scored(self):
        self.assertEqual(sorted(T8.findings()), sorted(T8.FINDINGS))
        self.assertEqual(len(T8.FINDINGS), 6)

    def test_the_best_cell_is_still_not_the_full_combination(self):
        """The most surprising thing the arc produced, re-measured."""
        self.assertEqual(T8.best_cell(), "GA")
        self.assertLess(T8.cell_total("GA"), T8.cell_total("GTA"))

    def test_the_old_ordering_and_the_new_ordering_agree(self):
        self.assertEqual(VS.best_cell("mul"), T8.best_cell())
        self.assertLess(VS.panel(("G", "A"))["mul"], VS.panel(("G", "T", "A"))["mul"])

    def test_no_finding_broke(self):
        self.assertEqual(T8.casualties(), ())
        self.assertEqual(len(T8.survivors()), len(T8.FINDINGS))


class TheHistory(unittest.TestCase):
    def test_the_committed_records_are_untouched(self):
        """A record edited to match a later corpus has stopped being evidence."""
        self.assertTrue(T8.the_committed_records_are_untouched())

    def test_the_committed_trace_is_unchanged(self):
        self.assertEqual(len(VR.TRACE), 8)
        for f in T8.kept():
            self.assertIn(f, VR.TRACE)

    def test_the_old_floor_is_still_the_old_floor(self):
        """This rung reports beside the old totals; it does not replace them."""
        self.assertNotEqual(T8.floor()["walked"], VO.total("walked"))
        self.assertEqual(VO.overdraw()[1], T8.overdraw()[1])

    def test_nothing_is_promoted(self):
        self.assertTrue(T8.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(T8.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(T8.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(T8.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(T8.a_tampered_row_refuses())

    def test_a_drop_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\ndrop 1\n")

    def test_a_search_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\nsearch 0 0 1\n")

    def test_a_frame_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\nframe 0 a 1 2 3\n")

    def test_a_floor_row_naming_no_counter_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\nfloor strolled 1 2\n")

    def test_a_cell_row_naming_no_cell_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\ncell ZZ 1 2 3 4 5 6 7 8\n")

    def test_a_finding_row_naming_no_finding_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\nfinding wishful SURVIVES nothing\n")

    def test_a_finding_row_of_an_unknown_verdict_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\nfinding overdraw MAYBE nothing\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(T8.generate(), T8._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in T8.SCENES:
            self.assertEqual(T8.scene_result(name), T8.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.scene_case("trace2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(T8.Voxtrace8Error):
            T8.golden("nope")


if __name__ == "__main__":
    unittest.main()
