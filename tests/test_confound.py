# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""confound (URDRCNF1) — a treatment axis may not be a proxy for elapsed time, and a cell is not an
experiment.

RED-FIRST, AND THE RED CAME FROM A REAL HOST LOG. `rollbench` v1.2 reported `narrowed` faster than
`moulded` in 23 of 28 cells — while `narrowed` executes `moulded`'s timed path PLUS a widths tuple
that replay never reads. A representation doing strictly more work cannot be faster, so the log was
measuring something else: `cells()` iterated representation-outermost, putting `flat` at run
positions 0-27 and `narrowed` at 56-83, perfectly aligned with the machine warming up."""
import os
import statistics
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import confound as CF                                        # noqa: E402
import measure as MS                                         # noqa: E402
import rollbench as RB                                       # noqa: E402


class TheLaw(unittest.TestCase):
    def test_no_axis_is_confounded(self):
        """The fixture the scenes pin, AND the live plan the harness actually runs."""
        self.assertTrue(CF.no_axis_is_confounded())
        for cells in (CF.FIXTURE, tuple(MS.bench_cells())):
            for a in CF.AXES:
                with self.subTest(f"{len(cells)}:{a}"):
                    self.assertEqual(CF.verdict(CF.schedule(cells), a), CF.BALANCED)

    def test_the_module_imports_nothing_from_this_tree(self):
        """THE LATTICE CAUGHT THE FIRST DRAFT. Reading `measure` for the live plan put a node
        between the harness and the plan and pushed `reachable` to import-depth 14 against a sealed
        ceiling of 13 — and the depth proof was right about more than depth: a detector that grades
        SCHEDULES has no business knowing what a rollback benchmark is."""
        import ast
        with open(os.path.join(_ROOT, "tools", "terrain", "confound.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods.update(a.name.split(".")[0] for a in n.names)
            if isinstance(n, ast.ImportFrom) and n.module:
                mods.add(n.module.split(".")[0])
        self.assertEqual(mods - {"hashlib", "os", "statistics", "math"}, set())

    def test_the_harness_actually_uses_the_schedule(self):
        """A schedule nothing runs is a claim. `rollbench.run_order` must BE the graded order."""
        self.assertEqual(RB.run_order(), CF.schedule(RB.cells()))
        self.assertNotEqual(RB.run_order(), RB.cells())
        self.assertTrue(RB.the_run_order_is_not_the_plan_order())


class ThePlantsBite(unittest.TestCase):
    def test_the_shipped_order_reads_confounded(self):
        """Not a constructed example — the order that produced the host log."""
        self.assertTrue(CF.the_old_schedule_is_confounded())
        old = tuple(MS.bench_cells())
        self.assertEqual(CF.verdict(old, "representation"), CF.CONFOUNDED)
        self.assertTrue(CF.blocked(old, "representation"))

    def test_the_blocks_are_the_thirds_the_log_showed(self):
        """The exact defect, in positions: three representations, three disjoint contiguous runs."""
        old = tuple(MS.bench_cells())
        pos = CF.positions(old, "representation")
        self.assertEqual(len(pos), len(MS.REPRESENTATIONS))
        spans = sorted((min(p), max(p)) for p in pos.values())
        self.assertEqual(spans, [(0, 27), (28, 55), (56, 83)])
        for lo, hi in spans:
            self.assertEqual(hi - lo + 1, 28)

    def test_interleaved_but_skewed_is_a_separate_verdict(self):
        """CONFOUNDED and SKEWED fail differently. A detector with only the block test would call a
        merely front-loaded factor balanced."""
        self.assertTrue(CF.a_merely_interleaved_schedule_can_still_be_skewed())
        self.assertEqual(len({CF.BALANCED, CF.CONFOUNDED, CF.SKEWED}), 3)

    def test_a_stride_sharing_a_factor_refuses(self):
        self.assertTrue(CF.a_stride_sharing_a_factor_refuses())
        with self.assertRaises(CF.ConfoundError) as ctx:
            CF.schedule(MS.bench_cells(), stride=2)
        self.assertEqual(ctx.exception.code, "CONFOUND-REFUSE")

    def test_an_empty_plan_refuses(self):
        with self.assertRaises(CF.ConfoundError):
            CF.schedule(())

    def test_an_unknown_axis_refuses(self):
        with self.assertRaises(CF.ConfoundError):
            CF.positions(CF.schedule(MS.bench_cells()), "temperature")


class TheScheduleIsAPermutation(unittest.TestCase):
    def test_every_cell_exactly_once(self):
        self.assertTrue(CF.every_cell_is_visited_exactly_once())

    def test_no_randomness_is_used(self):
        """Determinism is the floor. Randomisation would balance just as well and is refused,
        because a seed is one more thing a result can depend on — asserted on the SOURCE."""
        with open(os.path.join(_ROOT, "tools", "terrain", "confound.py"), encoding="utf-8") as fh:
            src = fh.read()
        import ast
        names = set()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                names.update(a.name.split(".")[0] for a in n.names)
            if isinstance(n, ast.ImportFrom) and n.module:
                names.add(n.module.split(".")[0])
        self.assertNotIn("random", names)
        self.assertNotIn("secrets", names)

    def test_the_schedule_is_stable_across_calls(self):
        self.assertEqual(CF.schedule(MS.bench_cells()), CF.schedule(MS.bench_cells()))


class TheStrideIsAMeasuredChoice(unittest.TestCase):
    def test_it_is_re_derived_by_search(self):
        """The pin is reproduced rather than trusted: search every co-prime stride against the
        criterion fixed in advance and STRIDE must be the smallest attaining the floor."""
        ok, floor, ties = CF.the_stride_is_optimal_by_search()
        self.assertTrue(ok)
        self.assertGreater(ties, 1)                          # several tie; the smallest is taken
        self.assertLess(floor, CF.TOLERANCE)

    def test_the_tolerance_is_non_vacuous_in_both_directions(self):
        """Below the structural floor no schedule could pass; above the shipped order's deviation
        it would admit the defect it exists to catch."""
        self.assertTrue(CF.the_tolerance_admits_the_floor_and_refuses_the_defect())
        shipped = CF.deviation(tuple(MS.bench_cells()), "representation")
        _ok, floor, _t = CF.the_stride_is_optimal_by_search()
        self.assertLess(floor, CF.TOLERANCE)
        self.assertLess(CF.TOLERANCE, shipped)

    def test_the_deviation_of_a_perfect_split_is_zero(self):
        """A sanity anchor for the metric itself: two levels alternating are exactly centred."""
        order = tuple(("A" if i % 2 == 0 else "B", "w", 1) for i in range(8))
        self.assertAlmostEqual(CF.deviation(order, "representation"), 0.5 / 8, places=9)


class ACellIsNotAnExperiment(unittest.TestCase):
    def test_a_repeated_key_is_one_experiment(self):
        self.assertTrue(CF.a_repeated_key_is_counted_as_one_experiment())
        self.assertEqual(CF.duplicates(("a", "a", "b")), (3, 2, 1))

    def test_the_counts_are_exact(self):
        cells, distinct, dupes = MS.bench_duplicate_count()
        self.assertEqual((cells, distinct, dupes), (28, 17, 11))
        self.assertEqual(cells - distinct, dupes)

    def test_all_airborne_collapses_five_depths_into_one(self):
        """The sharpest instance: five rows of the table, one experiment."""
        self.assertEqual(MS.bench_experiments()[("all_airborne", 2)], (2, 4, 8, 16, 32, 64))
        for d in (4, 8, 16, 32, 64):
            self.assertEqual(MS.effective_ticks("all_airborne", d), 2)

    def test_depth_and_ticks_part_company(self):
        """`depth` is the REQUEST, `ticks` is the WORK, and a table reporting only the first cannot
        be read as a table of experiments."""
        self.assertEqual(MS.effective_ticks("alternating", 4), 4)
        self.assertEqual(MS.effective_ticks("alternating", 64), 11)
        self.assertTrue(RB.the_row_carries_the_work_not_only_the_request())
        for f in ("ticks", "pos"):
            self.assertIn(f, RB.ROW_FIELDS)


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in CF.SCENES:
            with self.subTest(name):
                self.assertEqual(CF.scene_result(name), CF.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(CF.confound_digest(), CF.golden("confound"))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual([CF.scene_result(n) for n in CF.SCENES],
                         [CF.scene_result(n) for n in CF.SCENES])

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(CF.ConfoundError):
            CF.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
