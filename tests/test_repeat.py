# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""repeat (URDRRPT1) — variance has levels, and 200 iterations in one process sample exactly one.

Every quantile `rollbench` has ever reported is a WITHIN-execution quantile. The hash seed, the
address-space layout and the allocator's starting state are fixed for the life of a process and were
never sampled at all. Kalibera and Jones: more iterations inside one execution CANNOT reduce
execution-level variance."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import repeat as RP                                          # noqa: E402
import rollbench as RB                                       # noqa: E402


class TheLaw(unittest.TestCase):
    def test_one_execution_can_separate_nothing(self):
        """THE FINDING, and it indicts every log this repository has produced."""
        self.assertTrue(RP.one_execution_can_separate_nothing())
        for gap in (1, 10 ** 3, 10 ** 9):
            with self.subTest(gap):
                self.assertEqual(RP.verdict(RP._arm(100, [0]), RP._arm(100 + gap, [0])),
                                 RP.UNDETERMINED)

    def test_more_iterations_do_not_help(self):
        """Kalibera and Jones, reproduced as a falsifier rather than cited."""
        self.assertTrue(RP.more_iterations_do_not_help())

    def test_the_three_verdicts_are_distinct(self):
        self.assertEqual(len({RP.SEPARATED, RP.INDISTINGUISHABLE, RP.UNDETERMINED}), 3)


class ThePlantsBite(unittest.TestCase):
    def test_below_the_floor_is_indistinguishable(self):
        self.assertTrue(RP.an_effect_below_the_between_spread_is_indistinguishable())

    def test_above_the_floor_separates(self):
        """NON-VACUITY: a law refusing every result would be a wall."""
        self.assertTrue(RP.an_effect_above_the_between_spread_separates())

    def test_the_same_gap_flips_with_the_floor(self):
        """The verdict must move with the SPREAD and not only with the gap — otherwise it is a
        threshold on the difference wearing a statistical name."""
        tight = RP.verdict(RP._arm(1000, [0, 1, 2]), RP._arm(1050, [0, 1, 2]))
        loose = RP.verdict(RP._arm(1000, [0, 500, 1000]), RP._arm(1050, [0, 500, 1000]))
        self.assertEqual(tight, RP.SEPARATED)
        self.assertEqual(loose, RP.INDISTINGUISHABLE)

    def test_empty_or_ragged_input_refuses(self):
        self.assertTrue(RP.an_empty_or_ragged_input_refuses())
        with self.assertRaises(RP.RepeatError) as ctx:
            RP.median([])
        self.assertEqual(ctx.exception.code, "REPEAT-REFUSE")

    def test_the_spread_refuses_below_the_minimum(self):
        with self.assertRaises(RP.RepeatError):
            RP.between_spread(RP._arm(100, [0]))


class TheLevelsStayApart(unittest.TestCase):
    def test_within_and_between_are_reported_separately(self):
        self.assertTrue(RP.the_two_levels_are_reported_apart())
        r = RP.report(RP._arm(1000, [0, 50, 100], jitter=tuple(range(40))),
                      RP._arm(1500, [0, 50, 100], jitter=tuple(range(40))))
        self.assertEqual(r["between"], 100)
        self.assertEqual(r["within"], 39)

    def test_an_undetermined_report_carries_no_numbers(self):
        """It must not hand back a gap that cannot be judged — that is how a floorless number gets
        quoted later."""
        r = RP.report(RP._arm(100, [0]), RP._arm(9999, [0]))
        self.assertEqual(r["verdict"], RP.UNDETERMINED)
        self.assertIsNone(r["gap"])
        self.assertIsNone(r["between"])


class TheArithmeticIsExact(unittest.TestCase):
    def test_integer_and_pinned(self):
        self.assertTrue(RP.the_arithmetic_is_integer_and_pinned())
        self.assertEqual(RP.median([1, 2, 3, 4]), 2)          # LOWER middle, declared
        self.assertEqual(RP.median([3, 1, 2]), 2)

    def test_no_division_anywhere_in_the_module(self):
        """A benchmark law introducing its own rounding choice has no business grading anyone —
        asserted on the SOURCE, since behaviour alone would not stop a mean appearing later."""
        import ast
        with open(os.path.join(_ROOT, "tools", "terrain", "repeat.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for n in ast.walk(tree):
            if isinstance(n, ast.BinOp):
                self.assertNotIsInstance(n.op, ast.Div)


class TheHarnessCarriesIt(unittest.TestCase):
    def test_the_row_carries_its_execution(self):
        self.assertIn("run", RB.ROW_FIELDS)
        self.assertTrue(RB.the_row_carries_its_execution_and_its_depths())

    def test_a_single_execution_log_reads_undetermined(self):
        self.assertTrue(RB.a_single_execution_log_cannot_separate_anything())

    def test_the_runner_accepts_a_run_count_and_refuses_a_bad_one(self):
        self.assertEqual(RB.runs_from(RB.parse_argv(["--bench", "--runs", "5"])), 5)
        self.assertEqual(RB.runs_from(RB.parse_argv(["--bench"])), 1)
        with self.assertRaises(RB.RollbenchError):
            RB.runs_from({"runs": "0"})
        with self.assertRaises(RB.RollbenchError):
            RB.runs_from({"runs": "many"})


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in RP.SCENES:
            with self.subTest(name):
                self.assertEqual(RP.scene_result(name), RP.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(RP.repeat_digest(), RP.golden("repeat"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RP.RepeatError):
            RP.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
