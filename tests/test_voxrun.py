# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxrun (URDRRUN1) — the predecessor's structure does not disappear, it fragments."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxrun as RN                                           # noqa: E402
import voxref as VR                                           # noqa: E402
import voxray as VX                                           # noqa: E402
import voxtrace8 as T8                                        # noqa: E402
import voxstate as VT                                         # noqa: E402


class TheRuns(unittest.TestCase):
    def test_the_runs_partition_every_scanline(self):
        """Maximal and exhaustive, or every count in this rung names something else."""
        self.assertTrue(RN.the_runs_partition_every_scanline())

    def test_a_run_is_never_empty_and_never_adjacent_to_its_own_owner(self):
        rs = RN.runs(RN.owner_map("lattice", 0))
        for _y, x0, x1, _k in rs:
            self.assertLessEqual(x0, x1)
        by_row = {}
        for (y, x0, x1, k) in rs:
            by_row.setdefault(y, []).append((x0, x1, k))
        for row in by_row.values():
            row.sort()
            for a, b in zip(row, row[1:]):
                self.assertNotEqual(a[2], b[2])

    def test_the_owner_map_comes_from_the_imported_instrument(self):
        """`voxray.render_winners`, whose own law binds it to `voxref.render`."""
        self.assertTrue(RN.no_rasteriser_is_transcribed())
        self.assertEqual(RN.owner_map("lattice", 0),
                         VX.render_winners(VX.primitives_with(RN.WINDING),
                                           RN.LATTICE[0][0], RN.LATTICE[0][1]))

    def test_the_winding_is_inherited_and_not_redeclared(self):
        self.assertIn(RN.WINDING, VX.WINDINGS)
        self.assertEqual(RN.WINDING, "reversed")

    def test_an_unknown_corpus_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.owner_map("wishful", 0)

    def test_an_unknown_population_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.structure("lattice", "hopeful")


class TheStructure(unittest.TestCase):
    def test_the_populations_are_reported_apart(self):
        """A run of background is a run of nobody; folding it in overstates compressibility."""
        self.assertTrue(RN.the_populations_are_reported_apart())

    def test_the_lattice_is_more_coherent_than_the_adversarial_corpus(self):
        """The scoping, as a law rather than a caveat a reader has to remember."""
        self.assertTrue(RN.the_lattice_is_more_coherent_than_the_adversarial_corpus())

    def test_the_observations_are_the_whole_frame_for_the_all_population(self):
        for c in RN.CORPORA:
            n = len(RN.ADVERSARIAL) if c == "adversarial" else len(RN.LATTICE)
            self.assertEqual(RN.structure(c, "all")["observations"], VR.W * VR.H * n)

    def test_coverage_falls_as_the_threshold_rises(self):
        for c in RN.CORPORA:
            s = RN.structure(c)
            seq = [s["cover%d" % m] for m in RN.COVERAGE]
            self.assertEqual(seq, sorted(seq, reverse=True))

    def test_the_percentiles_are_ordered(self):
        for c in RN.CORPORA:
            s = RN.structure(c)
            self.assertLessEqual(s["median"], s["p90"])
            self.assertLessEqual(s["p90"], s["p99"])
            self.assertLessEqual(s["p99"], s["max"])


