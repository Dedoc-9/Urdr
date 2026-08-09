# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `caustic` (URDRCAU1) — the scale at which a pinned law spends its budget.

The module exists because generalizing `sealframe`'s caustic across subsystems would have
propagated its defect: a slope whose axis label was wrong. So the falsifiers here are mostly
about the REFUSALS — a generalization that cannot say no is how one error becomes five."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics", "render"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import caustic as CA                                        # noqa: E402


class TheClosedFormsAreCheckedNotQuoted(unittest.TestCase):
    def test_model_equals_execution_for_every_law(self):
        """Run, not quoted from the module that pinned it. A closed form agreeing with its own
        restatement proves that arithmetic is deterministic (L23) — these agree with the WORK."""
        for (name, *_r) in CA.LAWS:
            with self.subTest(name):
                self.assertTrue(CA.model_equals_execution(name))

    def test_every_law_is_monotone_over_its_domain(self):
        for (name, *_r) in CA.LAWS:
            self.assertTrue(CA.is_monotone(name))

    def test_the_check_can_fail(self):
        """NON-VACUITY: a law whose form disagrees with its execution must be caught."""
        bad = ("planted", CA.KIND_PROVEN, "n", "u", (1, 2, 3),
               lambda n: n, lambda n: n + 1, "", "CORE")
        real = CA.LAWS
        try:
            CA.LAWS = real + (bad,)
            self.assertFalse(CA.model_equals_execution("planted"))
            with self.assertRaises(CA.CausticError):
                CA.caustic("planted", 2)
        finally:
            CA.LAWS = real


class TheRefusalsAreTheMechanism(unittest.TestCase):
    def test_a_fitted_law_is_refused_by_name(self):
        with self.assertRaises(CA.CausticError) as ctx:
            CA.caustic("sealframe.synthetic_primitives", 39000)
        self.assertIn("COVERAGE", str(ctx.exception))

    def test_the_refusal_is_selective(self):
        """A refuser that refuses everything is as useless as one that refuses nothing."""
        self.assertTrue(CA.the_refusal_is_selective())

    def test_a_budget_outside_the_verified_domain_is_refused(self):
        """The domain IS part of the law. Answering past where the form was checked against
        execution would extrapolate a formula — the move this module exists to refuse."""
        with self.assertRaises(CA.CausticError) as ctx:
            CA.caustic("storecost.snapshot_bytes", 10 ** 12)
        self.assertIn("NOT BINDING", str(ctx.exception))

    def test_an_unknown_law_is_refused(self):
        with self.assertRaises(CA.CausticError):
            CA.caustic("nothing.at.all", 10)

    def test_every_kind_is_populated(self):
        """L61 — including the REFUSING kind, whose member is the slope that produced the defect."""
        self.assertTrue(CA.every_kind_is_populated())


class TheCausticIsExact(unittest.TestCase):
    def test_the_answer_brackets_the_budget(self):
        """The defining property, checked rather than the computation restated: the caustic fits
        and one more does not."""
        for name, budget in CA.BUDGETS.items():
            if CA.law(name)[1] == CA.KIND_FITTED:
                continue
            with self.subTest(name):
                n = CA.caustic(name, budget)
                form = CA.law(name)[5]
                self.assertLessEqual(form(n), budget)
                self.assertGreater(form(n + 1), budget)

    def test_deterministic(self):
        self.assertEqual(CA.caustic_digest(), CA.caustic_digest())


class MostPinnedLawsAreNotLinear(unittest.TestCase):
    """THE FINDING, and it was not the one expected. The first `caustic` divided by a single slope
    and so demanded affineness — which refused THREE OF FOUR registered laws on its first run.
    `warden_edge_checks` is quadratic in grid side; `raster_samples` is sublinear in subdivision
    level because bounding-box slack grows slower than the count. Only `snapshot_bytes` is
    actually linear in the axis it names.

    That makes every `headroom x N` reading elsewhere in the repository suspect — it is the exact
    arithmetic the affine version was about to commit — and it is why the mechanism bisects."""

    def test_the_affine_and_non_affine_laws_are_both_populated(self):
        """Both kinds present, so neither the bisection nor the affine report is decoration."""
        affine = [n for (n, *_r) in CA.LAWS if CA.is_affine(n)]
        rest = [n for (n, *_r) in CA.LAWS if not CA.is_affine(n)]
        self.assertTrue(affine and rest)
        self.assertIn("storecost.snapshot_bytes", affine)
        self.assertIn("opcost.warden_edge_checks", rest)

    def test_affineness_is_not_evidence_of_a_sound_axis(self):
        """THE SHARPEST FORM OF THE LESSON, and it was not written until the previous assertion
        went red for the right reason. The CONFOUNDED law is affine — PERFECTLY affine, an exact
        equality, because every added triangle contributes an equal bounding box. That beautiful
        linearity is precisely what made the wrong axis persuasive. So affineness and axis
        soundness are INDEPENDENT: a clean straight line through the data says nothing about
        whether the variable on the x-axis is the one doing the work."""
        self.assertTrue(CA.is_affine("sealframe.synthetic_primitives"))
        with self.assertRaises(CA.CausticError):
            CA.caustic("sealframe.synthetic_primitives", 39000)

    def test_affineness_is_reported_not_required(self):
        """The non-affine laws still answer — the demotion is what makes the module general."""
        self.assertFalse(CA.is_affine("opcost.warden_edge_checks"))
        self.assertIsInstance(CA.caustic("opcost.warden_edge_checks", 5000), int)


