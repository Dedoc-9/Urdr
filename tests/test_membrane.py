# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/membrane.py — THE SEMANTIC MEMBRANE (URDRMEM1).

  INVARIANCE — nine membranes, including hostile ones, produce the identical admitted set.
  ADVISORY IS STRUCTURAL — a membrane returns an ORDER; there is no channel for a verdict.
  THE ENERGY CORRECTION — reordering leaves E invariant; only DISCHARGE reduces it. A membrane that
    lowers E by itself is doing proof work, which is what advisory-not-authoritative forbids.
  TERMINATION IS FREE — E is a non-negative integer strictly decreasing, so nothing can starve.
  THE LATTICE ORDER IS A FINDING — checking length before duplication masks the specific failure.

Every test can go red (L5); all three plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import membrane as MB                                              # noqa: E402


class TheInvariance(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in MB.SCENES:
            self.assertEqual(MB.scene_result(n), MB.golden(n), n)
            self.assertEqual(MB.scene_result(n), MB.scene_result(n), n)

    def test_every_membrane_gives_the_identical_admitted_set(self):
        """THE THEOREM. Nine membranes, several deliberately hostile."""
        self.assertTrue(MB.invariance_holds())
        om = MB.obligations()
        ref = MB.admitted(om, MB.identity_membrane)
        for m in MB.MEMBRANES:
            self.assertEqual(MB.admitted(om, m), ref, m.__name__)
        self.assertGreaterEqual(len(MB.MEMBRANES), 9)

    def test_canalization_is_the_same_statement(self):
        """Waddington's endpoint-invariance-under-path-perturbation, kept under its own name because
        the biological framing makes the failure mode legible."""
        self.assertTrue(MB.canalization_holds())
        self.assertEqual(MB.canalization_holds(), MB.invariance_holds())

    def test_advisory_is_a_signature_not_a_discipline(self):
        self.assertTrue(MB.advisory_is_structural())
        import inspect
        for m in MB.MEMBRANES:
            params = list(inspect.signature(m).parameters)
            self.assertEqual(params[0], "omega", m.__name__)


class TheEnergyCorrection(unittest.TestCase):
    def test_reordering_leaves_energy_exactly_invariant(self):
        """The correction the handed-down statement needed: the membrane does NOT reduce E."""
        self.assertTrue(MB.reordering_leaves_energy_invariant())
        om = MB.obligations()
        for m in MB.MEMBRANES:
            self.assertEqual(MB.energy(m(om)), MB.energy(om), m.__name__)

    def test_only_discharge_reduces_energy(self):
        self.assertTrue(MB.discharge_strictly_decreases_energy())

    def test_energy_is_a_nonnegative_integer(self):
        """Which is what makes termination free rather than something to prove separately."""
        e = MB.energy(MB.obligations())
        self.assertIsInstance(e, int)
        self.assertGreaterEqual(e, 0)
        self.assertEqual(e, 780)

    def test_termination_and_no_starvation(self):
        self.assertTrue(MB.terminates_within_energy())
        self.assertTrue(MB.membrane_cannot_starve())
        om = MB.obligations()
        self.assertIn(om[0], set(MB.starving_membrane(om)),
                      "the starved obligation is still discharged")


class ThePlantsBite(unittest.TestCase):
    def test_each_plant_is_refused_with_its_own_name(self):
        self.assertTrue(MB.plants_are_refused())
        om = MB.obligations()
        self.assertEqual(MB.check_membrane(om, MB._membrane_that_filters(om)), MB.R_DROPPED)
        self.assertEqual(MB.check_membrane(om, MB._membrane_that_injects(om)), MB.R_INJECTED)
        self.assertEqual(MB.check_membrane(om, MB._membrane_that_discharges(om)), MB.R_DROPPED)

    def test_the_lattice_order_is_itself_a_finding(self):
        """A same-length proposal carrying a duplicate must report DUPLICATED, not INJECTED. Testing
        length first masks the specific failure behind the coarser one."""
        om = MB.obligations()
        dup = tuple(om[:-1]) + (om[0],)
        self.assertEqual(len(dup), len(om), "same length — only duplication distinguishes it")
        self.assertEqual(MB.check_membrane(om, dup), MB.R_DUPLICATED)
        self.assertEqual(MB._REASON_NAME[MB.R_DUPLICATED], "MEMBRANE-DUPLICATED")

    def test_were_the_refusal_lifted_the_plants_would_change_the_admitted_set(self):
        """L15 — which is why it is a refusal and not a warning."""
        self.assertEqual(MB.plants_would_change_the_admitted_set(), 2)

    def test_a_malformed_proposal_raises_rather_than_degrades(self):
        om = MB.obligations()
        with self.assertRaises(MB.MembraneError):
            MB.admitted(om, MB._membrane_that_filters)
        with self.assertRaises(MB.MembraneError):
            MB.admitted(om, MB._membrane_that_injects)


if __name__ == "__main__":
    unittest.main()