class TheSurvival(unittest.TestCase):
    def test_the_survival_classes_are_exhaustive_and_disjoint(self):
        self.assertTrue(RN.the_survival_classes_are_exhaustive_and_disjoint())

    def test_long_runs_fragment_rather_than_disappear(self):
        """THE FINDING. Reddens the day disappearance overtakes fragmentation by length."""
        self.assertTrue(RN.long_runs_fragment_rather_than_disappear())

    def test_the_finding_is_not_the_saturation_result(self):
        """`voxstate`'s saturation is about DEPTH and still holds; this is about OWNERSHIP."""
        self.assertTrue(RN.the_finding_is_not_the_saturation_result())
        self.assertTrue(VT.the_observable_distance_is_saturated())

    def test_disappearance_is_the_smallest_class_by_length(self):
        by_len = {f: RN.survival()[f][1] for f in RN.FATES}
        self.assertEqual(min(by_len, key=by_len.get), "disappeared")

    def test_the_longest_runs_are_the_ones_that_break(self):
        """Short runs vanish, middling runs survive, LONG ones fragment. The weightings disagree and
        the disagreement is the finding: by count most runs survive, by length most fragments."""
        self.assertTrue(RN.the_longest_runs_are_the_ones_that_break())
        by_count = {f: RN.survival()[f][0] for f in RN.FATES}
        by_len = {f: RN.survival()[f][1] for f in RN.FATES}
        self.assertEqual(max(by_count, key=by_count.get), "survived")
        self.assertEqual(max(by_len, key=by_len.get), "fragmented")

    def test_the_mean_lengths_are_monotone_across_the_fates(self):
        seq = [RN.mean_length_tenths(f) for f in ("disappeared", "survived", "fragmented")]
        self.assertEqual(seq, sorted(seq))

    def test_an_unknown_fate_has_no_mean_length(self):
        with self.assertRaises(RN.VoxrunError):
            RN.mean_length_tenths("thrived")

    def test_the_shares_are_exact_integer_tenths(self):
        for f in RN.FATES:
            for by in ("count", "length"):
                self.assertIsInstance(RN.survival_share(f, by), int)

    def test_the_shares_very_nearly_sum_to_one(self):
        """Floor division loses at most a tenth per class, and never more."""
        for by in ("count", "length"):
            total = sum(RN.survival_share(f, by) for f in RN.FATES)
            self.assertLessEqual(total, 1000)
            self.assertGreaterEqual(total, 1000 - len(RN.FATES))

    def test_an_unknown_fate_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.survival_share("thrived")

    def test_an_unknown_weighting_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.survival_share("survived", "vibes")

    def test_survival_is_measured_only_where_an_adjacency_exists(self):
        """The adversarial corpus has none; a survival figure across it would measure its design."""
        self.assertEqual(len(RN.Z3_PRED), len(RN.LATTICE))
        self.assertIsNone(RN.Z3_PRED[0])
        self.assertEqual(sum(1 for p in RN.Z3_PRED if p is not None), len(RN.LATTICE) - 1)


class TheStream(unittest.TestCase):
    def test_no_economics_are_claimed(self):
        """The boundary between a census and the business it exists to decide on."""
        self.assertTrue(RN.no_economics_are_claimed())

    def test_every_stream_variable_is_recorded(self):
        for n in RN.STREAM:
            self.assertGreater(RN.stream_variable(n), 0)

    def test_the_variables_are_never_combined_by_this_module(self):
        """Recorded separately; combining them is the stream rung's whole job. Checked on the AST,
        not on the text: the docstring legitimately QUOTES the inequality a later rung must score,
        and a substring search cannot tell a quotation from a computation."""
        import ast as _ast
        with open(os.path.join(_ROOT, "tools", "terrain", "voxrun.py"), encoding="utf-8") as fh:
            src = fh.read()

        def calls_stream(node):
            return (isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name)
                    and node.func.id == "stream_variable")

        for node in _ast.walk(_ast.parse(src)):
            if isinstance(node, _ast.BinOp):
                self.assertFalse(calls_stream(node.left) and calls_stream(node.right))
            if isinstance(node, _ast.Compare):
                self.assertFalse(calls_stream(node.left)
                                 and any(calls_stream(c) for c in node.comparators))

    def test_an_unknown_stream_variable_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.stream_variable("wishful")

    def test_retired_is_the_surviving_length(self):
        self.assertEqual(RN.stream_variable("retired"), RN.survival()["survived"][1])


