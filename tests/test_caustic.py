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
               lambda n: n, lambda n: n + 1, "")
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

    def test_only_one_SOUND_law_is_affine(self):
        affine = [n for (n, *_r) in CA.LAWS if CA.is_affine(n)]
        sound_affine = [n for n in affine if CA.law(n)[1] != CA.KIND_FITTED]
        self.assertEqual(sound_affine, ["storecost.snapshot_bytes"])

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


if __name__ == "__main__":
    unittest.main()