class TheFrozenDivisionBridge(unittest.TestCase):
    """THE ONE REAL INSTANCE, CHECKED. §4 says: measure your host's cost-per-frozen-division once,
    multiply by the pinned counts, and the sim budget becomes an audit.

    Two things are wrong with taking that at face value. First it is CIRCULAR as stated:
    `frontbench.measure_samples` computes ns/division as tick-time DIVIDED BY the division count,
    so multiplying it back by that same count returns the number it started from and predicts
    nothing (L23). It only carries information when transferred to a DIFFERENT count — and that
    transfer was never checked.

    Second, checked here, it does not hold across scale. ns/division measured on this host runs
    ~3276 at one biped and converges to ~1468 by a hundred: a 2.2x drift, fixed per-call cost
    dominating at small n. So the bridge is sound in a CONVERGED REGIME and materially wrong below
    it, and §4 states the bridge without stating the regime.

    What IS exactly linear is the COUNT — `sim_tick_divisions(n) = 132n`, proven and registered.
    The count was never the problem; the cost per count was."""

    def test_the_division_count_is_exactly_linear_and_proven(self):
        self.assertTrue(CA.is_affine("frontbench.sim_tick_divisions"))
        self.assertTrue(CA.model_equals_execution("frontbench.sim_tick_divisions"))

    def test_the_count_law_is_counted_not_restated(self):
        """The execution side threads an instrumented divider through the real work, so the
        agreement is between a formula and a RUN rather than between a formula and itself."""
        form, execute = CA.law("frontbench.sim_tick_divisions")[5:7]
        for n in (1, 7, 25):
            self.assertEqual(form(n), execute(n))

    def test_the_caustic_lands_on_the_pinned_workload(self):
        """13 200 divisions is §4's pinned per-tick count, so the caustic at that budget must be
        the 100 bipeds it was measured on — the registry agreeing with the document."""
        self.assertEqual(CA.caustic("frontbench.sim_tick_divisions", 13200), 100)


if __name__ == "__main__":
    unittest.main()


class TheFourQuestions(unittest.TestCase):
    """L65 MECHANIZED. Five instrument defects landed in one session, every one invisible to a
    green gate, and each was a different one of these left unanswered: UNIT (ns/pixel was the
    wrong denominator), AXIS (linear in primitives was linear in coverage), LAYER (the observer
    was timed as the renderer), DOMAIN (a closed form trusted past where it was checked).

    A schema is the only form in which "state your denominator" survives the author who learned
    it — a habit is not inherited and a docstring is not enforced."""

    def test_every_registered_law_answers_all_four(self):
        self.assertTrue(CA.every_law_answers_four_questions())

    def test_the_layer_field_carries_information(self):
        """L61 on the schema itself: a classification every member shares is decoration."""
        self.assertTrue(CA.every_layer_is_populated())

    def test_a_law_missing_any_one_is_refused(self):
        real = CA.LAWS
        base = ("probe", CA.KIND_PROVEN, "n", "u", (1, 2, 3), lambda n: n, lambda n: n, "", "CORE")
        broken = {"no layer": base[:8] + ("NOPE",),
                  "no unit": base[:3] + ("",) + base[4:],
                  "no axis": base[:2] + ("",) + base[3:],
                  "degenerate domain": base[:4] + ((5,),) + base[5:]}
        try:
            for label, entry in broken.items():
                with self.subTest(label):
                    CA.LAWS = real + (entry,)
                    self.assertFalse(CA.answers_four_questions("probe"))
                    with self.assertRaises(CA.CausticError):
                        CA.caustic("probe", 2)
        finally:
            CA.LAWS = real