class ThePercentages(unittest.TestCase):
    """The second occurrence of a failure `voxtile` already paid for."""

    def test_the_percentages_in_the_prose_are_the_measured_ones(self):
        self.assertTrue(RN.the_percentages_in_the_prose_are_the_measured_ones())

    def test_the_percentage_law_catches_the_drift_it_was_built_for(self):
        """Run over the exact figure the first draft of this docstring got wrong."""
        self.assertTrue(RN.the_percentage_law_catches_the_drift_it_was_built_for())
        self.assertEqual(RN.unattributed_percentages("53.8 per cent", exempt=()), ("53.8",))

    def test_every_declared_percentage_is_rendered_at_its_declared_precision(self):
        """The shared law checks a rendering at ITS OWN precision, so a coverage figure may be a
        whole number and a share a tenth. What must hold is that the rendering carries exactly the
        digits the declaration says and no more."""
        import attributed as AT
        for n in RN.PERCENTS:
            with self.subTest(percent=n):
                whole, _, frac = RN.percent_text(n).partition(".")
                self.assertTrue(whole.isdigit())
                self.assertEqual(len(frac), RN.PLACES[n])
                self.assertTrue(AT.truncates(RN.percent_text(n), *RN.percent_exact(n)))

    def test_the_complement_is_taken_on_the_exact_value(self):
        """THE DEFECT THIS MODULE SHIPPED. `not_disappeared` was one thousand tenths minus the
        TRUNCATED disappearing share, and a constant minus a floor is a ceiling: it printed 95.5
        where the measurement is 95.443673. The complement is now taken on the exact rational."""
        sv = RN.survival()
        total = sum(sv[f][1] for f in RN.FATES)
        self.assertEqual(RN.percent_exact("not_disappeared"),
                         (total - sv["disappeared"][1], total))
        self.assertEqual(RN.percent_text("not_disappeared"), "95.4")

    def test_the_declared_percentages_are_pairwise_distinct(self):
        vals = [RN.percent_text(n) for n in RN.PERCENTS]
        self.assertEqual(len(set(vals)), len(vals))

    def test_an_undeclared_percentage_name_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.percent_text("wishful")


class TheDependency(unittest.TestCase):
    def test_neither_corpus_is_imported(self):
        """`voxbaggage` learned this one commit ago; here it is built in rather than discovered."""
        self.assertTrue(RN.neither_corpus_is_imported())

    def test_the_fixtures_match_the_live_corpora(self):
        """A fixture nobody compares is a guess with a comment on it."""
        self.assertTrue(RN.the_fixtures_match_the_live_corpora(T8, VT))

    def test_the_adversarial_fixture_is_voxtrace8s_own(self):
        live = tuple((n, tuple(e), tuple(f)) for n, e, f in T8.trace8())
        self.assertEqual(live, tuple((n, tuple(e), tuple(f)) for n, e, f in RN.ADVERSARIAL))

    def test_the_lattice_fixture_is_voxstates_own(self):
        for i, (eye, fwd) in enumerate(RN.LATTICE):
            self.assertEqual(tuple(VT.state(i)[1]), eye)
            self.assertEqual(tuple(VT.state(i)[2]), fwd)

    def test_the_traversal_fixture_is_voxstates_own(self):
        seq, pred = VT.order("Z3")
        self.assertEqual(tuple(seq), RN.Z3_ORDER)
        self.assertEqual(tuple(pred[n] for n in range(len(VT.STATES))), RN.Z3_PRED)

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(RN.no_wall_clock_enters_this_rung())


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_ships_before_the_stream(self):
        self.assertTrue(RN.the_prediction_ships_before_the_stream())

    def test_the_prediction_names_no_result(self):
        self.assertTrue(RN.the_prediction_names_no_result())

    def test_the_prediction_declares_five(self):
        t = RN.prediction_text()
        self.assertEqual(sum(1 for ln in t.split("\n") if ln.startswith("predict ")), 5)

    def test_the_prediction_digest_is_pinned(self):
        self.assertEqual(RN.prediction_digest(), RN.golden("prediction"))

    def test_the_safety_contract_is_not_scored_as_a_prediction(self):
        t = RN.prediction_text()
        self.assertIn("NOT A PREDICTION", t)
        self.assertNotIn("predict R6", t)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(RN.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(RN.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(RN.a_tampered_row_refuses())

    def test_a_struct_row_naming_no_corpus_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\nstruct wishful all " + " ".join("1" * 12) + "\n")

    def test_a_struct_row_naming_no_population_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\nstruct lattice hopeful " + " ".join("1" * 12) + "\n")

    def test_a_fate_row_naming_no_fate_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\nfate thrived 1 2\n")

    def test_a_share_row_naming_no_fate_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\nshare thrived 1 2\n")

    def test_a_stream_row_naming_no_variable_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\nstream wishful 1\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(RN.generate(), RN._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in RN.SCENES:
            self.assertEqual(RN.scene_result(name), RN.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.scene_case("survival2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.golden("nope")


if __name__ == "__main__":
    unittest.main()
