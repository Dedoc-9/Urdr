# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/recirc.py — RECIRCULATION ON THE FRONTIER (URDRRCC1).

  ONE STEP, ALWAYS — gamma.alpha is a closure operator, so idempotence is a theorem of the adjunction
    and the step count is a constant. It cannot be a per-capture defect.
  THE COLLAPSE IS DANGEROUS — 400 distinct raw sets become 5 fixed points, and an honest capture
    collides with a doctored one. Fixed-point equality is WEAKER than raw equality.
  THE SALVAGE — refining the level when the iteration stalls is genuinely multi-step and bounded by
    the LEVEL ladder, not the cell count.

Every test can go red (L5); both plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import recirc as RC                                                # noqa: E402
import disjoint as DJ                                              # noqa: E402


class TheClosureCollapsesTheIteration(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in RC.SCENES:
            self.assertEqual(RC.scene_result(n), RC.golden(n), n)
            self.assertEqual(RC.scene_result(n), RC.scene_result(n), n)

    def test_gamma_alpha_is_a_closure_operator(self):
        """Extensive, monotone, idempotent — and idempotence is what collapses the iteration."""
        self.assertTrue(RC.is_extensive())
        self.assertTrue(RC.is_monotone())
        self.assertTrue(RC.is_idempotent())

    def test_iteration_converges_in_at_most_one_step(self):
        self.assertTrue(RC.converges_in_at_most_one_step())
        self.assertLessEqual(max(RC.step_counts()), 1)
        self.assertEqual(RC.step_counts(), (1, 1, 1, 1, 1, 1, 0, 0))

    def test_the_step_count_plant_is_constant(self):
        """L15 — a metric that does not vary with what it measures cannot measure it."""
        self.assertTrue(RC.step_count_is_constant())
        vals = {RC._step_count_as_defect(P) for P in RC._samples()}
        self.assertLessEqual(vals, {0, 1})


class TheCollapseIsDangerous(unittest.TestCase):
    def test_distinct_captures_share_a_fixed_point(self):
        raw, fixed = RC.collapse_census()
        self.assertEqual((raw, fixed), (400, 5))
        self.assertLess(fixed, raw, "the closure must be coarser")
        self.assertTrue(RC.fixed_point_is_a_weaker_check())

    def test_an_honest_capture_collides_with_a_doctored_one(self):
        """The case that matters: the proposed check is blind to the omission attack geoquorum
        exists to catch."""
        raw_differ, closures_collide = RC.doctored_collides_with_honest()
        self.assertTrue(raw_differ, "the raw sets must differ")
        self.assertTrue(closures_collide, "and the closures must NOT — which is the refutation")

    def test_the_integrity_plant_conflates_them(self):
        """L15 — raw equality sees what the proposed fixed-point check cannot."""
        self.assertTrue(RC.raw_equality_sees_what_the_closure_cannot())
        dom = RC.pair_domain()
        honest, doctored = frozenset(dom[:12]), frozenset(dom[:11])
        self.assertNotEqual(honest, doctored)
        self.assertTrue(RC._fixedpoint_as_integrity(honest, doctored))


class TheSalvage(unittest.TestCase):
    def test_refinement_is_bounded_by_levels_not_cells(self):
        """The honest termination bound — a level ladder of size 3, not |cells|."""
        self.assertTrue(RC.refinement_steps_are_level_bounded())
        n_levels = DJ.LEVELS + 1
        for P in RC._samples():
            _fp, steps, _lv = RC.refine_to_fixed_point(P)
            self.assertLessEqual(steps, n_levels)
            self.assertGreater(steps, 0)

    def test_refinement_is_total(self):
        self.assertTrue(RC.refinement_is_total())

    def test_refinement_reaches_a_closed_set(self):
        for P in RC._samples()[:4]:
            fp, _s, lv = RC.refine_to_fixed_point(P)
            self.assertEqual(RC.closure(fp, RC.FAMILY, lv), fp, "the result must be closed")


class ThePinning(unittest.TestCase):
    def test_samples_and_domain_are_pinned(self):
        self.assertEqual(RC._samples(), RC._samples())
        self.assertEqual(RC.pair_domain(), RC.pair_domain())
        self.assertEqual(RC.collapse_census(), RC.collapse_census())

    def test_the_census_is_not_vacuous(self):
        """The vacuity law applied here: a collapse census over identical inputs would report a
        collapse that is really just a lack of variety."""
        raw, _fixed = RC.collapse_census()
        self.assertGreater(raw, 1, "the raw sample must contain distinct captures at all")


if __name__ == "__main__":
    unittest.main()
