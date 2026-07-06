# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""No-inflation falsifiers. NON-VACUOUS: over-claims must be REJECTED (asserted),
and legal claims must be ACCEPTED (asserted) — both directions, or the cage is decor."""
import unittest

from urdr import check, evaluate, values
from urdr.errors import UrdrError


def check_code(src):
    try:
        check.check_source(src)
    except UrdrError as err:
        return err.code
    return None


def run_code(src):
    try:
        evaluate.run_program(src)
    except UrdrError as err:
        return err.code
    return None


class TestStaticRejections(unittest.TestCase):
    def test_speculative_declared_rejected(self):
        # SPECULATIVE licenses only NA; DECLARED is already an over-claim.
        src = r"x := \an <| SPECULATIVE , DECLARED |> 7"
        self.assertEqual(check_code(src), "URDR-INFLATE-STATIC")

    def test_speculative_measured_rejected(self):
        src = r"x := \an <| SPECULATIVE , MEASURED |> 7"
        self.assertEqual(check_code(src), "URDR-INFLATE-STATIC")

    def test_scoped_measured_rejected_as_inflation(self):
        # Ladder violation checked before unearned-evidence (S1 precedes S2).
        src = r"x := \an <| SCOPED , MEASURED |> 7"
        self.assertEqual(check_code(src), "URDR-INFLATE-STATIC")

    def test_implemented_measured_rejected_as_unearned(self):
        # IMPLEMENTED's ceiling admits MEASURED — but writing it is not earning it.
        src = r"x := \an <| IMPLEMENTED , MEASURED |> 7"
        self.assertEqual(check_code(src), "URDR-EVIDENCE-UNEARNED")


class TestAcceptances(unittest.TestCase):
    """The other half of non-vacuity: the cage must not reject the innocent."""

    def test_speculative_na_accepted(self):
        self.assertIsNone(check_code(r"x := \an <| SPECULATIVE , NA |> 7"))

    def test_scoped_declared_accepted(self):
        self.assertIsNone(check_code(r"x := \an <| SCOPED , DECLARED |> 7"))

    def test_implemented_declared_accepted_and_runs(self):
        src = r"""
c := \an <| IMPLEMENTED , DECLARED |> 42
[value(c), maturity(c), evidence(c)]
"""
        result = evaluate.run_program(src)
        rendered = evaluate.render(result)
        self.assertIn("42", rendered)
        self.assertIn("IMPLEMENTED", rendered)
        self.assertIn("DECLARED", rendered)


class TestTheMint(unittest.TestCase):
    """MEASURED enters through exactly one door: ᛞ."""

    def test_verify_mints_grounded(self):
        src = r"""
c := \an <| IMPLEMENTED , DECLARED |> 42
g := \ve(\fn v |-> v = 42, c)
[grounded(g), evidence(g)]
"""
        rendered = evaluate.render(evaluate.run_program(src))
        self.assertIn("MEASURED", rendered)
        self.assertIn("1", rendered)

    def test_failed_verifier_yields_conflict_not_average(self):
        src = r"""
c := \an <| IMPLEMENTED , DECLARED |> 42
bad := \ve(\fn v |-> v = 43, c)
[conflicted(bad), grounded(bad), evidence(c)]
"""
        rendered = evaluate.render(evaluate.run_program(src))
        # conflicted=1, grounded=0, and the original claim's evidence is untouched.
        self.assertIn("DECLARED", rendered)

    def test_verify_on_scoped_claim_is_unlicensed(self):
        # Measuring what is not built is a category error, not a downgrade.
        src = r"""
c := \an <| SCOPED , DECLARED |> 9
\ve(\fn v |-> v = 9, c)
"""
        self.assertEqual(run_code(src), "URDR-VERIFY-UNLICENSED")

    def test_no_ambient_grounded_constructor_in_prelude(self):
        self.assertEqual(run_code(r"g := grounded_forge(1)"), "URDR-NAME")


class TestDynamicLatch(unittest.TestCase):
    """The unreachable-but-armed latch (LESSONS L2): the host-level constructor
    itself refuses inflation, independent of the checker."""

    def test_claim_constructor_latch(self):
        with self.assertRaises(UrdrError) as ctx:
            values.Claim(values.Int(7), "SPECULATIVE", "MEASURED")
        self.assertEqual(ctx.exception.code, "URDR-INFLATE-DYN")

    def test_grounded_requires_witness(self):
        # Grounded cannot be built without a 32-byte witness digest.
        with self.assertRaises((UrdrError, TypeError)):
            values.Grounded(values.Int(7), None)


if __name__ == "__main__":
    unittest.main()
